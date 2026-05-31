"""One-click triage profiles — pre-built command sets for the script builder."""

from __future__ import annotations

from dataclasses import dataclass

from collector.models import CollectorCommand


@dataclass
class TriageProfile:
    id: str
    name: str
    description: str
    platform: str  # windows | linux
    command_ids: list[str] = None  # type: ignore[assignment]
    id_prefixes: list[str] = None  # type: ignore[assignment]
    categories: list[str] = None  # type: ignore[assignment]
    tags: list[str] = None  # type: ignore[assignment]
    exclude_ids: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.command_ids = self.command_ids or []
        self.id_prefixes = self.id_prefixes or []
        self.categories = self.categories or []
        self.tags = self.tags or []
        self.exclude_ids = self.exclude_ids or []


PROFILES: list[TriageProfile] = [
    TriageProfile(
        id="win-quick-triage",
        name="Quick triage (Windows)",
        description="Fast host snapshot: system, network, users, processes, and key security logs.",
        platform="windows",
        command_ids=["win-ir-triage-banner"],
        categories=["Network", "Process", "System", "User/Group", "Log Analysis", "Security"],
        exclude_ids=["win-kape-zone-identifier"],
    ),
    TriageProfile(
        id="win-full-triage",
        name="Full triage (Windows)",
        description="Comprehensive DFIR collection: legacy collectors + KAPE artifacts + WEF queries + pentest checks.",
        platform="windows",
        categories=[
            "Network",
            "Process",
            "System",
            "Registry",
            "Service",
            "User/Group",
            "Security",
            "Persistence",
            "Log Analysis",
            "Forensics",
            "AV/EDR",
            "Active Directory",
            "Browser",
            "Troubleshooting",
        ],
        exclude_ids=["win-kape-zone-identifier"],  # very slow on large profiles
    ),
    TriageProfile(
        id="win-kape-essential",
        name="KAPE essential artifacts",
        description="File/registry artifacts similar to a KAPE Basic collection target.",
        platform="windows",
        id_prefixes=["win-kape-"],
        exclude_ids=["win-kape-zone-identifier", "win-kape-ntuser-all-users"],
    ),
    TriageProfile(
        id="win-wef-security",
        name="WEF / Event log pack",
        description="Targeted Windows Event Log queries and EVTX exports for incident response.",
        platform="windows",
        id_prefixes=["win-wef-"],
    ),
    TriageProfile(
        id="win-pentest-recon",
        name="Pentest recon (Windows)",
        description="Permission, share, proxy, service, and misconfiguration checks.",
        platform="windows",
        id_prefixes=["win-pentest-"],
    ),
    TriageProfile(
        id="win-troubleshoot",
        name="Troubleshooting pack (Windows)",
        description="Health checks: SFC, DISM, disks, memory, reliability.",
        platform="windows",
        id_prefixes=["win-trouble-"],
        categories=["Troubleshooting"],
    ),
    TriageProfile(
        id="linux-quick-triage",
        name="Quick triage (Linux)",
        description="Hostname, users, network, processes, cron, auth log tail.",
        platform="linux",
        command_ids=[
            "lin-ir-full-triage-banner",
        ],
        categories=["Network", "Process", "User/Group", "Log Analysis"],
    ),
    TriageProfile(
        id="linux-full-triage",
        name="Full triage (Linux)",
        description="Full RHEL/Ubuntu IR: persistence, logs, packages, forensics copies.",
        platform="linux",
        categories=[
            "Network",
            "Process",
            "System",
            "Security",
            "Persistence",
            "Log Analysis",
            "Forensics",
            "User/Group",
            "File System",
        ],
        exclude_ids=["lin-pentest-capabilities", "lin-pentest-world-writable"],
    ),
    TriageProfile(
        id="linux-kape-style",
        name="KAPE-style (Linux)",
        description="Config and log archives under Artifacts/.",
        platform="linux",
        id_prefixes=["lin-forensics-copy-", "lin-hash-artifacts"],
    ),
    TriageProfile(
        id="linux-pentest-recon",
        name="Pentest recon (Linux)",
        description="SUID, sudoers, capabilities, world-writable, SSH.",
        platform="linux",
        id_prefixes=["lin-pentest-"],
    ),
    TriageProfile(
        id="win-config-review",
        name="Configuration review (Windows)",
        description="System, network, services, policies, and settings for configuration audit.",
        platform="windows",
        id_prefixes=["win-config-"],
    ),
    TriageProfile(
        id="win-remote-access",
        name="Remote access artifacts (Windows)",
        description="TeamViewer and AnyDesk logs, registry, and configuration files.",
        platform="windows",
        id_prefixes=["win-artifact-teamviewer", "win-artifact-anydesk"],
    ),
    TriageProfile(
        id="linux-config-review",
        name="Configuration review (Linux)",
        description="OS, network, firewall, SSH, sysctl, and systemd for configuration audit.",
        platform="linux",
        id_prefixes=["lin-config-"],
    ),
    TriageProfile(
        id="linux-remote-access",
        name="Remote access artifacts (Linux)",
        description="TeamViewer and AnyDesk paths, logs, and configs on Linux.",
        platform="linux",
        id_prefixes=["lin-artifact-teamviewer", "lin-artifact-anydesk"],
    ),
]


def _legacy_must_have(catalog: list[CollectorCommand], platform: str) -> list[CollectorCommand]:
    return [c for c in catalog if c.platform == platform and c.required_step]


def resolve_profile(profile_id: str, catalog: list[CollectorCommand]) -> list[CollectorCommand]:
    profile = next((p for p in PROFILES if p.id == profile_id), None)
    if not profile:
        raise KeyError(f"Unknown profile: {profile_id}")

    platform_cmds = [c for c in catalog if c.platform == profile.platform]
    by_id = {c.id: c for c in platform_cmds}
    chosen: dict[str, CollectorCommand] = {}

    # Explicit IDs
    for cid in profile.command_ids:
        if cid in by_id:
            chosen[cid] = by_id[cid]

    # Prefix match
    for prefix in profile.id_prefixes:
        for cmd in platform_cmds:
            if cmd.id.startswith(prefix):
                chosen[cmd.id] = cmd

    # Category match
    for cat in profile.categories:
        for cmd in platform_cmds:
            if cmd.category == cat:
                chosen[cmd.id] = cmd

    # Tag match (any tag on command)
    for tag in profile.tags:
        for cmd in platform_cmds:
            if tag in cmd.dfir_tags:
                chosen[cmd.id] = cmd

    for eid in profile.exclude_ids:
        chosen.pop(eid, None)

    # Always include must-have setup + hash steps for windows
    for cmd in _legacy_must_have(catalog, profile.platform):
        chosen[cmd.id] = cmd

    # Stable order: required first, then name
    result = list(chosen.values())
    result.sort(key=lambda c: (not c.required_step, c.category, c.name.lower()))
    return result


def list_profiles(platform: str | None = None) -> list[TriageProfile]:
    if platform:
        return [p for p in PROFILES if p.platform == platform.lower()]
    return list(PROFILES)


def get_profile(profile_id: str) -> TriageProfile | None:
    return next((p for p in PROFILES if p.id == profile_id), None)
