#!/usr/bin/env python3
"""
Test script to verify the build process works locally.
This simulates what the GitHub Actions workflow will do.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description} exists ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description} missing")
        return False


def main():
    """Main test routine."""
    print("pyComicConverter Build Test")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    success = True
    
    # Test 1: Install build dependencies
    if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=6.0'], 
                      "Installing PyInstaller"):
        success = False
    
    # Test 2: Clean previous builds
    print(f"\n🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"✅ Removed {dir_name}/")
    
    # Test 3: Run build script
    if not run_command([sys.executable, 'build.py'], "Running build script"):
        success = False
    
    # Test 4: Verify outputs exist
    print(f"\n📋 Verifying build outputs...")
    
    cli_path = "dist/pycomicconverter-cli"
    gui_path = "dist/pycomicconverter-gui"
    app_path = "dist/pyComicConverter.app"
    
    if platform.system() == "Windows":
        cli_path += ".exe"
        gui_path += ".exe"
    
    if not check_file_exists(cli_path, "CLI executable"):
        success = False
    
    if platform.system() == "Darwin":  # macOS
        if not check_file_exists(app_path, "macOS app bundle"):
            success = False
    else:
        if not check_file_exists(gui_path, "GUI executable"):
            success = False
    
    # Test 5: Test CLI executable
    if os.path.exists(cli_path):
        if not run_command([cli_path, '--help'], "Testing CLI executable"):
            success = False
    
    # Test 6: List dist directory contents
    print(f"\n📁 Contents of dist/ directory:")
    if os.path.exists("dist"):
        for item in Path("dist").rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                print(f"  {item} ({size:,} bytes)")
    
    # Summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Build process is working correctly")
        print("✅ Ready for GitHub Actions deployment")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Fix issues before deploying to GitHub Actions")
        sys.exit(1)
    print(f"{'='*50}")


if __name__ == '__main__':
    main()