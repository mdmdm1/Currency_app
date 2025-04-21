# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all bcrypt submodules
bcrypt_imports = collect_submodules('bcrypt')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons', 'icons'),
        ('pages', 'pages'),
        ('dialogs', 'dialogs'),
        ('database', 'database'),
        ('utils', 'utils'),
        ('translations', 'translations'),
        ('style.css', '.'),
        ('down_arrow.png', '.'),
        ('config.py', '.'),
        ('.env', '.'),
        ('icons/profile.png', 'icons'),  # Add profile.png to icons directory
    ] + collect_data_files('bcrypt'),  # Add bcrypt data files
    hiddenimports=[
        'pages', 'dialogs', 'database', 'utils', 'translations', 'PyQt5',
        'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'requests',
        , 'json', 'datetime', 'pathlib',
        'bcrypt', '_bcrypt', 'bcrypt._bcrypt', 'bcrypt.bcrypt'
    ] + bcrypt_imports,  # Add all bcrypt submodules
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/app-icon.png',
)
