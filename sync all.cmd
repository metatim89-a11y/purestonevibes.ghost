@echo off
:: ============================================================
:: WINDOWS SECTION (PowerShell)
:: ============================================================
echo [System] Attempting Windows PowerShell Sync...

powershell -ExecutionPolicy Bypass -Command "& {
    $Watch = 'C:\Users\Customer\Desktop\fishesstonevibeexample10mins';
    $Dest = 'G:\My Drive\Backups';
    if (!(Test-Path $Watch)) { exit 1 }
    Write-Host 'Monitoring: $Watch';
    $w = New-Object IO.FileSystemWatcher $Watch -Property @{IncludeSubdirectories=$true;EnableRaisingEvents=$true};
    Register-ObjectEvent $w 'Changed' -Action { Copy-Item $Event.SourceEventArgs.FullPath 'G:\My Drive\Backups' -Force; Write-Host 'Synced' };
    while($true) { sleep 5 }
}"

:: If PowerShell fails (exit code not 0), move to Bash/WSL
if %ERRORLEVEL% NEQ 0 (
    echo [System] PowerShell failed or folder not found. 
    echo [System] Switching to WSL/Debian (Bash)...
    
    wsl bash -c "
        WATCH_DIR='/mnt/c/Users/Customer/Desktop/fishesstonevibeexample10mins'
        DEST_DIR='/mnt/g/My Drive/Backups'
        
        if [ ! -d \"\$WATCH_DIR\" ]; then
            echo 'Error: Local folder not found in WSL path.'
            exit 1
        fi

        echo 'Monitoring via WSL: \$WATCH_DIR'
        # Check if inotify-tools is installed
        if ! command -v inotifywait &> /dev/null; then
            echo 'Installing inotify-tools...'
            sudo apt update && sudo apt install -y inotify-tools
        fi

        while inotifywait -re modify,create,delete \"\$WATCH_DIR\"; do
            rsync -av --delete \"\$WATCH_DIR/\" \"\$DEST_DIR/\"
            echo 'WSL Sync Complete: \$(date)'
        done
    "
)

pause