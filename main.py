import typer

from commands import auth
from commands import machines
from commands import set

app = typer.Typer()

app.add_typer(set.app, name="set")
app.add_typer(machines.app, name="machines")
app.add_typer(auth.app, name="auth")

if __name__ == "__main__":
    app()
