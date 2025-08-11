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
            # Track extracted image XREFs to avoid duplicates
            extracted_xrefs = set()

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
                    
                    # Skip if we've already extracted this image
                    if xref in extracted_xrefs:
                        print(f"[!] Skipping duplicate image (XREF {xref}) on page {page_index}")
                        continue
                    
                    # Mark this XREF as extracted
                    extracted_xrefs.add(xref)

                    # extract the image bytes
                    base_image = comic_file.extract_image(xref)
                    image_bytes = base_image["image"]

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
            # Handle CBZ files - extract images from zip archive
            print(f"[+] Processing CBZ file: {file_path}")
            
            # Counter for sequential image naming
            image_counter = 0
            
            with zipfile.ZipFile(file_path, 'r') as cbz_file:
                # Get all image files from CBZ, sorted by name
                image_files = sorted([f for f in cbz_file.namelist() 
                                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'))])
                
                if not image_files:
                    print("[!] No image files found in CBZ archive")
                    return False
                
                print(f"[+] Found {len(image_files)} images in CBZ archive")
                
                # Extract each image to temp directory
                for image_file in image_files:
                    try:
                        # Extract image data
                        image_data = cbz_file.read(image_file)
                        
                        # Save with sequential naming
                        image_name = f"{image_counter:03d}.jpeg"
                        image_path = os.path.join(temp_dir, image_name)
                        
                        # Convert to JPEG if necessary using PIL
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            # Convert to RGB if necessary (for PNG with transparency, etc.)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                            img.save(image_path, 'JPEG', quality=95)
                            print(f"[+] Image saved as {image_path}")
                        except Exception as e:
                            print(f"[!] Error processing image {image_file}: {str(e)}")
                            continue
                        
                        image_counter += 1
                        
                    except Exception as e:
                        print(f"[!] Error extracting {image_file}: {str(e)}")
                        continue
            
            print(f"[+] CBZ extraction completed, {image_counter} images processed")
        
        # Handle different output types
        if output_type.lower() == "cbz":
            # Create CBZ file from extracted images
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            cbz_filename = f"{input_basename}.cbz"
            cbz_path = os.path.join(output_dir, cbz_filename)
            
            print(f"[+] Creating CBZ archive: {cbz_path}")
            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file_name in sorted(files):
                        file_path = os.path.join(root, file_name)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            print(f"[+] CBZ archive created successfully: {cbz_path}")
            
        elif output_type.lower() == "pdf":
            # Create PDF file from extracted images
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            pdf_filename = f"{input_basename}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            print(f"[+] Creating PDF document: {pdf_path}")
            
            # Get list of images sorted by name
            image_files = sorted([f for f in os.listdir(temp_dir) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            
            if not image_files:
                print("[!] No images found for PDF creation")
                return False
            
            # Create PDF document
            pdf_doc = fitz.open()  # Create new PDF document
            
            for image_file in image_files:
                image_path = os.path.join(temp_dir, image_file)
                try:
                    # Open image to get dimensions
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    img.close()
                    
                    # Create page with image dimensions (convert pixels to points, 72 DPI)
                    page_width = img_width * 72 / 96  # Assuming 96 DPI for pixel to point conversion
                    page_height = img_height * 72 / 96
                    
                    # Create new page in PDF
                    page = pdf_doc.new_page(width=page_width, height=page_height)
                    
                    # Insert image to fill the entire page
                    page.insert_image(fitz.Rect(0, 0, page_width, page_height), filename=image_path)
                    
                    print(f"[+] Added image {image_file} to PDF")
                    
                except Exception as e:
                    print(f"[!] Error adding image {image_file} to PDF: {str(e)}")
                    continue
            
            # Save PDF document
            pdf_doc.save(pdf_path)
            pdf_doc.close()
            print(f"[+] PDF document created successfully: {pdf_path}")
            
        else:
            print(f"[!] Output type '{output_type}' not supported")
            print(f"[!] Supported output types: cbz, pdf")
            print(f"[+] Images remain in temporary directory: {temp_dir}")
            return False
        
        return True
        
    finally:
        # Clean up temp directory
        print(f"[+] Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

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
