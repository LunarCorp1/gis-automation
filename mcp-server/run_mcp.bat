@echo off
set "SHAPEFILES_DIR=C:\Users\LUNAR\Desktop\SHAPEFILES"
set "QT_QPA_PLATFORM=offscreen"
set "PYTHONHOME=C:\Program Files\QGIS 3.40.1\apps\Python312"
set "PYTHONPATH=C:\Program Files\QGIS 3.40.1\apps\qgis\python"
set "PATH=C:\Program Files\QGIS 3.40.1\apps\qgis\bin;C:\Program Files\QGIS 3.40.1\bin;C:\Program Files\QGIS 3.40.1\apps\Python312\Scripts;C:\Program Files\QGIS 3.40.1\apps\Python312;%PATH%"
"C:\Program Files\QGIS 3.40.1\bin\python3.exe" -u "%~dp0server.py" %*
