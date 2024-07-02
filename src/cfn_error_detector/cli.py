import sys
from pathlib import Path

import click
from tzlocal import get_localzone

from .aws import get_stacks, rollback_stack
from .detector import detect
from .path_finder import find_stack_template

local_tz = get_localzone()

TypePath = click.types.Path(path_type=Path, exists=True)


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    # ctx.obj = App()
    pass


@main.command("detect")
@click.argument("stack_name", type=str, required=True)
@click.option("--template-file", "-t", type=TypePath, required=False, default=None)
def cmd_detect(stack_name: str, template_file: Path | None) -> None:
    stacks = get_stacks()
    error_events, stack_not_founds = detect(stacks, stack_name)

    for s in sorted(stack_not_founds, key=lambda s: s.stack_name):
        print(f"!! Stack not found: {s.stack_name}", file=sys.stderr)

    for index, ev in enumerate(sorted(error_events, key=lambda ev: ev.at)):
        print(f"[{index + 1}] {ev.at.astimezone(local_tz)}")
        print(f"  Status: {ev.status}")
        print(f"  ID: {ev.resource_id}")
        print(f"  Type: {ev.resource_type}")
        print(f"  Reason: {ev.reason}")
        print(f"  Stack: {" / ".join(ev.path)}")
        if template_file is not None:
            found_on = find_stack_template(template_file, ev.path)
            found_on = found_on.relative_to(template_file.parent)
            print(f"  Path: {found_on}")


@main.command("rollback")
@click.argument("stack_name", type=str, required=True)
def cmd_rollback(stack_name: str) -> None:
    if click.confirm("Are you sure you want to rollback?", abort=True):
        click.echo("Rollback starting...")
        rollback_stack(stack_name, True)
        click.echo("Rollback completed.")
    else:
        click.echo("Rollback cancelled.")


if __name__ == "__main__":
    main()
