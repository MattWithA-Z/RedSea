# RedSea for macOS - YouTube Audio/Video Downloader

A Python/Tkinter GUI application for downloading audio and video from YouTube videos and playlists on macOS.

## Features

- Download MP3 audio, MP4 video, or both formats simultaneously
- Support for YouTube playlists
- Download cancellation
- Progress tracking with dual progress bars
- Queue management for batch downloads
- Configurable output directory and audio quality

## For End Users (Non-Technical)

### Option 1: Download the Pre-built App (Easiest)
1. Download `RedSea.app` from releases
2. Drag `RedSea.app` to your Applications folder
3. Install FFmpeg: Open Terminal and run `brew install ffmpeg`
   - If you don't have Homebrew, install it first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
4. Double-click RedSea.app to run

## For Developers

### Building a Standalone App

To create a `.app` bundle that includes all dependencies:

```bash
# Install build dependencies
pip3 install pyinstaller

# Run the build script
python3 build_mac.py
```

This creates `RedSea.app` in the `dist/` folder that users can drag to Applications.

### Manual Setup (Development)

#### 1. Install FFmpeg

Install FFmpeg using Homebrew (recommended):

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

#### 2. Install Python Dependencies

```bash
# Install required Python packages
pip3 install -r requirements.txt
```

#### 3. Running the Application

```bash
python3 "RedSea - Mac.py"
```

## Usage

1. **Add URLs**: Enter YouTube video or playlist URLs in the input field
2. **Choose Format**: Select MP3 audio only, MP4 video only, or both formats  
3. **Set Output Directory**: Browse to select where files should be saved
4. **Configure Quality**: Choose audio quality (128-320 kbps for MP3)
5. **Download**: Click "Download Queue" to start batch downloading
6. **Cancel**: Use the Cancel button to stop downloads at any time

## Troubleshooting

### FFmpeg Issues
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check installation paths: `/usr/local/bin/ffmpeg` or `/opt/homebrew/bin/ffmpeg`

### Python Dependencies
- Make sure you're using Python 3.x: `python3 --version`
- Install dependencies with pip3, not pip

### Permission Issues
- Make sure the output directory is writable
- Check file permissions if downloads fail

## Notes

- The app automatically detects playlist URLs and extracts all videos
- Duplicate videos in the queue are automatically skipped
- All features from the Windows version are supported on macOS