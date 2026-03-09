---
name: Pure Stone Vibes Development
description: Guidelines, aesthetic requirements, and codebase conventions for the Pure Stone Vibes dynamic static portfolio.
---

# Pure Stone Vibes Core Directive
You are the developer for the "Pure Stone Vibes" minimalist portfolio site featuring handcrafted gemstone sculptures. Your primary objective is maintaining a high-aesthetic, minimalist dark-mode experience with flawless glassmorphism and pink accents (#ec4899).

## 1. Project Architecture & State
This is a **Dynamic Static Web App**. 
- Logic is driven entirely by vanilla JavaScript parsing JSON data.
- Layouts are powered by Tailwind CSS (via CDN) and Vanilla CSS.
- The single source of truth for the inventory is `inventory_final.json`. ANY updates to gallery pieces MUST align with this JSON structure.

## 2. Aesthetic & UI Requirements
Whenever building new components or modifying existing ones, you MUST strictly adhere to:
- **Color Palette & Theme**: Deep, high-contrast Dark Mode with blurred radial backgrounds. Use `#ec4899` exclusively for prominent accentuation.
- **Typography:** `Playfair Display` for elegant headings and `.graphic-text` elements; `Inter` for clean, readable body paragraphs.
- **The "Neon Glow":** The Gallery (The Grove) uses a specific `.graphic-text` class for sculpture titles. Do not attempt to style this with Tailwind—use the existing custom CSS to maintain the ethereal glow effect.
- **Layouts**: Employ "staggered" layout designs where appropriate, leaning into glassmorphic cards (`backdrop-blur`, subtle semi-transparent borders).

## 3. Data & Asset Management
- **Image Referencing**: All sculpture assets must live in `namedpics/` and follow the SEO-optimized naming convention: `Name_Number.ext`. Example: `Amethyst_Grove_01.jfif`. 
- **Inventory Syncing**: `inventory` objects in `gallery.html` and `inquiry.html` must remain in absolute sync. Whenever one is touched, the other must be validated against `inventory_final.json`.

## 4. Development Constraints & Approvals
- **Strict Working Context**: Be hyper-aware of your environment directory (e.g. `netlify/` vs root folder). Never alter files residing outside your current requested scope. 
- **Self-Documenting Standard**: Any JS logic written (like gallery sorting or URI encoding for pre-filled inquiry forms) must contain explicit block comments detailing the *what* and *why*.
- **Task Singularity**: You must accomplish exactly **ONE task at a time**. Do not perform unauthorized file clean-ups or re-factoring while in the middle of a feature request.
- **Explicit Approval**: Before enacting an architectural shift (e.g. changing how JSON is fetched), you must propose the approach and await User approval.

## 5. File Overview
- `index.html`: Main landing page / Hero.
- `gallery.html`: Dynamic grid layout, staggered names, price filtering.
- `process.html`: Root-to-Canopy process showcase.
- `inquiry.html`: Contact form w/ URL parameter parsing to pre-select items.
- `namedpics/`: The master repository of high-resolution sculpture images (28 verified assets). Images here are strictly formatted as `Name_Number.ext`.
- `inventory_final.json`: The source of truth for all gemstone sculpture metadata, prices, and energetic pairings.
- `logs/gdrive_sync.log`: The dedicated capture point for Google Drive upload/sync errors.
- `launch_vibes.ps1`: Unified Windows PowerShell script to launch both the Backend and Scribe in background mode.
- `deploy.sh`: Script for launching the dynamic self-hosted FastAPI backend.
- `sync all.cmd`: Automated Windows synchronization script to backup the project to Google Drive.

## 6. Deployment & Syncing Strategies
### Netlify (Primary Frontend)
To deploy the static frontend, use the contents of the `netlify/` directory. This is the production-ready environment for the gallery and portfolio.
- **How to deploy**: Simply push changes to the repository linked to Netlify, or use the Netlify CLI to deploy from the `netlify/` folder.

### Self-Hosted Backend (FastAPI)
The site features a dynamic component for handling inquiries and potential server-side logic (e.g., `main.py`).
- **How to deploy**: Run `./deploy.sh` in a Linux/WSL environment. This creates a virtual environment, installs `requirements.txt`, and launches the uvicorn server on port 8000.

### Google Drive Redundancy (Backup)
To ensure no assets are lost, the project is mirrored to Google Drive.
- **How to deploy**: Run `sync all.cmd` on Windows. This script monitors the local directory and automatically copies changes to `G:\My Drive\fishesstonevibeexample10mins`.
- **Alternative**: Use `autoupdategdrive.ps1` for PowerShell-native watching and syncing.
