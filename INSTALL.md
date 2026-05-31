# Install The Collector (Web Browser)

The Collector runs as a **local website** in your browser (no Python desktop GUI).

## Option A — Executable

1. Run `.\build_exe.ps1` or use `dist\TheCollector.exe`.
2. Double-click **TheCollector.exe**.
3. Your browser opens automatically (e.g. `http://127.0.0.1:8765`).
4. Leave the black console window open while you work.

## Option B — From source

```powershell
cd "C:\Users\Importme\Desktop\The collector"
pip install -r requirements.txt
python collector_gui.py
```

Or:

```powershell
python main.py --web
```

## Using the web app

- **Browse commands** — search, filter by topic, add to your script.
- **Quick start profiles** — one-click load (full triage, config review, TeamViewer/AnyDesk, etc.).
- **Preview** — see generated script; click **Download script** to save `.bat` / `.ps1`.
- **Run on the host** — execute the downloaded script in an elevated Command Prompt or PowerShell (collection runs on the machine, not inside the browser).

## CLI only (no browser)

```powershell
python main.py -o windows -l
python main.py -o windows -p win-config-review -n C:\Cases\HOST01
```

## Build the exe

```powershell
.\build_exe.ps1
```

Output: `dist\TheCollector.exe`
