import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yt_dlp
import os
import threading
import sys
import requests
import re

class RedSeaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Red Sea - YouTube Audio Extractor")
        self.root.geometry("1400x800")
        
        # Center the window on screen
        self.center_window()
        
        # Initialize download queue (list of dictionaries with url and title)
        self.download_queue = []
        
        # Download cancellation mechanism
        self.cancel_event = threading.Event()
        self.is_downloading = False
        self.current_download_thread = None
        
        # Create main frame with horizontal layout
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right panes
        left_pane = ttk.Frame(main_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        right_pane = ttk.Frame(main_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configure left pane width
        left_pane.config(width=600)
        left_pane.pack_propagate(False)
        
        # Header section with logo and title (left pane)
        header_frame = ttk.Frame(left_pane)
        header_frame.pack(pady=(0, 20))
        
        # Load logo image
        try:
            from PIL import Image, ImageTk
            logo_path = self.get_logo_path()
            
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = ttk.Label(header_frame, image=self.logo_photo)
                logo_label.pack(pady=(0, 10))
            else:
                logo_label = ttk.Label(header_frame, text="🌊", font=("Arial", 48))
                logo_label.pack(pady=(0, 10))
        except Exception as e:
            logo_label = ttk.Label(header_frame, text="🌊", font=("Arial", 48))
            logo_label.pack(pady=(0, 10))
        
        # Main title
        title_label = ttk.Label(header_frame, text="RedSea", 
                               font=("Arial", 24, "bold"))
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Download audio/video from YouTube videos & playlists", 
                                  font=("Arial", 11), foreground="gray")
        subtitle_label.pack(pady=(5, 0))
        
        # URL input frame (left pane)
        url_frame = ttk.LabelFrame(left_pane, text="YouTube URL or Playlist", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL input and add button
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, pady=5)
        
        self.url_entry = ttk.Entry(url_input_frame, font=("Arial", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        add_btn = ttk.Button(url_input_frame, text="Add to Queue", command=self.add_to_queue)
        add_btn.pack(side=tk.RIGHT)
        
        # Utility buttons
        button_frame = ttk.Frame(url_frame)
        button_frame.pack(pady=5)
        
        paste_btn = ttk.Button(button_frame, text="Paste from Clipboard", 
                              command=self.paste_url)
        paste_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        test_btn = ttk.Button(button_frame, text="Test with Sample Video", 
                             command=self.load_test_url)
        test_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Queue frame (left pane) - smaller height
        queue_frame = ttk.LabelFrame(left_pane, text="Download Queue", padding="10")
        queue_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Queue list with scrollbar
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create listbox with scrollbar - smaller height
        self.queue_listbox = tk.Listbox(queue_list_frame, height=8, font=("Arial", 9))
        queue_scrollbar = ttk.Scrollbar(queue_list_frame, orient="vertical", command=self.queue_listbox.yview)
        self.queue_listbox.configure(yscrollcommand=queue_scrollbar.set)
        
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        queue_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Queue control buttons
        queue_controls = ttk.Frame(queue_frame)
        queue_controls.pack(fill=tk.X)
        
        remove_btn = ttk.Button(queue_controls, text="Remove Selected", command=self.remove_from_queue)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(queue_controls, text="Clear All", command=self.clear_queue)
        clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Queue status
        self.queue_status = ttk.Label(queue_controls, text="Queue: 0 items")
        self.queue_status.pack(side=tk.RIGHT)
        
        # Settings frame (left pane)
        settings_frame = ttk.LabelFrame(left_pane, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output directory
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=tk.W)
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.output_entry = ttk.Entry(dir_frame, textvariable=self.output_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT)
        
        # Download format selection
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="Download Format:").pack(anchor=tk.W)
        
        format_radio_frame = ttk.Frame(format_frame)
        format_radio_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.format_var = tk.StringVar(value="mp3")
        
        mp3_radio = ttk.Radiobutton(format_radio_frame, text="MP3 Audio Only", 
                                   variable=self.format_var, value="mp3")
        mp3_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        mp4_radio = ttk.Radiobutton(format_radio_frame, text="MP4 Video Only", 
                                   variable=self.format_var, value="mp4")
        mp4_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        both_radio = ttk.Radiobutton(format_radio_frame, text="Both MP3 + MP4", 
                                    variable=self.format_var, value="both")
        both_radio.pack(side=tk.LEFT)
        
        # Quality selection
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quality_frame, text="Audio Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.StringVar(value="192")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                   values=["128", "192", "256", "320"], width=10, state="readonly")
        quality_combo.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(quality_frame, text="kbps (for MP3)").pack(side=tk.LEFT)
        
        # Download control buttons frame (left pane)
        download_frame = ttk.Frame(left_pane)
        download_frame.pack(pady=15)
        
        self.download_btn = ttk.Button(download_frame, text="🎵 Download Queue 🎵", 
                                     command=self.start_batch_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(download_frame, text="❌ Cancel", 
                                   command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Progress and Log section (right pane)
        progress_log_frame = ttk.LabelFrame(right_pane, text="Download Progress & Log", padding="10")
        progress_log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress frame with enhanced status (right pane)
        progress_frame = ttk.Frame(progress_log_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Overall progress bar
        progress_label = ttk.Label(progress_frame, text="Overall Progress:")
        progress_label.pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(2, 5))
        
        # Current item progress bar
        current_label = ttk.Label(progress_frame, text="Current Item:")
        current_label.pack(anchor=tk.W)
        
        self.current_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.current_progress.pack(fill=tk.X, pady=(2, 5))
        
        # Status labels
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready to download", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_label = ttk.Label(status_frame, text="", foreground="gray")
        self.progress_label.pack(side=tk.RIGHT)
        
        # Log output (right pane)
        self.log_text = scrolledtext.ScrolledText(progress_log_frame, height=25, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Initial log message
        self.log("Red Sea Audio/Video Downloader initialized successfully!")
        self.log("Add YouTube URLs to the queue, select your format, and click Download to begin.")
        
        # Set initial button state
        self.update_queue_display()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        
        width = 1400
        height = 800
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def get_logo_path(self):
        """Get the path to the logo file"""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'logo.png')
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(script_dir, 'logo.png')
    
    def get_ffmpeg_path(self):
        """Get the path to ffmpeg executable"""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'ffmpeg')
        else:
            import shutil
            if shutil.which('ffmpeg'):
                return None  # Let yt-dlp use the one in PATH
            
            # Check common macOS locations for ffmpeg
            mac_locations = [
                '/usr/local/bin/ffmpeg',
                '/opt/homebrew/bin/ffmpeg',
                '/usr/bin/ffmpeg'
            ]
            
            for location in mac_locations:
                if os.path.exists(location):
                    return location
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_ffmpeg = os.path.join(script_dir, 'ffmpeg')
            
            if os.path.exists(local_ffmpeg):
                return local_ffmpeg
            
            return None
    
    def get_title_fast(self, url):
        """Fast title extraction using HTML parsing"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            
            title_match = re.search(r'<title>(.+?)</title>', response.text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                title = title.replace(' - YouTube', '').replace(' - YouTube Music', '')
                title = title.strip()
                return title
            
            og_title_match = re.search(r'<meta property="og:title" content="(.+?)"', response.text, re.IGNORECASE)
            if og_title_match:
                return og_title_match.group(1).strip()
                
        except Exception:
            pass
        
        return "Unknown Title"
    
    def add_to_queue(self):
        """Add URL to download queue"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        # Check if it's a playlist URL
        if "playlist" in url or "list=" in url:
            self.add_playlist_to_queue(url)
            return
        
        # Check for duplicates
        for item in self.download_queue:
            if item['url'] == url:
                messagebox.showwarning("Duplicate", "This URL is already in the queue")
                return
        
        # Fetch video title in separate thread
        def fetch_and_add():
            try:
                self.log(f"Fetching title for: {url}")
                title = self.get_title_fast(url)
                
                queue_item = {
                    'url': url,
                    'title': title,
                    'duration': 0
                }
                
                self.download_queue.append(queue_item)
                self.update_queue_display()
                self.url_entry.delete(0, tk.END)
                
                self.log(f"✅ Added to queue: {title}")
                
            except Exception as e:
                queue_item = {
                    'url': url,
                    'title': 'Failed to fetch title',
                    'duration': 0
                }
                self.download_queue.append(queue_item)
                self.update_queue_display()
                self.url_entry.delete(0, tk.END)
                self.log(f"⚠️ Added to queue with unknown title: {url}")
        
        thread = threading.Thread(target=fetch_and_add)
        thread.daemon = True
        thread.start()
    
    def add_playlist_to_queue(self, playlist_url):
        """Add all videos from a YouTube playlist to the queue"""
        def fetch_playlist():
            try:
                self.log(f"🎵 Fetching playlist: {playlist_url}")
                self.log("This may take a moment...")
                
                # Configure yt-dlp to extract playlist info only
                ydl_opts = {
                    'extract_flat': True,  # Don't download, just get info
                    'quiet': True,
                    'no_warnings': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    playlist_info = ydl.extract_info(playlist_url, download=False)
                    
                    if 'entries' not in playlist_info:
                        self.log("❌ No videos found in playlist")
                        messagebox.showerror("Error", "No videos found in the playlist")
                        return
                    
                    playlist_title = playlist_info.get('title', 'Unknown Playlist')
                    entries = playlist_info['entries']
                    
                    # Filter out None entries (private/deleted videos)
                    valid_entries = [entry for entry in entries if entry is not None]
                    
                    if not valid_entries:
                        self.log("❌ No accessible videos found in playlist")
                        messagebox.showerror("Error", "No accessible videos found in the playlist")
                        return
                    
                    self.log(f"📋 Found playlist: {playlist_title}")
                    self.log(f"📹 Processing {len(valid_entries)} videos...")
                    
                    added_count = 0
                    skipped_count = 0
                    
                    for entry in valid_entries:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        video_title = entry.get('title', 'Unknown Title')
                        
                        # Check for duplicates
                        duplicate_found = False
                        for existing_item in self.download_queue:
                            if existing_item['url'] == video_url:
                                duplicate_found = True
                                break
                        
                        if duplicate_found:
                            skipped_count += 1
                            continue
                        
                        # Add to queue
                        queue_item = {
                            'url': video_url,
                            'title': video_title,
                            'duration': entry.get('duration', 0)
                        }
                        
                        self.download_queue.append(queue_item)
                        added_count += 1
                    
                    self.update_queue_display()
                    self.url_entry.delete(0, tk.END)
                    
                    self.log(f"✅ Added {added_count} videos from playlist")
                    if skipped_count > 0:
                        self.log(f"⚠️ Skipped {skipped_count} duplicate videos")
                    
                    messagebox.showinfo("Playlist Added", 
                                       f"Successfully added {added_count} videos from playlist:\n\n"
                                       f"{playlist_title}\n\n"
                                       f"{'Skipped ' + str(skipped_count) + ' duplicates' if skipped_count > 0 else ''}")
                    
            except Exception as e:
                error_msg = str(e)
                self.log(f"❌ Failed to fetch playlist: {error_msg}")
                messagebox.showerror("Playlist Error", f"Failed to fetch playlist:\n\n{error_msg}")
        
        thread = threading.Thread(target=fetch_playlist)
        thread.daemon = True
        thread.start()
    
    def remove_from_queue(self):
        """Remove selected URL from queue"""
        selection = self.queue_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a URL to remove")
            return
        
        index = selection[0]
        removed_item = self.download_queue.pop(index)
        self.update_queue_display()
        self.log(f"Removed from queue: {removed_item['title']}")
    
    def clear_queue(self):
        """Clear all URLs from queue"""
        if not self.download_queue:
            return
        
        if messagebox.askyesno("Clear Queue", "Are you sure you want to clear all items from the queue?"):
            self.download_queue.clear()
            self.update_queue_display()
            self.log("Queue cleared")
    
    def update_queue_display(self):
        """Update the queue listbox and status"""
        self.queue_listbox.delete(0, tk.END)
        
        for i, item in enumerate(self.download_queue, 1):
            title = item['title']
            url = item['url']
            
            if len(title) > 50:
                title = title[:47] + "..."
            
            if "youtube.com/watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
                url_short = f"youtu.be/{video_id}"
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
                url_short = f"youtu.be/{video_id}"
            else:
                url_short = url[:20] + "..." if len(url) > 20 else url
            
            display_text = f"{i}. {title} - {url_short}"
            self.queue_listbox.insert(tk.END, display_text)
        
        count = len(self.download_queue)
        self.queue_status.config(text=f"Queue: {count} item{'s' if count != 1 else ''}")
        
        if count == 0:
            self.download_btn.config(text="🎵 Add URLs to Queue 🎵", state="disabled")
        else:
            # Don't enable download button if currently downloading
            if not self.is_downloading:
                self.download_btn.config(text=f"🎵 Download {count} Item{'s' if count != 1 else ''} 🎵", state="normal")
            else:
                self.download_btn.config(text=f"🎵 Download {count} Item{'s' if count != 1 else ''} 🎵", state="disabled")
    
    def load_test_url(self):
        """Load a test URL that should work"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, test_url)
        self.log("Loaded test video URL")
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if "youtube.com" in clipboard_content or "youtu.be" in clipboard_content:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_content)
                self.log("URL pasted from clipboard")
            else:
                messagebox.showwarning("Warning", "Clipboard doesn't contain a YouTube URL")
        except tk.TclError:
            messagebox.showerror("Error", "Could not access clipboard")
    
    def browse_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)
            self.log(f"Output directory changed to: {folder}")
    
    def log(self, message):
        """Add message to log with color coding"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert message
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Color coding based on message content
        line_start = f"{self.log_text.index(tk.END)}-2l"  # -2l because we just added a line
        line_end = f"{self.log_text.index(tk.END)}-2l lineend"
        
        # Configure color tags if not already done
        if not hasattr(self, '_tags_configured'):
            self.log_text.tag_configure("green", foreground="#008000")
            self.log_text.tag_configure("red", foreground="#CC0000")
            self.log_text.tag_configure("orange", foreground="#FF8C00")
            self.log_text.tag_configure("blue", foreground="#0066CC")
            self.log_text.tag_configure("purple", foreground="#800080")
            self._tags_configured = True
        
        # Apply colors based on message content
        if "✅" in message or "Completed successfully" in message or "Successful:" in message:
            self.log_text.tag_add("green", line_start, line_end)
        elif "❌" in message or "Failed:" in message or "Error:" in message:
            self.log_text.tag_add("red", line_start, line_end)
        elif "⚠️" in message or "Warning" in message or "unknown title" in message:
            self.log_text.tag_add("orange", line_start, line_end)
        elif "Starting:" in message or "Downloading" in message or "Fetching" in message:
            self.log_text.tag_add("blue", line_start, line_end)
        elif "📊" in message or "Batch Download Complete" in message or "Duration:" in message:
            self.log_text.tag_add("purple", line_start, line_end)
        
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_batch_download(self):
        """Start batch download of all URLs in queue"""
        if not self.download_queue:
            messagebox.showerror("Empty Queue", "Please add some URLs to the queue first")
            return
        
        if self.is_downloading:
            messagebox.showwarning("Download In Progress", "A download is already in progress")
            return
        
        # Clear any previous cancellation
        self.cancel_event.clear()
        self.is_downloading = True
        
        # Update UI states
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        self.current_download_thread = threading.Thread(target=self.batch_download)
        self.current_download_thread.daemon = True
        self.current_download_thread.start()
    
    def cancel_download(self):
        """Cancel the entire download operation"""
        if not self.is_downloading:
            return
        
        if messagebox.askyesno("Cancel Downloads", "Are you sure you want to cancel the download operation?"):
            self.cancel_event.set()
            self.log("❌ Download cancellation requested...")
            self.status_label.config(text="Cancelling download...")
    
    def batch_download(self):
        """Download all URLs in the queue"""
        try:
            # Don't disable download_btn here - it's already done in start_batch_download
            # Don't start progress here - we'll set specific values
            
            total_urls = len(self.download_queue)
            output_path = self.output_var.get()
            os.makedirs(output_path, exist_ok=True)
            
            self.log(f"Starting batch download of {total_urls} items...")
            
            # Initialize progress to 0
            self.progress.config(mode='determinate', value=0)
            self.progress_label.config(text=f"0/{total_urls} items")
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, item in enumerate(self.download_queue, 1):
                # Check for cancellation before each download
                if self.cancel_event.is_set():
                    self.log("❌ Download cancelled by user")
                    self.status_label.config(text="Download cancelled")
                    break
                
                url = item['url']
                title = item['title']
                try:
                    # Update overall progress
                    progress_percent = ((i-1) / total_urls) * 100
                    self.progress.config(value=progress_percent)
                    self.progress_label.config(text=f"{i-1}/{total_urls} items")
                    
                    # Start current item progress (spinning)
                    self.current_progress.start()
                    
                    format_choice = self.format_var.get()
                    format_text = {
                        'mp3': 'MP3 audio',
                        'mp4': 'MP4 video', 
                        'both': 'MP3 + MP4'
                    }.get(format_choice, 'files')
                    
                    self.status_label.config(text=f"Downloading {i}/{total_urls}: {title} ({format_text})")
                    self.log(f"[{i}/{total_urls}] Starting: {title} ({format_text})")
                    
                    self.queue_listbox.selection_clear(0, tk.END)
                    self.queue_listbox.selection_set(i-1)
                    self.queue_listbox.see(i-1)
                    
                    # Check cancellation again before starting download
                    if self.cancel_event.is_set():
                        self.current_progress.stop()
                        self.log("❌ Download cancelled by user")
                        break
                    
                    self.download_single_url(url, output_path)
                    
                    # Stop current item progress
                    self.current_progress.stop()
                    
                    # Check if cancelled during download
                    if self.cancel_event.is_set():
                        self.log(f"[{i}/{total_urls}] ❌ {title} - Download cancelled")
                        break
                    
                    successful_downloads += 1
                    format_choice = self.format_var.get()
                    format_text = {
                        'mp3': 'MP3 audio',
                        'mp4': 'MP4 video', 
                        'both': 'MP3 + MP4'
                    }.get(format_choice, 'files')
                    self.log(f"[{i}/{total_urls}] ✅ {title} ({format_text}) - Completed successfully")
                    
                    # Update progress after completion
                    progress_percent = (i / total_urls) * 100
                    self.progress.config(value=progress_percent)
                    self.progress_label.config(text=f"{i}/{total_urls} items")
                    
                except Exception as e:
                    # Stop current item progress on error too
                    self.current_progress.stop()
                    
                    # Check if the error was due to cancellation
                    if self.cancel_event.is_set():
                        self.log(f"[{i}/{total_urls}] ❌ {title} - Download cancelled")
                        break
                    
                    failed_downloads += 1
                    self.log(f"[{i}/{total_urls}] ❌ {title} - Failed: {str(e)}")
                    
                    # Still update progress even on failure
                    progress_percent = (i / total_urls) * 100
                    self.progress.config(value=progress_percent)
                    self.progress_label.config(text=f"{i}/{total_urls} items")
                    continue
            
            # Check if cancelled before showing completion
            if not self.cancel_event.is_set():
                # Final progress - 100%
                self.progress.config(value=100)
                self.progress_label.config(text=f"{total_urls}/{total_urls} items - Complete!")
                
                self.log(f"\n📊 Batch Download Complete!")
                self.log(f"✅ Successful: {successful_downloads}")
                self.log(f"❌ Failed: {failed_downloads}")
                self.log(f"📁 Files saved to: {output_path}")
                
                messagebox.showinfo("Batch Download Complete", 
                                   f"Downloaded {successful_downloads} out of {total_urls} videos.\n\n"
                                   f"Files saved to: {output_path}")
                
                if messagebox.askyesno("Clear Queue", "Would you like to clear the completed queue?"):
                    self.clear_queue()
                
                if messagebox.askyesno("Open Folder", "Would you like to open the download folder?"):
                    try:
                        import subprocess
                        subprocess.run(['open', output_path])
                    except Exception as e:
                        self.log(f"Could not open folder: {e}")
            else:
                # Download was cancelled
                self.progress.config(value=0)
                self.progress_label.config(text="Download cancelled")
                if successful_downloads > 0:
                    self.log(f"\n📊 Download Cancelled - Partial Results:")
                    self.log(f"✅ Completed before cancellation: {successful_downloads}")
                    self.log(f"❌ Failed: {failed_downloads}")
                    self.log(f"📁 Files saved to: {output_path}")
                else:
                    self.log(f"\n❌ Download cancelled - no files completed")
        
        except Exception as e:
            self.log(f"❌ Batch download error: {str(e)}")
            messagebox.showerror("Batch Download Error", f"Batch download failed:\n\n{str(e)}")
        
        finally:
            # Reset download state
            self.is_downloading = False
            self.current_download_thread = None
            
            # Reset progress if not cancelled (to avoid overriding cancellation message)
            if not self.cancel_event.is_set():
                self.progress.config(value=0)
                self.progress_label.config(text="")
                self.status_label.config(text="Ready to download")
            
            # Reset button states
            self.download_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.queue_listbox.selection_clear(0, tk.END)
    
    def download_single_url(self, url, output_path):
        """Download a single URL in the selected format(s) with cancellation support"""
        # Check for cancellation before starting
        if self.cancel_event.is_set():
            raise Exception("Download cancelled by user")
        
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path and not os.path.exists(ffmpeg_path):
            raise Exception(f"FFmpeg not found at: {ffmpeg_path}")
        
        # Custom progress hook to check for cancellation
        def progress_hook(d):
            if self.cancel_event.is_set():
                raise Exception("Download cancelled by user")
        
        # Get format selection
        format_choice = self.format_var.get()
        
        # First, extract video info
        info_opts = {
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            if self.cancel_event.is_set():
                raise Exception("Download cancelled by user")
            
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            self.log(f"Video title: {title}")
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                self.log(f"Duration: {minutes}:{seconds:02d}")
        
        # Download based on format choice
        if format_choice == "mp3":
            self._download_mp3(url, output_path, progress_hook, ffmpeg_path)
        elif format_choice == "mp4":
            self._download_mp4(url, output_path, progress_hook, ffmpeg_path)
        elif format_choice == "both":
            self.log("Downloading MP3 audio...")
            self._download_mp3(url, output_path, progress_hook, ffmpeg_path)
            
            if self.cancel_event.is_set():
                raise Exception("Download cancelled by user")
            
            self.log("Downloading MP4 video...")
            self._download_mp4(url, output_path, progress_hook, ffmpeg_path)
    
    def _download_mp3(self, url, output_path, progress_hook, ffmpeg_path):
        """Download MP3 audio only"""
        if self.cancel_event.is_set():
            raise Exception("Download cancelled by user")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality_var.get(),
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'progress_hooks': [progress_hook],
            'extractor_retries': 3,
            'fragment_retries': 3,
        }
        
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    def _download_mp4(self, url, output_path, progress_hook, ffmpeg_path):
        """Download MP4 video"""
        if self.cancel_event.is_set():
            raise Exception("Download cancelled by user")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'progress_hooks': [progress_hook],
            'extractor_retries': 3,
            'fragment_retries': 3,
        }
        
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    # macOS doesn't use .ico files for window icons
    # Tkinter on Mac uses the app bundle icon automatically
    try:
        # Try to set icon if available (optional)
        if os.path.exists('icon.png'):
            root.iconphoto(True, tk.PhotoImage(file='icon.png'))
    except:
        pass
    
    app = RedSeaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()