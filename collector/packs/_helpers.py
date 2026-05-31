"""Shared helpers for building pack commands."""

from __future__ import annotations

from collector.models import CollectorCommand

WIN_OUT = r"%USERPROFILE%\Desktop\%computername%"
PS = r"powershell -NoProfile -ExecutionPolicy Bypass -Command"


def win_cmd(
    cid: str,
    name: str,
    category: str,
    shell: str,
    lines: list[str],
    *,
    description: str = "",
    syntax: str = "",
    output_type: str = "text",
    os_min: str = "xp",
    os_max: str = "11",
    tags: list[str] | None = None,
) -> CollectorCommand:
    return CollectorCommand(
        id=cid,
        name=name,
        description=description or name,
        shell=shell,
        platform="windows",
        category=category,
        lines=lines,
        syntax=syntax or (lines[0] if lines else ""),
        output_type=output_type,
        os_min=os_min,
        os_max=os_max,
        dfir_tags=tags or ["dfir", "kape"],
    )


def linux_cmd(
    cid: str,
    name: str,
    category: str,
    lines: list[str],
    *,
    description: str = "",
    syntax: str = "",
    output_type: str = "text",
    distros: list[str] | None = None,
    tags: list[str] | None = None,
) -> CollectorCommand:
    header = [
        r'OUT="$HOME/Desktop/$(hostname)"',
        'mkdir -p "$OUT"',
    ]
    return CollectorCommand(
        id=cid,
        name=name,
        description=description or name,
        shell="bash",
        platform="linux",
        category=category,
        lines=header + lines,
        syntax=syntax or (lines[0] if lines else ""),
        output_type=output_type,
        distros=distros or ["rhel", "ubuntu", "generic"],
        dfir_tags=tags or ["dfir", "linux"],
    )
