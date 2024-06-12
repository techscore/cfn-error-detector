from typing import Any

import boto3

Stack = Any
Event = Any

_cfn = boto3.client("cloudformation")

from .cache import Cache


@Cache
def get_stacks() -> list[Stack]:
    return _cfn.describe_stacks()["Stacks"]


@Cache
def get_stack_resource_map(stack_name: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for stack in _cfn.describe_stack_resources(StackName=stack_name)["StackResources"]:
        result[stack["LogicalResourceId"]] = stack
    return result


@Cache
def get_stack_events(stack_name: str) -> list[Event] | None:
    try:
        return _cfn.describe_stack_events(StackName=stack_name)["StackEvents"]
    except _cfn.exceptions.ClientError as e:
        if e.response["Error"]["Message"] == "Stack [{}] does not exist".format(stack_name):
            return None
        raise e


def rollback_stack(stack_name: str, do_wait: bool) -> None:
    _cfn.rollback_stack(StackName=stack_name)
    if not do_wait:
        return
    waiter = _cfn.get_waiter("stack_rollback_complete")
    waiter.wait(StackName=stack_name)
