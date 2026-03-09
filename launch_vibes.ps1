# --- Pure Stone Vibes | Unified Server Launcher ---
# This script launches both the FastAPI Backend and the Vibe Scribe auto-pusher.

$ProjectRoot = "C:\Users\Customer\Desktop\fishesstonevibeexample10mins"
Set-Location $ProjectRoot

# Ensure logs directory exists
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" -Force }

Write-Host "--- REACHING INTO THE GROVE: Launching Pure Stone Vibes ---" -ForegroundColor Cyan

# 1. Kill any existing processes (FastAPI on 8000)
Write-Host "[1/3] Clearing existing vibrations on Port 8000..." -ForegroundColor Yellow
$ExistingProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($ExistingProcess) {
    Stop-Process -Id $ExistingProcess.OwningProcess -Force
    Write-Host "      Cleaned." -ForegroundColor Gray
}

# 2. Launch FastAPI Backend
Write-Host "[2/3] Launching FastAPI Backend (with System Metrics)..." -ForegroundColor Yellow
$PythonExe = "$ProjectRoot\venv\bin\python"
$BackendArgs = "main.py"
Start-Process -FilePath $PythonExe -ArgumentList $BackendArgs -WindowStyle Hidden -RedirectStandardOutput "logs\backend_boot.log" -RedirectStandardError "logs\backend_error.log"
Write-Host "      Backend running in background (Port 8000)." -ForegroundColor Green

# 3. Launch Vibe Scribe (Auto-Pusher)
Write-Host "[3/3] Activating Vibe Scribe (GitHub Sync)..." -ForegroundColor Yellow
$ScribeArgs = "scribe.py"
Start-Process -FilePath $PythonExe -ArgumentList $ScribeArgs -WindowStyle Hidden -RedirectStandardOutput "logs\scribe_boot.log" -RedirectStandardError "logs\scribe_error.log"
Write-Host "      Scribe watching for vibrations." -ForegroundColor Green

Write-Host "`n--- SYSTEM CALIBRATED ---" -ForegroundColor Cyan
Write-Host "Vibe Access Points:" -ForegroundColor Magenta
Write-Host "  Landing Page:  http://localhost:8000/index.html"
Write-Host "  The Grove:     http://localhost:8000/gallery.html"
Write-Host "  The Process:   http://localhost:8000/process.html"
Write-Host "  Inquiries:     http://localhost:8000/inquiry.html"
Write-Host "  Splat Dash:    http://localhost:8000/dashboard.html"
Write-Host "  Stats Center:  http://localhost:8000/stats.html"
Write-Host "  Auction House: http://localhost:8000/auction.html"
Write-Host "  Login Portal:  http://localhost:8000/login.html"
Write-Host "  Debug Portal:  http://localhost:8000/debug.html"

Write-Host "`nCheck: logs/ for status updates"
Write-Host "Press any key to exit this window (Servers will stay running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
