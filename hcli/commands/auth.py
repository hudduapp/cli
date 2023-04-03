from getpass import getpass

import typer
from rich import print

from hcli.api.utils import ApiClient
from hcli.utils.permanent_storage import read_field, set_field, unset_field

app = typer.Typer()

core_api = ApiClient(
    "https://api.huddu.io", headers={"Authorization": f"Token {read_field('token')}"}
)

auth_api = ApiClient(
    "https://login-service-duqqqjtkbq-uc.a.run.app",
    headers={"Authorization": f"Token {read_field('token')}"},
)


@app.command()
def login():
    token = read_field("token")
    if token:
        print(
            f"You're already logged in. if you want to change accounts please log out first"
        )
    else:
        login = input("Login: ")
        password = getpass("Password: ")

        res = auth_api.request(
            "POST", "/login", body={"login": login, "password": password}
        )

        set_field("token", res["token"])
        print(f"[green]✨ successfully logged in as {login} [/green]")


@app.command()
def logout():
    token = read_field("token")
    if token:
        core_api.request("DELETE", "/me/tokens", body={"token": token})

        unset_field("token")
        print(f"[green]Successfully logged out[/green]")
    else:
        print(f"You're already logged out. To login run [bold]huddu auth login[/bold]")


if __name__ == "__main__":
    app()
