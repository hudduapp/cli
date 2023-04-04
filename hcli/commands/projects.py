import typer
from rich import print
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, set_field
from hcli.utils.permissions import org_required

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")
project_id = read_field("project_id")

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {token}"}
)


@app.command()
def list():
    org_required()

    projects = core_api.request("GET", f"/organizations/{organization_id}/projects")
    table = Table()

    table.add_column("Name")
    table.add_column("Project ID")

    for i in projects.get("data"):
        table.add_row(i.get("name"), i.get("id"))

    print(table)


@app.command()
def set(project_name: str):
    org_required()
    projects = core_api.request(
        "GET",
        f"/search?resource=projects&organization={organization_id}&q=name:{project_name}",
    )
    if len(projects.get("data")) == 0:
        print(
            f"[red]no project for name {project_name} found (are you in the correct organization?)"
        )
    else:
        organization = projects["data"][0]
        set_field("project_id", organization["id"])

        print(f"[green]successfully set project to [bold]{project_name}[/bold]")


@app.command()
def get():
    org_required()
    if organization_id and project_id:
        project = core_api.request(
            "GET", f"/organizations/{organization_id}/projects/{project_id}"
        )
        print(project)
    else:
        print(
            "[red]No organization and/or project set. You can do so via [bold]hcli projects set[/bold]"
        )
