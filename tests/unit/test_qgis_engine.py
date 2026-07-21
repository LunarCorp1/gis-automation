"""Tests for the QGISEngine wrapper.

NOTE: Full QGIS integration tests are in tests/test_qgis_engine_integration.py
(executed as a standalone script because QGIS C++ layer has known issues with
pytest's test collection and teardown lifecycle.)
"""
from gis_automate.engine.qgis_engine import QGISEngine, QGIS_INSTALL, QGIS_PYTHON, QGIS_PYTHONPATH


def test_constants_exist():
    assert QGIS_INSTALL.exists(), "QGIS install path must exist"
    assert QGIS_PYTHON.exists(), "QGIS Python path must exist"
    assert QGIS_PYTHONPATH.exists(), "QGIS pythonpath must exist"


def test_engine_can_be_instantiated():
    engine = QGISEngine()
    assert engine._app is None
