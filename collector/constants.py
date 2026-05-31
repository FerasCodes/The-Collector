from pathlib import Path

from collector.paths import ROOT, data_path, resource_path

APP_NAME = "The Collector"
APP_SUBTITLE = "Script Studio"
APP_CREDIT = "Built by Feras Faqeeh"
CATALOG_VERSION = 4

DATA_DIR = data_path()
LEGACY_PLUGINS = resource_path("plugins")
ASSETS_DIR = resource_path("assets")
LOGO_PNG = ASSETS_DIR / "logo.png"
LOGO_ICO = ASSETS_DIR / "logo.ico"
USER_DATA = Path.home() / ".the-collector"
FAVORITES_FILE = USER_DATA / "favorites.json"
RECENT_FILE = USER_DATA / "recent.json"
SNIPPETS_FILE = USER_DATA / "snippets.json"

WINDOWS_OS_ORDER = ["xp", "vista", "7", "8", "8.1", "10", "11"]
LINUX_DISTROS = ["rhel", "ubuntu", "generic"]

SIDEBAR_CATEGORIES = [
    "File System",
    "Network",
    "Process",
    "System",
    "Registry",
    "Service",
    "User/Group",
    "Hardware",
    "Security",
    "Persistence",
    "Log Analysis",
    "Forensics",
    "AV/EDR",
    "Active Directory",
    "Browser",
    "Troubleshooting",
    "Remote Access",
    "Configuration",
    "Other",
]

CATEGORY_KEYWORDS = {
    "Network": ("network", "ipconfig", "netstat", "dns", "arp", "routing", "firewall", "wifi", "wlan", "smb", "netbios", "rdp", "tcp", "udp", "pipe"),
    "Process": ("process", "tasklist", "task ", "dll", "prefetch"),
    "Registry": ("registry", "reg ", "hive", "shimcache", "amcache", "shellbag"),
    "Service": ("service", "schtasks", "scheduled"),
    "User/Group": ("user", "group", "password", "account", "admin", "sam "),
    "Security": ("audit", "security", "defender", "bitlocker", "ssl", "policy", "gpresult", "secedit"),
    "Persistence": ("startup", "run key", "cron", "at job", "scheduled"),
    "Log Analysis": ("event", "wevtutil", "journal", "auth.log", "secure"),
    "Forensics": ("mft", "prefetch", "jump", "recycle", "browser", "chrome", "firefox", "edge", "recent", "mfte"),
    "AV/EDR": ("mcafee", "symantec", "defender", "antivirus"),
    "Active Directory": ("ad ", "domain", "nltest", "repadmin", "trusted"),
    "Browser": ("chrome", "firefox", "edge", "browser", "history", "cache"),
    "Hardware": ("driver", "pnp", "disk", "volume", "lvm", "raid"),
    "File System": ("directory", "file", "xcopy", "dir ", "hosts"),
    "System": ("systeminfo", "patch", "feature", "time", "ntp", "w32tm", "dism", "uname", "boot"),
    "Troubleshooting": ("troubleshoot", "repair", "sfc", "dism"),
    "Remote Access": ("teamviewer", "anydesk", "remote access", "remote desktop"),
    "Configuration": ("configuration review", "config review", "msinfo", "netplan", "sysctl"),
}
