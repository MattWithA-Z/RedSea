# RedSea macOS Distribution Guide

## Creating a User-Friendly Distribution

### For Non-Technical Users

The best approach is to create a standalone `.app` bundle that includes all Python dependencies. Users only need to:

1. Download the `.app` file
2. Drag it to Applications
3. Install FFmpeg (one Terminal command)

### Building the Distribution

Run this command to build the standalone app:

```bash
python3 build_mac.py
```

This creates `RedSea.app` in the `dist/` folder.

## Distribution Options

### Option 1: Simple Zip File (Recommended)
1. Build the app with `python3 build_mac.py`
2. Zip the `dist/RedSea.app` folder
3. Share the zip file with users
4. Include instructions to install FFmpeg

### Option 2: DMG Installer (More Professional)
Create a disk image installer:

```bash
# After building the app
hdiutil create -volname "RedSea Installer" -srcfolder dist/RedSea.app -ov -format UDZO RedSea-Installer.dmg
```

### Option 3: Homebrew Cask (For Tech Users)
Submit to Homebrew for easy installation:
```bash
brew install --cask redsea
```

## User Instructions (Include with Distribution)

### Quick Start for Non-Technical Users:

1. **Download RedSea.app** from the provided link
2. **Drag RedSea.app** to your Applications folder
3. **Install FFmpeg** (required for audio conversion):
   - Open Terminal (press Cmd+Space, type "Terminal")
   - Copy and paste this command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && brew install ffmpeg
   ```
   - Press Enter and wait for installation to complete
4. **Run RedSea** by double-clicking the app in Applications

That's it! The app includes all other required components.

## Troubleshooting for Users

**If the app won't open:**
- Right-click → Open → Open (to bypass Gatekeeper)
- Go to System Preferences → Security & Privacy → Allow anyway

**If downloads fail:**
- Make sure FFmpeg is installed: `ffmpeg -version` in Terminal
- Check internet connection
- Try a different YouTube URL

## Advanced: Code Signing (Optional)

For professional distribution without security warnings:

```bash
# Sign the app (requires Apple Developer account)
codesign --deep --force --verify --verbose --sign "Your Developer ID" RedSea.app

# Create signed DMG
hdiutil create -volname "RedSea" -srcfolder RedSea.app -ov -format UDZO RedSea-Signed.dmg
codesign -s "Your Developer ID" RedSea-Signed.dmg
```

## File Structure After Build

```
dist/
└── RedSea.app/
    └── Contents/
        ├── MacOS/
        │   └── RedSea (executable)
        ├── Resources/
        │   ├── logo.png
        │   └── (bundled Python libraries)
        └── Info.plist
```

The `.app` bundle is completely self-contained except for FFmpeg, which users install once via Homebrew.