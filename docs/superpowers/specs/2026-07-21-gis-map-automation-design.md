# GIS Map Automation — Design Spec

## Overview

Automated map generation system for shapefiles in `C:\Users\LUNAR\Desktop\SHAPEFILES`. Supports static maps (PDF/PNG), web maps (interactive HTML), and data-driven thematic maps. Dual-engine: PyQGIS primary, ArcPy fallback (where available).

## Architecture

```
SHAPEFILES/
├── *.shp                    # input data
├── styles/                  # QGIS style .qml files
├── templates/               # layout .qpt templates for static maps
├── output/
│   ├── static/              # PDF/PNG exports
│   └── web/                 # Leaflet HTML + GeoJSON

gis-automate CLI (Python)
├── commands/
│   ├── map.py               # static map export
│   ├── web.py               # web map generation
│   ├── watch.py             # folder watcher daemon
│   └── batch.py             # bulk processor
├── engine/
│   ├── qgis_engine.py       # PyQGIS wrapper
│   └── arcpy_engine.py      # ArcPy wrapper (optional)
├── templates/               # web map HTML templates
└── qgis-venv/               # isolated QGIS Python env
```

## Components

### 1. CLI (`gis-automate`)

| Command | Args | Description |
|---------|------|-------------|
| `map` | `<shp> [--format pdf|png] [--style qml] [--layout qpt]` | Export static map |
| `web` | `<shp> [--title str]` | Generate interactive Leaflet map |
| `watch` | `<dir> [--interval 30]` | Watch folder, auto-generate on new files |
| `batch` | `<dir> [--recursive] [--format pdf]` | Process all shapefiles |
| `list` | — | Show available shapefiles and output |

### 2. PyQGIS Engine

- Initializes `QgsApplication` in headless mode (`--novideo`)
- Loads vector layer from shapefile
- Applies .qml style if provided, else auto-default
- Static: builds `QgsLayout` from .qpt template (or default), exports
- Web: reads attributes, renders to GeoJSON, wraps in Leaflet HTML

### 3. Folder Watcher

- Uses `watchdog` library to monitor the shapefiles directory
- On file create/modify for `.shp`, triggers `batch` after debounce
- Configurable interval and output directory

### 4. Web Map Generator

- Converts shapefile to GeoJSON via PyQGIS
- Generates self-contained HTML file with Leaflet + a basemap (OSM)
- Attribute popups on feature click
- Optional choropleth coloring via attribute field

### 5. ArcPy Fallback

- Detects if arcpy is available at runtime
- Provides equivalent static map output using ArcGIS Desktop's `arcpy.mapping`
- No web map support (falls back to PyQGIS)

## Workflows

**Static map on demand:**
```
gis-automate map myshp.shp --format pdf --style my_style.qml
```

**Generate web map:**
```
gis-automate web myshp.shp --title "Land Use 2026"
```

**Watch folder and auto-export:**
```
gis-automate watch C:\Users\LUNAR\Desktop\SHAPEFILES --interval 10
```

**Batch everything:**
```
gis-automate batch C:\Users\LUNAR\Desktop\SHAPEFILES --recursive --format png
```

## Tech Stack

- **Python 3.12** (QGIS bundled) via isolated venv wrapping QGIS's Python
- **PyQGIS** (QGIS 3.40.1) — core GIS engine
- **Click** — CLI framework
- **Watchdog** — file watcher
- **Jinja2** — HTML template rendering
- **Leaflet.js** — web map frontend (bundled in output)
- **ArcPy** (Python 2.7) — optional fallback for ArcGIS Desktop 10.8

## Environment Setup

- Create a wrapper venv that inherits QGIS's Python 3.12 with proper PATH/PYTHONHOME
- Activate via a `.bat` launcher that sets env vars before launching Python
- ArcPy used via subprocess to Python 2.7 if needed

## Error Handling

- Missing shapefile → clear CLI error
- Invalid geometry → skip with warning
- No style found → apply auto-default (random color fill)
- ArcPy unavailable → skip with note, suggest PyQGIS
