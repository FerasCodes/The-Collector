"""Resolve bundled resources when running from source or as a PyInstaller exe."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _BUNDLE = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    ROOT = Path(sys.executable).resolve().parent
else:
    _BUNDLE = Path(__file__).resolve().parent.parent
    ROOT = _BUNDLE


def resource_path(*parts: str) -> Path:
    """Read-only files bundled inside the executable."""
    return _BUNDLE.joinpath(*parts)


def data_path() -> Path:
    """Command catalog directory (bundled when frozen; writable copy beside exe)."""
    if getattr(sys, "frozen", False):
        beside = ROOT / "data"
        bundled = resource_path("data")
        if not beside.exists() and bundled.is_dir():
            shutil.copytree(bundled, beside)
        return beside if beside.exists() else bundled
    return ROOT / "data"
