from pathlib import Path


def run_batch(
    directory: str,
    fmt: str,
    recursive: bool = False,
    style: str | None = None,
    output: str | None = None,
):
    from .map_command import run_map

    shp_dir = Path(directory)
    pattern = "**/*.shp" if recursive else "*.shp"
    shp_files = sorted(shp_dir.glob(pattern))

    if not shp_files:
        print(f"No shapefiles found in {directory}")
        return

    for shp in shp_files:
        try:
            print(f"Processing: {shp.name}")
            run_map(str(shp), fmt, style=style, output=output)
        except Exception as e:
            print(f"  ERROR: {e}")
