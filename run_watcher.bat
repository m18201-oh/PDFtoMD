@echo off
set "PYTHON_EXE=C:\Code\PDFtoMD\.venv\Scripts\python.exe"
set "WATCHER_SCRIPT=C:\Code\PDFtoMD\watcher.py"

echo Starting PDFtoMD Watcher...
cd /d "C:\Code\PDFtoMD"
"%PYTHON_EXE%" "%WATCHER_SCRIPT%"
pause
