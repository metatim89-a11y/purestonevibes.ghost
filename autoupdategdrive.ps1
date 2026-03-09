# --- Pure Stone Vibes | G-Drive Sync Routine ---
# Monitors the project folder and mirrors changes to Google Drive
# Logs errors specifically to logs/gdrive_sync.log

$WatchFolder = "c:\Users\Customer\Desktop\fishesstonevibeexample10mins"
$DestinationFolder = "G:\My Drive\fishesstonevibeexample10mins"
$LogFile = "$WatchFolder\logs\gdrive_sync.log"

# Create logs directory if it doesn't exist
if (!(Test-Path "$WatchFolder\logs")) { New-Item -ItemType Directory -Path "$WatchFolder\logs" -Force }

function Write-SyncLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp - $Level - $Message"
    $LogEntry | Out-File -FilePath $LogFile -Append
    Write-Host $LogEntry
}

$ExcludeFolders = @("node_modules", "venv", ".git", "__pycache__", ".tmp.driveupload")

$Filter = "*.*" 
$Watcher = New-Object IO.FileSystemWatcher $WatchFolder, $Filter -Property @{
    IncludeSubdirectories = $true
    EnableRaisingEvents = $true
}

Write-SyncLog "VIBE SYNC START: Monitoring $WatchFolder"

$Action = {
    $Path = $Event.SourceEventArgs.FullPath
    $Name = $Event.SourceEventArgs.Name
    $ChangeType = $Event.SourceEventArgs.ChangeType
    
    # Ignore excluded directories
    foreach ($Exclude in $ExcludeFolders) {
        if ($Path -like "*\$Exclude\*") { return }
    }

    try {
        # Determine relative path for destination
        $RelativePath = $Path.Replace($WatchFolder, "")
        $DestPath = "$DestinationFolder$RelativePath"
        
        Write-SyncLog "Syncing: $Name ($ChangeType)"
        
        if (Test-Path -Path $Path -PathType Container) {
            New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
        } else {
            Copy-Item -Path $Path -Destination $DestPath -Force -ErrorAction Stop
        }
    } catch {
        Write-SyncLog "G-DRIVE ERROR: Failed to sync $Name. Details: $($_.Exception.Message)" "ERROR"
    }
}

Register-ObjectEvent $Watcher "Changed" -Action $Action
Register-ObjectEvent $Watcher "Created" -Action $Action
Register-ObjectEvent $Watcher "Deleted" -Action $Action
Register-ObjectEvent $Watcher "Renamed" -Action $Action

while ($true) { sleep 5 }