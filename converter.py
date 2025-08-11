import fitz  # PyMuPDF
import io
import tempfile
import os
import shutil
import zipfile
from PIL import Image
from typing import Callable, Optional, List


class ConversionProgress:
    """Class to track and report conversion progress"""
    def __init__(self, total_files: int = 1):
        self.total_files = total_files
        self.current_file = 0
        self.current_operation = ""
        self.success_count = 0
        self.error_count = 0
        self.errors = []
    
    def update(self, operation: str, file_index: int = None):
        """Update progress with current operation"""
        self.current_operation = operation
        if file_index is not None:
            self.current_file = file_index
    
    def add_success(self):
        """Mark a file as successfully converted"""
        self.success_count += 1
    
    def add_error(self, error_msg: str):
        """Add an error message"""
        self.error_count += 1
        self.errors.append(error_msg)
    
    def get_progress_percent(self) -> int:
        """Get current progress as percentage"""
        if self.total_files == 0:
            return 100
        return int((self.current_file / self.total_files) * 100)


def convert_single_file(file_path: str, output_dir: str, output_type: str, 
                       progress_callback: Optional[Callable[[ConversionProgress], None]] = None) -> bool:
    """
    Convert a single PDF or CBZ file
    
    Args:
        file_path: Path to input file
        output_dir: Directory to save output
        output_type: 'pdf' or 'cbz'
        progress_callback: Optional callback for progress updates
    
    Returns:
        True if successful, False otherwise
    """
    progress = ConversionProgress(1)
    
    def update_progress(operation: str):
        progress.update(operation)
        if progress_callback:
            progress_callback(progress)
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Create temp directory for images in current folder
    temp_dir = tempfile.mkdtemp()
    update_progress(f"Processing: {os.path.basename(file_path)}")
    
    try:
        if file_extension == '.pdf':
            update_progress("Extracting images from PDF...")
            success = _extract_pdf_images(file_path, temp_dir, update_progress)
            if not success:
                return False
                
        elif file_extension == '.cbz':
            update_progress("Extracting images from CBZ...")
            success = _extract_cbz_images(file_path, temp_dir, update_progress)
            if not success:
                return False
        else:
            progress.add_error(f"Unsupported file format: {file_extension}")
            return False
        
        # Create output file
        if output_type.lower() == "cbz":
            update_progress("Creating CBZ archive...")
            success = _create_cbz(file_path, temp_dir, output_dir, update_progress)
        elif output_type.lower() == "pdf":
            update_progress("Creating PDF document...")
            success = _create_pdf(file_path, temp_dir, output_dir, update_progress)
        else:
            progress.add_error(f"Unsupported output type: {output_type}")
            return False
        
        if success:
            progress.add_success()
            update_progress("Conversion completed successfully")
        
        return success
        
    except Exception as e:
        progress.add_error(f"Error processing {file_path}: {str(e)}")
        return False
        
    finally:
        # Clean up temp directory
        update_progress("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)


def convert_multiple_files(file_paths: List[str], output_dir: str, output_type: str,
                          progress_callback: Optional[Callable[[ConversionProgress], None]] = None) -> ConversionProgress:
    """
    Convert multiple files
    
    Args:
        file_paths: List of file paths to convert
        output_dir: Directory to save outputs
        output_type: 'pdf' or 'cbz'
        progress_callback: Optional callback for progress updates
    
    Returns:
        ConversionProgress object with results
    """
    progress = ConversionProgress(len(file_paths))
    
    for i, file_path in enumerate(file_paths):
        progress.update(f"Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}", i)
        if progress_callback:
            progress_callback(progress)
        
        try:
            success = convert_single_file(file_path, output_dir, output_type)
            if success:
                progress.add_success()
            else:
                progress.add_error(f"Failed to convert {os.path.basename(file_path)}")
        except Exception as e:
            progress.add_error(f"Error processing {os.path.basename(file_path)}: {str(e)}")
    
    progress.current_file = len(file_paths)
    progress.update("Batch conversion completed")
    if progress_callback:
        progress_callback(progress)
    
    return progress


def _extract_pdf_images(file_path: str, temp_dir: str, update_progress: Callable[[str], None]) -> bool:
    """Extract images from PDF file"""
    try:
        comic_file = fitz.open(file_path)
        image_counter = 0
        extracted_xrefs = set()
        
        for page_index in range(len(comic_file)):
            page = comic_file.load_page(page_index)
            image_list = page.get_images(full=True)
            
            if image_list:
                update_progress(f"Found {len(image_list)} images on page {page_index}")
            
            for img in image_list:
                xref = img[0]
                
                if xref in extracted_xrefs:
                    continue
                
                extracted_xrefs.add(xref)
                base_image = comic_file.extract_image(xref)
                image_bytes = base_image["image"]
                
                image_name = f"{image_counter:03d}.jpeg"
                image_path = os.path.join(temp_dir, image_name)
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                image_counter += 1
        
        comic_file.close()
        return image_counter > 0
        
    except Exception as e:
        update_progress(f"Error extracting PDF images: {str(e)}")
        return False


def _extract_cbz_images(file_path: str, temp_dir: str, update_progress: Callable[[str], None]) -> bool:
    """Extract images from CBZ file"""
    try:
        image_counter = 0
        
        with zipfile.ZipFile(file_path, 'r') as cbz_file:
            image_files = sorted([f for f in cbz_file.namelist() 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'))])
            
            if not image_files:
                update_progress("No image files found in CBZ archive")
                return False
            
            update_progress(f"Found {len(image_files)} images in CBZ archive")
            
            for image_file in image_files:
                try:
                    image_data = cbz_file.read(image_file)
                    
                    image_name = f"{image_counter:03d}.jpeg"
                    image_path = os.path.join(temp_dir, image_name)
                    
                    img = Image.open(io.BytesIO(image_data))
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    img.save(image_path, 'JPEG', quality=95)
                    
                    image_counter += 1
                    
                except Exception as e:
                    update_progress(f"Error processing image {image_file}: {str(e)}")
                    continue
        
        return image_counter > 0
        
    except Exception as e:
        update_progress(f"Error extracting CBZ images: {str(e)}")
        return False


def _create_cbz(input_file_path: str, temp_dir: str, output_dir: str, update_progress: Callable[[str], None]) -> bool:
    """Create CBZ file from images"""
    try:
        input_basename = os.path.splitext(os.path.basename(input_file_path))[0]
        cbz_filename = f"{input_basename}.cbz"
        cbz_path = os.path.join(output_dir, cbz_filename)
        
        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file_name in sorted(files):
                    file_path = os.path.join(root, file_name)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        update_progress(f"CBZ archive created: {cbz_path}")
        return True
        
    except Exception as e:
        update_progress(f"Error creating CBZ: {str(e)}")
        return False


def _create_pdf(input_file_path: str, temp_dir: str, output_dir: str, update_progress: Callable[[str], None]) -> bool:
    """Create PDF file from images"""
    try:
        input_basename = os.path.splitext(os.path.basename(input_file_path))[0]
        pdf_filename = f"{input_basename}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        image_files = sorted([f for f in os.listdir(temp_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        
        if not image_files:
            update_progress("No images found for PDF creation")
            return False
        
        pdf_doc = fitz.open()
        
        for image_file in image_files:
            image_path = os.path.join(temp_dir, image_file)
            try:
                img = Image.open(image_path)
                img_width, img_height = img.size
                img.close()
                
                page_width = img_width * 72 / 96
                page_height = img_height * 72 / 96
                
                page = pdf_doc.new_page(width=page_width, height=page_height)
                page.insert_image(fitz.Rect(0, 0, page_width, page_height), filename=image_path)
                
            except Exception as e:
                update_progress(f"Error adding image {image_file} to PDF: {str(e)}")
                continue
        
        pdf_doc.save(pdf_path)
        pdf_doc.close()
        update_progress(f"PDF document created: {pdf_path}")
        return True
        
    except Exception as e:
        update_progress(f"Error creating PDF: {str(e)}")
        return False


def get_supported_files(directory: str) -> List[str]:
    """Get list of supported files in directory"""
    supported_extensions = ['.pdf', '.cbz']
    files = []
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in supported_extensions:
                files.append(file_path)
    
    return sorted(files)