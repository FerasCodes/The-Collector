"""Extended Linux DFIR / pentest collectors (RHEL & Ubuntu)."""

from __future__ import annotations

from collector.models import CollectorCommand
from collector.packs._helpers import linux_cmd


def linux_pack_commands() -> list[CollectorCommand]:
    cmds: list[CollectorCommand] = []

    def add(*args, **kwargs) -> None:
        cmds.append(linux_cmd(*args, **kwargs))

    add(
        "lin-ir-full-triage-banner",
        "IR — Host triage header",
        "System",
        [
            'echo "=== The Collector Linux triage ===" > "$OUT/00_triage_header.txt"',
            "date -u >> \"$OUT/00_triage_header.txt\"",
            "uptime >> \"$OUT/00_triage_header.txt\"",
            "who -a >> \"$OUT/00_triage_header.txt\"",
        ],
    )

    add(
        "lin-pentest-sudoers",
        "Pentest — sudoers and sudo config",
        "Security",
        [
            "cat /etc/sudoers >> \"$OUT/sudoers.txt\" 2>/dev/null",
            "ls -la /etc/sudoers.d >> \"$OUT/sudoers.txt\" 2>/dev/null",
            "cat /etc/sudoers.d/* >> \"$OUT/sudoers_d.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-pentest-cron-all",
        "Persistence — all cron sources",
        "Persistence",
        [
            "cat /etc/crontab >> \"$OUT/cron_all.txt\" 2>/dev/null",
            "ls -la /etc/cron.* >> \"$OUT/cron_all.txt\" 2>/dev/null",
            "cat /etc/cron.d/* >> \"$OUT/cron_all.txt\" 2>/dev/null",
            "for u in $(cut -f1 -d: /etc/passwd); do crontab -l -u \"$u\" 2>/dev/null; done >> \"$OUT/cron_per_user.txt\"",
        ],
    )

    add(
        "lin-pentest-systemd-generators",
        "Persistence — systemd unit files",
        "Persistence",
        [
            "systemctl list-unit-files --type=service >> \"$OUT/systemd_unit_files.txt\" 2>/dev/null",
            "ls -laR /etc/systemd/system >> \"$OUT/systemd_etc_units.txt\" 2>/dev/null",
            "ls -laR /lib/systemd/system >> \"$OUT/systemd_lib_units.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-forensics-deleted-open",
        "Forensics — deleted files still open (lsof)",
        "Forensics",
        ["lsof -nP | grep deleted >> \"$OUT/lsof_deleted.txt\" 2>/dev/null"],
    )

    add(
        "lin-forensics-mounts",
        "Forensics — mount points and fstab",
        "File System",
        [
            "mount >> \"$OUT/mounts.txt\"",
            "cat /etc/fstab >> \"$OUT/fstab.txt\" 2>/dev/null",
            "findmnt -lo TARGET,SOURCE,FSTYPE,OPTIONS >> \"$OUT/findmnt.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-network-arp-route",
        "Network — ARP and routing",
        "Network",
        [
            "ip neigh >> \"$OUT/ip_neigh.txt\" 2>/dev/null",
            "arp -an >> \"$OUT/arp.txt\" 2>/dev/null",
            "ip route >> \"$OUT/ip_route.txt\"",
        ],
    )

    add(
        "lin-network-listening",
        "Network — listening sockets",
        "Network",
        [
            "ss -tulpn >> \"$OUT/listening_sockets.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-pentest-users-lastlog",
        "User/Group — passwd/shadow perms & lastlog",
        "User/Group",
        [
            "ls -la /etc/passwd /etc/shadow /etc/group >> \"$OUT/account_files_perm.txt\"",
            "lastlog >> \"$OUT/lastlog.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-rhel-yum-history",
        "RHEL — yum/dnf history",
        "System",
        ["yum history list >> \"$OUT/yum_history.txt\" 2>/dev/null", "dnf history list >> \"$OUT/dnf_history.txt\" 2>/dev/null"],
        distros=["rhel"],
    )

    add(
        "lin-ubuntu-apt-history",
        "Ubuntu — apt history",
        "System",
        [
            "cat /var/log/apt/history.log >> \"$OUT/apt_history.txt\" 2>/dev/null",
            "cat /var/log/dpkg.log >> \"$OUT/dpkg_log.txt\" 2>/dev/null",
        ],
        distros=["ubuntu"],
    )

    add(
        "lin-forensics-bash-history-all",
        "Forensics — shell history (all users)",
        "Forensics",
        [
            "find /home /root -name \".bash_history\" -o -name \".zsh_history\" 2>/dev/null | while read f; do echo \"=== $f ===\" >> \"$OUT/shell_histories.txt\"; cat \"$f\" >> \"$OUT/shell_histories.txt\" 2>/dev/null; done",
        ],
    )

    add(
        "lin-forensics-ssh-config",
        "Forensics — sshd_config & host keys fingerprints",
        "Security",
        [
            "cat /etc/ssh/sshd_config >> \"$OUT/sshd_config.txt\" 2>/dev/null",
            "sha256sum /etc/ssh/ssh_host_* 2>/dev/null >> \"$OUT/ssh_host_key_hashes.txt\"",
        ],
    )

    add(
        "lin-pentest-capabilities",
        "Pentest — file capabilities",
        "Security",
        ["getcap -r / 2>/dev/null >> \"$OUT/file_capabilities.txt\""],
        description="Can take time on large disks; consider scope.",
    )

    add(
        "lin-pentest-world-writable",
        "Pentest — world-writable dirs (top-level)",
        "Security",
        [
            "find /tmp /var/tmp /dev/shm -type f -perm -0002 2>/dev/null >> \"$OUT/world_writable_files.txt\"",
            "find / -xdev -type d -perm -0002 2>/dev/null | head -500 >> \"$OUT/world_writable_dirs.txt\"",
        ],
    )

    add(
        "lin-forensics-docker",
        "Forensics — Docker containers/images",
        "Process",
        [
            "docker ps -a >> \"$OUT/docker_ps.txt\" 2>/dev/null",
            "docker images >> \"$OUT/docker_images.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-log-auth-failed",
        "Log Analysis — failed SSH/auth (grep)",
        "Log Analysis",
        [
            "grep -i \"failed\\|failure\\|invalid\" /var/log/auth.log 2>/dev/null | tail -500 >> \"$OUT/auth_failures.txt\"",
            "grep -i \"failed\\|failure\\|invalid\" /var/log/secure 2>/dev/null | tail -500 >> \"$OUT/secure_failures.txt\"",
        ],
        distros=["rhel", "ubuntu", "generic"],
    )

    add(
        "lin-forensics-persistence-profile",
        "Persistence — profile/bashrc/system-wide",
        "Persistence",
        [
            "cat /etc/profile /etc/bash.bashrc 2>/dev/null >> \"$OUT/profile_system.txt\"",
            "find /home -maxdepth 3 \\( -name .bashrc -o -name .profile \\) -exec echo \"=== {} ===\" \\; -exec cat {} \\; >> \"$OUT/profile_users.txt\" 2>/dev/null",
        ],
    )

    add(
        "lin-rhel-selinux-denials",
        "RHEL — SELinux denials (ausearch)",
        "Log Analysis",
        ["ausearch -m avc -ts recent 2>/dev/null | tail -300 >> \"$OUT/selinux_avc.txt\""],
        distros=["rhel"],
    )

    add(
        "lin-forensics-copy-etc",
        "KAPE-style — copy /etc (configs)",
        "Forensics",
        [
            "mkdir -p \"$OUT/Artifacts/etc\"",
            "cp -a /etc/passwd /etc/group /etc/shadow /etc/hosts /etc/resolv.conf /etc/fstab /etc/crontab \"$OUT/Artifacts/etc/\" 2>/dev/null",
            "cp -a /etc/ssh \"$OUT/Artifacts/etc/\" 2>/dev/null",
        ],
        output_type="binary",
        tags=["dfir", "kape", "linux"],
    )

    add(
        "lin-forensics-copy-var-log",
        "KAPE-style — archive /var/log",
        "Log Analysis",
        [
            "mkdir -p \"$OUT/Artifacts\"",
            "tar -czf \"$OUT/Artifacts/var_log.tgz\" /var/log 2>/dev/null",
        ],
        output_type="binary",
        tags=["dfir", "kape", "linux"],
    )

    add(
        "lin-pentest-kernel-modules",
        "Troubleshooting — loaded kernel modules",
        "Hardware",
        ["lsmod >> \"$OUT/lsmod.txt\"", "modinfo $(lsmod | awk 'NR>1 {print $1}' | head -50) >> \"$OUT/modinfo_sample.txt\" 2>/dev/null"],
    )

    return cmds
