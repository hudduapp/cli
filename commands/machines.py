import os
from enum import Enum

import typer
from rich import print

from api.utils import ApiClient
from utils.permanent_storage import read_field

app = typer.Typer()

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {read_field('token')}"}
)

organization_id = read_field("organization_id")
project_id = read_field("project_id")

machines_api = ApiClient(
    f"https://machines.huddu.io/organizations/{organization_id}/projects/{project_id}",
    headers={"Authorization": f"Token {read_field('token')}"}
)


class MachineType(str, Enum):
    dedicated_cpu_x1 = "dedicated-cpu-x1"
    dedicated_cpu_x2 = "dedicated-cpu-x2"


class Region(str, Enum):
    us_central = "us-central"
    eu_west = "eu-west"


@app.command()
def create(
        name: str = typer.Option(..., prompt=True),
        region: Region = typer.Option(..., show_choices=True, prompt=True),
        machine_type: MachineType = typer.Option(..., show_choices=True, prompt=True),
        hostname: str = typer.Option(..., prompt=True),
        disk_size: int = typer.Option(..., prompt=True),
):
    machine_type = machine_type.value
    region = region.value

    if disk_size > 20:
        print("[red] disks larger than 20GB are not recommended (yet). Please send us a mail at contact@huddu.io[red]")
    else:

        print("[yellow]this action might take up to a minute[/yellow]")
        res = machines_api.request("POST", "machines", body={
            "name": name,
            "region": region,
            "machine_type": machine_type,
            "hostname": hostname,
            "disk_size": disk_size
        })

        print(res)


@app.command()
def list(
        skip: int = 0
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine%20$and%20project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85&limit=10&skip={skip}")

    for i in res.get("data"):
        print(f"[bold]{i['name']}[/bold] | {i['id']} | {i['machine_type']}")


@app.command()
def connect(
        machine_id: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine $and project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85 $and id:{machine_id}&limit=1")

    machine_resource = res.get("data")[0]

    with open("priv_cert.pem", "w") as f:
        f.write(machine_resource["ssh"]["private_cert"])
        f.close()

    os.system("chmod 400 priv_cert.pem")
    os.system(f"ssh -i priv_cert.pem admin@{machine_resource['external_ip']}")

    print("Closed terminal session")


@app.command()
def info(
        machine_id: str, show_ssh: bool = False
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine $and project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85 $and id:{machine_id}&limit=1")

    machine_resource = res.get("data")[0]
    if not show_ssh:
        machine_resource["ssh"]["private_cert"] = "*****"

    print(machine_resource)


@app.command()
def suspend(
        machine_id: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine $and project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85 $and id:{machine_id}&limit=1")

    machine_resource = res.get("data")[0]

    print("[yellow]this action might take up to 20 seconds[/yellow]")
    machines_api.request("POST", f"machines/{machine_resource.get('id')}/suspend")
    print("Suspended vm")


@app.command()
def resume(
        machine_id: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine $and project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85 $and id:{machine_id}&limit=1")

    machine_resource = res.get("data")[0]

    print("[yellow]this action might take up to 20 seconds[/yellow]")
    machines_api.request("POST", f"machines/{machine_resource.get('id')}/resume")
    print("Resumed vm")


@app.command()
def delete(
        machine_id: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization=org_bf826581-6336-45eb-a3f0-8e1dd8d1a2ab&q=type:machine $and project:prj_e616b0aa-1911-41db-a0ec-f18d164b7d85 $and id:{machine_id}&limit=1")

    machine_resource = res.get("data")[0]

    print("[yellow]this action might take up to 20 seconds[/yellow]")
    machines_api.request("POST", f"machines/{machine_resource.get('id')}/delete")
    print("[red]Deleted the vm[/red]")
