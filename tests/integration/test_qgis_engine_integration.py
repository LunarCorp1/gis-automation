"""Integration test for QGISEngine - runs as standalone script.

QGIS C++ layer has known crashes during pytest collection/teardown,
so full integration tests run via launch.bat as an isolated process.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from gis_automate.engine.qgis_engine import QGISEngine

SHAPEFILE = Path(r"C:\Users\LUNAR\Desktop\SHAPEFILES\Africa\Africa.shp")
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


engine = QGISEngine()

# Test 1: init_qgis
engine.init_qgis()
check(engine._app is not None, "init_qgis creates QgsApplication")

# Test 2: double init is safe
engine.init_qgis()
check(engine._app is not None, "double init_qgis is safe")

# Test 3: load valid layer
layer = engine.load_layer(str(SHAPEFILE))
check(layer.isValid(), f"load_layer('{SHAPEFILE}') returns valid layer")
check(layer.name() == "Africa", f"layer name is 'Africa', got '{layer.name()}'")

# Test 4: load nonexistent raises
try:
    engine.load_layer(r"C:\nonexistent\file.shp")
    errors.append("Expected ValueError for nonexistent file")
    print("  FAIL: Expected ValueError for nonexistent file")
except ValueError:
    print("  PASS: load_layer(nonexistent) raises ValueError")

# Test 5: close
engine.close()
check(engine._app is None, "close() resets _app to None")

print(f"\n{'='*40}")
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL INTEGRATION TESTS PASSED")
    sys.exit(0)
