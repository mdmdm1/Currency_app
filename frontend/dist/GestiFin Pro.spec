# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\medma\\Desktop\\Currency_app\\frontend\\dist\\main.exe', '.'), ('C:\\Users\\medma\\Desktop\\Currency_app\\frontend\\translations', 'translations'), ('C:\\Users\\medma\\Desktop\\Currency_app\\frontend\\icons', 'icons'), ('C:\\Users\\medma\\Desktop\\Currency_app\\frontend\\style.css', '.')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'requests', 'database', 'utils', 'pages', 'dialogs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GestiFin Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app-icon.ico'],
)
