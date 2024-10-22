import typer
from typing_extensions import Annotated
from ._generate import system

app = typer.Typer()
app.add_typer(system.app, name="system")

if __name__ == "__main__":
    app()