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
