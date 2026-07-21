from __future__ import annotations

import os
import sys
from pathlib import Path


QGIS_INSTALL = Path(r"C:\Program Files\QGIS 3.40.1")
QGIS_PYTHON = QGIS_INSTALL / "apps" / "Python312"
QGIS_PYTHONPATH = QGIS_INSTALL / "apps" / "qgis" / "python"
QGIS_BIN = QGIS_INSTALL / "apps" / "qgis" / "bin"


class QGISEngine:
    def __init__(self) -> None:
        self._app = None

    def init_qgis(self) -> None:
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
        try:
            from qgis.core import QgsApplication

            self._app = QgsApplication([], False)
        except Exception as exc:
            raise RuntimeError(
                f"QGIS engine failed to initialize: {exc}"
            ) from exc
        self._app.initQgis()

    def load_layer(self, shapefile_path: str) -> QgsVectorLayer:
        from qgis.core import QgsVectorLayer

        path = str(Path(shapefile_path).resolve())
        layer_name = Path(path).stem
        layer = QgsVectorLayer(path, layer_name, "ogr")
        if not layer.isValid():
            raise ValueError(f"Failed to load layer: {shapefile_path}")
        return layer

    def close(self) -> None:
        if self._app:
            self._app.exitQgis()
            self._app = None
