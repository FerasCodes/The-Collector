from __future__ import annotations

import argparse
import sys
from pathlib import Path

from collector.catalog import build_catalog, filter_commands
from collector.profiles import list_profiles, resolve_profile
from collector.script_builder import BuildOptions, build_script


def _list_commands(platform: str, category: str | None) -> None:
    cmds = filter_commands(platform=platform, category=category)
    print(f"\n{platform.upper()} commands ({len(cmds)}):\n")
    for i, cmd in enumerate(cmds, 1):
        shell = cmd.shell.upper()
        print(f"  {i:4}. [{shell:10}] [{cmd.category:16}] {cmd.name}")


def _build_from_indices(
    platform: str,
    indices: list[int],
    name: str,
    output_format: str,
) -> Path:
    all_cmds = filter_commands(platform=platform)
    required = [c for c in all_cmds if c.required_step]
    selected = [all_cmds[i - 1] for i in indices if 0 < i <= len(all_cmds)]
    merged_ids = {c.id for c in required}
    ordered = required + [c for c in selected if c.id not in merged_ids]

    fmt = output_format
    if platform == "linux":
        fmt = "sh"
    opts = BuildOptions(output_format=fmt, platform=platform)
    result = build_script(ordered, opts)

    out_dir = Path(name).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / result.path_hint
    out_file.write_text(result.content, encoding="utf-8")
    if result.companion_content and result.companion_path_hint:
        (out_dir / result.companion_path_hint).write_text(result.companion_content, encoding="utf-8")
    if fmt == "sh":
        try:
            import os

            os.chmod(out_file, 0o755)
        except OSError:
            pass
    print(f"Wrote {out_file} ({len(ordered)} command blocks)")
    return out_file


def main(argv: list[str] | None = None) -> int:
    build_catalog()

    parser = argparse.ArgumentParser(
        prog="the-collector",
        description="The Collector — build DFIR / pentest / troubleshooting collection scripts.",
    )
    parser.add_argument(
        "-o",
        "--os",
        choices=["windows", "linux"],
        help="Target platform",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List available commands for the selected OS",
    )
    parser.add_argument(
        "-c",
        "--category",
        help="Filter list by category",
    )
    parser.add_argument(
        "-b",
        "--basic",
        nargs="*",
        type=int,
        default=[],
        help="Command indices to include (1-based, from -l list)",
    )
    parser.add_argument(
        "-a",
        "--advanced",
        nargs="*",
        type=int,
        default=[],
        help="Additional command indices (merged with -b; legacy alias)",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="Output folder name for generated script",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", "bat", "ps1", "sh"],
        default="auto",
        help="Script format (default: auto = CMD+PS per command on Windows)",
    )
    parser.add_argument("--gui", action="store_true", help="Launch the graphical studio")
    parser.add_argument("--rebuild-catalog", action="store_true", help="Rebuild data/*.json from plugins")
    parser.add_argument(
        "-p",
        "--profile",
        help="Load a triage profile by id (e.g. win-full-triage, linux-quick-triage)",
    )
    parser.add_argument("--list-profiles", action="store_true", help="List triage profile ids")

    args = parser.parse_args(argv)

    if args.list_profiles:
        for p in list_profiles(args.os):
            print(f"  {p.id:24}  {p.name}")
            print(f"    {p.description}")
        if not args.os:
            print("\nUse -o windows or -o linux to filter.")
        return 0

    if args.rebuild_catalog:
        from collector.catalog import build_catalog as bc

        bc(force_rebuild=True)
        print("Catalog rebuilt under data/")
        return 0

    if args.gui:
        from gui.app import run_gui

        run_gui()
        return 0

    if args.list:
        if not args.os:
            parser.error("-o/--os is required with --list")
        _list_commands(args.os, args.category)
        return 0

    if not args.os:
        parser.print_help()
        print("\nHint: use --gui for the studio, or -o windows -l to list commands.")
        return 0

    if not args.name:
        parser.error("-n/--name is required when generating a script")

    if args.profile:
        catalog = build_catalog()
        try:
            selected = resolve_profile(args.profile, catalog)
        except KeyError as exc:
            print(exc, file=sys.stderr)
            return 1
        fmt = "sh" if args.os == "linux" else args.format
        opts = BuildOptions(output_format=fmt, platform=args.os)
        result = build_script(selected, opts)
        out_dir = Path(args.name).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / result.path_hint
        out_file.write_text(result.content, encoding="utf-8")
        if result.companion_content and result.companion_path_hint:
            (out_dir / result.companion_path_hint).write_text(result.companion_content, encoding="utf-8")
        print(f"Wrote {out_file} ({len(selected)} command blocks) from profile '{args.profile}'")
        return 0

    indices = list(dict.fromkeys((args.basic or []) + (args.advanced or [])))
    if not indices:
        parser.error("Select at least one command index with -b/-a, use -p/--profile, or use --gui")

    _build_from_indices(args.os, indices, args.name, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
