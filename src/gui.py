import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from typing import List, Optional
import queue

from converter import convert_single_file, convert_multiple_files, get_supported_files, ConversionProgress


class ComicConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Converter - PDF ↔ CBZ")
        self.root.geometry("700x800")
        self.root.minsize(600, 500)
        
        # Variables
        self.selected_files = []
        self.output_format = tk.StringVar(value="cbz")
        self.output_directory = tk.StringVar(value=str(Path.home()))
        self.is_converting = False
        
        # Queue for thread communication
        self.progress_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_drag_drop()
        
        # Start checking for progress updates
        self.check_progress_queue()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Comic Book Format Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # File list with scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(list_frame, height=6)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        listbox_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        # File selection buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Add Directory...", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT)
        
        # Drag and drop hint
        hint_label = ttk.Label(file_frame, text="💡 Tip: You can drag and drop files or folders here", 
                              font=("Arial", 9), foreground="gray")
        hint_label.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        # Conversion options section
        options_frame = ttk.LabelFrame(main_frame, text="Conversion Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Output format
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Radiobutton(format_frame, text="PDF", variable=self.output_format, 
                       value="pdf").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(format_frame, text="CBZ", variable=self.output_format, 
                       value="cbz").pack(side=tk.LEFT)
        
        # Output directory
        ttk.Label(options_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        dir_frame = ttk.Frame(options_frame)
        dir_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_directory)
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=1)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress text
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=8, state=tk.DISABLED)
        self.progress_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Convert button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.convert_button = ttk.Button(button_frame, text="Convert Files", 
                                       command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack()
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Enable drag and drop on the file listbox
        self.file_listbox.bind("<Button-1>", lambda e: self.file_listbox.focus_set())
        
        # For now, we'll implement basic drag and drop
        # Full drag and drop would require additional libraries like tkinterdnd2
        pass
    
    def add_files(self):
        """Open file dialog to add files"""
        files = filedialog.askopenfilenames(
            title="Select PDF or CBZ files",
            filetypes=[
                ("Comic files", "*.pdf *.cbz"),
                ("PDF files", "*.pdf"),
                ("CBZ files", "*.cbz"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
    
    def add_directory(self):
        """Add all supported files from a directory"""
        directory = filedialog.askdirectory(title="Select directory containing comic files")
        if not directory:
            return
        
        try:
            supported_files = get_supported_files(directory)
            added_count = 0
            
            for file_path in supported_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_listbox.insert(tk.END, os.path.basename(file_path))
                    added_count += 1
            
            if added_count == 0:
                messagebox.showinfo("No New Files", "No new supported files found in the selected directory.")
            else:
                self.log_message(f"Added {added_count} files from directory: {directory}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error reading directory: {str(e)}")
    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.log_message("Cleared all files from list")
    
    def remove_selected(self):
        """Remove selected files from the list"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.selected_files.pop(index)
            self.file_listbox.delete(index)
        
        self.log_message(f"Removed {len(selection)} file(s) from list")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select output directory",
            initialdir=self.output_directory.get()
        )
        if directory:
            self.output_directory.set(directory)
    
    def log_message(self, message: str):
        """Add a message to the progress text area"""
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, f"{message}\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if self.is_converting:
            return
        
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to convert first.")
            return
        
        if not os.path.exists(self.output_directory.get()):
            messagebox.showerror("Invalid Directory", "Please select a valid output directory.")
            return
        
        # Clear progress
        self.progress_var.set(0)
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state=tk.DISABLED)
        
        # Disable convert button
        self.is_converting = True
        self.convert_button.config(text="Converting...", state=tk.DISABLED)
        
        # Start conversion thread
        thread = threading.Thread(target=self.conversion_worker)
        thread.daemon = True
        thread.start()
    
    def conversion_worker(self):
        """Worker function that runs in a separate thread"""
        try:
            def progress_callback(progress: ConversionProgress):
                self.progress_queue.put(progress)
            
            # Convert files
            result = convert_multiple_files(
                self.selected_files,
                self.output_directory.get(),
                self.output_format.get(),
                progress_callback
            )
            
            # Send final result
            self.progress_queue.put(("COMPLETE", result))
            
        except Exception as e:
            self.progress_queue.put(("ERROR", str(e)))
    
    def check_progress_queue(self):
        """Check for progress updates from the worker thread"""
        try:
            while True:
                item = self.progress_queue.get_nowait()
                
                if isinstance(item, ConversionProgress):
                    # Update progress
                    self.progress_var.set(item.get_progress_percent())
                    self.log_message(item.current_operation)
                    
                elif isinstance(item, tuple):
                    if item[0] == "COMPLETE":
                        result = item[1]
                        self.conversion_complete(result)
                    elif item[0] == "ERROR":
                        self.conversion_error(item[1])
                    break
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)
    
    def conversion_complete(self, result: ConversionProgress):
        """Handle conversion completion"""
        self.progress_var.set(100)
        
        # Show summary
        summary = f"\n=== Conversion Complete ===\n"
        summary += f"Total files: {result.total_files}\n"
        summary += f"Successfully converted: {result.success_count}\n"
        summary += f"Failed: {result.error_count}\n"
        
        if result.errors:
            summary += f"\nErrors:\n"
            for error in result.errors:
                summary += f"- {error}\n"
        
        self.log_message(summary)
        
        # Re-enable convert button
        self.is_converting = False
        self.convert_button.config(text="Convert Files", state=tk.NORMAL)
        
        # Show completion message
        if result.error_count == 0:
            messagebox.showinfo("Success", f"All {result.success_count} files converted successfully!")
        else:
            messagebox.showwarning("Partial Success", 
                                 f"{result.success_count} files converted, {result.error_count} failed. Check the log for details.")
    
    def conversion_error(self, error_msg: str):
        """Handle conversion error"""
        self.log_message(f"ERROR: {error_msg}")
        self.is_converting = False
        self.convert_button.config(text="Convert Files", state=tk.NORMAL)
        messagebox.showerror("Conversion Error", f"An error occurred during conversion:\n{error_msg}")


def main():
    root = tk.Tk()
    
    # Try to set a nice theme
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass  # Fall back to default theme
    
    app = ComicConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()