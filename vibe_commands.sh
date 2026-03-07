#!/bin/bash
# This file defines the 'anotherone' git-sync function and the 'ano1' alias,
# as well as the 'run_vibe_server' function and 'startvibe' alias.
# To use them, load this file into your current shell session by running:
#
#    source vibe_commands.sh
#
# After that, you can use the 'ano1' and 'startvibe' commands directly.

# --- Git Sync Function and Alias ---
# This function automates the process of staging, committing with an incrementing
# version number, and syncing with the remote repository.
anotherone() {
    # --- Helper function to get the next version number ---
    get_next_version() {
        last_commit_msg=$(git log -1 --grep="^anotherone(" --pretty=%B)
        if [ -z "$last_commit_msg" ]; then
            echo "001"
        else
            last_version=$(echo "$last_commit_msg" | grep -o -E '\(([0-9]+)\)' | tr -d '()')
            next_version=$((10#$last_version + 1))
            printf "%03d" "$next_version"
        fi
    }

    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        echo "Error: This is not a git repository."
        return 1
    fi

    next_version_num=$(get_next_version)
    commit_message="anotherone($next_version_num)"

    echo "--> Staging all changes..."
    git add .

    echo "--> Committing with message: $commit_message"
    git commit -m "$commit_message"

    echo "--> Syncing with remote repository..."
    if git pull --rebase; then
        git push
        echo "✅ Sync complete. The vibes are aligned."
    else
        echo "⚠️ Pull failed, likely due to merge conflicts. Please resolve them and then run 'git push'."
        return 1
    fi
}
alias ano1='anotherone'

# --- Server Run Function and Alias ---
# This function stops any running servers, activates venv, installs dependencies,
# and runs main.py while logging all output to 'startuplog.log' AND echoing to the terminal.
run_vibe_server() {
    local log_file="startuplog.log"
    echo "--> All server output will be logged to: $log_file (and echoed to terminal)"
    # Overwrite the log file for a clean start on each run.
    > "$log_file"

    # Check for and kill any existing instances of the server process.
    echo "--> Checking for and stopping any existing server processes..." | tee -a "$log_file"
    # Use a variable for the process name to avoid repetition
    local server_process_name="python3.3 main.py|python3 main.py"
    if pkill -f "$server_process_name"; then
        echo "--> Existing server processes stopped." | tee -a "$log_file"
        sleep 1 # Give a moment for the port to be released.
    else
        echo "--> No existing server process found." | tee -a "$log_file"
    fi

    local venv_activated=0
    # Activate the virtual environment if it exists.
    if [ -f "./venv/bin/activate" ]; then
        echo "--> Activating virtual environment..." | tee -a "$log_file"
        source "./venv/bin/activate"
        venv_activated=1
    else
        echo "--> No virtual environment found at ./venv/bin/activate. Proceeding without." | tee -a "$log_file"
    fi

    # --- Install/Update Python Dependencies ---
    if [ "$venv_activated" -eq 1 ]; then
        echo "--> Installing/Updating Python dependencies from requirements.txt..." | tee -a "$log_file"
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt 2>&1 | tee -a "$log_file"
            if [ ${PIPESTATUS[0]} -ne 0 ]; then # Check pip's exit code, not tee's
                echo "Error: Failed to install Python dependencies. Aborting." | tee -a "$log_file"
                deactivate
                return 1
            fi
        else
            echo "Warning: requirements.txt not found. Skipping dependency installation." | tee -a "$log_file"
        fi
    else
        echo "--> Virtual environment not activated, skipping dependency installation." | tee -a "$log_file"
    fi

    # --- Find correct Python command ---
    local python_cmd=""
    if command -v python3.3 &>/dev/null; then
        python_cmd="python3.3"
    elif command -v python3 &>/dev/null; then
        python_cmd="python3"
        echo "--> Note: python3.3 not found. Falling back to 'python3'." | tee -a "$log_file"
    fi

    # --- Start Server ---
    if [ -n "$python_cmd" ]; then
        echo "--> Starting FastAPI server with '$python_cmd'..." | tee -a "$log_file"
        echo "Access the app at: http://localhost:8000"
        echo "Press Ctrl+C to stop the server."
        echo "You can monitor the server's activity by running: tail -f $log_file"

        # Execute the server using the found python command
        $python_cmd main.py 2>&1 | tee -a "$log_file"
    else
        echo "Error: Neither 'python3.3' nor 'python3' were found. Please install Python 3." | tee -a "$log_file"
        if [ "$venv_activated" -eq 1 ]; then deactivate; fi
        return 1
    fi

    echo "--> Server stopped." | tee -a "$log_file"
    # Deactivate the virtual environment if it was activated by this function.
    if [ "$venv_activated" -eq 1 ]; then
        echo "--> Deactivating virtual environment." | tee -a "$log_file"
        deactivate
    fi
}
alias startvibe='run_vibe_server'

echo "✅ 'anotherone' and 'run_vibe_server' functions, along with 'ano1' and 'startvibe' aliases, are now loaded."
echo "You can now use the 'ano1' and 'startvibe' commands."
