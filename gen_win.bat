@echo off
REM Script to build Windows executable for printer-dont-die
REM This script must be run from the project root directory

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Change to project root (where this script is located)
cd /d "%SCRIPT_DIR%"

echo Building Windows executable...
echo Working directory: %CD%

REM Install dependencies from pyproject.toml
echo Installing dependencies...
pip install -e . >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Failed to install dependencies. Trying pip install loguru pyinstaller...
    pip install loguru pyinstaller
)

REM Run pyinstaller
pyinstaller --onefile --name printer-dont-die --hidden-import loguru --add-data="config.json;." --add-data="app/resources;app/resources" app/main.py

REM Check if dist directory exists
if not exist "dist" (
    echo ERROR: dist directory was not created
    exit /b 1
)

REM Check if config.json exists in dist, if not copy it from root
if not exist "dist\config.json" (
    echo config.json not found in dist\, copying from root...
    if exist "config.json" (
        copy config.json dist\config.json >nul
        echo Copied config.json to dist\
    ) else (
        echo WARNING: config.json not found in root directory
    )
) else (
    echo config.json already exists in dist\
)

echo.
echo Build complete!
echo Executable location: dist\printer-dont-die.exe
echo To run: dist\printer-dont-die.exe

endlocal
