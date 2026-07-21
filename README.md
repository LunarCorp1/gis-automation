# GIS Automate

Automated map generation from shapefiles using PyQGIS. Supports static maps (PDF/PNG), interactive web maps (Leaflet), folder watching, and batch processing.

## Prerequisites

- [QGIS 3.40.1+](https://qgis.org/) — provides the PyQGIS engine
- Python 3.12 (bundled with QGIS)
- Windows (tested on Windows 11)

## Quick Start

```batch
launch.bat -m gis_automate map "C:\path\to\shapefile.shp" --format png
```

## Commands

### `map` — Export static map

```batch
launch.bat -m gis_automate map <shapefile> [--format pdf|png] [--style style.qml] [--output out.pdf]
```

### `web` — Generate interactive web map

```batch
launch.bat -m gis_automate web <shapefile> [--title "My Map"] [--field attribute_name]
```

Output is a self-contained HTML file with Leaflet + GeoJSON.

### `batch` — Process all shapefiles

```batch
launch.bat -m gis_automate batch <directory> [--format png] [--recursive]
```

### `watch` — Watch folder for new files

```batch
launch.bat -m gis_automate watch <directory> [--interval 30] [--format png]
```

Automatically generates maps when new `.shp` files appear.

### `list` — List available shapefiles

```batch
launch.bat -m gis_automate list [directory]
```

## Output Structure

```
output/
├── static/       # PDF/PNG exports
└── web/          # Leaflet HTML files
```

## Architecture

```
gis_automate/
├── cli.py                    # Click CLI entrypoint
├── commands/
│   ├── map_command.py        # Static map export (PyQGIS)
│   ├── web_command.py        # Leaflet web map generation
│   ├── batch_command.py      # Batch processor
│   └── watch_command.py      # Folder watcher daemon
├── engine/
│   ├── qgis_engine.py        # PyQGIS headless wrapper
│   └── arcpy_engine.py       # ArcPy fallback (optional)
└── templates/
    └── map.html              # Leaflet HTML template
```

## ArcPy Fallback

ArcGIS Desktop 10.8 support is available but requires Python 2.7 (`C:\Python27\ArcGIS10.8`). Falls back gracefully to PyQGIS if unavailable.

## License

MIT
