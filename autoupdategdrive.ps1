# --- CONFIGURATION ---
$WatchFolder = "C:\Users\YourName\Documents\MyLocalProject" # Folder to watch
$DestinationFolder = "G:\My Drive\Backups"                 # Your Google Drive path
# ---------------------

$Filter = "*.*" 
$Watcher = New-Object IO.FileSystemWatcher $WatchFolder, $Filter -Property @{
    IncludeSubdirectories = $true
    EnableRaisingEvents = $true
}

Write-Host "Monitoring $WatchFolder for changes... Press CTRL+C to stop." -ForegroundColor Cyan

# Action to take when a file is created or changed
$Action = {
    $Path = $Event.SourceEventArgs.FullPath
    $Name = $Event.SourceEventArgs.Name
    $ChangeType = $Event.SourceEventArgs.ChangeType
    
    Write-Host "Change detected: $Name ($ChangeType). Syncing..." -ForegroundColor Yellow
    
    # Copy the file to Google Drive (Overwrites if exists)
    Copy-Item -Path $Path -Destination $DestinationFolder -Force
}

# Link the events to the action
Register-ObjectEvent $Watcher "Changed" -Action $Action
Register-ObjectEvent $Watcher "Created" -Action $Action

# Keep the script running
while ($true) { sleep 5 }