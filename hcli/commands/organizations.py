import typer
from rich import print
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, set_field

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {token}"}
)


@app.command()
def list():
    organizations = core_api.request("GET", f"/organizations")
    table = Table()

    table.add_column("Name")
    table.add_column("Organization ID")

    for i in organizations.get("data"):
        table.add_row(i.get("name"), i.get("id"))

    print(table)


@app.command()
def set(organization_name: str):
    organizations = core_api.request(
        "GET", f"/search?resources=organizations&q=name:{organization_name}"
    )
    if len(organizations.get("data")) == 0:
        print(f"[red]no organization for name {organization_name} found")
    else:
        organization = organizations["data"][0]
        set_field("organization_id", organization["id"])

        print(
            f"[green]successfully set organization to [bold]{organization_name}[/bold]"
        )


@app.command()
def get():
    if organization_id:
        organization = core_api.request("GET", f"/organizations/{organization_id}")
        print(organization)
    else:
        print(
            "[red]No organization set. You can do so via [bold]hcli organizations set[/bold]"
        )
