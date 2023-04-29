import typer

from hcli.commands import apps
from hcli.commands import auth
from hcli.commands import machines
from hcli.commands import organizations
from hcli.commands import set
from hcli.commands.deploy import deploy_to_app

app = typer.Typer()


@app.command()
def deploy(filename: str = "huddu.yml"):
    deploy_to_app(filename)


app.add_typer(organizations.app, name="organizations")
app.add_typer(set.app, name="set")
app.add_typer(apps.app, name="apps")
app.add_typer(auth.app, name="auth")
app.add_typer(machines.app, name="machines")

if __name__ == "__main__":
    app()
