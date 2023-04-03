import typer
from rich import print

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, set_field

app = typer.Typer()

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {read_field('token')}"}
)


@app.command()
def organization(organization_id: str):
    organization = core_api.request("GET", f"/organizations/{organization_id}")
    print(organization)
    if organization.get("id"):
        print(f"[green]successfully set organization to `{organization.get('name')}` ({organization_id})[/green]")
        set_field("organization_id", organization_id)
    else:
        print(f"[red]no organization found for id `{organization_id}`[/red]")


@app.command()
def project(project_id: str):
    organization_id = read_field("organization_id")
    if not organization_id:
        print(f"[red]make sure to set an organization first using [bold]huddu set organization[/bold][/red]")
    else:
        project = core_api.request("GET", f"/organizations/{organization_id}/projects/{project_id}")
        if project.get("id"):
            print(f"[green]successfully set project to `{project.get('name')}` ({project_id})[/green]")
            set_field("project_id", project_id)
        else:
            print(f"[red]no project found for id `{project_id}`[/red]")
