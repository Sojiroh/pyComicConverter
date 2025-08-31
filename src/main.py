import argparse
import os
from converter import convert_single_file, get_supported_files

def main():
    parser = argparse.ArgumentParser(description="Convert between PDF and CBZ comic formats")
    parser.add_argument("filePath", help="Path to a PDF/CBZ file or directory containing PDF/CBZ files")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for images")
    parser.add_argument("-t", "--output-type", default="cbz", help="Output type: cbz (default) or pdf")
    
    args = parser.parse_args()
    input_path = args.filePath
    
    # Check if input is a directory or file
    if os.path.isdir(input_path):
        # Process directory - find all supported files
        files_to_process = get_supported_files(input_path)
        
        if not files_to_process:
            print(f"[!] No supported files found in directory: {input_path}")
            print(f"[!] Supported formats: PDF, CBZ")
            return
        print(f"[+] Found {len(files_to_process)} supported files to process")
        
    elif os.path.isfile(input_path):
        # Single file processing
        file_extension = os.path.splitext(input_path)[1].lower()
        if file_extension not in ['.pdf', '.cbz']:
            print(f"[!] Error: Unsupported file format '{file_extension}'. Only PDF and CBZ files are supported.")
            return
        files_to_process = [input_path]
        
    else:
        print(f"[!] Error: Path does not exist: {input_path}")
        return

    # Process all files
    total_files = len(files_to_process)
    successful_conversions = 0
    failed_conversions = 0
    
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n[+] === Processing file {i}/{total_files} ===")
        try:
            success = convert_single_file(file_path, args.output_dir, args.output_type)
            if success:
                successful_conversions += 1
            else:
                failed_conversions += 1
        except Exception as e:
            print(f"[!] Error processing {file_path}: {str(e)}")
            failed_conversions += 1
    
    # Summary
    print(f"\n[+] === Batch Processing Complete ===")
    print(f"[+] Total files processed: {total_files}")
    print(f"[+] Successful conversions: {successful_conversions}")
    if failed_conversions > 0:
        print(f"[!] Failed conversions: {failed_conversions}")


if __name__ == "__main__":
    main()
