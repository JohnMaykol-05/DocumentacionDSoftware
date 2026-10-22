@echo off
setlocal
cd /d "%~dp0"
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 goto fallo
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fallo
echo.
echo Instalacion completada. Abre jugar.bat para iniciar.
pause
exit /b 0
:fallo
echo.
echo No se pudo completar la instalacion. Revisa el error y el archivo README.md.
pause
exit /b 1
