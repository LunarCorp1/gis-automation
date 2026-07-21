from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
SHAPEFILES_DIR = Path(os.environ.get("SHAPEFILES_DIR", "C:/Users/LUNAR/Desktop/SHAPEFILES"))
OUTPUT_DIR = PROJECT_ROOT / "output"

QGIS_PYTHON = r"C:\Program Files\QGIS 3.40.1\bin\python3.exe"


def _run_qgis(script: str, *args: str) -> str:
    env = os.environ.copy()
    env["PYTHONHOME"] = r"C:\Program Files\QGIS 3.40.1\apps\Python312"
    env["PYTHONPATH"] = r"C:\Program Files\QGIS 3.40.1\apps\qgis\python"
    env["QT_QPA_PLATFORM"] = "offscreen"
    qgis_dirs = [
        r"C:\Program Files\QGIS 3.40.1\apps\qgis\bin",
        r"C:\Program Files\QGIS 3.40.1\bin",
        r"C:\Program Files\QGIS 3.40.1\apps\Python312\Scripts",
        r"C:\Program Files\QGIS 3.40.1\apps\Python312",
    ]
    env["PATH"] = ";".join(qgis_dirs + [env.get("PATH", "")])

    script_path = str(SCRIPTS_DIR / script)
    cmd = [QGIS_PYTHON, "-u", script_path, *args]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_ROOT), env=env,
    )
    out = result.stdout.strip()
    if result.returncode != 0 and not out:
        msg = (result.stderr.strip() or "failed")[:500]
        raise RuntimeError(f"exit={result.returncode} {msg}")
    if not out:
        raise RuntimeError(f"no output (stderr: {result.stderr.strip()[:200]})")
    return out


server = FastMCP(
    "GIS Automation Server",
    instructions="Generate cartographic maps and interactive web maps from shapefiles using PyQGIS",
)


def _get_shapefiles() -> list[dict]:
    if not SHAPEFILES_DIR.is_dir():
        return []
    results = []
    for f in sorted(SHAPEFILES_DIR.rglob("*.shp")):
        rel = f.relative_to(SHAPEFILES_DIR)
        stats = f.stat()
        results.append({
            "name": f.stem,
            "path": str(f.resolve()),
            "relative_path": str(rel),
            "size_bytes": stats.st_size,
        })
    return results


@server.tool(
    name="list_shapefiles",
    description="List all available shapefiles in the SHAPEFILES directory with their paths and sizes",
)
def list_shapefiles() -> list[dict]:
    return _get_shapefiles()


@server.tool(
    name="get_layer_info",
    description="Get field names, types, CRS, extent, and feature count for a shapefile layer",
)
def get_layer_info(shapefile_path: str) -> dict:
    stdout = _run_qgis("run_info.py", shapefile_path)
    return json.loads(stdout)


@server.tool(
    name="create_map",
    description="Generate a cartographic static map (PDF or PNG) from a shapefile with title, legend, scale bar, and north arrow",
)
def create_map(
    shapefile_path: str,
    title: str | None = None,
    fmt: str = "png",
    style_path: str | None = None,
    output_path: str | None = None,
) -> str:
    _run_qgis("run_map_cli.py", shapefile_path, fmt, title or "", style_path or "", output_path or "")
    return "Map generated successfully"


@server.tool(
    name="create_web_map",
    description="Generate an interactive Leaflet web map (HTML) from a shapefile with attribute popups and optional choropleth coloring on a numeric field",
)
def create_web_map(
    shapefile_path: str,
    title: str = "Map",
    field: str | None = None,
    output_path: str | None = None,
) -> str:
    _run_qgis("run_web_cli.py", shapefile_path, title, field or "", output_path or "")
    return "Web map generated successfully"


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
