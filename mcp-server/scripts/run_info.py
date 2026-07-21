from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from gis_automate.engine import QGISEngine

engine = QGISEngine()
engine.init_qgis()
layer = engine.load_layer(sys.argv[1])
fields = []
for field in layer.fields():
    fields.append({
        "name": field.name(),
        "type": field.typeName(),
        "precision": field.precision(),
        "length": field.length(),
    })
result = {
    "name": layer.name(),
    "feature_count": layer.featureCount(),
    "crs": layer.crs().authid() if layer.crs().isValid() else None,
    "extent": {
        "x_min": layer.extent().xMinimum(),
        "y_min": layer.extent().yMinimum(),
        "x_max": layer.extent().xMaximum(),
        "y_max": layer.extent().yMaximum(),
    },
    "fields": fields,
}
print(json.dumps(result), flush=True)
os._exit(0)
