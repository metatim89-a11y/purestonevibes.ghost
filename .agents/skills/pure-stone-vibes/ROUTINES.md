---
name: Pure Stone Vibes | Deployment, Logging & Routine Management
description: Detailed procedures for infrastructure maintenance, observability levels, and automated system routines.
---

# Infrastructure & Routine Management

## 1. System Logging Architecture
The project uses a multi-tiered logging strategy to monitor backend health and file synchronization events.

### Observability Levels
- **DEBUG**: Verbose details for internal troubleshooting (e.g., specific file watcher events in `scribe.py`).
- **INFO**: Standard operational events (e.g., successful API requests, static file delivery, WebSocket connections).
- **WARNING**: Non-critical anomalies (e.g., failed static file requests, 304 cache hits that might indicate staleness).
- **ERROR**: Critical failures (e.g., Database connection errors, inquiry submission failures).
- **CRITICAL**: System-level outages needing immediate intervention.

### Primary Log Files
- `scribe.log`: The central repository for FastAPI application logs and operational metrics.
- `startuplog.log`: Captures deployment-time events from the `deploy.sh` routine.
- `server.log`: Raw stdout/stderr from the Uvicorn process.

## 2. Automated Routines

### Vibe Scribe (`scribe.py`)
A custom Python-based watcher that ensures the remote GitHub repository is always in sync with local high-aesthetic changes.
- **Trigger**: Watches for changes in `.html`, `.css`, `.js`, `.json`, `.py`, and `.db` files.
- **Debounce**: Waits 5 seconds after the last detected change to prevent redundant pushes.
- **Action**: Executes the `./syv` script (Sync Your Vibe) to push updates.

### System Health Sync (`main.py`)
The FastAPI backend maintains a live "Pulse" via WebSockets.
- **Health Check**: Every new WebSocket connection triggers an immediate validation of the SQLite database (`inquiries.db`) and the Inventory integrity (`inventory_final.json`).
- **Real-time Errors**: System-level exceptions are broadcast instantly to the `dashboard.html` (the "Splat" page) for visual monitoring.

## 3. Deployment Routines

### The "Pulse" Launch (`deploy.sh`)
Standard procedure for starting the dynamic backend:
1. **Clean**: Kills existing processes on Port 8000.
2. **Setup**: Validates/creates the `venv` and installs dependencies.
3. **Ghost Mode**: Launches Uvicorn via `nohup` to ensure the server persists after the terminal closes.

### G-Drive Mirroring (`sync all.cmd`)
Automated backup routine for Windows:
- Registers a `FileSystemWatcher` to mirror the entire project to Google Drive (`G:\My Drive`).
- Runs in a persistent loop to ensure total redundancy of high-resolution sculpture assets.

---

# Note on GEMINI.md
The `GEMINI.md` file in the root directory is now a **legacy reference**. All operational truth and development rules have been moved to these specialized **Skills**. Use `GEMINI.md` only for high-level project branding or as a "Quick Start" for human developers who are not using the Agentic Skill system.
