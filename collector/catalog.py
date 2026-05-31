from __future__ import annotations

import json
from pathlib import Path

from collector.constants import CATALOG_VERSION, DATA_DIR, FAVORITES_FILE, USER_DATA
from collector.extras import extra_linux_commands, extra_windows_commands
from collector.legacy import load_all_legacy
from collector.packs import all_pack_commands
from collector.models import CollectorCommand

_catalog_cache: list[CollectorCommand] | None = None


def _dedupe(commands: list[CollectorCommand]) -> list[CollectorCommand]:
    seen: set[str] = set()
    out: list[CollectorCommand] = []
    for cmd in commands:
        if cmd.id in seen:
            continue
        seen.add(cmd.id)
        out.append(cmd)
    return out


def _load_json_catalog(path: Path) -> list[CollectorCommand]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return [CollectorCommand.from_dict(item) for item in data]


def _save_json_catalog(path: Path, commands: list[CollectorCommand]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in commands], f, indent=2)


def build_catalog(force_rebuild: bool = False) -> list[CollectorCommand]:
    global _catalog_cache
    if _catalog_cache is not None and not force_rebuild:
        return _catalog_cache

    windows_path = DATA_DIR / "windows.json"
    linux_path = DATA_DIR / "linux.json"

    version_file = DATA_DIR / ".catalog_version"
    stored_version = 0
    if version_file.exists():
        try:
            stored_version = int(version_file.read_text(encoding="utf-8").strip())
        except ValueError:
            stored_version = 0
    version_stale = stored_version < CATALOG_VERSION

    need_win = force_rebuild or not windows_path.exists() or version_stale
    need_lin = force_rebuild or not linux_path.exists() or version_stale
    legacy: list[CollectorCommand] = []
    if need_win or need_lin:
        legacy = load_all_legacy()

    if need_win:
        windows = _dedupe(
            legacy + extra_windows_commands() + [c for c in all_pack_commands() if c.platform == "windows"]
        )
        windows = [c for c in windows if c.platform == "windows"]
        _save_json_catalog(windows_path, windows)

    if need_lin:
        linux_legacy = [c for c in legacy if c.platform == "linux"]
        linux = _dedupe(
            linux_legacy
            + extra_linux_commands()
            + [c for c in all_pack_commands() if c.platform == "linux"]
        )
        _save_json_catalog(linux_path, linux)

    if need_win or need_lin:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        version_file.write_text(str(CATALOG_VERSION), encoding="utf-8")

    commands = _load_json_catalog(windows_path) + _load_json_catalog(linux_path)
    _apply_favorites(commands)
    _catalog_cache = commands
    return commands


def _apply_favorites(commands: list[CollectorCommand]) -> None:
    if not FAVORITES_FILE.exists():
        return
    try:
        fav_ids = set(json.loads(FAVORITES_FILE.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return
    for cmd in commands:
        if cmd.id in fav_ids:
            cmd.favorite = True


def catalog_stats() -> dict[str, int]:
    """Total commands in the repository by platform."""
    catalog = build_catalog()
    windows = sum(1 for c in catalog if c.platform == "windows")
    linux = sum(1 for c in catalog if c.platform == "linux")
    return {"total": len(catalog), "windows": windows, "linux": linux}


def get_command_by_id(cmd_id: str) -> CollectorCommand | None:
    for cmd in build_catalog():
        if cmd.id == cmd_id:
            return cmd
    return None


def filter_commands(
    *,
    platform: str | None = None,
    shell: str | None = None,
    category: str | None = None,
    search: str = "",
    favorites_only: bool = False,
    os_version: str | None = None,
    linux_distro: str | None = None,
) -> list[CollectorCommand]:
    results = build_catalog()
    if platform:
        results = [c for c in results if c.platform == platform.lower()]
    if shell and shell.lower() != "all":
        results = [c for c in results if c.shell == shell.lower()]
    if category and category != "All":
        results = [c for c in results if c.category == category]
    if favorites_only:
        results = [c for c in results if c.favorite]
    if search:
        q = search.lower()
        results = [
            c
            for c in results
            if q in c.name.lower()
            or q in c.description.lower()
            or q in c.syntax.lower()
            or any(q in t.lower() for t in c.dfir_tags)
        ]
    if os_version:
        results = [c for c in results if _os_supported(c, os_version)]
    if linux_distro:
        results = [c for c in results if _distro_supported(c, linux_distro)]
    return sorted(results, key=lambda c: c.name.lower())


def _os_index(version: str) -> int:
    order = ["xp", "vista", "7", "8", "8.1", "10", "11"]
    v = version.lower().replace("windows ", "").strip()
    try:
        return order.index(v)
    except ValueError:
        return len(order) - 1


def _os_supported(cmd: CollectorCommand, version: str) -> bool:
    if cmd.platform != "windows":
        return True
    if not cmd.os_min and not cmd.os_max:
        return True
    idx = _os_index(version)
    min_i = _os_index(cmd.os_min) if cmd.os_min else 0
    max_i = _os_index(cmd.os_max) if cmd.os_max else len(["xp"]) + 10
    return min_i <= idx <= max_i


def _distro_supported(cmd: CollectorCommand, distro: str) -> bool:
    if cmd.platform != "linux":
        return True
    if not cmd.distros:
        return True
    d = distro.lower()
    return d in [x.lower() for x in cmd.distros] or "generic" in [x.lower() for x in cmd.distros]


def category_counts(platform: str | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cmd in build_catalog():
        if platform and cmd.platform != platform:
            continue
        counts[cmd.category] = counts.get(cmd.category, 0) + 1
    return counts


def shell_counts(platform: str | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cmd in build_catalog():
        if platform and cmd.platform != platform:
            continue
        counts[cmd.shell] = counts.get(cmd.shell, 0) + 1
    return counts


def toggle_favorite(cmd_id: str) -> bool:
    USER_DATA.mkdir(parents=True, exist_ok=True)
    favs: set[str] = set()
    if FAVORITES_FILE.exists():
        try:
            favs = set(json.loads(FAVORITES_FILE.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            favs = set()
    if cmd_id in favs:
        favs.remove(cmd_id)
        new_state = False
    else:
        favs.add(cmd_id)
        new_state = True
    FAVORITES_FILE.write_text(json.dumps(sorted(favs), indent=2), encoding="utf-8")
    cmd = get_command_by_id(cmd_id)
    if cmd:
        cmd.favorite = new_state
    return new_state
