from __future__ import annotations

import re
from dataclasses import dataclass

from collector.models import CollectorCommand

PS_LAUNCHER = "powershell -NoProfile -ExecutionPolicy Bypass"


@dataclass
class BuildOptions:
    output_format: str = "auto"  # auto | bat | ps1 | sh
    encoding: str = "UTF-8"
    add_error_handling: bool = True
    add_header: bool = True
    include_comments: bool = True
    platform: str = "windows"
    case_folder: str = r"%USERPROFILE%\Desktop\%computername%"


@dataclass
class ScriptBuildResult:
    content: str
    extension: str
    path_hint: str
    format_label: str = ""
    companion_path_hint: str | None = None
    companion_content: str | None = None


def _comment_line(text: str, fmt: str) -> str:
    if fmt in ("ps1", "auto_ps"):
        return f"# {text}"
    if fmt == "sh":
        return f"# {text}"
    return f"REM {text}"


def _expand_lines(cmd: CollectorCommand) -> list[str]:
    return list(cmd.lines)


def _is_powershell_command(cmd: CollectorCommand) -> bool:
    if cmd.shell == "powershell":
        return True
    blob = " ".join(cmd.lines).lower()
    return blob.strip().startswith("powershell") or "powershell.exe" in blob[:120]


def _strip_existing_ps_invocation(line: str) -> str:
    """If line already launches PowerShell, return the inner -Command payload when possible."""
    s = line.strip()
    low = s.lower()
    if "-command" in low:
        m = re.search(r"-Command\s+(.+)$", s, re.IGNORECASE)
        if m:
            return m.group(1).strip().strip('"')
    if low.startswith("powershell"):
        return s
    return s


def _bat_escape_for_cmd(s: str) -> str:
    return s.replace("%", "%%")


def _emit_bat_block(lines: list[str], cmd: CollectorCommand, options: BuildOptions) -> list[str]:
    out: list[str] = []
    if options.include_comments:
        shell_tag = "powershell" if _is_powershell_command(cmd) else "cmd"
        out.append(_comment_line(f"=== {cmd.name} [{shell_tag}] ===", "bat"))

    if options.add_error_handling:
        out.append(f"echo [{cmd.name}]")

    if _is_powershell_command(cmd):
        ps_lines: list[str] = []
        for raw in lines:
            stripped = _strip_existing_ps_invocation(raw)
            if stripped.lower().startswith("powershell"):
                ps_lines.append(stripped)
            else:
                ps_lines.append(stripped)
        script_body = "; ".join(ps_lines)
        out.append(f'{PS_LAUNCHER} -Command "{_bat_escape_for_cmd(script_body)}"')
    else:
        out.extend(lines)

    if options.add_error_handling:
        out.append(f"if errorlevel 1 echo WARNING: step failed - {cmd.name}")
    return out


def _emit_ps1_block(lines: list[str], cmd: CollectorCommand, options: BuildOptions) -> list[str]:
    out: list[str] = []
    if options.include_comments:
        shell_tag = "powershell" if _is_powershell_command(cmd) else "cmd"
        out.append(_comment_line(f"=== {cmd.name} [{shell_tag}] ===", "ps1"))

    if options.add_error_handling:
        out.append(f"Write-Host '[{cmd.name}]'")

    if _is_powershell_command(cmd):
        for raw in lines:
            stripped = _strip_existing_ps_invocation(raw)
            if stripped.lower().startswith("powershell"):
                m = re.search(r'-Command\s+(.+)$', stripped, re.IGNORECASE)
                out.append(m.group(1).strip().strip('"') if m else stripped)
            else:
                out.append(stripped)
    else:
        for raw in lines:
            escaped = raw.replace('"', '`"')
            out.append(f'cmd /c "{escaped}"')

    if options.add_error_handling:
        out.append(f"if (-not $?) {{ Write-Warning 'Step failed: {cmd.name}' }}")
    return out


def _ordered_commands(commands: list[CollectorCommand]) -> list[CollectorCommand]:
    required = [c for c in commands if c.required_step]
    optional = [c for c in commands if not c.required_step]
    return required + optional


def _build_auto_windows(
    commands: list[CollectorCommand],
    options: BuildOptions,
) -> ScriptBuildResult:
    """Master .bat runs CMD inline; PowerShell steps invoke powershell.exe per block."""
    ordered = _ordered_commands(commands)
    bat_lines: list[str] = []

    if options.add_header:
        bat_lines.append("@echo off")
        bat_lines.append("setlocal EnableExtensions EnableDelayedExpansion")
    if options.include_comments:
        bat_lines.append(_comment_line("The Collector — mixed CMD + PowerShell collection", "bat"))
        bat_lines.append(_comment_line("Each step uses the shell required by that command.", "bat"))

    ps_only_blocks: list[str] = []
    if options.add_header:
        ps_only_blocks.append("$ErrorActionPreference = 'Continue'")
        ps_only_blocks.append(_comment_line("The Collector — PowerShell-only steps", "ps1"))

    has_ps = False
    has_cmd = False

    for cmd in ordered:
        block = _expand_lines(cmd)
        is_ps = _is_powershell_command(cmd)
        if is_ps:
            has_ps = True
            ps_only_blocks.extend(_emit_ps1_block(block, cmd, options))
            ps_only_blocks.append("")
        else:
            has_cmd = True
        bat_lines.extend(_emit_bat_block(block, cmd, options))
        bat_lines.append("")

    bat_lines.append("echo Collection complete.")
    bat_lines.append("pause")

    companion_content: str | None = None
    companion_hint: str | None = None
    if has_ps and has_cmd:
        companion_content = "\n".join(ps_only_blocks).rstrip() + "\n"
        companion_hint = "TheCollector.ps1"

    label = "Auto (CMD + PowerShell per command)"
    if has_ps and not has_cmd:
        label = "Auto → all PowerShell (.ps1)"
        content = "\n".join(ps_only_blocks).rstrip() + "\n"
        return ScriptBuildResult(
            content=content,
            extension=".ps1",
            path_hint="TheCollector.ps1",
            format_label=label,
        )

    return ScriptBuildResult(
        content="\n".join(bat_lines).rstrip() + "\n",
        extension=".bat",
        path_hint="TheCollector.bat",
        format_label=label,
        companion_path_hint=companion_hint,
        companion_content=companion_content,
    )


def build_script(
    commands: list[CollectorCommand],
    options: BuildOptions,
) -> ScriptBuildResult:
    fmt = options.output_format.lower()
    ordered = _ordered_commands(commands)

    if options.platform == "windows" and fmt == "auto":
        return _build_auto_windows(commands, options)

    lines: list[str] = []

    if fmt == "bat":
        if options.add_header:
            lines.append("@echo off")
            lines.append("setlocal EnableExtensions EnableDelayedExpansion")
        if options.include_comments:
            lines.append(_comment_line("The Collector — DFIR collection script", "bat"))
        for cmd in ordered:
            lines.extend(_emit_bat_block(_expand_lines(cmd), cmd, options))
            lines.append("")
        if options.platform == "windows":
            lines.append("echo Collection complete.")
            lines.append("pause")
        ext, hint = ".bat", "TheCollector.bat"
        label = "Batch (.bat)"

    elif fmt == "ps1":
        if options.add_header:
            lines.append("$ErrorActionPreference = 'Continue'")
        if options.include_comments:
            lines.append(_comment_line("The Collector — DFIR collection script (PowerShell)", "ps1"))
        for cmd in ordered:
            lines.extend(_emit_ps1_block(_expand_lines(cmd), cmd, options))
            lines.append("")
        ext, hint = ".ps1", "TheCollector.ps1"
        label = "PowerShell (.ps1)"

    else:
        if options.add_header:
            lines.append("#!/usr/bin/env bash")
            lines.append("set -euo pipefail")
        if options.include_comments:
            lines.append(_comment_line("The Collector — DFIR collection script (Linux)", "sh"))
        for cmd in ordered:
            if options.include_comments:
                lines.append(_comment_line(f"=== {cmd.name} ===", "sh"))
            if options.add_error_handling:
                lines.append(f"echo '[{cmd.name}]'")
            lines.extend(_expand_lines(cmd))
            lines.append("")
        ext, hint = ".sh", "TheCollector.sh"
        label = "Bash (.sh)"

    return ScriptBuildResult(
        content="\n".join(lines).rstrip() + "\n",
        extension=ext,
        path_hint=hint,
        format_label=label,
    )
