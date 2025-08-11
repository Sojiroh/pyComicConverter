# Build Guide

This document explains how to build pyComicConverter executables for different platforms.

## Local Building

### Prerequisites
- Python 3.13+
- uv package manager (recommended) or pip

### Quick Build
```bash
# Install build dependencies
uv sync --extra build

# Build both CLI and GUI executables
python build.py
```

### Platform-Specific Scripts
```bash
# Unix/Linux/macOS
./build.sh

# Windows
build.bat
```

### Manual PyInstaller Commands
```bash
# CLI version
python -m PyInstaller --clean pycomicconverter-cli.spec

# GUI version (creates .app bundle on macOS)
python -m PyInstaller --clean pycomicconverter-gui.spec
```

## Automated Building (GitHub Actions)

### On Every Push/PR
- Quick Linux build test runs automatically
- Validates that the build process works

### On Release
1. Create a new release on GitHub
2. Multi-platform builds trigger automatically
3. Executables are built for:
   - Linux x64 (`pycomicconverter-linux-x64.tar.gz`)
   - Windows x64 (`pycomicconverter-windows-x64.zip`)
   - macOS ARM64 (`pycomicconverter-macos-arm64.tar.gz`)
4. Release assets are automatically uploaded

## Output Files

### Linux/Windows
- `pycomicconverter-cli` - Command-line version
- `pycomicconverter-gui` - GUI version (directory-based)

### macOS
- `pycomicconverter-cli` - Command-line version
- `pyComicConverter.app` - Native macOS app bundle

## Distribution

The built executables are self-contained and include:
- Python runtime
- All dependencies (PyMuPDF, Pillow, tkinter)
- No installation required on target systems

### System Requirements
- **Linux**: glibc 2.17+ (most modern distributions)
- **Windows**: Windows 10/11, Windows Server 2019+
- **macOS**: macOS 11+ (Big Sur), Apple Silicon Macs

## Troubleshooting

### Build Fails
1. Ensure Python 3.13+ is installed
2. Install build dependencies: `uv sync --extra build`
3. Clean previous builds: `rm -rf build dist`

### Missing Dependencies on Target Systems
The executables should be self-contained. If issues occur:
- On Linux: Install `libfontconfig1` if missing
- On Windows: Install Visual C++ Redistributable if needed
- On macOS: No additional dependencies required

### Performance
- First run may be slower (PyInstaller extraction)
- Subsequent runs are at native speed
- File sizes are larger due to bundled dependencies (~50-100MB)