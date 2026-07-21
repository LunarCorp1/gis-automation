from pathlib import Path

from ..engine import QGISEngine

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "static"


def run_map(
    shapefile: str,
    fmt: str,
    title: str | None = None,
    style: str | None = None,
    output: str | None = None,
):
    engine = QGISEngine()
    engine.init_qgis()
    try:
        layer = engine.load_layer(shapefile)

        from qgis.core import (
            QgsProject,
            QgsLayout,
            QgsLayoutItemMap,
            QgsLayoutItemLabel,
            QgsLayoutItemLegend,
            QgsLayoutItemScaleBar,
            QgsLayoutItemPicture,
            QgsLayoutExporter,
            QgsLayoutSize,
            QgsLayoutPoint,
            QgsUnitTypes,
            QgsFillSymbol,
            QgsSimpleFillSymbolLayer,
        )
        from qgis.PyQt.QtCore import QRectF, QSizeF
        from qgis.PyQt.QtGui import QFont, QColor

        project = QgsProject.instance()
        project.removeAllMapLayers()
        project.addMapLayer(layer)

        if style:
            layer.loadNamedStyle(style)

        auto_title = title or layer.name()

        output_path = Path(output) if output else OUTPUT_DIR / f"{layer.name()}.{fmt}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        layout = QgsLayout(project)
        layout.initializeDefaults()
        layout.setUnits(QgsUnitTypes.LayoutMillimeters)
        layout.pageCollection().pages().clear()
        layout.pageCollection().beginPageSizeChange()
        page = layout.pageCollection().addPage()
        page.setPageSize("A4", QgsLayoutSize.Orientation.Landscape)
        layout.pageCollection().endPageSizeChange()
        page_width = 297.0
        page_height = 210.0

        map_item = QgsLayoutItemMap(layout)
        map_item.attemptMove(QgsLayoutPoint(10, 20))
        map_item.attemptResize(QgsLayoutSize(190, 170))
        map_item.setExtent(layer.extent())
        map_item.setBackgroundColor(QColor(255, 255, 255))
        layout.addLayoutItem(map_item)

        title_item = QgsLayoutItemLabel(layout)
        title_item.setText(auto_title)
        title_item.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_item.adjustSizeToText()
        title_item.attemptMove(QgsLayoutPoint(10, 2))
        layout.addLayoutItem(title_item)

        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        legend.setFont(QFont("Arial", 8))
        legend.setStyleFont(QgsLayoutItemLegend.FontStyle.Title, QFont("Arial", 10, QFont.Weight.Bold))
        legend.attemptMove(QgsLayoutPoint(210, 20))
        layout.addLayoutItem(legend)

        scale_bar = QgsLayoutItemScaleBar(layout)
        scale_bar.setStyle("Numeric")
        scale_bar.setLinkedMap(map_item)
        scale_bar.applyDefaultSize()
        scale_bar.setFont(QFont("Arial", 7))
        scale_bar.setNumberOfSegments(2)
        scale_bar.setNumberOfSegmentsLeft(1)
        scale_bar.attemptMove(QgsLayoutPoint(10, 192))
        layout.addLayoutItem(scale_bar)

        north_svg = Path(__file__).resolve().parent.parent.parent / "gis_automate" / "templates" / "north.svg"
        if not north_svg.exists():
            north_svg.parent.mkdir(parents=True, exist_ok=True)
            north_svg.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <polygon points="50,2 42,35 50,30 58,35" fill="#333"/>
  <polygon points="50,2 42,35 50,40 58,35" fill="#999"/>
  <polygon points="42,35 50,40 50,98 42,65" fill="#999"/>
  <polygon points="58,35 50,40 50,98 58,65" fill="#ccc"/>
  <text x="50" y="13" font-family="Arial" font-size="10" font-weight="bold" text-anchor="middle" fill="#fff">N</text>
</svg>""")
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(str(north_svg))
        north.attemptMove(QgsLayoutPoint(210, 170))
        north.attemptResize(QgsLayoutSize(20, 20))
        layout.addLayoutItem(north)

        if fmt == "pdf":
            exporter = QgsLayoutExporter(layout)
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.forceVectorOutput = True
            exporter.exportToPdf(str(output_path), settings)
        else:
            exporter = QgsLayoutExporter(layout)
            img_settings = QgsLayoutExporter.ImageExportSettings()
            img_settings.imageWidth = 2480
            img_settings.imageHeight = 1754
            img_settings.dpi = 300
            exporter.exportToImage(str(output_path), img_settings)

        print(f"Map saved: {output_path}")
    finally:
        engine.close()
