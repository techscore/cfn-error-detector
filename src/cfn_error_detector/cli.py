import sys

import click
from tzlocal import get_localzone

from .aws import get_stacks, rollback_stack
from .detector import detect

local_tz = get_localzone()


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    # ctx.obj = App()
    pass


@main.command("detect")
@click.argument("stack_name", type=str, required=True)
def cmd_detect(stack_name: str) -> None:
    stacks = get_stacks()
    error_events, stack_not_founds = detect(stacks, stack_name)

    for s in sorted(stack_not_founds, key=lambda s: s.stack_name):
        print(f"!! Stack not found: {s.stack_name}", file=sys.stderr)

    for ev in sorted(error_events, key=lambda ev: ev.at):
        print(f"Stack: {" / ".join(ev.path)}")
        print(f"  At: {ev.at.astimezone(local_tz)}")
        print(f"  Status: {ev.status}")
        print(f"  Resource: {ev.resource_id} - {ev.resource_type}")
        print(f"  Reason: {ev.reason}")


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
