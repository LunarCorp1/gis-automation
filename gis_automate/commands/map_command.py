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
            QgsMapRendererParallelJob,
        )
        from qgis.PyQt.QtCore import QSize
        from qgis.PyQt.QtGui import QColor, QImage, QPainter

        project = QgsProject.instance()
        project.removeAllMapLayers()
        project.addMapLayer(layer)

        if style:
            layer.loadNamedStyle(style)

        output_path = Path(output) if output else OUTPUT_DIR / f"{layer.name()}.{fmt}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "pdf":
            layout_obj = QgsPrintLayout(project)
            layout_obj.initializeDefaults()
            layout_obj.setName(layer.name())

            page = layout_obj.pageCollection().pages()[0]
            page.setPageSize("A4", QgsLayoutSize.Orientation.Landscape)

            map_item = layout_obj.itemById("map")
            if map_item:
                map_item.zoomToExtent(layer.extent())

            exporter = QgsLayoutExporter(layout_obj)
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
