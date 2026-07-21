@echo off
set "PYTHONHOME=C:\Program Files\QGIS 3.40.1\apps\Python312"
set "PYTHONPATH=C:\Program Files\QGIS 3.40.1\apps\qgis\python"
set "PATH=C:\Program Files\QGIS 3.40.1\apps\qgis\bin;C:\Program Files\QGIS 3.40.1\bin;C:\Program Files\QGIS 3.40.1\apps\Python312\Scripts;C:\Program Files\QGIS 3.40.1\apps\Python312;%PATH%"
"C:\Program Files\QGIS 3.40.1\bin\python3.exe" %*
