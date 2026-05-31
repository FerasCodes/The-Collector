#!/usr/bin/env python3
"""Launch The Collector in your web browser."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web.server import run_server  # noqa: E402


def main() -> None:
    run_server(open_browser=True)


if __name__ == "__main__":
    main()
