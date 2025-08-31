#!/usr/bin/env python3
"""
Build script for pyComicConverter using PyInstaller.
Creates both CLI and GUI executables for the current platform.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.pyc']
    
    print("Cleaning previous build artifacts...")
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"[OK] Removed {dir_name}/")
    
    print("[OK] Build artifacts cleaned")


def build_cli():
    """Build the CLI version."""
    return run_command([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'pycomicconverter-cli.spec'
    ], "Building CLI executable")


def build_gui():
    """Build the GUI version."""
    return run_command([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'pycomicconverter-gui.spec'
    ], "Building GUI executable")


def main():
    """Main build process."""
    print("pyComicConverter Build Script")
    print("=" * 40)
    
    # Check if PyInstaller is available
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("[FAIL] PyInstaller not found. Install with: uv sync --extra build")
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build both versions
    cli_success = build_cli()
    gui_success = build_gui()
    
    print("\n" + "=" * 40)
    print("Build Summary:")
    print(f"CLI Build: {'[OK] Success' if cli_success else '[FAIL] Failed'}")
    print(f"GUI Build: {'[OK] Success' if gui_success else '[FAIL] Failed'}")
    
    if cli_success and gui_success:
        print("\n[OK] All builds completed successfully!")
        print("Executables are in the dist/ directory:")
        dist_path = Path("dist")
        if dist_path.exists():
            for exe in dist_path.iterdir():
                if exe.is_file():
                    print(f"  - {exe}")
    else:
        print("\n[FAIL] Some builds failed. Check the output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()