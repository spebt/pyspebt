import typer
from typing_extensions import Annotated
from . import generate
from . import render

app = typer.Typer()
app.add_typer(generate.app, name="generate")
app.add_typer(render.app, name="render")
  
if __name__ == "__main__":
    app()