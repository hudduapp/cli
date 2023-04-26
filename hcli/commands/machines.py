import os

import typer
from rich import print

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
def connect(internal_name: str):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/instances/search?internal_name={internal_name}&limit=1",
    )

    machine_resource = res.get("data")[0]

    if not machine_resource.get("status") == "running":
        print(
            f"[red]Machine needs to be running but is in state: {machine_resource.get('status')}[/red]"
        )
    else:
        os.system(f"sudo rm {priv_cert_path}")
        with open(priv_cert_path, "w") as f:
            f.write(machine_resource["ssh"]["private_cert"])
            f.close()

        os.system(f"sudo chmod 400 {priv_cert_path}")
        os.system(f"ssh -i {priv_cert_path} admin@{machine_resource['external_ip']}")

        print("Closed terminal session")


@app.command()
def suspend(internal_name: str):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/instances/search?internal_name={internal_name}&limit=1",
    )

    machine_resource = res.get("data")[0]

    machines_api = ApiClient(
        base_url=f"{machine_resource['api_endpoint']}",
        headers={"Authorization": f"Token {token}"},
    )

    if not machine_resource.get("status") == "running":
        print(
            f"[red]Machine is not in running state anymore and thus can't be suspended[/red]"
        )
    else:
        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request(
            "POST",
            f"/organizations/{organization_id}/machines/{machine_resource.get('id')}/suspend",
        )
        print("Suspended vm")


@app.command()
def resume(internal_name: str):
    auth_required()
    org_required()
    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/instances/search?internal_name={internal_name}&limit=1",
    )

    machine_resource = res.get("data")[0]

    machines_api = ApiClient(
        base_url=f"{machine_resource['api_endpoint']}",
        headers={"Authorization": f"Token {token}"},
    )

    if not machine_resource.get("status") == "suspended":
        print(f"[red]This machine is already running[/red]")
    else:
        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request(
            "POST",
            f"/organizations/{organization_id}/machines/{machine_resource.get('id')}/resume",
        )
        print("Resumed vm")


@app.command()
def delete(
    internal_name: str,
    confirm_deletion: str = typer.Option(..., prompt="Are you sure? (y/n)"),
):
    auth_required()
    org_required()
    if confirm_deletion == "y":
        res = core_api.request(
            "GET",
            f"/organizations/{organization_id}/instances/search?internal_name={internal_name}&limit=1",
        )

        machine_resource = res.get("data")[0]

        machines_api = ApiClient(
            base_url=f"{machine_resource['api_endpoint']}",
            headers={"Authorization": f"Token {token}"},
        )

        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request(
            "POST",
            f"/organizations/{organization_id}/machines/{machine_resource.get('id')}/delete",
        )
        print("[red]Deleted the vm[/red]")
    else:
        print("[red]Aborted deleting this machine[/red]")
