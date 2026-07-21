from .qgis_engine import QGISEngine

try:
    from .arcpy_engine import arcpy_available
except ImportError:
    def arcpy_available() -> bool:
        return False

__all__ = ["QGISEngine", "arcpy_available"]
