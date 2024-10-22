import typer
from typing_extensions import Annotated

app = typer.Typer()
@app.command("matrix")
def generate_matrix(config: Annotated[str, "YAML configuration file of the imaging system"]):
		typer.echo(f"Using: {config}")


if __name__ == "__main__":
    app()