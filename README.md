# pyComicConverter

A Python utility for converting between PDF and CBZ comic book formats. Extract images from PDF files and package them into CBZ archives for use with comic book readers.

## Features

- 📚 Extract images from PDF files
- 📦 Create CBZ (Comic Book ZIP) archives  
- 🔢 Sequential image naming (000.jpeg, 001.jpeg, etc.)
- 🗂️ Customizable output directory
- 📁 **Batch processing** - Process entire directories of files
- 📊 Progress tracking and success/failure reporting
- 🧹 Automatic cleanup of temporary files
- ⚡ Fast processing with PyMuPDF

## Installation

### Prerequisites

- Python 3.13+
- uv (recommended) or pip

### Using uv (recommended)

```bash
git clone https://github.com/sojiroh/pyComicConverter.git
cd pyComicConverter
uv sync
```

### Using pip

```bash
git clone https://github.com/sojiroh/pyComicConverter.git
cd pyComicConverter
pip install -r requirements.txt
```

## Usage

### Basic Usage

**Single File Conversion:**
```bash
python main.py "path/to/your/comic.pdf"
```

**Batch Processing (Directory):**
```bash
python main.py "/path/to/comics/directory/"
```

### Advanced Options

```bash
# Single file with options
python main.py "input.pdf" -o "/output/directory" -t cbz

# Batch process directory with options  
python main.py "/comics/folder/" -o "/converted/" -t cbz
```

### Command Line Arguments

- `file` - Path to a PDF/CBZ file **or directory** containing PDF/CBZ files
- `-o, --output-dir` - Output directory for converted files (default: current directory)
- `-t, --output-type` - Output format: `cbz` (default) or other formats (coming soon)

### Examples

```bash
# Convert single PDF to CBZ in current directory
python main.py "Manga Vol 1.pdf"

# Convert single file with custom output directory
python main.py "Comic Book.pdf" -o ~/Comics/

# Batch process entire directory
python main.py "/home/user/Comics/" -o ~/Converted/

# Process directory with explicit CBZ output
python main.py "/Comics/PDFs/" -t cbz -o ~/Downloads/CBZ/
```

### Batch Processing Features

- 📁 **Automatic file discovery** - Finds all `.pdf` and `.cbz` files in the directory
- 📊 **Progress tracking** - Shows "Processing file X/Y" for each file
- 🛡️ **Error resilience** - Individual file failures don't stop the entire batch
- 📋 **Processing summary** - Final report shows successful/failed conversions
- 🔤 **Alphabetical order** - Files are processed in sorted order for consistency

## Supported Formats

### Input Formats
- **PDF** - Portable Document Format
- **CBZ** - Comic Book ZIP (coming soon)

### Output Formats
- **CBZ** - Comic Book ZIP format
- **Other formats** - Additional formats planned

## How It Works

1. **Extraction**: The tool opens the PDF file and extracts all images from each page
2. **Processing**: Images are saved with sequential naming (000.jpeg, 001.jpeg, etc.)
3. **Packaging**: All extracted images are compressed into a CBZ archive
4. **Cleanup**: Temporary files are automatically removed

## Technical Details

### Dependencies

- **PyMuPDF (fitz)** - PDF processing and image extraction
- **Pillow** - Image processing capabilities
- **zipfile** - CBZ archive creation (built-in)

### Image Naming Convention

Images are named using zero-padded sequential numbers:
- `000.jpeg` - First image
- `001.jpeg` - Second image  
- `002.jpeg` - Third image
- ... and so on

This ensures proper sorting in comic book readers.

## Development

### Project Structure

```
pyComicConverter/
   main.py           # Main application
   pyproject.toml    # Project configuration
   uv.lock          # Dependency lock file
   README.md        # This file
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sojiroh/pyComicConverter.git
cd pyComicConverter

# Install dependencies
uv sync

# Run the application
python main.py "test.pdf"

# Or use uv to run
uv run python main.py "test.pdf"
```

## Troubleshooting

### Common Issues

**File not found error**
- Ensure the PDF file path is correct
- Use quotes around file paths with spaces

**Permission errors**
- Check write permissions in the output directory
- Run with appropriate user permissions

**Unsupported file format**
- Only PDF and CBZ files are supported
- Check file extension is `.pdf` or `.cbz`

### Error Messages

- `Unsupported file format` - File must be .pdf or .cbz
- `CBZ file processing not yet implemented` - CBZ input support coming soon
- `Output type 'X' not yet implemented` - Only CBZ output currently supported

## Roadmap

- [x] **Batch processing multiple files** ✅ *Completed!*
- [x] **CBZ to PDF conversion** ✅ *Completed!*
- [x] **CBZ to CBZ reprocessing** ✅ *Completed!* 
- [ ] Additional output formats (CBR, EPUB)
- [x] **GUI interface** ✅ *Completed!* 
- [ ] Image optimization options
- [ ] Metadata preservation
- [ ] Recursive directory processing (subdirectories)
- [ ] File filtering options (by size, page count, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [AGPL-3.0 License](LICENSE).

## Acknowledgments

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for robust PDF processing
- Uses [Pillow](https://pillow.readthedocs.io/) for image handling
- Developed with [uv](https://github.com/astral-sh/uv) for modern Python packaging

---

**Note**: This tool is designed for personal use with legally owned comic books and PDFs. Please respect copyright laws and only convert content you have the right to modify.