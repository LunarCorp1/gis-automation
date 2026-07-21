import click

from .engine import QGISEngine


@click.group()
def cli():
    pass


@cli.command()
@click.argument("shapefile", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["pdf", "png"]), default="pdf")
@click.option("--style", "-s", type=click.Path(exists=True), default=None)
@click.option("--layout", "-l", type=click.Path(exists=True), default=None)
@click.option("--output", "-o", type=click.Path(), default=None)
def map(shapefile, format, style, layout, output):
    """Export a static map from a shapefile to PDF or PNG."""
    from .commands.map_command import run_map
    engine = QGISEngine()
    engine.init_qgis()
    try:
        run_map(shapefile, format, style, layout, output)
    finally:
        engine.close()


@cli.command()
@click.argument("shapefile", type=click.Path(exists=True))
@click.option("--title", "-t", default="Map")
@click.option("--field", default=None, help="Attribute field for choropleth coloring")
@click.option("--output", "-o", type=click.Path(), default=None)
def web(shapefile, title, field, output):
    """Generate an interactive Leaflet web map from a shapefile."""
    from .commands.web_command import run_web
    engine = QGISEngine()
    engine.init_qgis()
    try:
        run_web(shapefile, title, field, output)
    finally:
        engine.close()


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--interval", "-i", default=30, help="Poll interval in seconds")
@click.option("--format", "-f", type=click.Choice(["pdf", "png"]), default="pdf")
@click.option("--recursive", "-r", is_flag=True)
def watch(directory, interval, format, recursive):
    """Watch a directory for new shapefiles and auto-generate maps."""
    from .commands.watch_command import run_watch
    run_watch(directory, interval, format, recursive)


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["pdf", "png"]), default="pdf")
@click.option("--recursive", "-r", is_flag=True)
@click.option("--style", "-s", type=click.Path(exists=True), default=None)
@click.option("--output", "-o", type=click.Path(), default=None)
def batch(directory, format, recursive, style, output):
    """Batch-process all shapefiles in a directory."""
    from .commands.batch_command import run_batch
    engine = QGISEngine()
    engine.init_qgis()
    try:
        run_batch(directory, format, recursive, style, output)
    finally:
        engine.close()


@cli.command("list")
@click.argument("directory", type=click.Path(exists=True), default=r"C:\Users\LUNAR\Desktop\SHAPEFILES")
def list_shp(directory):
    """List available shapefiles in a directory."""
    from pathlib import Path
    shp_dir = Path(directory)
    for f in sorted(shp_dir.glob("**/*.shp") if True else shp_dir.glob("*.shp")):
        print(f)


if __name__ == "__main__":
    cli()
