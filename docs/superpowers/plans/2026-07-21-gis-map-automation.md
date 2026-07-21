# GIS Map Automation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that automates map generation from shapefiles using PyQGIS (primary) and ArcPy (fallback).

**Architecture:** Single Python package `gis_automate/` with subcommands `map`, `web`, `watch`, `batch`. QGIS engine initializes headless using the system QGIS 3.40.1 installation. Web maps are self-contained Leaflet HTML files. Folder watcher uses watchdog.

**Tech Stack:** Python 3.12 (QGIS-bundled), PyQGIS, Click, Watchdog, Jinja2, Leaflet.js, ArcPy (optional)

## Global Constraints

- All shapefiles come from `C:\Users\LUNAR\Desktop\SHAPEFILES`
- Output goes to `C:\Users\LUNAR\Desktop\gis\output\`
- QGIS 3.40.1 is at `C:\Program Files\QGIS 3.40.1\`
- QGIS Python at `C:\Program Files\QGIS 3.40.1\apps\Python312\`
- QGIS Python path: `C:\Program Files\QGIS 3.40.1\apps\qgis\python`
- QGIS DLL path: `C:\Program Files\QGIS 3.40.1\apps\qgis\bin`
- Must use `PYTHONHOME` + `PYTHONPATH` + `PATH` to bootstrap QGIS Python
- ArcGIS Desktop 10.8 installed at `C:\Program Files (x86)\ArcGIS\Desktop10.8\bin`
- ArcPy Python 2.7 at `C:\Python27\ArcGIS10.8`
- All public functions have type annotations

---

### Task 1: Project Scaffold & QGIS Wrapper

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\__init__.py`
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\__init__.py`
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\qgis_engine.py`
- Create: `C:\Users\LUNAR\Desktop\gis\launch.bat`

**Interfaces:**
- Consumes: QGIS installation at known paths
- Produces: `QGISEngine` class with `init_qgis()`, `load_layer(shapefile_path) -> QgsVectorLayer`

- [ ] **Step 1: Create package structure**

```bash
mkdir -p gis_automate\engine gis_automate\commands output\static output\web
```

- [ ] **Step 2: Write `__init__.py`**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\__init__.py`:
```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Write `engine/__init__.py`**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\__init__.py`:
```python
from .qgis_engine import QGISEngine

__all__ = ["QGISEngine"]
```

- [ ] **Step 4: Write QGIS engine wrapper**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\qgis_engine.py`:
```python
import os
import sys
from pathlib import Path


QGIS_INSTALL = Path(r"C:\Program Files\QGIS 3.40.1")
QGIS_PYTHON = QGIS_INSTALL / "apps" / "Python312"
QGIS_PYTHONPATH = QGIS_INSTALL / "apps" / "qgis" / "python"
QGIS_BIN = QGIS_INSTALL / "apps" / "qgis" / "bin"


class QGISEngine:
    def __init__(self):
        self._app = None

    def init_qgis(self):
        if self._app is not None:
            return
        os.environ["PYTHONHOME"] = str(QGIS_PYTHON)
        os.environ["PYTHONPATH"] = str(QGIS_PYTHONPATH)
        qgis_path = str(QGIS_BIN)
        python_bin = str(QGIS_PYTHON)
        env_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{qgis_path};{python_bin};{env_path}"
        if str(QGIS_PYTHONPATH) not in sys.path:
            sys.path.insert(0, str(QGIS_PYTHONPATH))
        from qgis.core import QgsApplication
        self._app = QgsApplication([], False)
        self._app.initQgis()

    def load_layer(self, shapefile_path: str):
        from qgis.core import QgsVectorLayer
        path = str(Path(shapefile_path).resolve())
        layer_name = Path(path).stem
        layer = QgsVectorLayer(path, layer_name, "ogr")
        if not layer.isValid():
            raise ValueError(f"Failed to load layer: {shapefile_path}")
        return layer

    def close(self):
        if self._app:
            self._app.exitQgis()
```

- [ ] **Step 5: Write launch batch script**

Write `C:\Users\LUNAR\Desktop\gis\launch.bat`:
```batch
@echo off
set "PYTHONHOME=C:\Program Files\QGIS 3.40.1\apps\Python312"
set "PYTHONPATH=C:\Program Files\QGIS 3.40.1\apps\qgis\python"
set "PATH=C:\Program Files\QGIS 3.40.1\apps\qgis\bin;C:\Program Files\QGIS 3.40.1\bin;C:\Program Files\QGIS 3.40.1\apps\Python312\Scripts;C:\Program Files\QGIS 3.40.1\apps\Python312;%PATH%"
"C:\Program Files\QGIS 3.40.1\bin\python3.exe" %*
```

- [ ] **Step 6: Verify QGIS wrapper works**

Run:
```batch
launch.bat -c "from gis_automate.engine.qgis_engine import QGISEngine; e = QGISEngine(); e.init_qgis(); l = e.load_layer(r'C:\Users\LUNAR\Desktop\SHAPEFILES\*.shp'); print('OK:', l.name())"
```
(Replace `*.shp` with an actual shapefile in the directory — use any `.shp` you find)

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: project scaffold and QGIS engine wrapper"
```

---

### Task 2: CLI Framework with Click

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\cli.py`
- Modify: `C:\Users\LUNAR\Desktop\gis\gis_automate\__init__.py`

**Interfaces:**
- Consumes: `QGISEngine` from Task 1
- Produces: CLI entrypoint with subcommands `map`, `web`, `watch`, `batch`, `list`

- [ ] **Step 1: Create CLI entrypoint**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\cli.py`:
```python
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
```

- [ ] **Step 2: Update `__init__.py`**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\__init__.py`:
```python
__version__ = "0.1.0"

from .cli import cli

__all__ = ["cli"]
```

- [ ] **Step 3: Install Click and verify CLI loads**

Run:
```batch
launch.bat -m pip install click
```

Run:
```batch
launch.bat -c "from gis_automate import cli; print('CLI OK')"
```

Expected: `CLI OK`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: CLI framework with Click subcommands"
```

---

### Task 3: Static Map Command (PyQGIS Layout Export)

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\__init__.py`
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\map_command.py`

**Interfaces:**
- Consumes: `QGISEngine.load_layer()`, shapefile path, format, optional .qml style, optional .qpt layout
- Produces: PDF or PNG file on disk

- [ ] **Step 1: Write `commands/__init__.py`**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\__init__.py`:
```python
```

- [ ] **Step 2: Write map command**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\map_command.py`:
```python
from pathlib import Path

from ..engine import QGISEngine

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "static"


def run_map(
    shapefile: str,
    fmt: str,
    style: str | None = None,
    layout: str | None = None,
    output: str | None = None,
):
    engine = QGISEngine()
    engine.init_qgis()
    try:
        layer = engine.load_layer(shapefile)

        from qgis.core import (
            QgsProject,
            QgsMapSettings,
            QgsLayoutExporter,
            QgsPrintLayout,
            QgsLayoutPoint,
            QgsLayoutSize,
            QgsUnitTypes,
            QgsLayerTreeLayer,
            QgsMapRendererParallelJob,
            QgsMapSettingsFlags,
            QgsCoordinateReferenceSystem,
        )
        from qgis.gui import QgsLayoutView
        from qgis.PyQt.QtCore import QSize
        from qgis.PyQt.QtGui import QColor, QImage, QPainter
        from qgis.PyQt.QtXml import QDomDocument

        project = QgsProject.instance()
        project.removeAllMapLayers()
        project.addMapLayer(layer)

        if style:
            from qgis.core import QgsStyle
            layer.loadNamedStyle(style)

        output_path = Path(output) if output else OUTPUT_DIR / f"{layer.name()}.{fmt}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "pdf":
            layout = QgsPrintLayout(project)
            layout.initializeDefaults()
            layout.setName(layer.name())

            page = layout.pageCollection().pages()[0]
            page.setPageSize("A4", QgsLayoutSize.Orientation.Landscape)

            map_item = layout.itemById("map")
            if map_item:
                map_item.zoomToExtent(layer.extent())

            exporter = QgsLayoutExporter(layout)
            exporter.exportToPdf(str(output_path), QgsLayoutExporter.PdfExportSettings())
        else:
            img = QImage(QSize(1920, 1080), QImage.Format_ARGB32_Premultiplied)
            img.setDotsPerMeterX(118)
            img.setDotsPerMeterY(118)

            settings = QgsMapSettings()
            settings.setLayers([layer])
            settings.setExtent(layer.extent())
            settings.setOutputSize(QSize(1920, 1080))
            settings.setBackgroundColor(QColor(255, 255, 255))

            job = QgsMapRendererParallelJob(settings)
            job.start()
            job.waitForFinished()

            rendered = job.renderedImage()
            painter = QPainter(img)
            painter.drawImage(0, 0, rendered)
            painter.end()

            img.save(str(output_path), "PNG")

        print(f"Map saved: {output_path}")
    finally:
        engine.close()
```

- [ ] **Step 3: Test the map command**

```batch
launch.bat -c "from gis_automate.commands.map_command import run_map; run_map(r'C:\Users\LUNAR\Desktop\SHAPEFILES\*.shp', 'png')"
```
(Replace `*.shp` with an actual file)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: static map export (PDF/PNG) via PyQGIS"
```

---

### Task 4: Web Map Command (Leaflet HTML)

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\web_command.py`
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\templates\map.html`

**Interfaces:**
- Consumes: `QGISEngine.load_layer()`, shapefile path, optional title, optional choropleth field
- Produces: self-contained Leaflet HTML file with embedded GeoJSON

- [ ] **Step 1: Create templates directory**

```bash
mkdir -p gis_automate\templates
```

- [ ] **Step 2: Write Leaflet template**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\templates\map.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin: 0; padding: 0; }
  #map { width: 100vw; height: 100vh; }
</style>
</head>
<body>
<div id="map"></div>
<script>
const geojsonData = {{ geojson | safe }};
const map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 18
}).addTo(map);
const layer = L.geoJSON(geojsonData, {
  onEachFeature: (feature, fLayer) => {
    if (feature.properties) {
      const props = Object.entries(feature.properties).map(([k, v]) =>
        `<tr><td><b>${k}</b></td><td>${v}</td></tr>`
      ).join('');
      fLayer.bindPopup(`<table>${props}</table>`);
    }
  }
}).addTo(map);
map.fitBounds(layer.getBounds());
</script>
</body>
</html>
```

- [ ] **Step 3: Write web command**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\web_command.py`:
```python
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "web"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def run_web(
    shapefile: str,
    title: str = "Map",
    field: str | None = None,
    output: str | None = None,
):
    from ..engine import QGISEngine

    engine = QGISEngine()
    engine.init_qgis()
    try:
        layer = engine.load_layer(shapefile)

        geojson_path = Path(shapefile).with_suffix(".geojson")
        from qgis.core import QgsVectorFileWriter
        save_opts = QgsVectorFileWriter.SaveVectorOptions()
        save_opts.driverName = "GeoJSON"
        QgsVectorFileWriter.writeAsVectorFormatV3(
            layer, str(geojson_path), layer.transformContext(), save_opts
        )

        with open(geojson_path, encoding="utf-8") as f:
            geojson_data = json.load(f)

        if field:
            values = [feat["properties"].get(field) for feat in geojson_data["features"]]
            values = [v for v in values if v is not None]
            if values:
                min_v, max_v = min(values), max(values)

                def color_for(val):
                    import colorsys
                    ratio = (val - min_v) / (max_v - min_v) if max_v > min_v else 0.5
                    r, g, b = colorsys.hls_to_rgb(0.6 * (1 - ratio), 0.5, 0.8)
                    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

                for feat in geojson_data["features"]:
                    val = feat["properties"].get(field)
                    if val is not None:
                        feat["properties"]["_fillColor"] = color_for(val)

        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        template = env.get_template("map.html")
        html = template.render(title=title, geojson=json.dumps(geojson_data))

        output_path = Path(output) if output else OUTPUT_DIR / f"{layer.name()}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        geojson_path.unlink(missing_ok=True)
        print(f"Web map saved: {output_path}")
    finally:
        engine.close()
```

- [ ] **Step 4: Install Jinja2**

```batch
launch.bat -m pip install jinja2
```

- [ ] **Step 5: Test the web command**

```batch
launch.bat -c "from gis_automate.commands.web_command import run_web; run_web(r'C:\Users\LUNAR\Desktop\SHAPEFILES\*.shp', 'Test Map')"
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: web map generation (Leaflet HTML + GeoJSON)"
```

---

### Task 5: Batch Processing Command

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\batch_command.py`

**Interfaces:**
- Consumes: directory path, format, recursive flag, optional style
- Produces: maps for every .shp file found

- [ ] **Step 1: Write batch command**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\batch_command.py`:
```python
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
```

- [ ] **Step 2: Test batch**

```batch
launch.bat -c "from gis_automate.commands.batch_command import run_batch; run_batch(r'C:\Users\LUNAR\Desktop\SHAPEFILES', 'png', recursive=False)"
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: batch processing command"
```

---

### Task 6: Folder Watcher Daemon

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\watch_command.py`

**Interfaces:**
- Consumes: directory path, interval seconds, format
- Produces: runs `run_batch` when new .shp files appear

- [ ] **Step 1: Install watchdog**

```batch
launch.bat -m pip install watchdog
```

- [ ] **Step 2: Write watch command**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\commands\watch_command.py`:
```python
import time
from pathlib import Path


def run_watch(
    directory: str,
    interval: int = 30,
    fmt: str = "pdf",
    recursive: bool = False,
):
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ShpHandler(FileSystemEventHandler):
        def __init__(self):
            self._debounce: dict[str, float] = {}

        def on_created(self, event):
            if event.src_path.endswith(".shp"):
                self._process(event.src_path)

        def on_modified(self, event):
            if event.src_path.endswith(".shp"):
                self._process(event.src_path)

        def _process(self, path: str):
            now = time.time()
            if path in self._debounce and now - self._debounce[path] < 5:
                return
            self._debounce[path] = now
            from .batch_command import run_batch
            print(f"New shapefile detected: {path}")
            try:
                run_batch(str(Path(path).parent), fmt, recursive=recursive)
            except Exception as e:
                print(f"  ERROR: {e}")

    observer = Observer()
    handler = ShpHandler()
    observer.schedule(handler, directory, recursive=recursive)
    observer.start()
    print(f"Watching {directory} for shapefiles (every {interval}s)...")
    try:
        while True:
            time.sleep(interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

- [ ] **Step 3: Test the watch command (quick smoke test)**

```batch
launch.bat -c "from gis_automate.commands.watch_command import run_watch; print('Watch command loaded OK')"
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: folder watcher daemon with watchdog"
```

---

### Task 7: ArcPy Fallback Engine

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\arcpy_engine.py`
- Modify: `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\__init__.py`

**Interfaces:**
- Consumes: ArcGIS Desktop 10.8 installation
- Produces: `arcpy_available() -> bool`, static map export via arcpy (optional)

- [ ] **Step 1: Write ArcPy engine**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\arcpy_engine.py`:
```python
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


def export_static_map_py2(shp: str, output_pdf: str):
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
    result = subprocess.run([ARCPY_PYTHON, "-c", code], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"ArcPy export failed: {result.stderr}")


if __name__ == "__main__":
    print("ArcPy available:", arcpy_available())
```

- [ ] **Step 2: Update engine `__init__.py`**

Write `C:\Users\LUNAR\Desktop\gis\gis_automate\engine\__init__.py`:
```python
from .qgis_engine import QGISEngine

try:
    from .arcpy_engine import arcpy_available
except ImportError:
    def arcpy_available() -> bool:
        return False

__all__ = ["QGISEngine", "arcpy_available"]
```

- [ ] **Step 3: Verify ArcPy availability check works**

```batch
launch.bat -c "from gis_automate.engine import arcpy_available; print('ArcPy:', arcpy_available())"
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: ArcPy fallback engine (Python 2.7 subprocess)"
```

---

### Task 8: pyproject.toml & Installable Package

**Files:**
- Create: `C:\Users\LUNAR\Desktop\gis\pyproject.toml`

**Interfaces:**
- Consumes: all source files
- Produces: pip-installable package

- [ ] **Step 1: Write pyproject.toml**

Write `C:\Users\LUNAR\Desktop\gis\pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "gis-automate"
version = "0.1.0"
description = "Automated map generation from shapefiles using PyQGIS"
requires-python = ">=3.12"
dependencies = [
    "click>=8.0",
    "jinja2>=3.0",
    "watchdog>=4.0",
]

[project.scripts]
gis-automate = "gis_automate:cli"

[tool.setuptools.packages.find]
include = ["gis_automate*"]
```

- [ ] **Step 2: Verify the package structure**

```bash
launch.bat -c "import gis_automate; print('Package OK:', gis_automate.__version__)"
```

Expected: `Package OK: 0.1.0`

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: pyproject.toml and package configuration"
```

---

### Task 9: Verify End-to-End

**Files:**
- None (verification only)

- [ ] **Step 1: Test `list` command**

```batch
launch.bat -m gis_automate list C:\Users\LUNAR\Desktop\SHAPEFILES
```

Expected: list of .shp files

- [ ] **Step 2: Test `map` command on a real shapefile**

```batch
launch.bat -m gis_automate map C:\Users\LUNAR\Desktop\SHAPEFILES\*.shp --format png
```

- [ ] **Step 3: Test `web` command**

```batch
launch.bat -m gis_automate web C:\Users\LUNAR\Desktop\SHAPEFILES\*.shp --title "My Map"
```

- [ ] **Step 4: Verify output files exist**

```bash
dir output\static\ && dir output\web\
```

- [ ] **Step 5: Test `batch` command**

```batch
launch.bat -m gis_automate batch C:\Users\LUNAR\Desktop\SHAPEFILES --format png
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: end-to-end verification of all commands"
```
