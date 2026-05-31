#!/usr/bin/env python3
"""Build assets/logo.ico from assets/logo.png (requires Pillow)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PNG = ROOT / "assets" / "logo.png"
ICO = ROOT / "assets" / "logo.ico"


def main() -> None:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("Install Pillow: pip install Pillow")

    if not PNG.is_file():
        raise SystemExit(f"Missing {PNG} — add a 256x256 PNG logo first.")

    img = Image.open(PNG).convert("RGBA")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ICO.parent.mkdir(parents=True, exist_ok=True)
    img.save(ICO, format="ICO", sizes=sizes)
    print(f"Wrote {ICO}")


if __name__ == "__main__":
    main()
