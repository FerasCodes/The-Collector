# Build The Collector — opens in web browser
param([switch]$OneFile)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== The Collector — build (web browser app) ===" -ForegroundColor Cyan

python -m pip install -q -r requirements.txt -r requirements-build.txt

if (Test-Path "assets\logo.png") {
    New-Item -ItemType Directory -Force -Path "web\static\img" | Out-Null
    Copy-Item "assets\logo.png" "web\static\img\logo.png" -Force
    python scripts\make_icon.py 2>$null
}

if ($OneFile) {
    pyinstaller --noconfirm --clean --onefile --console `
        --name TheCollector `
        --icon "assets\logo.ico" `
        --add-data "data;data" `
        --add-data "plugins;plugins" `
        --add-data "assets;assets" `
        --add-data "web;web" `
        --hidden-import flask `
        --hidden-import werkzeug `
        --hidden-import jinja2 `
        --exclude-module customtkinter `
        --exclude-module tkinter `
        collector_gui.py
} else {
    pyinstaller --noconfirm --clean build\TheCollector.spec
}

Write-Host ""
Write-Host "Done. Run dist\TheCollector.exe — your browser will open automatically." -ForegroundColor Green
