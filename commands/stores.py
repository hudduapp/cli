import typer
from rich import print
from rich.table import Table

from api.utils import ApiClient
from utils.permanent_storage import read_field

app = typer.Typer()

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {read_field('token')}"}
)

organization_id = read_field("organization_id")
project_id = read_field("project_id")


def make_store_client(client_id, management_token):
    return ApiClient(
        f"https://store.huddu.io",
        headers={"X-Client-ID": client_id, "X-Client-Secret": management_token}
    )


@app.command()
def create(
        name: str = typer.Option(..., prompt=True)
):
    stores_api = ApiClient(
        f"https://store.huddu.io",
        headers={"Authorization": f"Token {read_field('token')}"}
    )

    res = stores_api.request("POST", "setup", body={
        "project": project_id, "organization": organization_id, "name": name
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
                           f"/search?resource=resources&organization={organization_id}&q=type:store%20$and%20project:{project_id}&limit=10&skip={skip}")

    table = Table()

    table.add_column(
        "Name"
    )
    table.add_column(
        "Store ID"
    )
    table.add_column(
        "Client ID"
    )

    for i in res.get("data"):
        table.add_row(
            i.get("name"),
            i.get("id"),
            i.get("client_id"),
        )

    if len(res.get("data")):
        print(table)
    else:
        print("No entries. You can create a new store with huddu stores create")


@app.command()
def info(
        store_id: str, show_secret: bool = False
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")

    store_resource = res.get("data")[0]
    if not show_secret:
        store_resource["management_token"] = "*****"

    print(store_resource)


@app.command()
def get(
        store_id: str,
        key: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")
    store_resource = res["data"][0]

    store_api = make_store_client(store_resource.get("client_id"), store_resource.get("management_token"))

    res = store_api.request("GET", f"documents?keys={key}")
    if len(res.get("data")) > 0:
        print(res.get("data")[0])
    else:
        print("[red]No entry for key found[/red]")


@app.command()
def set(
        store_id: str,
        key: str,
        value: str = typer.Option(..., prompt=True),
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")
    store_resource = res["data"][0]

    store_api = make_store_client(store_resource.get("client_id"), store_resource.get("management_token"))

    res = store_api.request("GET", f"documents?keys={key}")
    if len(res.get("data")) > 0:
        print(f"[red]Entry with key {key} already exists use [bold]huddu stores update[/bold] instead[/red]")

    store_api.request("POST", f"documents", body={
        "key": key,
        "value": value
    })

    print("[green]Set new entry[/green]")


@app.command()
def update(
        store_id: str,
        key: str, value: str = typer.Option(..., prompt=True),
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")
    store_resource = res["data"][0]

    store_api = make_store_client(store_resource.get("client_id"), store_resource.get("management_token"))

    store_api.request("POST", f"documents", body={
        "key": key,
        "value": value
    })

    print("[green]Updated entry[/green]")


@app.command()
def delete(
        store_id: str,
        key: str
):
    res = core_api.request("GET",
                           f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")
    store_resource = res["data"][0]

    store_api = make_store_client(store_resource.get("client_id"), store_resource.get("management_token"))

    store_api.request("DELETE", f"documents", body={
        "key": key
    })

    print("[green]Deleted entry[/green]")


@app.command()
def delete_store(
        store_id: str,
        confirm_deletion: str = typer.Option(...,
                                             prompt="Are you sure? (y/n)")
):
    if confirm_deletion == "y":
        res = core_api.request("GET",
                               f"/search?resource=resources&organization={organization_id}&q=type:store $and project:{project_id} $and id:{store_id}&limit=1")
        store_resource = res["data"][0]

        store_api = make_store_client(store_resource.get("client_id"), store_resource.get("management_token"))
        store_api.request("POST", "delete", body={
            "resource": store_resource.get("id"),
            "project": project_id,
            "organization": organization_id
        })
        print("[red]Deleted the store[/red]")
    else:
        print("[red]Aborted deleting this store[/red]")
