import typer
from rich import print
from rich.table import Table

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field
from hcli.utils.permissions import auth_required, project_and_org_required

app = typer.Typer()

token = read_field("token")
organization_id = read_field("organization_id")
project_id = read_field("project_id")

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {token}"}
)


def make_queue_client(client_id, management_token):
    auth_required()
    project_and_org_required()
    return ApiClient(
        f"https://queue.huddu.io",
        headers={"X-Client-ID": client_id, "X-Client-Secret": management_token},
    )


@app.command()
def create(name: str = typer.Option(..., prompt=True)):
    auth_required()
    project_and_org_required()
    queues_api = ApiClient(
        f"https://queue.huddu.io", headers={"Authorization": f"Token {token}"}
    )

    res = queues_api.request(
        "POST",
        "setup",
        body={"project": project_id, "organization": organization_id, "name": name},
    )

    if res.get("error"):
        print(res)
    else:
        print(f"[green]✨ Successfully created a new queue [/green]")


@app.command()
def list(skip: int = 0):
    auth_required()
    project_and_org_required()
    res = core_api.request(
        "GET",
        f"/search?resource=resources&organization={organization_id}&q=type:queue%20$and%20project:{project_id}&limit=10&skip={skip}",
    )

    table = Table()

    table.add_column("Name")
    table.add_column("Store ID")
    table.add_column("Client ID")

    for i in res.get("data"):
        table.add_row(
            i.get("name"),
            i.get("id"),
            i.get("client_id"),
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No entries. You can create a new queue with huddu queues create")


@app.command()
def info(queue_name: str, show_management_token: bool = False):
    auth_required()
    project_and_org_required()
    res = core_api.request(
        "GET",
        f"/search?resource=resources&organization={organization_id}&q=type:queue $and project:{project_id} $and name:{queue_name}&limit=1",
    )

    queue_resource = res.get("data")[0]
    if not show_management_token:
        queue_resource["management_token"] = "*****"

    print(queue_resource)


@app.command()
def events_pull(
    queue_name: str, topic: str = typer.Option(..., prompt=True), limit: int = 5
):
    auth_required()
    project_and_org_required()
    res = core_api.request(
        "GET",
        f"/search?resource=resources&organization={organization_id}&q=type:queue $and project:{project_id} $and name:{queue_name}&limit=1",
    )
    queue_resource = res["data"][0]

    queues_api = make_queue_client(
        queue_resource.get("client_id"), queue_resource.get("management_token")
    )

    res = queues_api.request("GET", f"pull?topic={topic}&limit={limit}")

    if len(res.get("data")) > 0:
        print(res.get("data")[0])
    else:
        print("[red]No events found[/red]")


@app.command()
def entries_push(
    queue_name: str,
    topic: str = typer.Option(..., prompt=True),
    event: str = typer.Option(..., prompt=True),
):
    auth_required()
    project_and_org_required()
    res = core_api.request(
        "GET",
        f"/search?resource=resources&organization={organization_id}&q=type:queue $and project:{project_id} $and name:{queue_name}&limit=1",
    )
    queue_resource = res["data"][0]

    queues_api = make_queue_client(
        queue_resource.get("client_id"), queue_resource.get("management_token")
    )

    queues_api.request("POST", f"push", body={"topic": topic, "event": event})

    print("[green]Pushed to queue[/green]")


@app.command()
def events_acknowledge(queue_name: str, event_id: str = typer.Option(..., prompt=True)):
    auth_required()
    project_and_org_required()
    res = core_api.request(
        "GET",
        f"/search?resource=resources&organization={organization_id}&q=type:queue $and project:{project_id} $and name:{queue_name}&limit=1",
    )
    queue_resource = res["data"][0]

    queues_api = make_queue_client(
        queue_resource.get("client_id"), queue_resource.get("management_token")
    )

    queues_api.request("POST", f"acknowledge", body={"ids": [id]})

    print("[green]Deleted entry[/green]")


@app.command()
def delete(
    queue_name: str,
    confirm_deletion: str = typer.Option(..., prompt="Are you sure? (y/n)"),
):
    auth_required()
    project_and_org_required()
    if confirm_deletion == "y":
        res = core_api.request(
            "GET",
            f"/search?resource=resources&organization={organization_id}&q=type:queue $and project:{project_id} $and name:{queue_name}&limit=1",
        )
        queue_resource = res["data"][0]

        queues_api = ApiClient(
            f"https://queue.huddu.io", headers={"Authorization": f"Token {token}"}
        )
        queues_api.request(
            "DELETE",
            "delete",
            body={
                "resource": queue_resource.get("id"),
                "project": project_id,
                "organization": organization_id,
            },
        )
        print("[red]Deleted the queue[/red]")
    else:
        print("[red]Aborted deleting this queue[/red]")
