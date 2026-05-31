"""Convert legacy plugins/*.json into the v2 command schema."""

from __future__ import annotations

import json
import re
from pathlib import Path

from collector.constants import CATEGORY_KEYWORDS, LEGACY_PLUGINS, SIDEBAR_CATEGORIES
from collector.models import CollectorCommand


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:80] or "cmd"


def _infer_shell(terminal_type: str) -> str:
    t = (terminal_type or "").lower()
    if "powershell" in t or "ps" in t:
        return "powershell"
    if "bash" in t or "sh" in t:
        return "bash"
    return "cmd"


def _infer_output_type(lines: list[str], name: str) -> str:
    blob = " ".join(lines).lower() + " " + name.lower()
    if ".evtx" in blob or "wevtutil epl" in blob:
        return "evtx"
    if ".csv" in blob or "export-csv" in blob:
        return "csv"
    if ".json" in blob or "convertto-json" in blob:
        return "json"
    if "reg.exe save" in blob or "reg save" in blob or ".dat" in blob:
        return "dat"
    if ".zip" in blob or "compress-archive" in blob:
        return "zip"
    if "xcopy" in blob and ("cache" in blob or "prefetch" in blob or "history" in blob):
        return "binary"
    return "text"


def _infer_category(name: str, lines: list[str]) -> str:
    blob = (name + " " + " ".join(lines)).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in blob for k in keywords):
            return category
    return "Other"


def _infer_os_range(shell: str, lines: list[str], platform: str) -> tuple[str, str]:
    blob = " ".join(lines).lower()
    if platform == "linux":
        return "", ""
    if shell == "powershell":
        if "get-bitlocker" in blob or "get-net" in blob or "get-localgroup" in blob:
            return "8", "11"
        if "get-pnpdevice" in blob:
            return "10", "11"
        return "7", "11"
    if "wmic" in blob:
        return "xp", "10"
    if "dism" in blob:
        return "7", "11"
    if "auditpol" in blob:
        return "vista", "11"
    if "wevtutil" in blob:
        return "vista", "11"
    return "xp", "11"


def _infer_distros(platform: str, lines: list[str]) -> list[str]:
    if platform != "linux":
        return []
    blob = " ".join(lines).lower()
    distros: list[str] = []
    if "firewall-cmd" in blob or "/var/log/secure" in blob or "sestatus" in blob:
        distros.append("rhel")
    if "ufw" in blob or "auth.log" in blob or "dpkg" in blob:
        distros.append("ubuntu")
    if not distros:
        distros = ["rhel", "ubuntu", "generic"]
    return distros


def _first_syntax_line(lines: list[str]) -> str:
    for line in lines:
        s = line.strip()
        if not s or s.startswith("echo ") or s.startswith("@") or s.startswith("rem "):
            continue
        if s.startswith("(") or s.startswith("for ") or s.startswith("if "):
            continue
        return s[:200]
    return lines[0][:200] if lines else ""


def convert_legacy_entry(entry: dict, platform: str, index: int) -> CollectorCommand | None:
    name = (entry.get("Command_Name") or entry.get("name") or "").strip()
    lines = entry.get("Command") or entry.get("lines") or []
    if not name or not lines:
        return None

    shell = _infer_shell(entry.get("terminal_type", entry.get("shell", "")))
    category = entry.get("category_sidebar") or _infer_category(name, lines)
    if category not in SIDEBAR_CATEGORIES:
        category = _infer_category(name, lines)

    legacy_cat = (entry.get("category") or "").lower()
    required = legacy_cat == "must" or "directory" in name.lower() and "creat" in name.lower()
    if "hashing" in name.lower():
        required = True

    os_min, os_max = _infer_os_range(shell, lines, platform)
    cmd_id = f"{platform[:3]}-{_slug(name)}-{index}"

    return CollectorCommand(
        id=cmd_id,
        name=name,
        description=entry.get("description") or f"Collect {name.lower()} artifacts and write output to the case folder.",
        shell=shell if platform == "windows" else "bash",
        platform=platform,
        category=category,
        lines=lines,
        syntax=entry.get("syntax") or _first_syntax_line(lines),
        output_type=entry.get("output_type") or _infer_output_type(lines, name),
        os_min=entry.get("os_min") or os_min,
        os_max=entry.get("os_max") or os_max,
        distros=_infer_distros(platform, lines),
        dfir_tags=list(entry.get("dfir_tags") or []),
        required_step=required,
    )


def load_legacy_platform(path: Path, platform: str) -> list[CollectorCommand]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    commands: list[CollectorCommand] = []
    for i, entry in enumerate(raw):
        cmd = convert_legacy_entry(entry, platform, i)
        if cmd:
            commands.append(cmd)
    return commands


def load_all_legacy() -> list[CollectorCommand]:
    windows = load_legacy_platform(LEGACY_PLUGINS / "Windows_commands.json", "windows")
    linux = load_legacy_platform(LEGACY_PLUGINS / "Linux_commands.json", "linux")
    return windows + linux
