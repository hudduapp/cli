import os
from enum import Enum

import typer
from rich import print
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field

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
        if res.get("error"):
            print(res)
        else:
            print(f"[green]✨ Successfully created a new store [/green]")


@app.command()
def list(
        skip: int = 0
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:machine%20$and%20project:{project_id}&limit=10&skip={skip}")

    table = Table()

    table.add_column(
        "Name"
    )
    table.add_column(
        "Machine ID"
    )
    table.add_column(
        "Machine IP"
    )
    table.add_column(
        "Machine Type"
    )

    for i in res.get("data"):
        table.add_row(
            i.get("name"),
            i.get("id"),
            i.get("external_ip"),
            i.get("machine_type")
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No entries. You can create a new machine with huddu machines create")


@app.command()
def connect(
        machine_name: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:machine $and project:{project_id} $and name:{machine_name}&limit=1")

    machine_resource = res.get("data")[0]

    if not machine_resource.get("status") == "running":
        print(f"[red]Machine needs to be running but is in state: {machine_resource.get('status')}[/red]")
    else:
        with open("priv_cert.pem", "w") as f:
            f.write(machine_resource["ssh"]["private_cert"])
            f.close()

        os.system("chmod 400 priv_cert.pem")
        os.system(f"ssh -i priv_cert.pem admin@{machine_resource['external_ip']}")

        print("Closed terminal session")


@app.command()
def info(
        machine_name: str, show_ssh: bool = False
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:machine $and project:{project_id} $and name:{machine_name}&limit=1")

    machine_resource = res.get("data")[0]
    if not show_ssh:
        machine_resource["ssh"]["private_cert"] = "*****"

    print(machine_resource)


@app.command()
def suspend(
        machine_name: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:machine $and project:{project_id} $and name:{machine_name}&limit=1")

    machine_resource = res.get("data")[0]

    if not machine_resource.get("status") == "running":
        print(f"[red]Machine is not in running state anymore and thus can't be suspended[/red]")
    else:
        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request("POST", f"machines/{machine_resource.get('id')}/suspend")
        print("Suspended vm")


@app.command()
def resume(
        machine_name: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:machine $and project:{project_id} $and name:{machine_name}&limit=1")

    machine_resource = res.get("data")[0]

    if not machine_resource.get("status") == "suspended":
        print(f"[red]This machine is already running[/red]")
    else:
        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request("POST", f"machines/{machine_resource.get('id')}/resume")
        print("Resumed vm")


@app.command()
def delete(
        machine_name: str,
        confirm_deletion: str = typer.Option(...,
                                             prompt="Are you sure? (y/n)")
):
    if confirm_deletion == "y":
        res = core_api.request("GET",
                               f"/search?resource=resources&organization={organization_id}&q=type:machine $and project:{project_id} $and name:{machine_name}&limit=1")

        machine_resource = res.get("data")[0]

        print("[yellow]this action might take up to 20 seconds[/yellow]")
        machines_api.request("POST", f"machines/{machine_resource.get('id')}/delete")
        print("[red]Deleted the vm[/red]")
    else:
        print("[red]Aborted deleting this machine[/red]")
