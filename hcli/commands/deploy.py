import os
import time
import uuid

import typer
import yaml

from hcli.api.utils import ApiClient
from hcli.utils.apps import get_app
from hcli.utils.machines import get_machines_for_an_app, Machine
from hcli.utils.permanent_storage import read_field
from hcli.utils.terminal.prompt import confirmation_prompt
from hcli.utils.terminal.render import print

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")

core_api = ApiClient(
    "http://public-api-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {token}"},
)


def generate_command(custom_command: str):
    command = ""
    # install some requirements (incl. metrics)
    command += "sudo apt-get install atop; "
    command += f"nohup sudo {custom_command} > /home/admin/out.txt &"

    return command


def deploy_to_app(filename: str = "huddu.yml") -> None:
    print("Starting deployment...")
    # defining a few vars
    dir = os.getcwd()
    full_filename = f"{dir}/{filename}"
    deployment_id = str(uuid.uuid4())
    with open(full_filename, "r") as f:
        configfile = yaml.safe_load(f.read())

    # search the app to which to deploy
    app = get_app(configfile["app"])

    print(
        "Running a new deployment will remove old resources and then deploy new ones as defined in your config file."
    )
    confirmation_prompt()

    # Finding old machines that are to be deployed post/pre deployment
    to_delete = list(
        get_machines_for_an_app(app["id"], params={"meta.delete_on_redeploy": "true"})
    )

    # delete machines if strategy is recreate
    if configfile.get("strategy", "blue/green").lower() == "recreate":
        for i in to_delete:
            machine = Machine(region=i["region"])
            machine.delete(instance_id=i["id"])

    # find machines to create in configfile
    machines_to_create = (
        configfile.get("machines") if configfile.get("machines") else []
    )

    # create machines
    for i in machines_to_create:
        machine_status = list(i.values())[0]
        machine = Machine(machine_status.get("region", "us-central"))
        # default region to us-central
        if not machine_status.get("region"):
            print("No region set! Defaulting to us-central")

        print("Creating machine...")

        machine.create(
            app=app["id"],
            name=list(i.keys())[0],
            machine_type=machine_status.get("machine_type", "small-1"),
            disk_size=machine_status.get("disk_size", 10),
            meta={
                "delete_on_redeploy": i.get("delete_on_redeploy", True),
                "deployment_id": deployment_id,
                "command": generate_command(machine_status.get("run", None)),
            },
        )

        configfile["machines"].remove(i)

    if configfile.get("strategy", "blue/green").lower() == "blue/green":
        for i in to_delete:
            machine = Machine(region=i["region"])
            machine.delete(instance_id=i["id"])

    machines_to_run_commands_on = list(
        get_machines_for_an_app(app["id"], {"meta.deployment_id": deployment_id})
    )

    print("💻 Starting to run your commands inside machines.")
    while len(machines_to_run_commands_on):
        for i in machines_to_run_commands_on:
            machine = Machine(i.get("region"))
            machine_status = machine.get_info(i["id"])["status"]
            if i["meta"].get("command"):
                if machine_status == "running":
                    print(f"Preparing to run command on {i.get('name')}")
                    time.sleep(5)
                    print(f"Running {i['meta'].get('command')} on {i.get('name')}")
                    try:
                        machine.run_command(i["id"], i["meta"].get("command"))
                        machines_to_run_commands_on.remove(i)
                    except:
                        print("failed to run command. Will retry...")

                else:
                    print(
                        f"Current status for {i['name']} is {machine_status}. Waiting..."
                    )
                    print(f"Will retry for {i['name']} in circa 10 seconds")
            else:
                machines_to_run_commands_on.remove(i)
        time.sleep(10)
    print("🚀 Mission Success!")
    print(
        "Need more info about this deployment? Check the dashboard: https://huddu.io/app"
    )
