"""System configuration review, TeamViewer, and AnyDesk artifact collectors."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs._helpers import PS, WIN_OUT, linux_cmd, win_cmd

O = WIN_OUT


def config_and_remote_commands() -> list[CollectorCommand]:
    cmds: list[CollectorCommand] = []

    # --- Windows configuration review ---
    cmds.append(
        win_cmd(
            "win-config-msinfo",
            "Configuration review — MSInfo32 report",
            "Configuration",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'msinfo32 /nfo "{O}\\Configuration\\%computername%_msinfo32.nfo" /categories +all 2>nul',
                f'echo MSInfo export attempted > "{O}\\Configuration\\%computername%_msinfo_note.txt"',
            ],
            description="Full system configuration snapshot (NFO) for configuration review.",
            output_type="binary",
            os_min="7",
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-network-full",
            "Configuration review — network (adapters, DNS, routes, wins)",
            "Network",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'ipconfig /all > "{O}\\Configuration\\%computername%_ipconfig_all.txt"',
                f'netsh interface show interface >> "{O}\\Configuration\\%computername%_ipconfig_all.txt"',
                f'route print >> "{O}\\Configuration\\%computername%_routes.txt"',
                f'netsh winhttp show proxy > "{O}\\Configuration\\%computername%_proxy.txt"',
                f'netsh wlan show profiles >> "{O}\\Configuration\\%computername%_wlan_profiles.txt" 2>nul',
            ],
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-system-settings",
            "Configuration review — computer name, domain, timezone, power",
            "Configuration",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'systeminfo > "{O}\\Configuration\\%computername%_systeminfo.txt"',
                f'wmic computersystem get Name,Domain,PartOfDomain,Workgroup /format:list >> "{O}\\Configuration\\%computername%_systeminfo.txt"',
                f'tzutil /g > "{O}\\Configuration\\%computername%_timezone.txt" 2>nul',
                f'powercfg /list > "{O}\\Configuration\\%computername%_powercfg.txt" 2>nul',
            ],
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-services-startup",
            "Configuration review — services (startup type & status)",
            "Service",
            "powershell",
            [
                f'{PS} "$d=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\Configuration\"; New-Item -Force -ItemType Directory -Path $d | Out-Null; Get-CimInstance Win32_Service | Select Name,DisplayName,State,StartMode,PathName,StartName | Export-Csv -NoTypeInformation (Join-Path $d \"$env:COMPUTERNAME`_Services.csv\")"',
            ],
            output_type="csv",
            os_min="7",
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-registry-policies",
            "Configuration review — key policy registry (RDP, UAC, NTLM, LSA)",
            "Security",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'reg export "HKLM\\SOFTWARE\\Policies" "{O}\\Configuration\\%computername%_HKLM_Policies.reg" /y 2>nul',
                f'reg export "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" "{O}\\Configuration\\%computername%_RDP_policy.reg" /y 2>nul',
                f'reg export "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" "{O}\\Configuration\\%computername%_LSA.reg" /y 2>nul',
            ],
            output_type="binary",
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-windows-update",
            "Configuration review — Windows Update settings",
            "Configuration",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'reg query "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /s > "{O}\\Configuration\\%computername%_WU_Policy.txt" 2>nul',
                f'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate" /s >> "{O}\\Configuration\\%computername%_WU_Policy.txt" 2>nul',
            ],
            os_min="7",
            tags=["config", "review"],
        )
    )

    cmds.append(
        win_cmd(
            "win-config-features-optional",
            "Configuration review — optional features & capabilities",
            "Configuration",
            "cmd",
            [
                f'mkdir "{O}\\Configuration" 2>nul',
                f'dism /online /get-features /format:table > "{O}\\Configuration\\%computername%_features.txt" 2>nul',
                f'dism /online /get-capabilities >> "{O}\\Configuration\\%computername%_features.txt" 2>nul',
            ],
            os_min="7",
            tags=["config", "review"],
        )
    )

    # --- TeamViewer Windows ---
    cmds.append(
        win_cmd(
            "win-artifact-teamviewer-logs",
            "TeamViewer — logs and config (AppData & ProgramData)",
            "Remote Access",
            "cmd",
            [
                f'mkdir "{O}\\RemoteAccess\\TeamViewer" 2>nul',
                f'xcopy "%APPDATA%\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\AppData" /E /I /Y 2>nul',
                f'xcopy "%ProgramData%\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\ProgramData" /E /I /Y 2>nul',
                f'xcopy "%ProgramFiles%\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\ProgramFiles" /E /I /Y 2>nul',
                f'xcopy "%ProgramFiles(x86)%\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\ProgramFiles_x86" /E /I /Y 2>nul',
            ],
            output_type="binary",
            tags=["teamviewer", "remote", "artifact"],
        )
    )

    cmds.append(
        win_cmd(
            "win-artifact-teamviewer-registry",
            "TeamViewer — registry (ClientID, settings)",
            "Registry",
            "cmd",
            [
                f'mkdir "{O}\\RemoteAccess\\TeamViewer" 2>nul',
                f'reg export "HKCU\\Software\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\%computername%_TeamViewer_HKCU.reg" /y 2>nul',
                f'reg export "HKLM\\SOFTWARE\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\%computername%_TeamViewer_HKLM.reg" /y 2>nul',
                f'reg export "HKLM\\SOFTWARE\\WOW6432Node\\TeamViewer" "{O}\\RemoteAccess\\TeamViewer\\%computername%_TeamViewer_HKLM32.reg" /y 2>nul',
            ],
            output_type="binary",
            tags=["teamviewer", "remote"],
        )
    )

    cmds.append(
        win_cmd(
            "win-artifact-teamviewer-connections",
            "TeamViewer — connection manager text export",
            "Remote Access",
            "powershell",
            [
                f'{PS} "$d=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\RemoteAccess\\TeamViewer\"; New-Item -Force -ItemType Directory -Path $d | Out-Null; Get-ChildItem -Path $env:APPDATA,\"$env:ProgramData\\TeamViewer\" -Recurse -Include *.log,*.txt,connections*.txt -ErrorAction SilentlyContinue | Select FullName,Length,LastWriteTime | Export-Csv -NoTypeInformation (Join-Path $d \"$env:COMPUTERNAME`_TeamViewer_Files.csv\")"',
            ],
            output_type="csv",
            tags=["teamviewer", "remote"],
        )
    )

    # --- AnyDesk Windows ---
    cmds.append(
        win_cmd(
            "win-artifact-anydesk-files",
            "AnyDesk — config, traces, and session files",
            "Remote Access",
            "cmd",
            [
                f'mkdir "{O}\\RemoteAccess\\AnyDesk" 2>nul',
                f'xcopy "%APPDATA%\\AnyDesk" "{O}\\RemoteAccess\\AnyDesk\\AppData" /E /I /Y 2>nul',
                f'xcopy "%ProgramData%\\AnyDesk" "{O}\\RemoteAccess\\AnyDesk\\ProgramData" /E /I /Y 2>nul',
                f'xcopy "%ProgramFiles(x86)%\\AnyDesk" "{O}\\RemoteAccess\\AnyDesk\\ProgramFiles" /E /I /Y 2>nul',
            ],
            output_type="binary",
            tags=["anydesk", "remote", "artifact"],
        )
    )

    cmds.append(
        win_cmd(
            "win-artifact-anydesk-ad-trace",
            "AnyDesk — ad.trace and connection history",
            "Remote Access",
            "powershell",
            [
                f'{PS} "$d=Join-Path $env:USERPROFILE \"Desktop\\$env:COMPUTERNAME\\RemoteAccess\\AnyDesk\"; New-Item -Force -ItemType Directory -Path $d | Out-Null; $paths=@(\"$env:APPDATA\\AnyDesk\",\"$env:ProgramData\\AnyDesk\"); foreach($p in $paths){{ if(Test-Path $p){{ Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue | Where-Object {{ $_.Name -match \"trace|conf|cache|history\" }} | Copy-Item -Destination $d -Recurse -Force -ErrorAction SilentlyContinue }} }}; Get-ChildItem $d -Recurse | Select FullName,Length,LastWriteTime | Export-Csv -NoTypeInformation (Join-Path $d \"$env:COMPUTERNAME`_AnyDesk_Manifest.csv\")"',
            ],
            output_type="csv",
            tags=["anydesk", "remote"],
        )
    )

    cmds.append(
        win_cmd(
            "win-artifact-anydesk-registry",
            "AnyDesk — registry settings",
            "Registry",
            "cmd",
            [
                f'mkdir "{O}\\RemoteAccess\\AnyDesk" 2>nul',
                f'reg export "HKCU\\Software\\AnyDesk" "{O}\\RemoteAccess\\AnyDesk\\%computername%_AnyDesk_HKCU.reg" /y 2>nul',
                f'reg export "HKLM\\SOFTWARE\\AnyDesk" "{O}\\RemoteAccess\\AnyDesk\\%computername%_AnyDesk_HKLM.reg" /y 2>nul',
            ],
            output_type="binary",
            tags=["anydesk", "remote"],
        )
    )

    # --- Linux configuration review ---
    cmds.append(
        linux_cmd(
            "lin-config-system-overview",
            "Configuration review — hostname, OS, kernel, time",
            "Configuration",
            [
                'mkdir -p "$OUT/Configuration"',
                'hostnamectl >> "$OUT/Configuration/system_overview.txt" 2>/dev/null',
                'timedatectl >> "$OUT/Configuration/system_overview.txt" 2>/dev/null',
                'uname -a >> "$OUT/Configuration/system_overview.txt"',
                'cat /etc/os-release >> "$OUT/Configuration/system_overview.txt" 2>/dev/null',
            ],
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-network",
            "Configuration review — network interfaces, DNS, routes",
            "Network",
            [
                'mkdir -p "$OUT/Configuration"',
                'ip addr >> "$OUT/Configuration/network.txt" 2>/dev/null',
                'ip route >> "$OUT/Configuration/network.txt" 2>/dev/null',
                'cat /etc/resolv.conf >> "$OUT/Configuration/network.txt" 2>/dev/null',
                'cat /etc/hosts >> "$OUT/Configuration/network.txt" 2>/dev/null',
                'ls -la /etc/netplan >> "$OUT/Configuration/network.txt" 2>/dev/null',
                'cat /etc/netplan/*.yaml >> "$OUT/Configuration/netplan.yaml.txt" 2>/dev/null',
                'nmcli device show >> "$OUT/Configuration/nmcli_devices.txt" 2>/dev/null',
            ],
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-sysctl-limits",
            "Configuration review — sysctl and limits",
            "Configuration",
            [
                'mkdir -p "$OUT/Configuration"',
                'sysctl -a >> "$OUT/Configuration/sysctl.txt" 2>/dev/null',
                'cat /etc/security/limits.conf >> "$OUT/Configuration/limits.txt" 2>/dev/null',
                'cat /proc/cmdline >> "$OUT/Configuration/kernel_cmdline.txt"',
            ],
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-firewall-all",
            "Configuration review — firewall (iptables, nft, ufw, firewalld)",
            "Security",
            [
                'mkdir -p "$OUT/Configuration"',
                'iptables-save >> "$OUT/Configuration/firewall.txt" 2>/dev/null',
                'nft list ruleset >> "$OUT/Configuration/firewall.txt" 2>/dev/null',
                'ufw status verbose >> "$OUT/Configuration/firewall.txt" 2>/dev/null',
                'firewall-cmd --list-all-zones >> "$OUT/Configuration/firewall.txt" 2>/dev/null',
            ],
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-ssh-sshd",
            "Configuration review — SSH server config",
            "Security",
            [
                'mkdir -p "$OUT/Configuration"',
                'cp -a /etc/ssh/sshd_config "$OUT/Configuration/sshd_config" 2>/dev/null',
                'cp -a /etc/ssh/ssh_config "$OUT/Configuration/ssh_config" 2>/dev/null',
            ],
            output_type="binary",
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-systemd-enabled",
            "Configuration review — enabled systemd units",
            "Service",
            [
                'mkdir -p "$OUT/Configuration"',
                'systemctl list-unit-files --state=enabled >> "$OUT/Configuration/systemd_enabled.txt" 2>/dev/null',
                'systemctl list-units --type=service --state=running >> "$OUT/Configuration/systemd_running.txt" 2>/dev/null',
            ],
            tags=["config", "review", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-config-packages-held",
            "Configuration review — package holds (apt/yum)",
            "Configuration",
            [
                'mkdir -p "$OUT/Configuration"',
                'apt-mark showhold >> "$OUT/Configuration/package_holds.txt" 2>/dev/null',
                'yum versionlock list >> "$OUT/Configuration/package_holds.txt" 2>/dev/null',
                'dnf versionlock list >> "$OUT/Configuration/package_holds.txt" 2>/dev/null',
            ],
            distros=["rhel", "ubuntu", "generic"],
            tags=["config", "review", "linux"],
        )
    )

    # --- TeamViewer Linux ---
    cmds.append(
        linux_cmd(
            "lin-artifact-teamviewer",
            "TeamViewer — logs and configuration (Linux)",
            "Remote Access",
            [
                'mkdir -p "$OUT/RemoteAccess/TeamViewer"',
                'cp -a /opt/teamviewer/logs "$OUT/RemoteAccess/TeamViewer/" 2>/dev/null',
                'cp -a ~/.config/teamviewer "$OUT/RemoteAccess/TeamViewer/user_config" 2>/dev/null',
                'cp -a /etc/teamviewer "$OUT/RemoteAccess/TeamViewer/etc" 2>/dev/null',
                'find /var/log -iname "*teamviewer*" 2>/dev/null -exec cp -a {} "$OUT/RemoteAccess/TeamViewer/" \\;',
            ],
            output_type="binary",
            tags=["teamviewer", "remote", "linux"],
        )
    )

    # --- AnyDesk Linux ---
    cmds.append(
        linux_cmd(
            "lin-artifact-anydesk",
            "AnyDesk — user config, cache, and system config (Linux)",
            "Remote Access",
            [
                'mkdir -p "$OUT/RemoteAccess/AnyDesk"',
                'cp -a ~/.anydesk "$OUT/RemoteAccess/AnyDesk/user" 2>/dev/null',
                'cp -a /etc/anydesk "$OUT/RemoteAccess/AnyDesk/etc" 2>/dev/null',
                'cp -a /var/lib/anydesk "$OUT/RemoteAccess/AnyDesk/varlib" 2>/dev/null',
                'find /var/log -iname "*anydesk*" 2>/dev/null -exec cp -a {} "$OUT/RemoteAccess/AnyDesk/" \\;',
            ],
            output_type="binary",
            tags=["anydesk", "remote", "linux"],
        )
    )

    cmds.append(
        linux_cmd(
            "lin-artifact-anydesk-trace",
            "AnyDesk — trace files listing",
            "Remote Access",
            [
                'mkdir -p "$OUT/RemoteAccess/AnyDesk"',
                'find /home /root /etc /var -iname "*anydesk*" 2>/dev/null >> "$OUT/RemoteAccess/AnyDesk/file_paths.txt"',
                'find ~/.anydesk /etc/anydesk -type f 2>/dev/null -exec ls -la {} \\; >> "$OUT/RemoteAccess/AnyDesk/file_listing.txt"',
            ],
            tags=["anydesk", "remote", "linux"],
        )
    )

    return cmds
