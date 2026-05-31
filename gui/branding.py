"""Window icon and header logo."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

from collector.constants import LOGO_ICO, LOGO_PNG

_LOGO_CACHE: tk.PhotoImage | None = None


def apply_window_icon(window: tk.Misc) -> None:
    ico = LOGO_ICO if LOGO_ICO.is_file() else None
    png = LOGO_PNG if LOGO_PNG.is_file() else None
    try:
        if ico:
            window.iconbitmap(str(ico))
        elif png:
            img = tk.PhotoImage(file=str(png))
            window.iconphoto(True, img)
            window._collector_icon = img  # type: ignore[attr-defined]
    except tk.TclError:
        pass


def load_header_logo(max_size: int = 36) -> tk.PhotoImage | None:
    global _LOGO_CACHE
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE
    path = LOGO_PNG if LOGO_PNG.is_file() else None
    if not path:
        return None
    try:
        img = tk.PhotoImage(file=str(path))
        w, h = img.width(), img.height()
        if w > max_size or h > max_size:
            factor = max(1, max(w, h) // max_size)
            img = img.subsample(factor, factor)
        _LOGO_CACHE = img
        return img
    except tk.TclError:
        return None
