@echo off
REM Build script for Windows

echo pyComicConverter Build Script (Windows)
echo ======================================

REM Check if uv is available
where uv >nul 2>nul
if %errorlevel% == 0 (
    echo Installing build dependencies...
    uv sync --extra build
) else (
    echo uv not found. Installing PyInstaller with pip...
    pip install "pyinstaller>=6.0"
)

REM Run the Python build script
python build.py

echo.
echo Build completed! Check the dist\ directory for executables.
pause