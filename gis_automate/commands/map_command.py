from pathlib import Path

from ..engine import QGISEngine

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "static"

QGIS_SVG = r"C:\Program Files\QGIS 3.40.1\apps\qgis\svg"


def _style_polygon_layer(layer):
    from qgis.core import QgsFillSymbol, QgsSimpleFillSymbolLayer, QgsSingleSymbolRenderer
    from qgis.PyQt.QtGui import QColor

    fill = QgsSimpleFillSymbolLayer()
    fill.setColor(QColor(255, 245, 230))
    fill.setStrokeColor(QColor(60, 40, 20))
    fill.setStrokeWidth(0.3)

    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, fill)
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


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
            QgsLayoutItemPage,
            QgsLegendStyle,
        )
        from qgis.PyQt.QtGui import QFont, QColor

        project = QgsProject.instance()
        project.removeAllMapLayers()

        if style:
            layer.loadNamedStyle(style)
        else:
            _style_polygon_layer(layer)

        project.addMapLayer(layer)

        auto_title = title or layer.name()

        output_path = Path(output) if output else OUTPUT_DIR / f"{layer.name()}.{fmt}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        layout = QgsLayout(project)
        layout.initializeDefaults()
        layout.setUnits(QgsUnitTypes.LayoutMillimeters)
        page = layout.pageCollection().pages()[0]
        page.setPageSize("A4", QgsLayoutItemPage.Landscape)

        page_width = 297.0
        page_height = 210.0
        margin = 8

        map_item = QgsLayoutItemMap(layout)
        map_item.attemptMove(QgsLayoutPoint(margin, 22))
        map_item.attemptResize(QgsLayoutSize(178, page_height - 30))
        map_item.setExtent(layer.extent())
        map_item.setBackgroundColor(QColor(230, 240, 250))
        map_item.setFrameEnabled(True)
        map_item.setFrameStrokeWidth(map_item.frameStrokeWidth())
        map_item.setFrameStrokeColor(QColor(50, 50, 50))
        layout.addLayoutItem(map_item)

        title_item = QgsLayoutItemLabel(layout)
        title_item.setText(f"<h2>{auto_title}</h2>")
        title_item.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_item.setMode(QgsLayoutItemLabel.ModeHtml)
        title_item.adjustSizeToText()
        title_item.attemptMove(QgsLayoutPoint(margin, 1))
        layout.addLayoutItem(title_item)

        right_x = margin + 178 + 5
        right_w = page_width - right_x - margin

        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        legend.setStyleFont(QgsLegendStyle.Title, QFont("Arial", 11, QFont.Weight.Bold))
        legend.setStyleFont(QgsLegendStyle.Subgroup, QFont("Arial", 9))
        legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Arial", 9))
        legend.setColumnCount(1)
        legend.attemptMove(QgsLayoutPoint(right_x, 22))
        legend.attemptResize(QgsLayoutSize(right_w, 50))
        layout.addLayoutItem(legend)

        scale_bar = QgsLayoutItemScaleBar(layout)
        scale_bar.setStyle("Line Ticks Up")
        scale_bar.setLinkedMap(map_item)
        scale_bar.applyDefaultSize()
        scale_bar.setFont(QFont("Arial", 7))
        scale_bar.setNumberOfSegments(3)
        scale_bar.setNumberOfSegmentsLeft(0)
        scale_bar.attemptMove(QgsLayoutPoint(margin, page_height - margin - 8))
        scale_bar.attemptResize(QgsLayoutSize(80, 10))
        layout.addLayoutItem(scale_bar)

        north_path = str(Path(QGIS_SVG) / "arrows" / "NorthArrow_02.svg")
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(north_path)
        north.attemptMove(QgsLayoutPoint(right_x, 100))
        north.attemptResize(QgsLayoutSize(24, 24))
        north.setFrameEnabled(False)
        layout.addLayoutItem(north)

        credit = QgsLayoutItemLabel(layout)
        credit.setText("Generated with GIS Automate")
        credit.setFont(QFont("Arial", 6))
        credit.setFontColor(QColor(150, 150, 150))
        credit.adjustSizeToText()
        credit.attemptMove(QgsLayoutPoint(
            page_width - margin - credit.sizeWithUnits().width(),
            page_height - margin - 3,
        ))
        layout.addLayoutItem(credit)

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
