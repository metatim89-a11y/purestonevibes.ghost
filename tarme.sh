tar -czvf snapshot_$(date +%Y-%m-%d_%H%M).tar.gz --exclude=".git" --exclude="node_modules" --exclude="*.tar.gz" .
