import json

import requests
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


def create_machine(
    base_url: str, organization: str, app: str, machine_config: dict
) -> None:
    machine_config["app"] = app
    requests.request(
        "POST",
        base_url + f"/organizations/{organization}/machines",
        data=json.dumps(machine_config),
        headers={"Authorization": f"Token {token}"},
    )


@app.command()
def deploy():
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"organizations/{organization_id}/resources/search?type=machine&limit=10&skip={skip}",
    )

    table = Table()

    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Machine ID")
    table.add_column("Machine IP")
    table.add_column("Machine Type")

    for i in res.get("data"):
        table.add_row(
            i.get("name"),
            f"[green]{i.get('status')}"
            if i.get("status") == "running"
            else i.get("status"),
            i.get("id"),
            i.get("external_ip"),
            i.get("machine_type"),
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No entries. You can create a new machine with huddu machines create")
