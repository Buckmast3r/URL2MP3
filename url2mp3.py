#!/usr/bin/env python3
"""
URL2MP3 - A lightweight desktop application for downloading audio from online media links.
Supports YouTube and YouTube Music with single/multiple links and batch downloads.
Built with Python, yt-dlp, and FFmpeg.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from pathlib import Path
import yt_dlp
from datetime import datetime


class DownloadStatus:
    """Enum-like class for download status tracking."""
    PENDING = "Pending"
    DOWNLOADING = "Downloading"
    CONVERTING = "Converting"
    COMPLETED = "Completed"
    ERROR = "Error"


class DownloadItem:
    """Represents a single download item with its status."""
    def __init__(self, url, index):
        self.url = url
        self.index = index
        self.status = DownloadStatus.PENDING
        self.title = "Unknown"
        self.progress = 0
        self.error_message = ""


class URL2MP3App:
    def __init__(self, root):
        self.root = root
        self.root.title("URL2MP3 - Audio Downloader")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Configuration file for persistent settings
        self.config_file = Path.home() / ".url2mp3_config.json"

        # Load saved configuration
        config = self.load_config()

        # Variables
        self.output_folder = tk.StringVar(value=config.get("last_output_folder", str(Path.home() / "Downloads")))
        self.format_var = tk.StringVar(value=config.get("last_format", "mp3"))
        self.quality_var = tk.StringVar(value=config.get("last_quality", "192"))
        self.embed_metadata = tk.BooleanVar(value=config.get("embed_metadata", True))
        self.embed_thumbnail = tk.BooleanVar(value=config.get("embed_thumbnail", True))

        # Download tracking
        self.download_items = []
        self.is_downloading = False
        self.current_download_index = 0

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface with all components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="URL2MP3 Audio Downloader",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="Media Links (YouTube, YouTube Music, etc.)", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(url_frame, text="Enter URLs (one per line for batch download):").grid(
            row=0, column=0, sticky=tk.W, pady=5)

        self.url_text = scrolledtext.ScrolledText(url_frame, height=5, width=70, wrap=tk.WORD)
        self.url_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        url_frame.columnconfigure(0, weight=1)

        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Output folder
        ttk.Label(options_frame, text="Output Folder:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(options_frame, textvariable=self.output_folder, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(options_frame, text="Browse...", command=self.browse_folder).grid(
            row=0, column=2, padx=5)

        # Format selection
        ttk.Label(options_frame, text="Audio Format:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var,
                                     values=["mp3", "m4a", "opus", "wav", "flac"],
                                     state="readonly", width=15)
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5)

        # Quality/Bitrate selection
        ttk.Label(options_frame, text="Bitrate (kbps):").grid(
            row=1, column=2, sticky=tk.W, pady=5, padx=(20, 5))
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var,
                                      values=["128", "192", "256", "320"],
                                      state="readonly", width=15)
        quality_combo.grid(row=1, column=3, sticky=tk.W, padx=5)

        # Metadata options
        ttk.Checkbutton(options_frame, text="Embed metadata",
                       variable=self.embed_metadata).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Checkbutton(options_frame, text="Embed thumbnail as cover art",
                       variable=self.embed_thumbnail).grid(
            row=2, column=2, columnspan=2, sticky=tk.W, pady=5)

        options_frame.columnconfigure(1, weight=1)

        # Download Button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.download_btn = ttk.Button(button_frame, text="Start Download",
                                       command=self.start_download,
                                       width=20)
        self.download_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(button_frame, text="Cancel",
                                     command=self.cancel_download,
                                     state=tk.DISABLED, width=15)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Status Section - Shows individual download status
        status_frame = ttk.LabelFrame(main_frame, text="Download Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Create Treeview for status display
        columns = ("url", "title", "status", "progress")
        self.status_tree = ttk.Treeview(status_frame, columns=columns, show="headings", height=6)

        self.status_tree.heading("url", text="URL")
        self.status_tree.heading("title", text="Title")
        self.status_tree.heading("status", text="Status")
        self.status_tree.heading("progress", text="Progress")

        self.status_tree.column("url", width=200)
        self.status_tree.column("title", width=250)
        self.status_tree.column("status", width=100)
        self.status_tree.column("progress", width=100)

        # Scrollbar for treeview
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=status_scrollbar.set)

        self.status_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        # Overall Progress Section
        overall_frame = ttk.Frame(main_frame)
        overall_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.overall_label = ttk.Label(overall_frame, text="Ready")
        self.overall_label.pack(side=tk.LEFT, padx=5)

        # Overall progress bar
        self.overall_progress_bar = ttk.Progressbar(overall_frame, mode='determinate', length=400)
        self.overall_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Current download progress bar
        current_frame = ttk.Frame(main_frame)
        current_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.current_label = ttk.Label(current_frame, text="")
        self.current_label.pack(side=tk.LEFT, padx=5)

        self.current_progress_bar = ttk.Progressbar(current_frame, mode='determinate', length=400)
        self.current_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def load_config(self):
        """Load saved configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
        return {}

    def save_config(self):
        """Save current configuration to file."""
        try:
            config = {
                "last_output_folder": self.output_folder.get(),
                "last_format": self.format_var.get(),
                "last_quality": self.quality_var.get(),
                "embed_metadata": self.embed_metadata.get(),
                "embed_thumbnail": self.embed_thumbnail.get(),
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def browse_folder(self):
        """Open folder browser dialog and remember the selection."""
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)
            self.save_config()

    def update_status_item(self, item):
        """Update the status display for a download item."""
        # Truncate URL for display
        display_url = item.url if len(item.url) <= 40 else item.url[:37] + "..."
        display_title = item.title if len(item.title) <= 40 else item.title[:37] + "..."

        # Determine progress text
        if item.status == DownloadStatus.COMPLETED:
            progress_text = "100%"
        elif item.status == DownloadStatus.ERROR:
            progress_text = "Failed"
        elif item.progress > 0:
            progress_text = f"{item.progress}%"
        else:
            progress_text = "-"

        # Update treeview
        tree_id = f"item_{item.index}"
        if self.status_tree.exists(tree_id):
            self.status_tree.item(tree_id, values=(display_url, display_title, item.status, progress_text))
        else:
            self.status_tree.insert("", tk.END, iid=tree_id,
                                   values=(display_url, display_title, item.status, progress_text))

        # Scroll to current item
        self.status_tree.see(tree_id)

    def update_overall_progress(self):
        """Update the overall progress bar and label."""
        if not self.download_items:
            return

        completed = sum(1 for item in self.download_items if item.status == DownloadStatus.COMPLETED)
        errors = sum(1 for item in self.download_items if item.status == DownloadStatus.ERROR)
        total = len(self.download_items)

        progress = int((completed + errors) / total * 100)
        self.overall_progress_bar['value'] = progress
        self.overall_label.config(text=f"Overall: {completed + errors}/{total} completed ({completed} success, {errors} failed)")


    def start_download(self):
        """Initialize and start the download process."""
        # Get URLs from text widget
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("No URLs", "Please enter at least one URL to download.")
            return

        # Parse and validate URLs
        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        if not urls:
            messagebox.showwarning("No URLs", "Please enter valid URLs.")
            return

        # Validate output folder
        output_dir = self.output_folder.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output directory: {e}")
            return

        # Save configuration
        self.save_config()

        # Clear previous downloads
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)

        # Initialize download items
        self.download_items = [DownloadItem(url, i) for i, url in enumerate(urls)]
        self.current_download_index = 0

        # Populate status tree with pending items
        for item in self.download_items:
            self.update_status_item(item)

        # Update UI state
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.is_downloading = True

        # Reset progress bars
        self.overall_progress_bar['value'] = 0
        self.current_progress_bar['value'] = 0
        self.current_label.config(text="Initializing...")

        # Start download in separate thread
        thread = threading.Thread(target=self.download_worker)
        thread.daemon = True
        thread.start()

    def cancel_download(self):
        """Cancel the current download operation."""
        self.is_downloading = False
        self.cancel_btn.config(state=tk.DISABLED)
        self.current_label.config(text="Cancelling...")


    def download_worker(self):
        """Worker thread for downloading audio from all URLs."""
        try:
            success_count = 0
            failed_count = 0

            for item in self.download_items:
                # Check if download was cancelled
                if not self.is_downloading:
                    item.status = DownloadStatus.ERROR
                    item.error_message = "Cancelled by user"
                    self.root.after(0, lambda i=item: self.update_status_item(i))
                    continue

                self.current_download_index = item.index

                try:
                    # Update status to downloading
                    item.status = DownloadStatus.DOWNLOADING
                    self.root.after(0, lambda i=item: self.update_status_item(i))
                    self.root.after(0, lambda: self.current_label.config(
                        text=f"Downloading {item.index + 1}/{len(self.download_items)}..."))

                    # Configure yt-dlp options
                    postprocessors = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.format_var.get(),
                        'preferredquality': self.quality_var.get(),
                    }]

                    # Add metadata embedding if requested
                    if self.embed_metadata.get():
                        postprocessors.append({
                            'key': 'FFmpegMetadata',
                            'add_metadata': True,
                        })

                    # Add thumbnail embedding if requested
                    if self.embed_thumbnail.get():
                        postprocessors.append({
                            'key': 'EmbedThumbnail',
                            'already_have_thumbnail': False,
                        })

                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.output_folder.get(), '%(title)s.%(ext)s'),
                        'postprocessors': postprocessors,
                        'writethumbnail': self.embed_thumbnail.get(),  # Download thumbnail if embedding
                        'progress_hooks': [lambda d: self.progress_hook(d, item)],
                        'quiet': True,
                        'no_warnings': True,
                    }

                    # Download and extract audio
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(item.url, download=True)
                        item.title = info.get('title', 'Unknown')

                    # Update status to completed
                    item.status = DownloadStatus.COMPLETED
                    item.progress = 100
                    self.root.after(0, lambda i=item: self.update_status_item(i))
                    success_count += 1

                except Exception as e:
                    # Handle error
                    item.status = DownloadStatus.ERROR
                    item.error_message = str(e)
                    self.root.after(0, lambda i=item: self.update_status_item(i))
                    failed_count += 1

                # Update overall progress
                self.root.after(0, self.update_overall_progress)

            # Show completion message
            if self.is_downloading:
                if failed_count == 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Download Complete",
                        f"Successfully downloaded {success_count} file(s) to:\n{self.output_folder.get()}"))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Download Complete with Errors",
                        f"Completed: {success_count} successful, {failed_count} failed\n"
                        f"Files saved to: {self.output_folder.get()}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}"))

        finally:
            # Re-enable download button and reset UI
            self.root.after(0, self.download_complete)

    def progress_hook(self, d, item):
        """Hook for yt-dlp progress updates for individual downloads."""
        if not self.is_downloading:
            raise Exception("Download cancelled by user")

        try:
            if d['status'] == 'downloading':
                # Extract progress percentage
                if 'downloaded_bytes' in d and 'total_bytes' in d:
                    progress = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                    progress = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
                else:
                    progress = 0

                item.progress = progress

                # Update current progress bar
                self.root.after(0, lambda: self.current_progress_bar.config(value=progress))

            elif d['status'] == 'finished':
                # Download finished, now processing
                item.status = DownloadStatus.CONVERTING
                self.root.after(0, lambda: self.update_status_item(item))
                self.root.after(0, lambda: self.current_label.config(
                    text=f"Converting {item.index + 1}/{len(self.download_items)}..."))
                self.root.after(0, lambda: self.current_progress_bar.config(value=100))

        except Exception as e:
            print(f"Progress hook error: {e}")

    def download_complete(self):
        """Called when all downloads are complete or cancelled."""
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.current_progress_bar['value'] = 0
        self.current_label.config(text="Ready")
        self.is_downloading = False


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = URL2MP3App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
