"""Pentest, troubleshooting, and live-response commands for Windows."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs._helpers import PS, WIN_OUT, win_cmd

O = WIN_OUT


def misc_windows_pack_commands() -> list[CollectorCommand]:
    cmds: list[CollectorCommand] = []

    def add(*args, **kwargs) -> None:
        tags = kwargs.pop("tags", ["dfir", "pentest", "troubleshoot"])
        cmds.append(win_cmd(*args, tags=tags, **kwargs))

    add(
        "win-ir-triage-banner",
        "IR — Collection header / timestamp",
        "System",
        "cmd",
        [
            f'echo The Collector Windows triage > "{O}\\%computername%_00_HEADER.txt"',
            f'echo Started: %DATE% %TIME% >> "{O}\\%computername%_00_HEADER.txt"',
            f'hostname >> "{O}\\%computername%_00_HEADER.txt"',
            f'whoami /all >> "{O}\\%computername%_00_HEADER.txt"',
        ],
        tags=["dfir", "triage"],
    )

    add(
        "win-pentest-local-admins",
        "Pentest — Local administrators",
        "User/Group",
        "cmd",
        [f'net localgroup administrators > "{O}\\%computername%_LocalAdmins.txt"'],
    )

    add(
        "win-pentest-shares",
        "Pentest — Share permissions",
        "Network",
        "cmd",
        [
            f'net share > "{O}\\%computername%_Shares.txt"',
            f'net view > "{O}\\%computername%_NetView.txt" 2>&1',
        ],
    )

    add(
        "win-pentest-hotfixes",
        "Troubleshooting — Installed hotfixes",
        "System",
        "cmd",
        [f'wmic qfe get HotFixID,Description,InstalledOn > "{O}\\%computername%_Hotfixes.txt"'],
        os_min="xp",
    )

    add(
        "win-pentest-env-vars",
        "Troubleshooting — Environment variables",
        "System",
        "cmd",
        [f'set > "{O}\\%computername%_Environment.txt"'],
    )

    add(
        "win-pentest-path-permissions",
        "Pentest — Unquoted service paths",
        "Service",
        "powershell",
        [
            f'{PS} "Get-WmiObject Win32_Service | Where-Object {{ $_.PathName -and $_.PathName -notmatch \'^\"\' -and $_.PathName -match \' \' }} | Select Name,DisplayName,PathName,StartMode,State | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_UnquotedServicePaths.csv\")"',
        ],
        output_type="csv",
    )

    add(
        "win-pentest-weak-service-acls",
        "Pentest — Services with weak permissions (summary)",
        "Service",
        "cmd",
        [f'sc sdshow type= service state= all > "{O}\\%computername%_ServiceACLs.txt" 2>&1'],
        os_min="7",
    )

    add(
        "win-pentest-autoruns-registry",
        "Pentest — Autoruns (registry Run keys + Winlogon)",
        "Persistence",
        "cmd",
        [
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /s > "{O}\\%computername%_Autoruns.txt"',
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /s >> "{O}\\%computername%_Autoruns.txt"',
            f'reg query "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /s >> "{O}\\%computername%_Autoruns.txt"',
        ],
    )

    add(
        "win-pentest-cached-creds",
        "Pentest — Cached logon count (metadata)",
        "Security",
        "cmd",
        [
            f'reg query "HKLM\\SECURITY\\Cache" > "{O}\\%computername%_CachedLogons.txt" 2>&1',
        ],
        description="Requires SYSTEM; documents presence of cached credential slots.",
    )

    add(
        "win-pentest-laps",
        "Pentest — LAPS (if deployed)",
        "Security",
        "cmd",
        [
            f'reg query "HKLM\\SOFTWARE\\Policies\\Microsoft Services\\AdmPwd" > "{O}\\%computername%_LAPS.txt" 2>&1',
            f'reg query "HKLM\\SOFTWARE\\LAPS" >> "{O}\\%computername%_LAPS.txt" 2>&1',
        ],
        os_min="7",
    )

    add(
        "win-trouble-dism-health",
        "Troubleshooting — DISM component store",
        "Troubleshooting",
        "cmd",
        [
            f'DISM /Online /Cleanup-Image /ScanHealth > "{O}\\%computername%_DISM_ScanHealth.txt" 2>&1',
        ],
        os_min="7",
    )

    add(
        "win-trouble-chkdsk-readonly",
        "Troubleshooting — chkdsk scan (read-only)",
        "Troubleshooting",
        "cmd",
        [f'chkdsk > "{O}\\%computername%_CHKDSK.txt" 2>&1'],
    )

    add(
        "win-trouble-reliability",
        "Troubleshooting — Reliability monitor events",
        "Troubleshooting",
        "powershell",
        [
            f'{PS} "Get-WinEvent -LogName \'Microsoft-Windows-Diagnosis-Operational\' -MaxEvents 300 -EA SilentlyContinue | Format-List | Out-File (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_Reliability.txt\")"',
        ],
        os_min="7",
    )

    add(
        "win-trouble-boot-config",
        "Troubleshooting — BCD boot configuration",
        "System",
        "cmd",
        [f'bcdedit /enum all > "{O}\\%computername%_BCD.txt" 2>&1'],
        os_min="vista",
    )

    add(
        "win-trouble-memory",
        "Troubleshooting — Memory summary",
        "Hardware",
        "powershell",
        [
            f'{PS} "Get-CimInstance Win32_PhysicalMemory | Select BankLabel,Capacity,Speed,Manufacturer,PartNumber | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_Memory.csv\")"',
        ],
        output_type="csv",
    )

    add(
        "win-trouble-disk-smart",
        "Troubleshooting — Disk drive info",
        "Hardware",
        "powershell",
        [
            f'{PS} "Get-CimInstance Win32_DiskDrive | Select Model,Size,Status,InterfaceType,SerialNumber | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_Disks.csv\")"',
        ],
        output_type="csv",
    )

    add(
        "win-pentest-listening-ports-process",
        "Pentest — Listening ports with owning process",
        "Network",
        "powershell",
        [
            f'{PS} "Get-NetTCPConnection -State Listen -EA SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE ''Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_ListenPorts.csv'')"',
        ],
        output_type="csv",
        os_min="8",
    )

    add(
        "win-pentest-dns-cache-export",
        "Pentest — DNS client cache export",
        "Network",
        "powershell",
        [
            f'{PS} "Get-DnsClientCache | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_DNSCache.csv\")"',
        ],
        output_type="csv",
        os_min="8",
    )

    add(
        "win-pentest-proxy-settings",
        "Pentest — WinHTTP / IE proxy settings",
        "Network",
        "cmd",
        [
            f'netsh winhttp show proxy > "{O}\\%computername%_WinHTTPProxy.txt"',
            f'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable > "{O}\\%computername%_IEProxy.txt"',
            f'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer >> "{O}\\%computername%_IEProxy.txt"',
        ],
    )

    add(
        "win-pentest-smb-signing",
        "Pentest — SMB signing configuration",
        "Network",
        "cmd",
        [
            f'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v RequireSecuritySignature > "{O}\\%computername%_SMBSigning.txt"',
            f'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkstation\\Parameters" /v RequireSecuritySignature >> "{O}\\%computername%_SMBSigning.txt"',
        ],
    )

    add(
        "win-pentest-uac",
        "Pentest — UAC / CredentialGuard settings",
        "Security",
        "cmd",
        [
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA > "{O}\\%computername%_UAC.txt"',
            f'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard" >> "{O}\\%computername%_UAC.txt" 2>&1',
        ],
    )

    add(
        "win-pentest-applocker",
        "Pentest — AppLocker policy (if used)",
        "Security",
        "powershell",
        [
            f'{PS} "Get-AppLockerPolicy -Effective -EA SilentlyContinue | Out-File (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_AppLocker.txt\")"',
        ],
        os_min="7",
    )

    add(
        "win-pentest-dotnet-versions",
        "Troubleshooting — .NET versions installed",
        "System",
        "cmd",
        [
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP" /s > "{O}\\%computername%_DotNet.txt" 2>&1',
        ],
    )

    add(
        "win-pentest-remote-desktop-users",
        "Pentest — Remote Desktop Users group",
        "User/Group",
        "cmd",
        [f'net localgroup "Remote Desktop Users" > "{O}\\%computername%_RDPUsers.txt" 2>&1'],
    )

    add(
        "win-pentest-winrm",
        "Pentest — WinRM configuration",
        "Network",
        "cmd",
        [
            f'winrm get winrm/config > "{O}\\%computername%_WinRM.txt" 2>&1',
        ],
        os_min="7",
    )

    add(
        "win-pentest-pshistory",
        "Pentest — PowerShell console history file",
        "Forensics",
        "cmd",
        [
            f'copy /Y "%AppData%\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt" "{O}\\Artifacts\\%computername%_PSHistory.txt" 2>nul',
        ],
        output_type="binary",
        os_min="7",
    )

    add(
        "win-pentest-clsid-hijack",
        "Pentest — COM hijack candidates (InprocServer32 without DLL)",
        "Persistence",
        "powershell",
        [
            f'{PS} "$o=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\"; Get-ChildItem HKLM:\\Software\\Classes\\CLSID -EA SilentlyContinue | ForEach-Object {{ $p=Join-Path $_.PSPath \"InprocServer32\"; if(Test-Path $p){{ $d=(Get-ItemProperty $p).\"(default)\"; if($d -and -not (Test-Path $d)){{ [PSCustomObject]@{{ CLSID=$_.PSChildName; DLL=$d }} }} }} }} | Export-Csv -NoTypeInformation (Join-Path $o \"$env:COMPUTERNAME`_COMHijack.csv\")"',
        ],
        output_type="csv",
        os_min="7",
    )

    return cmds
