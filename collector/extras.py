"""Additional DFIR / pentest / troubleshooting commands beyond legacy JSON."""

from __future__ import annotations

from collector.models import CollectorCommand

_WIN_OUT = r"%USERPROFILE%\Desktop\%computername%"
_PS = r'powershell -NoProfile -ExecutionPolicy Bypass -Command'


def _win_lines(*parts: str) -> list[str]:
    return list(parts)


def extra_windows_commands() -> list[CollectorCommand]:
    """Supplement legacy catalog with version-aware DFIR collectors."""
    o = _WIN_OUT
    cmds: list[CollectorCommand] = []

    def add(
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
        examples: list[str] | None = None,
    ) -> None:
        cmds.append(
            CollectorCommand(
                id=cid,
                name=name,
                description=description or f"DFIR collection: {name}",
                shell=shell,
                platform="windows",
                category=category,
                lines=lines,
                syntax=syntax or (lines[-1] if lines else ""),
                output_type=output_type,
                os_min=os_min,
                os_max=os_max,
                examples=examples or [],
                dfir_tags=["dfir", "pentest"],
            )
        )

    add(
        "win-eventlog-ps-4624",
        "Security log — recent logon events (4624/4625)",
        "Log Analysis",
        "powershell",
        _win_lines(
            f"echo Collecting recent logon events",
            f'{_PS} "Get-WinEvent -FilterHashtable @{{LogName=\'Security\'; ID=4624,4625}} -MaxEvents 500 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, LevelDisplayName, Message | Out-File -Encoding UTF8 \'{o}\\%computername%_LogonEvents.txt\'"',
        ),
        os_min="vista",
        output_type="text",
        syntax="Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625}",
    )

    add(
        "win-persistence-run-keys",
        "Persistence — Run / RunOnce registry keys",
        "Persistence",
        "cmd",
        _win_lines(
            "echo Collecting Run keys",
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /s > "{o}\\%computername%_RunKeys_HKLM.txt"',
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /s >> "{o}\\%computername%_RunKeys_HKLM.txt"',
            f'reg query "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /s > "{o}\\%computername%_RunKeys_HKCU.txt"',
            f'reg query "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /s >> "{o}\\%computername%_RunKeys_HKCU.txt"',
        ),
    )

    add(
        "win-persistence-wmi",
        "Persistence — WMI subscriptions",
        "Persistence",
        "powershell",
        _win_lines(
            f"echo Collecting WMI persistence",
            f'{_PS} "Get-WmiObject -Namespace root\\subscription -Class __EventFilter -ErrorAction SilentlyContinue | Format-List * | Out-File \'{o}\\%computername%_WMI_EventFilters.txt\'"',
            f'{_PS} "Get-WmiObject -Namespace root\\subscription -Class __EventConsumer -ErrorAction SilentlyContinue | Format-List * | Out-File \'{o}\\%computername%_WMI_EventConsumers.txt\'"',
            f'{_PS} "Get-WmiObject -Namespace root\\subscription -Class __FilterToConsumerBinding -ErrorAction SilentlyContinue | Format-List * | Out-File \'{o}\\%computername%_WMI_Bindings.txt\'"',
        ),
        os_min="7",
    )

    add(
        "win-security-defender-status",
        "Windows Defender status and threats",
        "AV/EDR",
        "powershell",
        _win_lines(
            f'{_PS} "Get-MpComputerStatus | Format-List | Out-File \'{o}\\%computername%_DefenderStatus.txt\'"',
            f'{_PS} "Get-MpThreatDetection -ErrorAction SilentlyContinue | Export-Csv -NoTypeInformation -Encoding UTF8 \'{o}\\%computername%_DefenderThreats.csv\'"',
        ),
        os_min="8",
        output_type="csv",
    )

    add(
        "win-forensics-usn-journal",
        "NTFS USN journal (if accessible)",
        "Forensics",
        "cmd",
        _win_lines(
            f"echo Collecting USN journal metadata",
            f'fsutil usn queryjournal C: > "{o}\\%computername%_USNJournal.txt" 2>&1',
        ),
        os_min="7",
    )

    add(
        "win-forensics-openfiles",
        "Open files and handles (handle.exe fallback via openfiles)",
        "Process",
        "cmd",
        _win_lines(
            f'openfiles /query /fo table > "{o}\\%computername%_OpenFiles.txt" 2>&1',
        ),
        os_min="xp",
    )

    add(
        "win-network-listening-ports",
        "Listening ports (netstat)",
        "Network",
        "cmd",
        _win_lines(
            f'netstat -ano | findstr LISTENING > "{o}\\%computername%_ListeningPorts.txt"',
            f'netstat -b > "{o}\\%computername%_NetstatWithProcess.txt" 2>&1',
        ),
    )

    add(
        "win-troubleshoot-sfc",
        "Troubleshooting — SFC scan results export",
        "Troubleshooting",
        "cmd",
        _win_lines(
            f'sfc /scannow > "{o}\\%computername%_SFC_Scan.txt" 2>&1',
        ),
        os_min="xp",
    )

    add(
        "win-security-lsass-dump-note",
        "Process list with paths (investigation triage)",
        "Process",
        "powershell",
        _win_lines(
            f'{_PS} "Get-CimInstance Win32_Process | Select-Object ProcessId, Name, ExecutablePath, CommandLine, CreationDate | Export-Csv -NoTypeInformation -Encoding UTF8 \'{o}\\%computername%_ProcessesFull.csv\'"',
        ),
        os_min="7",
        output_type="csv",
    )

    add(
        "win-ad-kerberos",
        "Domain — Kerberos policy (nltest / domain)",
        "Active Directory",
        "cmd",
        _win_lines(
            f'nltest /dsgetdc: > "{o}\\%computername%_DomainController.txt" 2>&1',
            f'net config workstation > "{o}\\%computername%_WorkstationDomain.txt" 2>&1',
        ),
    )

    add(
        "win-forensics-amcache-registry",
        "Amcache / InventoryApplicationFile (Win8+)",
        "Forensics",
        "cmd",
        _win_lines(
            f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AppCompatFlags\\InventoryApplicationFile" /s > "{o}\\%computername%_AmcacheInventory.txt" 2>&1',
        ),
        os_min="8",
    )

    add(
        "win-log-powershell",
        "PowerShell operational log (last 200)",
        "Log Analysis",
        "powershell",
        _win_lines(
            f'{_PS} "Get-WinEvent -LogName \'Microsoft-Windows-PowerShell/Operational\' -MaxEvents 200 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message | Out-File \'{o}\\%computername%_PowerShellLog.txt\'"',
        ),
        os_min="7",
    )

    add(
        "win-security-rdp-settings",
        "RDP configuration registry",
        "Security",
        "cmd",
        _win_lines(
            f'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /s > "{o}\\%computername%_RDP_Settings.txt" 2>&1',
        ),
    )

    add(
        "win-forensics-volume-shadow",
        "Volume Shadow Copies listing",
        "Forensics",
        "cmd",
        _win_lines(
            f'vssadmin list shadows > "{o}\\%computername%_VSS_Shadows.txt" 2>&1',
        ),
        os_min="vista",
    )

    return cmds


def extra_linux_commands() -> list[CollectorCommand]:
    out_var = r'OUT="$HOME/Desktop/$(hostname)"'
    cmds: list[CollectorCommand] = []

    def add(
        cid: str,
        name: str,
        category: str,
        lines: list[str],
        *,
        distros: list[str] | None = None,
        description: str = "",
        output_type: str = "text",
    ) -> None:
        full = [out_var, "mkdir -p \"$OUT\""] + lines
        cmds.append(
            CollectorCommand(
                id=cid,
                name=name,
                description=description or f"Linux collection: {name}",
                shell="bash",
                platform="linux",
                category=category,
                lines=full,
                syntax=lines[0] if lines else "",
                output_type=output_type,
                distros=distros or ["rhel", "ubuntu", "generic"],
                dfir_tags=["dfir", "linux"],
            )
        )

    add(
        "lin-persistence-systemd-timers",
        "Persistence — systemd timers",
        "Persistence",
        ["systemctl list-timers --all >> \"$OUT/systemd_timers.txt\" 2>/dev/null"],
    )

    add(
        "lin-persistence-ssh-keys",
        "User SSH authorized_keys",
        "Security",
        [
            "find /home -name authorized_keys 2>/dev/null -exec cat {} \\; >> \"$OUT/ssh_authorized_keys.txt\"",
        ],
    )

    add(
        "lin-forensics-recent-logins",
        "Recent logins (last / wtmp)",
        "Log Analysis",
        [
            "last -a >> \"$OUT/last_logins.txt\" 2>/dev/null",
            "lastb -a >> \"$OUT/last_failed_logins.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-network-connections-detailed",
        "Network connections with processes",
        "Network",
        [
            "ss -tunap >> \"$OUT/ss_connections.txt\" 2>/dev/null",
            "netstat -tunap >> \"$OUT/netstat_connections.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-forensics-suid",
        "SUID/SGID binaries",
        "Security",
        ["find / -xdev \\( -perm -4000 -o -perm -2000 \\) -type f 2>/dev/null >> \"$OUT/suid_sgid_files.txt\""],
    )

    add(
        "lin-log-journal-security",
        "Journal — security-related unit logs",
        "Log Analysis",
        [
            "journalctl -u sshd --no-pager >> \"$OUT/journal_sshd.txt\" 2>/dev/null",
            "journalctl -u ssh --no-pager >> \"$OUT/journal_ssh.txt\" 2>/dev/null",
        ],
        distros=["rhel", "ubuntu", "generic"],
    )

    add(
        "lin-rhel-audit-rules",
        "Audit rules (RHEL)",
        "Log Analysis",
        ["auditctl -l >> \"$OUT/audit_rules.txt\" 2>/dev/null"],
        distros=["rhel"],
    )

    add(
        "lin-ubuntu-ufw-rules",
        "UFW rules verbose (Ubuntu)",
        "Network",
        ["ufw status numbered >> \"$OUT/ufw_rules.txt\" 2>/dev/null"],
        distros=["ubuntu"],
    )

    add(
        "lin-forensics-deleted-process",
        "Running processes with cwd and cmdline",
        "Process",
        [
            "ps auxww >> \"$OUT/ps_auxww.txt\"",
            "for p in /proc/[0-9]*; do echo \"=== $p ===\"; ls -l \"$p/exe\" 2>/dev/null; tr '\\0' ' ' < \"$p/cmdline\" 2>/dev/null; echo; done >> \"$OUT/proc_cmdline.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-packages-rhel",
        "Installed RPM packages (RHEL)",
        "System",
        ["rpm -qa >> \"$OUT/rpm_packages.txt\" 2>/dev/null"],
        distros=["rhel"],
    )

    add(
        "lin-packages-ubuntu",
        "Installed packages (Ubuntu apt)",
        "System",
        ["apt list --installed 2>/dev/null >> \"$OUT/apt_packages.txt\""],
        distros=["ubuntu"],
    )

    add(
        "lin-forensics-var-log",
        "Copy key logs to case folder",
        "Log Analysis",
        [
            "mkdir -p \"$OUT/logs\"",
            "cp -a /var/log/syslog \"$OUT/logs/\" 2>/dev/null",
            "cp -a /var/log/messages \"$OUT/logs/\" 2>/dev/null",
            "cp -a /var/log/auth.log \"$OUT/logs/\" 2>/dev/null",
            "cp -a /var/log/secure \"$OUT/logs/\" 2>/dev/null",
        ],
        output_type="binary",
    )

    add(
        "lin-hash-artifacts",
        "SHA256 manifest of collected files",
        "Forensics",
        [
            "find \"$OUT\" -type f -exec sha256sum {} \\; >> \"$OUT/SHA256SUMS.txt\" 2>/dev/null",
        ],
        description="Hash all collected artifacts for chain of custody.",
    )

    return cmds
