#!/usr/bin/env python3
"""
Build script for creating a macOS app bundle of RedSea
This bundles all dependencies into a single .app file
"""

import os
import sys
import subprocess
import shutil

def check_dependencies():
    """Check if required build tools are installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check if FFmpeg is available
    ffmpeg_locations = [
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
        '/usr/bin/ffmpeg'
    ]
    
    ffmpeg_path = None
    for location in ffmpeg_locations:
        if os.path.exists(location):
            ffmpeg_path = location
            break
    
    if not ffmpeg_path:
        print("⚠️  FFmpeg not found. The app will try to use system FFmpeg.")
        print("   Users should install FFmpeg via: brew install ffmpeg")
        return None
    else:
        print(f"✅ FFmpeg found at: {ffmpeg_path}")
        return ffmpeg_path

def build_app():
    """Build the macOS application"""
    ffmpeg_path = check_dependencies()
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    print("🔨 Building RedSea.app...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=RedSea',
        '--windowed',  # Creates .app bundle
        '--onedir',    # Bundle everything in one directory
        '--icon=logo.png',  # Use logo as icon
        '--add-data=logo.png:.',  # Include logo in bundle
        '--osx-bundle-identifier=com.redsea.app',
        'RedSea - Mac.py'
    ]
    
    # Add FFmpeg if found
    if ffmpeg_path:
        cmd.extend(['--add-binary', f'{ffmpeg_path}:.'])
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build successful!")
        print("📁 RedSea.app created in dist/ folder")
        print("\nTo distribute:")
        print("1. Zip the dist/RedSea.app folder")
        print("2. Users just need to drag RedSea.app to Applications")
        print("3. If FFmpeg wasn't bundled, users need: brew install ffmpeg")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🌊 RedSea macOS Build Script")
    print("=" * 40)
    
    success = build_app()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("The RedSea.app is ready for distribution.")
    else:
        print("\n💥 Build failed. Check errors above.")