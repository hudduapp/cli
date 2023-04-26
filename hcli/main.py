import typer
from rich import print

from hcli.api.utils import ApiClient
from hcli.commands import apps
from hcli.commands import auth
from hcli.commands import machines
from hcli.commands import organizations
from hcli.commands import set
from hcli.utils.permanent_storage import read_field

app = typer.Typer()

app.add_typer(organizations.app, name="organizations")
app.add_typer(set.app, name="set")
app.add_typer(apps.app, name="apps")
app.add_typer(auth.app, name="auth")
app.add_typer(machines.app, name="machines")


@app.command()
def info():
    project_id = read_field("project_id")
    organization_id = read_field("organization_id")

    core_api = ApiClient(
        "https://public-api-duqqqjtkbq-uc.a.run.app",
        headers={"Authorization": f"Token {read_field('token')}"},
    )

    project = None
    organization = None

    if project_id:
        project = core_api.request(
            "GET", f"/organizations/{organization_id}/projects/{project_id}"
        )

    if organization_id:
        organization = core_api.request("GET", f"/organizations/{organization_id}")

    me = core_api.request("GET", f"/me")

    print("[bold]Currently set organization[/bold]")
    print(
        organization
        if organization
        else "[red]No organization set (use huddu set organization `organization_id`)"
    )

    print("\n[bold]Currently set project[/bold]")
    print(
        project
        if project
        else "[red]No project set (use huddu set project `project_id`)"
    )

    print("\n[bold]Your account[/bold]")
    print(me)


if __name__ == "__main__":
    app()
