# --- Pure Stone Vibes | Unified Deployment Script ---
# This script handles the entire GitHub workflow in one command:
# 1. Increments the version number in version.json
# 2. Stages all changes
# 3. Creates a unique branch for the update
# 4. Generates a thematic commit message
# 5. Commits, Pushes, and Merges back to main
# 6. Mirror the latest vibes to Google Drive (Secondary Backup)
# 7. Cleans up the temporary branch

$ProjectRoot = "C:\Users\Customer\Desktop\fishesstonevibeexample10mins"
Set-Location $ProjectRoot

$LogFile = "logs\deploy.log"
$GdriveDest = "G:\My Drive\fishesstonevibeexample10mins"

function Write-DeployLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp - $Level - $Message"
    $LogEntry | Out-File -FilePath $LogFile -Append
    Write-Host $LogEntry
}

Write-DeployLog "--- REACHING INTO THE GROVE: Automated Deployment ---" -ForegroundColor Cyan

# --- 1. Increment Version ---
Write-DeployLog "[1/7] Polishing version number..." -ForegroundColor Yellow
$VersionPath = "version.json"
if (Test-Path $VersionPath) {
    $VersionData = Get-Content $VersionPath | ConvertFrom-Json
    $CurrentVersion = [double]$VersionData.version
    $NewVersion = [math]::Round($CurrentVersion + 0.001, 3)
    $VersionData.version = $NewVersion
    $VersionData | ConvertTo-Json | Out-File $VersionPath -Encoding utf8
    Write-DeployLog "      New Version: $NewVersion" -ForegroundColor Gray
}

# --- 2. Stage Changes ---
Write-DeployLog "[2/7] Gathering all vibrations (git add)..." -ForegroundColor Yellow
git add .

# --- 3. Branch Management ---
$Timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$BranchName = "vibe-update-$Timestamp"
Write-DeployLog "[3/7] Creating temporary branch: $BranchName" -ForegroundColor Yellow
git checkout -b $BranchName

# --- 4. Generate Commit Message ---
$ThematicMessages = @(
    "Amethyst-powered sync: Version ${NewVersion} secured.",
    "Vibes are 100% pure at v${NewVersion}. Pushing to the grove.",
    "Hand-wrapped code v${NewVersion} committed with 20g tension.",
    "Celestial Moon-Bloom update: Data points locked in v${NewVersion}.",
    "Root-to-Canopy sync complete. Version ${NewVersion} vibes are rising.",
    "Polishing the inventory v${NewVersion}: 100% accurate labeling."
)
$RandomIndex = Get-Random -Maximum $ThematicMessages.Count
$CommitMsg = $ThematicMessages[$RandomIndex]

Write-DeployLog "[4/7] Committing with message: $CommitMsg" -ForegroundColor Yellow
git commit -m "$CommitMsg"

# --- 5. Push & Merge ---
Write-DeployLog "[5/7] Pushing to GitHub and Merging..." -ForegroundColor Yellow
git push origin $BranchName
git checkout main
git pull origin main
git merge $BranchName
git push origin main

# --- 6. Sync to Google Drive ---
Write-DeployLog "[6/7] Mirroring to Google Drive (The Ethereal Vault)..." -ForegroundColor Yellow
$ExcludeFolders = @("node_modules", "venv", ".git", "__pycache__", ".tmp.driveupload", ".gemini", "logs")

if (Test-Path $GdriveDest) {
    # Manual deep sync logic (Copy-Item -Recurse)
    # We copy everything except excluded folders
    Get-ChildItem -Path "." -Recurse -File | Where-Object { 
        $filePath = $_.FullName
        $isExcluded = $false
        foreach ($exclude in $ExcludeFolders) {
            if ($filePath -like "*\$exclude\*") { $isExcluded = $true; break }
        }
        $isExcluded -eq $false
    } | ForEach-Object {
        # Rebuild full relative path from ProjectRoot to Destination
        $fullRel = $_.FullName.Replace($ProjectRoot, "").TrimStart("\")
        $destFile = Join-Path $GdriveDest $fullRel
        $destDir = Split-Path $destFile -Parent
        if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Copy-Item -Path $_.FullName -Destination $destFile -Force
    }
    Write-DeployLog "      Mirror sync to G-Drive Complete." -ForegroundColor Gray
}
else {
    Write-DeployLog "      ERROR: Google Drive path not found ($GdriveDest). Skipping backup." "ERROR"
}

# --- 7. Cleanup ---
Write-DeployLog "[7/7] Cleaning up the grove..." -ForegroundColor Yellow
git branch -d $BranchName

Write-DeployLog "`n--- DEPLOYMENT COMPLETE: V$($NewVersion) IS LIVE ---" -ForegroundColor Cyan
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
