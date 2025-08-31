# RedSea for macOS - YouTube Audio/Video Downloader

A self-contained macOS application for downloading audio and video from YouTube videos and playlists. Built with Python/Tkinter and distributed as a standard macOS .dmg installer.

## Features

- Download MP3 audio, MP4 video, or both formats simultaneously
- Support for YouTube playlists
- Download cancellation
- Progress tracking with dual progress bars
- Queue management for batch downloads
- Configurable output directory and audio quality

## Installation

### Download the Pre-built App (Recommended)
1. Go to [Releases](https://github.com/MattWithA-Z/RedSea/releases) and download the latest `.dmg` file
2. Double-click the downloaded `.dmg` file to mount it
3. Drag `RedSea.app` to your Applications folder
4. Eject the disk image
5. Launch RedSea from Applications or Spotlight

**That's it!** The app is completely self-contained with FFmpeg and all dependencies bundled - no additional software installation required.

## For Developers

### Building from Source

#### Option 1: Using PyInstaller Spec (Recommended)
```bash
# Install build dependencies
pip3 install pyinstaller

# Build using spec file (automatically bundles FFmpeg)
pyinstaller RedSea.spec
```

#### Option 2: Using Build Script
```bash
# Install build dependencies
pip3 install pyinstaller

# Run the build script
python3 build_mac.py
```

Both methods create a self-contained `RedSea.app` in the `dist/` folder with FFmpeg bundled.

### Development Setup

For developers who want to run from source:

#### 1. Install FFmpeg (Development Only)
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

#### 3. Run from Source
```bash
python3 "RedSea - Mac.py"
```

**Note:** Development setup requires FFmpeg to be installed separately. The built app bundles FFmpeg automatically.

## Usage

1. **Add URLs**: Enter YouTube video or playlist URLs in the input field
2. **Choose Format**: Select MP3 audio only, MP4 video only, or both formats  
3. **Set Output Directory**: Browse to select where files should be saved
4. **Configure Quality**: Choose audio quality (128-320 kbps for MP3)
5. **Download**: Click "Download Queue" to start batch downloading
6. **Cancel**: Use the Cancel button to stop downloads at any time

## Troubleshooting

### App Issues
- If downloads fail, try restarting the app
- Check that you have a stable internet connection
- Verify the output directory is writable

### Development Issues
- Make sure you're using Python 3.x: `python3 --version`
- Install dependencies with pip3, not pip
- Ensure FFmpeg is installed for development: `ffmpeg -version`

### Build Issues
- Verify FFmpeg is available during build process
- Check that PyInstaller can find all dependencies
- Ensure sufficient disk space for building

## Technical Details

- **Self-contained**: FFmpeg and all dependencies are bundled in the app
- **Playlist support**: Automatically detects and processes YouTube playlists
- **Duplicate handling**: Automatically skips duplicate videos in queue
- **Cross-platform**: All features from the Windows version are supported
- **CI/CD**: Automated builds via GitHub Actions create .dmg installers
- **Architecture**: Built with Python/Tkinter, packaged with PyInstaller

## Distribution

- **Format**: Standard macOS .dmg installer
- **Size**: ~100MB (includes FFmpeg binary)
- **Compatibility**: macOS 10.14+ (Mojave and later)
- **Installation**: Drag-and-drop to Applications folder
- **Updates**: Download new .dmg releases from GitHub

