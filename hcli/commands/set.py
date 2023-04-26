import typer
from rich import print

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, set_field

app = typer.Typer()

core_api = ApiClient(
    "https://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {read_field('token')}"},
)


@app.command()
def organization(organization_id: str):
    organization = core_api.request("GET", f"/organizations/{organization_id}")
    print(organization)
    if organization.get("id"):
        print(
            f"[green]successfully set organization to `{organization.get('name')}` ({organization_id})[/green]"
        )
        set_field("organization_id", organization_id)
    else:
        print(f"[red]no organization found for id `{organization_id}`[/red]")
