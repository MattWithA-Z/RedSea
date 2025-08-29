#!/bin/bash
# RedSea macOS Installer Script
# Run this with: curl -sSL https://your-domain.com/install-mac.sh | bash

echo "🌊 Installing RedSea YouTube Downloader for macOS..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install FFmpeg
echo "🎵 Installing FFmpeg..."
brew install ffmpeg

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install yt-dlp Pillow requests

# Download RedSea
echo "⬇️  Downloading RedSea..."
curl -L https://github.com/yourusername/redsea/archive/main.zip -o redsea.zip
unzip redsea.zip
mv redsea-main/redsea-mac ~/Desktop/RedSea
rm -rf redsea.zip redsea-main

# Create launcher script
cat > ~/Desktop/RedSea/launch.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 "RedSea - Mac.py"
EOF
chmod +x ~/Desktop/RedSea/launch.command

echo "✅ Installation complete!"
echo "📁 RedSea installed to ~/Desktop/RedSea"
echo "🚀 Double-click 'launch.command' to run RedSea"