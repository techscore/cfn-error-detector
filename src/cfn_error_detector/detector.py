from datetime import datetime
from typing import Any, Tuple

from pydantic import BaseModel

from .aws import Event, Stack, get_stack_events, get_stack_resource_map


class ErrorEvent(BaseModel):
    at: datetime
    resource_id: str
    resource_type: str
    raw: Event
    path: list[str]
    status: str
    reason: str

    def new(raw: Event, path: list[str]) -> "ErrorEvent":
        return ErrorEvent(
            at=raw["Timestamp"],
            raw=raw,
            path=path,
            resource_type=raw["ResourceType"],
            resource_id=raw["LogicalResourceId"],
            status=raw["ResourceStatus"],
            reason=raw["ResourceStatusReason"],
        )


class StackNotFound(BaseModel):
    stack_name: str

    def __hash__(self) -> int:
        return hash(self.stack_name)


Detected = ErrorEvent | StackNotFound


def detect(stacks: list[Stack], stack_name: str) -> Tuple[list[ErrorEvent], set[StackNotFound]]:
    lefts: list[ErrorEvent] = []
    rights: set[StackNotFound] = set()

    for d in _detect(stacks, stack_name, path=[]):
        if isinstance(d, ErrorEvent):
            lefts.append(d)
        elif isinstance(d, StackNotFound):
            rights.add(d)
        else:
            raise ValueError(f"Unknown type: {d}")

    return lefts, rights


def _detect(stacks: list[Stack], stack_name: str, path: list[str] = []) -> list[Detected]:
    result: list[Detected] = []

    root_events = get_stack_events(stack_name)
    if root_events is None:
        return [StackNotFound(stack_name=stack_name)]

    recent_events = only_recent(root_events, stack_name)
    for event in recent_events:
        if not is_failure(event):
            continue
        if event["ResourceType"] == "AWS::CloudFormation::Stack":
            event_stack_name = stack_name_from_physical_id(event["PhysicalResourceId"])
            if event_stack_name == stack_name:
                continue
            in_nested = _detect(stacks, event_stack_name, path=[*path, event["LogicalResourceId"]])
            if 0 < len(in_nested):
                result.extend(in_nested)
                continue
        result.append(ErrorEvent.new(raw=event, path=path))

    return result


def stack_name_from_physical_id(physical_id: str) -> str:
    return physical_id.split("/")[1]


def is_failure(event: Any) -> bool:
    return event["ResourceStatus"] in ["CREATE_FAILED", "UPDATE_FAILED", "DELETE_FAILED"]


def is_stack_finish(event: Any, stack_name: str) -> bool:
    if not event["ResourceType"] == "AWS::CloudFormation::Stack":
        return False
    if not event["LogicalResourceId"] == stack_name:
        return False
    if event["ResourceStatus"] not in ["CREATE_COMPLETE", "UPDATE_COMPLETE", "UPDATE_ROLLBACK_COMPLETE"]:
        return False
    return True


def find_stack(stacks: list[Stack], by_name: str) -> None | Stack:
    for stack in stacks:
        if stack["StackName"] == by_name:
            return stack
    return None


def to_physical_id(parent_stack_name: str, logical_id: str) -> str:
    return get_stack_resource_map(parent_stack_name)[logical_id]["PhysicalResourceId"]


def find_nested_stack(stacks: list[Stack], by_name: str) -> None | Stack:
    for stack in stacks:
        if stack["StackName"] == by_name:
            return stack
    return None


def only_recent(events: list[Event], stack_name: str) -> list[Event]:
    found: None | int = None

    for i, event in enumerate(events):
        if is_stack_finish(event, stack_name):
            found = i
        else:
            break

    events = events[found + 1 :] if found is not None else events

    for i, event in enumerate(events):
        if is_stack_finish(event, stack_name):
            found = i
            break

    return events[:found] if found is not None else events
