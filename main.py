#!/usr/bin/env python3
"""The Collector — DFIR / pentest / troubleshooting command studio."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--gui", "-g", "--web"):
        from web.server import run_server

        run_server(open_browser=True)
        return 0
    from collector.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
