import typer

from commands import auth
from commands import stores

app = typer.Typer()

app.add_typer(stores.app, name="stores")
app.add_typer(auth.app, name="auth")

if __name__ == "__main__":
    app()
