#!/bin/bash
# This file defines the 'anotherone' git-sync function and the 'ano1' alias.
# To use them, load this file into your current shell session by running:
#
#    source vibe_commands.sh
#
# After that, you can use the 'ano1' command directly.

# This function automates the process of staging, committing with an incrementing
# version number, and syncing with the remote repository.
anotherone() {
    # --- Helper function to get the next version number ---
    get_next_version() {
        # Find the most recent commit message matching 'anotherone(XXX)'
        last_commit_msg=$(git log -1 --grep="^anotherone(" --pretty=%B)

        if [ -z "$last_commit_msg" ]; then
            # If no previous commit is found, start the count at 1.
            echo "001"
        else
            # Extract the number, increment it, and format with leading zeros.
            last_version=$(echo "$last_commit_msg" | grep -o -E '\(([0-9]+)\)' | tr -d '()')
            next_version=$((10#$last_version + 1)) # Use 10# to force base-10
            printf "%03d" "$next_version"
        fi
    }

    # --- Main function execution ---
    # Ensure we are inside a git repository.
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        echo "Error: This is not a git repository."
        return 1 # Use 'return' in functions
    fi

    # Generate the next commit message.
    next_version_num=$(get_next_version)
    commit_message="anotherone($next_version_num)"

    echo "--> Staging all changes..."
    git add .

    echo "--> Committing with message: $commit_message"
    git commit -m "$commit_message"

    echo "--> Syncing with remote repository..."
    # Pull the latest changes with rebase, then push.
    # If the pull fails due to conflicts, the script will stop.
    if git pull --rebase; then
        git push
        echo "✅ Sync complete. The vibes are aligned."
    else
        echo "⚠️ Pull failed, likely due to merge conflicts. Please resolve them and then run 'git push'."
        return 1
    fi
}

# Create the 'ano1' alias for the 'anotherone' function.
alias ano1='anotherone'

echo "✅ 'anotherone' function and 'ano1' alias are now loaded."
echo "You can now use the 'ano1' command."
