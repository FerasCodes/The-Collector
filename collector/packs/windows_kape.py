"""KAPE-style artifact collection — file copies, hives, and forensic paths."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs._helpers import PS, WIN_OUT, win_cmd

O = WIN_OUT


def _mkdir(sub: str) -> str:
    return f'mkdir "{O}\\{sub}" 2>nul'


def _robocopy(src: str, dest_sub: str, extra: str = "/E /R:0 /W:0 /NP") -> list[str]:
    dest = f'"{O}\\{dest_sub}"'
    return [
        _mkdir(dest_sub),
        f'robocopy "{src}" {dest} /COPY:DAT {extra} >> "{O}\\%computername%_robocopy.log" 2>&1',
    ]


def kape_pack_commands() -> list[CollectorCommand]:
    cmds: list[CollectorCommand] = []

    def add(*args, **kwargs) -> None:
        kwargs.setdefault("tags", ["dfir", "kape", "artifact"])
        cmds.append(win_cmd(*args, **kwargs))

    # --- Prefetch / ProgramData / System files ---
    add(
        "win-kape-prefetch-robocopy",
        "KAPE — Prefetch folder (robocopy)",
        "Forensics",
        "cmd",
        ["echo KAPE Prefetch"] + _robocopy(r"%SystemRoot%\Prefetch", "Artifacts\\Prefetch"),
        output_type="binary",
        os_min="xp",
    )

    add(
        "win-kape-wer",
        "KAPE — Windows Error Reporting",
        "Forensics",
        "cmd",
        ["echo KAPE WER"] + _robocopy(r"%ProgramData%\Microsoft\Windows\WER", "Artifacts\\WER"),
        output_type="binary",
        os_min="7",
    )

    add(
        "win-kape-srum",
        "KAPE — SRUM database (Win8+)",
        "Forensics",
        "cmd",
        [
            "echo KAPE SRUM",
            _mkdir("Artifacts\\SRUM"),
            f'copy /Y "%SystemRoot%\\System32\\sru\\SRUDB.dat" "{O}\\Artifacts\\SRUM\\" 2>nul',
            f'copy /Y "%SystemRoot%\\System32\\sru\\*.dat" "{O}\\Artifacts\\SRUM\\" 2>nul',
        ],
        output_type="binary",
        os_min="8",
        description="System Resource Usage Monitor database for program/network usage timeline.",
    )

    add(
        "win-kape-amcache-hve",
        "KAPE — Amcache.hve (inventory)",
        "Forensics",
        "cmd",
        [
            "echo KAPE Amcache",
            _mkdir("Artifacts\\Amcache"),
            f'copy /Y "%SystemRoot%\\appcompat\\Programs\\Amcache.hve" "{O}\\Artifacts\\Amcache\\" 2>nul',
            f'copy /Y "%SystemRoot%\\appcompat\\Programs\\Amcache.hve.LOG*" "{O}\\Artifacts\\Amcache\\" 2>nul',
        ],
        output_type="binary",
        os_min="8",
    )

    add(
        "win-kape-shimcache-file",
        "KAPE — AppCompatCache (ShimCache) binary",
        "Forensics",
        "cmd",
        [
            f'reg save "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\AppCompatCache" "{O}\\Artifacts\\%computername%_AppCompatCache.dat" 2>nul',
        ],
        output_type="dat",
    )

    add(
        "win-kape-bam-dam",
        "KAPE — BAM/DAM user settings (execution)",
        "Forensics",
        "powershell",
        [
            f'{PS} "$d=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\Artifacts\\BAM\"; New-Item -Force -ItemType Directory -Path $d | Out-Null; $bam=\"HKLM:\\SYSTEM\\CurrentControlSet\\Services\\bam\\State\\UserSettings\"; $dam=\"HKLM:\\SYSTEM\\CurrentControlSet\\Services\\dam\\State\\UserSettings\"; if(Test-Path $bam){{ reg export $bam (Join-Path $d \"bam.reg\") /y 2>$null }}; if(Test-Path $dam){{ reg export $dam (Join-Path $d \"dam.reg\") /y 2>$null }}"',
        ],
        os_min="10",
        output_type="binary",
    )

    add(
        "win-kape-userassist",
        "KAPE — UserAssist registry (GUI program execution)",
        "Forensics",
        "cmd",
        [
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist" "{O}\\Artifacts\\%computername%_UserAssist.reg" /y 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-muicache",
        "KAPE — MUICache / OpenSaveMRU",
        "Forensics",
        "cmd",
        [
            f'reg export "HKCU\\Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache" "{O}\\Artifacts\\%computername%_MuiCache.reg" /y 2>nul',
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSavePidlMRU" "{O}\\Artifacts\\%computername%_OpenSaveMRU.reg" /y 2>nul',
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\LastVisitedPidlMRU" "{O}\\Artifacts\\%computername%_LastVisitedMRU.reg" /y 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-recentdocs",
        "KAPE — RecentDocs registry",
        "Forensics",
        "cmd",
        [
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs" "{O}\\Artifacts\\%computername%_RecentDocs.reg" /y 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-typedpaths",
        "KAPE — TypedPaths / WordWheelQuery",
        "Forensics",
        "cmd",
        [
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths" "{O}\\Artifacts\\%computername%_TypedPaths.reg" /y 2>nul',
            f'reg export "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\WordWheelQuery" "{O}\\Artifacts\\%computername%_WordWheelQuery.reg" /y 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-timeline-activities",
        "KAPE — Windows Timeline (ActivitiesCache.db)",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\Timeline"),
            f'copy /Y "%LocalAppData%\\ConnectedDevicesPlatform\\*\\ActivitiesCache.db" "{O}\\Artifacts\\Timeline\\" 2>nul',
        ],
        output_type="binary",
        os_min="10",
    )

    add(
        "win-kape-lnk-recent",
        "KAPE — Recent LNK files",
        "Forensics",
        "cmd",
        ["echo KAPE Recent LNK"] + _robocopy(r"%APPDATA%\Microsoft\Windows\Recent", "Artifacts\\RecentLNK", "/S"),
        output_type="binary",
    )

    add(
        "win-kape-office-mru",
        "KAPE — Office MRU registry",
        "Forensics",
        "cmd",
        [
            f'reg export "HKCU\\Software\\Microsoft\\Office\\16.0\\Common\\Open Find" "{O}\\Artifacts\\%computername%_Office16_OpenFind.reg" /y 2>nul',
            f'reg export "HKCU\\Software\\Microsoft\\Office\\15.0\\Common\\Open Find" "{O}\\Artifacts\\%computername%_Office15_OpenFind.reg" /y 2>nul',
        ],
        output_type="binary",
        os_min="7",
    )

    add(
        "win-kape-wmi-repo",
        "KAPE — WMI Repository files",
        "Forensics",
        "cmd",
        ["echo KAPE WMI"] + _robocopy(r"%SystemRoot%\System32\wbem\Repository", "Artifacts\\WMI_Repository", "/E"),
        output_type="binary",
    )

    add(
        "win-kape-bits",
        "KAPE — BITS transfer database",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\BITS"),
            f'copy /Y "%AllUsersProfile%\\Microsoft\\Network\\Downloader\\qmgr*.dat" "{O}\\Artifacts\\BITS\\" 2>nul',
        ],
        output_type="binary",
        os_min="7",
    )

    add(
        "win-kape-certutil-cache",
        "KAPE — CertUtil URL cache",
        "Forensics",
        "cmd",
        [
            f'certutil -urlcache * > "{O}\\Artifacts\\%computername%_CertUtilURLCache.txt" 2>nul',
        ],
        os_min="7",
    )

    add(
        "win-kape-zone-identifier",
        "KAPE — Zone.Identifier ADS listing (downloads)",
        "Forensics",
        "powershell",
        [
            f'{PS} "$out=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\Artifacts\"; New-Item -Force -ItemType Directory -Path $out | Out-Null; Get-ChildItem -Path $env:USERPROFILE -Recurse -ErrorAction SilentlyContinue | ForEach-Object {{ Get-Content -Path ($_.FullName + \':Zone.Identifier\') -ErrorAction SilentlyContinue | ForEach-Object {{ [PSCustomObject]@{{ File=$_.FullName; Zone=$_ }} }} }} | Export-Csv -NoTypeInformation (Join-Path $out \"$env:COMPUTERNAME`_ZoneIdentifiers.csv\")"',
        ],
        output_type="csv",
        os_min="7",
        description="Enumerate Mark-of-the-Web Zone.Identifier alternate data streams under user profile (can be slow).",
    )

    add(
        "win-kape-rdp-cache",
        "KAPE — RDP bitmap cache",
        "Forensics",
        "cmd",
        ["echo KAPE RDP Cache"] + _robocopy(r"%LocalAppData%\Microsoft\Terminal Server Client\Cache", "Artifacts\\RDP_Cache"),
        output_type="binary",
        os_min="7",
    )

    add(
        "win-kape-iis-logs",
        "KAPE — IIS log files (if present)",
        "Forensics",
        "cmd",
        ["echo KAPE IIS"] + _robocopy(r"%SystemDrive%\inetpub\logs\LogFiles", "Artifacts\\IIS_Logs", "/E"),
        output_type="binary",
    )

    add(
        "win-kape-defender-support",
        "KAPE — Windows Defender support logs",
        "Forensics",
        "cmd",
        ["echo KAPE Defender logs"] + _robocopy(r"%ProgramData%\Microsoft\Windows Defender\Support", "Artifacts\\Defender_Support", "/E"),
        output_type="binary",
        os_min="8",
    )

    add(
        "win-kape-onedrive-logs",
        "KAPE — OneDrive sync logs",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\OneDrive"),
            f'copy /Y "%LocalAppData%\\Microsoft\\OneDrive\\logs\\*" "{O}\\Artifacts\\OneDrive\\" 2>nul',
        ],
        output_type="binary",
        os_min="8",
    )

    add(
        "win-kape-teamviewer",
        "KAPE — TeamViewer logs (if installed)",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\TeamViewer"),
            f'copy /Y "%AppData%\\TeamViewer\\*" "{O}\\Artifacts\\TeamViewer\\" 2>nul',
            f'copy /Y "%ProgramFiles%\\TeamViewer\\*.log" "{O}\\Artifacts\\TeamViewer\\" 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-usbstor-setupapi",
        "KAPE — USBSTOR & SetupAPI logs",
        "Forensics",
        "cmd",
        [
            f'reg export "HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR" "{O}\\Artifacts\\%computername%_USBSTOR.reg" /y 2>nul',
            f'copy /Y "%SystemRoot%\\inf\\setupapi.dev.log" "{O}\\Artifacts\\%computername%_setupapi.dev.log" 2>nul',
            f'copy /Y "%SystemRoot%\\inf\\setupapi.offline.log" "{O}\\Artifacts\\%computername%_setupapi.offline.log" 2>nul',
        ],
        output_type="binary",
    )

    add(
        "win-kape-pagefile-listing",
        "KAPE — Pagefile / hiberfil locations (metadata)",
        "Forensics",
        "cmd",
        [
            f'wmic pagefile list /format:list > "{O}\\Artifacts\\%computername%_pagefile.txt" 2>nul',
            f'dir /s /b "%SystemRoot%\\hiberfil.sys" 2>nul >> "{O}\\Artifacts\\%computername%_pagefile.txt"',
        ],
        os_min="xp",
    )

    add(
        "win-kape-syscache",
        "KAPE — Syscache (Win8)",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\Syscache"),
            f'copy /Y "C:\\Windows\\System32\\config\\systemprofile\\AppData\\Local\\Microsoft\\Windows\\WebCache\\*" "{O}\\Artifacts\\Syscache\\" 2>nul',
        ],
        output_type="binary",
        os_min="8",
    )

    add(
        "win-kape-webcache",
        "KAPE — WebCacheV01.dat (IE/legacy)",
        "Forensics",
        "cmd",
        [
            _mkdir("Artifacts\\WebCache"),
            f'copy /Y "%LocalAppData%\\Microsoft\\Windows\\WebCache\\WebCacheV01.dat" "{O}\\Artifacts\\WebCache\\" 2>nul',
        ],
        output_type="binary",
        os_min="8",
    )

    add(
        "win-kape-outlook-pst-list",
        "KAPE — Outlook PST/OST paths",
        "Forensics",
        "powershell",
        [
            f'{PS} "Get-ChildItem -Path $env:USERPROFILE -Include *.pst,*.ost -Recurse -ErrorAction SilentlyContinue | Select-Object FullName,Length,LastWriteTime | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\Artifacts\\$env:COMPUTERNAME`_OutlookStores.csv\")"',
        ],
        output_type="csv",
    )

    add(
        "win-kape-all-user-profiles",
        "KAPE — List all user profile paths",
        "User/Group",
        "cmd",
        [
            f'dir /b "%SystemDrive%\\Users" > "{O}\\Artifacts\\%computername%_UserProfiles.txt" 2>nul',
            f'wmic profile list brief >> "{O}\\Artifacts\\%computername%_UserProfiles.txt" 2>nul',
        ],
    )

    add(
        "win-kape-ntuser-all-users",
        "KAPE — NTUSER.DAT per profile (if accessible)",
        "Registry",
        "powershell",
        [
            f'{PS} "$d=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\Artifacts\\NTUSER\"; New-Item -Force -ItemType Directory -Path $d | Out-Null; Get-ChildItem C:\\Users -Directory | ForEach-Object {{ $f=Join-Path $_.FullName \"NTUSER.DAT\"; if(Test-Path $f){{ Copy-Item $f (Join-Path $d ($_.Name + \"_NTUSER.DAT\")) -ErrorAction SilentlyContinue }} }}"',
        ],
        output_type="binary",
        description="Copy NTUSER.DAT from each profile (requires rights; files may be locked).",
    )

    add(
        "win-kape-programs-inventory",
        "KAPE — Installed programs (registry uninstall keys)",
        "System",
        "cmd",
        [
            f'reg export "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall" "{O}\\Artifacts\\%computername%_UninstallHKLM.reg" /y 2>nul',
            f'reg export "HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall" "{O}\\Artifacts\\%computername%_UninstallHKLM32.reg" /y 2>nul',
            f'reg export "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall" "{O}\\Artifacts\\%computername%_UninstallHKCU.reg" /y 2>nul',
        ],
        output_type="binary",
    )

    return cmds
