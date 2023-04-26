import typer
from rich import print
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, dir_path
from hcli.utils.permissions import auth_required, org_required

priv_cert_path = dir_path + "/priv_cert.pem"

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "http://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {token}"},
)


@app.command()
def list(skip: int = 0):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"organizations/{organization_id}/apps/search?limit=10&skip={skip}",
    )

    table = Table()

    table.add_column("Name")
    table.add_column("ID")

    for i in res.get("data"):
        table.add_row(
            i.get("name"),
            i.get("id"),
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No entries. You can create a new machine with huddu machines create")


@app.command()
def get(app_name: str, skip: int = 0):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/apps/search?limit=1&name={app_name}",
    )

    app = res.get("data")[0]
    instances = core_api.request(
        "GET",
        f"/organizations/{organization_id}/instances/search?limit=10&skip={skip}&app={app['id']}",
    )

    print(f"You're viewing instances for [bold]{app['name']}[/bold]:")

    table = Table()

    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Hostname")
    table.add_column("Internal Name")
    table.add_column("External Ip")

    for i in instances.get("data"):
        table.add_row(
            i.get("name"),
            f"[green]{i.get('status')}"
            if i.get("status") == "running"
            else i.get("status"),
            i.get("hostname"),
            i.get("internal_name"),
            i.get("external_ip"),
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No instances.")
