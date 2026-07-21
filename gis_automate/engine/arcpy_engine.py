from __future__ import annotations

import subprocess
from pathlib import Path

ARCPY_PYTHON = r"C:\Python27\ArcGIS10.8\python.exe"


def arcpy_available() -> bool:
    if not Path(ARCPY_PYTHON).exists():
        return False
    try:
        result = subprocess.run(
            [ARCPY_PYTHON, "-c", "import arcpy; print(arcpy.__file__)"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def export_static_map_py2(shp: str, output_pdf: str) -> None:
    code = f"""
import arcpy
import os

arcpy.env.overwriteOutput = True
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
layer = arcpy.mapping.Layer(r"{shp}")
arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
arcpy.mapping.ExportToPDF(mxd, r"{output_pdf}")
del mxd
"""
    result = subprocess.run(
        [ARCPY_PYTHON, "-c", code], capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"ArcPy export failed: {result.stderr}")


if __name__ == "__main__":
    print("ArcPy available:", arcpy_available())
