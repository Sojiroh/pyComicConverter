#!/usr/bin/env python3
"""
Simple launcher for the Comic Converter GUI.
This script provides a fallback if tkinter has issues.
"""
import sys
import os

def main():
    try:
        # Try to import and run the GUI
        from gui import main as gui_main
        print("Starting Comic Converter GUI...")
        gui_main()
    
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("uv sync")
        print("or: pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("\nTkinter may not be properly configured on your system.")
        print("You can still use the command-line interface:")
        print("python main.py --help")
        
        # Offer to run a simple CLI version
        response = input("\nWould you like to try a simple file conversion now? (y/n): ").lower()
        if response == 'y':
            run_simple_conversion()
        sys.exit(1)

def run_simple_conversion():
    """Run a simple interactive conversion"""
    try:
        from converter import convert_single_file
        import os
        from pathlib import Path
        
        print("\n=== Simple Comic Converter ===")
        
        # Get input file
        while True:
            file_path = input("Enter path to PDF or CBZ file: ").strip().strip('"\'')
            if os.path.isfile(file_path):
                break
            print("File not found. Please try again.")
        
        # Get output format
        while True:
            output_type = input("Convert to (pdf/cbz): ").lower().strip()
            if output_type in ['pdf', 'cbz']:
                break
            print("Please enter 'pdf' or 'cbz'")
        
        # Get output directory
        output_dir = input(f"Output directory (press Enter for current directory): ").strip()
        if not output_dir:
            output_dir = "."
        
        print(f"\nConverting {os.path.basename(file_path)} to {output_type.upper()}...")
        
        # Perform conversion
        def progress_callback(progress):
            print(f"Progress: {progress.current_operation}")
        
        success = convert_single_file(file_path, output_dir, output_type, progress_callback)
        
        if success:
            print(f"\n✅ Conversion successful! Output saved to: {output_dir}")
        else:
            print("\n❌ Conversion failed. Check the messages above for details.")
    
    except KeyboardInterrupt:
        print("\nConversion cancelled.")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    main()