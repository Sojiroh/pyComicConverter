#!/bin/bash
# Build script for Unix-like systems (Linux/macOS)

set -e  # Exit on any error

echo "pyComicConverter Build Script (Unix)"
echo "===================================="

# Check if uv is available
if command -v uv >/dev/null 2>&1; then
    echo "Installing build dependencies..."
    uv sync --extra build
else
    echo "uv not found. Installing PyInstaller with pip..."
    pip install pyinstaller>=6.0
fi

# Run the Python build script
python src/build.py

echo ""
echo "Build completed! Check the dist/ directory for executables."