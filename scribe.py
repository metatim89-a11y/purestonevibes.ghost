import os
import time
import subprocess
from datetime import datetime

# --- Pure Stone Vibes "Scribe" Auto-Pusher ---
# Watches for local file changes and automatically runs ./syv

WATCH_EXTENSIONS = ('.html', '.css', '.js', '.json', '.py', '.db')
IGNORE_DIRS = ('venv', '.git', '__pycache__', 'node_modules')
DEBOUNCE_SECONDS = 5 # Wait 5 seconds after the last change before pushing

def get_last_mtime():
    max_mtime = 0
    for root, dirs, files in os.walk('.'):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(WATCH_EXTENSIONS):
                try:
                    mtime = os.path.getmtime(os.path.join(root, file))
                    if mtime > max_mtime:
                        max_mtime = mtime
                except OSError:
                    continue
    return max_mtime

def log_scribe(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}"
    with open('logs/scribe_vibe.log', 'a', encoding='utf-8') as f:
        f.write(entry + '\n')
    print(entry)

def sync_to_github():
    log_scribe("✍️  New vibration detected. Scribing to GitHub...")
    try:
        # Run your existing syv script
        subprocess.run(['./syv'], check=True)
        print("Done.")
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    print("--- VIBE SCRIBE ACTIVE: Watching for local changes ---")
    last_known_mtime = get_last_mtime()
    
    while True:
        time.sleep(1) # Check every second
        current_mtime = get_last_mtime()
        
        if current_mtime > last_known_mtime:
            # Wait a few seconds for other potential changes (debounce)
            time.sleep(DEBOUNCE_SECONDS)
            sync_to_github()
            last_known_mtime = get_last_mtime()
