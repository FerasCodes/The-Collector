# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — run: pyinstaller build/TheCollector.spec

from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent

added_datas = [
    (str(ROOT / "data"), "data"),
    (str(ROOT / "plugins"), "plugins"),
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "web"), "web"),
]

a = Analysis(
    [str(ROOT / "collector_gui.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=added_datas,
    hiddenimports=[
        "flask",
        "werkzeug",
        "jinja2",
        "collector",
        "collector.catalog",
        "collector.packs",
        "collector.profiles",
        "web",
        "web.server",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["customtkinter", "tkinter", "PIL"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="TheCollector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "logo.ico") if (ROOT / "assets" / "logo.ico").is_file() else None,
)
