import typer
from typing_extensions import Annotated
import spebtpy.system.config as spebtconfig

app = typer.Typer()


@app.command("system")
def render_system(
    config: Annotated[
        str,
        typer.Option(
            "--config", "-c", help="YAML configuration file of the imaging system"
        ),
    ],
    style: Annotated[
        str, typer.Option("--style", "-s", help="Style of the plot, 2D or 3D")
    ]="2D",
) -> None:
    import re

    typer.echo(f"Using: {config}")
    config_dict = spebtconfig.yaml.parse(config)
    basename = re.sub(r"\.(?:yaml|yml)$", "", config)
    if style is "2D":
        spebtconfig.yaml.plot_system_mpl(config_dict, basename=basename)


if __name__ == "__main__":
    app()
