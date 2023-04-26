import sys

from rich import print

from hcli.utils.permanent_storage import read_field

token = read_field("token")
organization_id = read_field("organization_id")
project_id = read_field("project_id")


def auth_required():
    if not token:
        print(
            "[red]You need to login to run this command. To do so run [bold]hcli auth login[/bold].[/red]"
        )
        sys.exit()


def org_required():
    if not organization_id:
        print(
            "[red]Please set a organization first. You can do so via [bold]hcli organizations set[/bold][/red]"
        )
        sys.exit()
