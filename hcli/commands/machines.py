import os

import typer

from hcli.api.utils import ApiClient
from hcli.utils.machines import Machine
from hcli.utils.permanent_storage import read_field, dir_path
from hcli.utils.permissions import auth_required, org_required
from hcli.utils.terminal.prompt import confirmation_prompt
from hcli.utils.terminal.render import print

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
    )["data"][0]

    instance = Machine(res["region"])
    machine_info = instance.get_info(res["id"])
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
            f"Machine is not in running state anymore and thus can't be suspended",
            type="error",
        )
    else:
        print("This action might take up to 20 seconds", type="warning")
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
        print(f"This machine is already running", type="error")
    else:
        print("This action might take up to 20 seconds", type="warning")
        machines_api.request(
            "POST",
            f"/organizations/{organization_id}/machines/{machine_resource.get('id')}/resume",
        )
        print("Resumed vm")


@app.command()
def delete(internal_name: str):
    auth_required()
    org_required()
    confirmation_prompt()

    res = core_api.request(
        "GET",
        f"/organizations/{organization_id}/instances/search?internal_name={internal_name}&limit=1",
    )

    machine_resource = res.get("data")[0]

    machines_api = ApiClient(
        base_url=f"{machine_resource['api_endpoint']}",
        headers={"Authorization": f"Token {token}"},
    )

    print("This action might take up to 20 seconds", type="warning")
    machines_api.request(
        "POST",
        f"/organizations/{organization_id}/machines/{machine_resource.get('id')}/delete",
    )
    print("Deleted the vm successfully")
