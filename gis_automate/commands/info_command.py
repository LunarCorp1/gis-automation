import json

from gis_automate.engine import QGISEngine


def run_info(shapefile: str) -> str:
    engine = QGISEngine()
    engine.init_qgis()
    try:
        layer = engine.load_layer(shapefile)
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
        return json.dumps(result)
    finally:
        engine.close()
