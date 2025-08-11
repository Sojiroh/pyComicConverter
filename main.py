import fitz  # PyMuPDF
import io
import argparse
import tempfile
import os
import shutil
import zipfile
from PIL import Image

def process_single_file(file_path, output_dir, output_type):
    """Process a single PDF or CBZ file"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Create temp directory for images in current folder
    temp_dir = tempfile.mkdtemp(dir=".")
    print(f"[+] Processing: {os.path.basename(file_path)}")
    print(f"[+] Saving images to temporary directory: {temp_dir}")

    try:
        if file_extension == '.pdf':
            # Handle PDF files
            comic_file = fitz.open(file_path)
            
            # Counter for sequential image naming
            image_counter = 0

            # iterate over PDF pages
            for page_index in range(len(comic_file)):

                # get the page itself
                page = comic_file.load_page(page_index)  # load the page
                image_list = page.get_images(full=True)  # get images on the page

                # printing number of images found in this page
                if image_list:
                    print(f"[+] Found a total of {len(image_list)} images on page {page_index}")
                else:
                    print("[!] No images found on page", page_index)

                for image_index, img in enumerate(image_list, start=1):
                    # get the XREF of the image
                    xref = img[0]

                    # extract the image bytes
                    base_image = comic_file.extract_image(xref)
                    image_bytes = base_image["image"]

                    # get the image extension
                    image_ext = base_image["ext"]

                    # save the image with zero-padded filename
                    image_name = f"{image_counter:03d}.jpeg"
                    image_path = os.path.join(temp_dir, image_name)
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                        print(f"[+] Image saved as {image_path}")
                    
                    # Increment counter for next image
                    image_counter += 1
            
            comic_file.close()
            print(f"[+] Image extraction completed")
            
        elif file_extension == '.cbz':
            # Placeholder for CBZ file handling
            print(f"[!] CBZ file processing not yet implemented")
            print(f"[+] CBZ file: {file_path}")
            # TODO: Implement CBZ file processing here
            return False
        
        # Handle different output types
        if output_type.lower() == "cbz":
            # Create CBZ file from extracted images
            pdf_basename = os.path.splitext(os.path.basename(file_path))[0]
            cbz_filename = f"{pdf_basename}.cbz"
            cbz_path = os.path.join(output_dir, cbz_filename)
            
            print(f"[+] Creating CBZ archive: {cbz_path}")
            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file_name in sorted(files):
                        file_path = os.path.join(root, file_name)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            print(f"[+] CBZ archive created successfully: {cbz_path}")
        else:
            # Placeholder for other output types
            print(f"[!] Output type '{output_type}' not yet implemented")
            print(f"[+] Images remain in temporary directory: {temp_dir}")
            # TODO: Implement other output formats here
            return False
        
        return True
        
    finally:
        # Clean up temp directory
        print(f"[+] Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description="Convert between PDF and CBZ comic formats")
    parser.add_argument("file", help="Path to a PDF/CBZ file or directory containing PDF/CBZ files")
    parser.add_argument("-o", "--output-dir", default=".", help="Output directory for images")
    parser.add_argument("-t", "--output-type", default="cbz", help="Output type: cbz (default) or other formats")
    
    args = parser.parse_args()
    input_path = args.file
    
    # Check if input is a directory or file
    if os.path.isdir(input_path):
        # Process directory - find all supported files
        supported_extensions = ['.pdf', '.cbz']
        files_to_process = []
        
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in supported_extensions:
                    files_to_process.append(file_path)
        
        if not files_to_process:
            print(f"[!] No supported files found in directory: {input_path}")
            print(f"[!] Supported formats: {', '.join(supported_extensions)}")
            return
        
        files_to_process.sort()  # Process in alphabetical order
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
            success = process_single_file(file_path, args.output_dir, args.output_type)
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
