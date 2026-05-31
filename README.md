# The Collector 2.0

**Script Studio** — build and run Windows (XP–11) and Linux (RHEL / Ubuntu) evidence-collection scripts from a dark IDE-style GUI or CLI. Built by Feras Faqeeh.

## Features

- **Command library** — migrated from your original `plugins/*.json`, plus extra DFIR/pentest collectors (persistence, logs, WMI, Defender, USN, SUID, journal, etc.).
- **Output-aware** — commands tagged as `text`, `csv`, `evtx`, `dat`, `json`, `binary`, or `zip`; file copies keep native formats.
- **OS / distro filters** — Windows XP through 11; Linux RHEL, Ubuntu, or generic.
- **Script builder** — drag sequence of collection steps; live preview as `.bat`, `.ps1`, or `.sh`.
- **Categories** — File System, Network, Process, Registry, Security, Persistence, Forensics, AV/EDR, AD, Browser, and more.
- **CLI** — same catalog for headless script generation (compatible with your original `-o` / `-b` / `-n` workflow).

## Quick start (web browser)

```powershell
pip install -r requirements.txt
python collector_gui.py
```

Your default browser opens to **http://127.0.0.1:PORT** — build scripts, browse commands, and download `.bat` / `.ps1` files from there.

### Executable

```powershell
.\build_exe.ps1
dist\TheCollector.exe
```

The exe starts the local web server and opens your browser. Keep the console window open while using the app.

See [INSTALL.md](INSTALL.md) for details.

## CLI (no browser)

```powershell
python main.py -o windows -l
python main.py -o windows -p win-full-triage -n C:\Cases\HOST01
```

Or:

```powershell
python The-Collector.py --gui
```

## Triage profiles (one-click)

In the GUI, use **Triage profiles** in the left sidebar → **Load profile**.

| Profile ID | Description |
|------------|-------------|
| `win-full-triage` | Full Windows DFIR (all categories) |
| `win-quick-triage` | Fast snapshot |
| `win-kape-essential` | KAPE-style artifact copies |
| `win-wef-security` | Event log / WEF-style queries + EVTX |
| `win-pentest-recon` | Misconfiguration & recon checks |
| `win-troubleshoot` | SFC, DISM, disks, reliability |
| `linux-full-triage` | Full Linux IR |
| `linux-quick-triage` | Fast Linux snapshot |
| `linux-kape-style` | `/etc` + `/var/log` archives |
| `linux-pentest-recon` | SUID, sudoers, SSH, etc. |

CLI example:

```powershell
python main.py --rebuild-catalog
python main.py -o windows -p win-full-triage -n C:\Cases\HOST01 -f bat
python main.py -o windows --list-profiles
```

## CLI examples

List Windows commands:

```powershell
python main.py -o windows -l
```

Rebuild `data/*.json` from legacy plugins:

```powershell
python main.py --rebuild-catalog
```

Generate a batch script (indices from `-l`):

```powershell
python main.py -o windows -n C:\Cases\HOST01 -b 1 2 3 4 -f bat
```

Linux shell script:

```powershell
python main.py -o linux -n ./case-host -b 1 2 3 -f sh
```

## Project layout

| Path | Purpose |
|------|---------|
| `main.py` | Entry point (`--gui` or CLI) |
| `collector/` | Catalog, script builder, legacy migration |
| `gui/` | CustomTkinter studio UI |
| `data/windows.json` | Built-in Windows command database |
| `data/linux.json` | Built-in Linux command database |
| `plugins/` | Legacy JSON (source for rebuild) |

## Adding commands

Edit `data/windows.json` or `data/linux.json`, or add entries to `plugins/` and run:

```powershell
python main.py --rebuild-catalog
```

Each command object supports:

```json
{
  "id": "win-example",
  "name": "Example collector",
  "description": "What it collects",
  "shell": "cmd",
  "platform": "windows",
  "category": "Network",
  "lines": ["ipconfig /all > \"%USERPROFILE%\\Desktop\\%computername%\\net.txt\""],
  "syntax": "ipconfig /all",
  "output_type": "text",
  "os_min": "xp",
  "os_max": "11"
}
```

## Notes

- **Run locally** — “Run Script” executes on the machine where the studio is open (Windows for `.bat`/`.ps1`).
- **Elevation** — registry hives, event logs, and some artifacts need Administrator.
- **MFTEcmd** — optional; place `MFTEcmd.exe` under `modules/` if you use the MFT collection step.
- **Favorites / recent** — stored under `%USERPROFILE%\.the-collector\`.

## License

MIT — see [LICENSE](LICENSE).
