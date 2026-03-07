#!/bin/bash

# --- Pure Stone Vibes "Pulse" Auto-Updater ---
# This script polls GitHub for changes and updates the local server automatically.

CHECK_INTERVAL=300 # Check every 5 minutes (300 seconds)
BRANCH="master"

echo "--- PULSE UPDATER ACTIVE (Branch: $BRANCH) ---"

while true; do
    # 1. Fetch the latest state from GitHub
    git fetch origin $BRANCH > /dev/null 2>&1
    
    # 2. Compare local HEAD with remote branch
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$BRANCH)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$(date)] New vibration detected on GitHub. Updating local Grove..."
        
        # 3. Pull the changes
        git pull origin $BRANCH
        
        # 4. Run your deployment script to restart the server and update deps
        chmod +x deploy.sh
        ./deploy.sh
        
        echo "[$(date)] Update complete. Server is fresh."
    fi

    # Wait before next check
    sleep $CHECK_INTERVAL
done
