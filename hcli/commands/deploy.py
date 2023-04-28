import os
import sys

import typer
import yaml
from rich import print

from hcli.api.utils import ApiClient
from hcli.utils.machines import get_machines_for_an_app, delete_machine, create_machine
from hcli.utils.permanent_storage import read_field, dir_path

priv_cert_path = dir_path + "/priv_cert.pem"

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "http://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {token}"},
)


def get_app(app: str) -> dict:
    try:
        return core_api.request(
            "POST", f"/organizations/{organization_id}/apps/search?limit=1&name={app}"
        )["data"][0]
    except:
        print(
            f"[red]couldn't find app with name [bold]{app}[/bold]. Make sure it exists by checking with [bold]hcli apps list[/bold][/red]"
        )
        sys.exit()


def deploy_to_app(filename: str = "huddu.yml") -> None:
    dir = os.getcwd()
    full_filename = f"{dir}/{filename}"

    with open(full_filename, "r") as f:
        configfile = yaml.safe_load(f.read())

    print("[green]Looking for your app...[/green]")
    app = get_app(configfile["app"])
    print(
        f"Found {app['name']}({app['id']}). Do you want to deploy to this application?"
    )
    if not typer.prompt("Are you sure? (y/n)") == "y":
        print("[red]Exiting...[/red]")
        sys.exit()

    to_delete = list(
        get_machines_for_an_app(app["id"], params={"meta.delete_on_redeploy": "true"})
    )
    if configfile.get("strategy", "blue/green").lower() == "recreate":
        print("Selected deployment strategy is recreate")
        print("Starting to delete machines")
        for i in to_delete:
            print(f"--- Deleting {i['name']} ({i['id']})")
            delete_machine(region=i["region"], instance_id=i["id"])
        print("Done deleting machines")

    print("[green]Trying to deploy your machines![/green]")

    machines = configfile.get("machines") if configfile.get("machines") else []

    print(f"--- {len(machines)} to go...")
    for i in machines:
        print(
            f"--- Starting to deploy machine for name [bold]{list(i.keys())[0]}[/bold]"
        )

        machine_info = list(i.values())[0]
        if not machine_info.get("region"):
            print("--- [yellow]No region set! Defaulting to us-central[/yellow]")

        create_machine(
            region=machine_info.get("region", "us-central"),
            app=app["id"],
            name=list(i.keys())[0],
            machine_type=machine_info.get("machine_type", "small-1"),
            disk_size=machine_info.get("disk_size", 10),
            meta={"delete_on_redeploy": i.get("delete_on_redeploy", True)},
        )
        configfile["machines"].remove(i)
        print(f"--- {len(machines)} more machines to go...")

    if configfile.get("strategy", "blue/green").lower() == "blue/green":
        print("Selected deployment strategy is blue/green")
        print("Starting to delete machines")
        for i in to_delete:
            print(f"--- Deleting {i['name']} ({i['id']})")
            delete_machine(region=i["region"], instance_id=i["id"])
        print("Done deleting machines")
    print("[green]done![/green]")
    print(
        "Need more info about this deployment? Check the dashboard: https://huddu.io/app"
    )
