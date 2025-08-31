# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

# Find FFmpeg binary
ffmpeg_path = None
ffmpeg_locations = [
    '/opt/homebrew/bin/ffmpeg',
    '/usr/local/bin/ffmpeg', 
    '/usr/bin/ffmpeg'
]

for location in ffmpeg_locations:
    if os.path.exists(location):
        ffmpeg_path = location
        break

# Prepare binaries list
binaries = []
if ffmpeg_path:
    binaries.append((ffmpeg_path, '.'))
    print(f"Including FFmpeg from: {ffmpeg_path}")
else:
    print("WARNING: FFmpeg not found - app will require external FFmpeg installation")

a = Analysis(
    ['RedSea - Mac.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('logo.png', '.'),
    ],
    hiddenimports=[
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'yt_dlp',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RedSea',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RedSea',
)

app = BUNDLE(
    coll,
    name='RedSea.app',
    icon=None,
    bundle_identifier='com.redsea.downloader',
)