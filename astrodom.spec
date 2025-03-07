from PyInstaller.utils.hooks import collect_submodules

# -*- mode: python ; coding: utf-8 -*-
# Add the following import statement

# Collect all submodules for hidden imports
hiddenimports = collect_submodules('astrodom')

# Update the Analysis section to include hidden imports
a = Analysis(
    ['astrodom/__main__.py'],
    pathex=['.'],  # Use the current directory as the search path
    binaries=[],
    datas=[
        ('rsc/*', 'rsc'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
block_cipher = None


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='astrodom',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='path/to/icon.ico'  # Optional: specify an icon file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='astrodom'
)