import os

import typer
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.machines import get_machines_for_an_app, get_machine_api_client, Machine
from hcli.utils.permanent_storage import read_field, dir_path
from hcli.utils.permissions import auth_required, org_required
from hcli.utils.terminal.prompt import choice_prompt
from hcli.utils.terminal.render import print

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
        print(table, type="table")
        print(
            "Try running hcli apps get <app_name> to see more information on your apps"
        )
    else:
        print("No entries. You can create a new machine with huddu machines create")


@app.command()
def info(app_name: str, skip: int = 0):
    auth_required()
    org_required()
    print(f"Looking for your app and it's machines...")
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
        i = get_machine_api_client(i.get("api_endpoint")).request(
            "GET", f"/organizations/{organization_id}/machines/{i.get('id')}"
        )

        table.add_row(
            i.get("name"),
            f"[green]{i.get('status')}"
            if i.get("status") == "running"
            else i.get("status"),
            i.get("hostname"),
            i.get("internal_name"),
            i.get("external_ip"),
        )

    if len(instances["data"]):
        print(table, type="table")
    else:
        print("This app doesn't contain any instances yet.")


@app.command()
def connect(app_name: str):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/apps/search?limit=1&name={app_name}",
    )

    app = res.get("data")[0]

    print("Directly connect to an apps machine via ssh")
    machines = get_machines_for_an_app(app["id"])
    machines_list = []
    options = []

    for i in machines:
        machines_list.append(i)
        options.append(f"{i['name']} | {i['id']}")
    choice = choice_prompt("Choose a machine", choices=options)
    print("Starting to connect...")
    machine_id = choice.split(" | ")[1]
    machine = None
    for i in machines_list:
        if i["id"] == machine_id:
            machine = i

    machine_client = Machine(machine["region"])
    machine_info = machine_client.get_info(machine["id"])
    priv_cert_path = dir_path + "/priv_cert.pem"

    if not machine_info.get("status") == "running":
        print(
            f"Machine needs to be running but is in state: {machine_info.get('status')}",
            type="error",
        )
    else:
        os.system(f"sudo rm {priv_cert_path}")
        with open(priv_cert_path, "w") as f:
            f.write(machine_info["ssh"]["private_cert"])
            f.close()

        os.system(f"sudo chmod 400 {priv_cert_path}")
        os.system(f"ssh -i {priv_cert_path} admin@{machine_info['external_ip']}")

        print("Closed terminal session")


@app.command()
def delete_machines(app_name: str):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/apps/search?limit=1&name={app_name}",
    )

    app = res.get("data")[0]

    print(
        f"[yellow]This action might take a few seconds per machine (fell free to grab a coffee!)[/yellow]"
    )
    for i in get_machines_for_an_app(app["id"]):
        instance = Machine(i["region"])
        instance.delete(i["id"])
        print(f"Deleted machine with name {i['name']}", type="error")
