"""Windows Event Log / WEF-style targeted queries for DFIR triage."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs._helpers import PS, WIN_OUT, win_cmd

O = WIN_OUT


def _wef_ps(script: str, outfile: str) -> str:
    safe = script.replace("'", "''")
    return f'{PS} "{safe} | Out-File -Encoding UTF8 \'{O}\\{outfile}\'"'


def wef_pack_commands() -> list[CollectorCommand]:
    cmds: list[CollectorCommand] = []

    def add(cid, name, category, shell, lines, **kwargs) -> None:
        kwargs.setdefault("tags", ["dfir", "wef", "eventlog"])
        kwargs.setdefault("os_min", "vista")
        cmds.append(win_cmd(cid, name, category, shell, lines, **kwargs))

    add(
        "win-wef-audit-cleared",
        "WEF — Event log cleared (1102, 104)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=1102} -MaxEvents 200 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_1102_AuditCleared.txt",
            ),
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='System'; ID=104} -MaxEvents 200 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_104_LogCleared.txt",
            ),
        ],
        syntax="Security 1102 / System 104",
        description="Detect security audit or log clearing — common anti-forensics.",
    )

    add(
        "win-wef-logon-all",
        "WEF — Logon events (4624, 4625, 4648, 4672)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625,4648,4672} -MaxEvents 1000 -EA SilentlyContinue | Select TimeCreated,Id,Message | Format-Table -Wrap",
                "%computername%_WEF_LogonEvents.txt",
            ),
        ],
        syntax="Security IDs 4624,4625,4648,4672",
    )

    add(
        "win-wef-account-changes",
        "WEF — Account management (4720-4726, 4732, 4738)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4720,4722,4723,4724,4725,4726,4732,4738} -MaxEvents 500 -EA SilentlyContinue | Select TimeCreated,Id,Message | Format-Table -Wrap",
                "%computername%_WEF_AccountChanges.txt",
            ),
        ],
    )

    add(
        "win-wef-service-install",
        "WEF — Service installed (7045, 4697)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='System'; ID=7045} -MaxEvents 300 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_7045_ServiceInstall.txt",
            ),
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4697} -MaxEvents 300 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_4697_ServiceAdded.txt",
            ),
        ],
    )

    add(
        "win-wef-scheduled-task",
        "WEF — Scheduled task created (4698-4702)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4698,4699,4700,4701,4702} -MaxEvents 400 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_ScheduledTasks.txt",
            ),
        ],
    )

    add(
        "win-wef-powershell-script",
        "WEF — PowerShell script block (4104) & module (4103)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -FilterXPath '*[System[(EventID=4104)]]' -MaxEvents 300 -EA SilentlyContinue | Select TimeCreated,Message | Format-List",
                "%computername%_WEF_PS4104_ScriptBlock.txt",
            ),
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -FilterXPath '*[System[(EventID=4103)]]' -MaxEvents 200 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_PS4103_Module.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-wmi-activity",
        "WEF — WMI activity (5857-5861)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-WMI-Activity/Operational' -MaxEvents 400 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_WMIActivity.txt",
            ),
        ],
        os_min="8",
    )

    add(
        "win-wef-rdp",
        "WEF — RDP session (1149, 4778, 4779, 21/22/23/24/25)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TerminalServices-LocalSessionManager/Operational'; ID=21,22,23,24,25} -MaxEvents 400 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_RDP_LocalSession.txt",
            ),
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational'; ID=1149} -MaxEvents 200 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_RDP_1149.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-defender-malware",
        "WEF — Defender detections & scans",
        "AV/EDR",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 500 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_DefenderOperational.txt",
            ),
        ],
        os_min="8",
    )

    add(
        "win-wef-sysmon",
        "WEF — Sysmon events (if installed)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 2000 -EA SilentlyContinue | Select TimeCreated,Id,Message | Format-Table -Wrap",
                "%computername%_WEF_Sysmon_All.txt",
            ),
        ],
        os_min="7",
        description="Exports Sysmon operational log when the agent is present.",
    )

    add(
        "win-wef-sysmon-process-create",
        "WEF — Sysmon process create (Event ID 1)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational'; ID=1} -MaxEvents 1500 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_Sysmon1_ProcessCreate.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-sysmon-network",
        "WEF — Sysmon network (Event ID 3)",
        "Network",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational'; ID=3} -MaxEvents 1500 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_Sysmon3_Network.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-sysmon-file",
        "WEF — Sysmon file create (Event ID 11)",
        "Forensics",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational'; ID=11} -MaxEvents 1000 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_Sysmon11_FileCreate.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-bits-client",
        "WEF — BITS client operational",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-Bits-Client/Operational' -MaxEvents 300 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_BITS.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-task-scheduler",
        "WEF — Task Scheduler operational",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' -MaxEvents 500 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_TaskScheduler.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-firewall",
        "WEF — Windows Firewall event log",
        "Security",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-Windows Firewall With Advanced Security/Firewall' -MaxEvents 400 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_FirewallEvents.txt",
            ),
        ],
        os_min="7",
    )

    add(
        "win-wef-appx-deployment",
        "WEF — AppX deployment (suspicious packages)",
        "Log Analysis",
        "powershell",
        [
            _wef_ps(
                "Get-WinEvent -LogName 'Microsoft-Windows-AppXDeploymentServer/Operational' -MaxEvents 300 -EA SilentlyContinue | Format-List",
                "%computername%_WEF_AppXDeploy.txt",
            ),
        ],
        os_min="10",
    )

    add(
        "win-wef-export-all-main",
        "WEF — Export main logs (.evtx)",
        "Log Analysis",
        "cmd",
        [
            "echo Exporting core event logs",
            f'mkdir "{O}\\EVTX" 2>nul',
            'for %%G in (System Application Security "Microsoft-Windows-PowerShell/Operational" "Microsoft-Windows-Sysmon/Operational" "Microsoft-Windows-Windows Defender/Operational") do (',
            f'  wevtutil epl "%%G" "{O}\\EVTX\\%COMPUTERNAME%_%%G.evtx" 2>nul',
            ")",
        ],
        output_type="evtx",
        description="Exports primary logs to EVTX subfolder (names sanitized on disk).",
    )

    add(
        "win-wef-failed-logins-summary",
        "WEF — Failed logon summary CSV",
        "Log Analysis",
        "powershell",
        [
            f'{PS} "Get-WinEvent -FilterHashtable @{{LogName=\'Security\'; ID=4625}} -MaxEvents 2000 -EA SilentlyContinue | ForEach-Object {{ $x=[xml]$_.ToXml(); [PSCustomObject]@{{ Time=$_.TimeCreated; User=$x.Event.EventData.Data[5].\'#text\'; IP=$x.Event.EventData.Data[19].\'#text\' }} }} | Export-Csv -NoTypeInformation (Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\$env:COMPUTERNAME`_FailedLogons.csv\")"',
        ],
        output_type="csv",
    )

    return cmds
