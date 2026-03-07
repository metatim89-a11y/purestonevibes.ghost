# Pure Stone Vibes | Project Overview

A high-aesthetic, minimalist portfolio website for **Pure Stone Vibes**, showcasing unique wire-wrapped gemstone sculptures handcrafted by artist **Fish** in Texas.

## Project Type
**Dynamic Static Web Portfolio / Asset Repository**

## Technology Stack
- **Frontend:** HTML5, Tailwind CSS (via CDN)
- **Typography:** Google Fonts (`Playfair Display`, `Inter`)
- **Aesthetic:** Minimalist dark mode, glassmorphism, pink accents (`#ec4899`)
- **Data Handling:** JSON-driven dynamic rendering (JavaScript)

## Directory Structure
- `index.html`: Main landing page with hero section and featured series preview.
- `gallery.html`: The principal inventory display (The Grove), featuring dynamic sorting and 28+ unique pieces.
- `process.html`: Artistic statement and detailed craftsmanship walkthrough.
- `inquiry.html`: Dynamic contact form with pre-selected item synchronization.
- `namedpics/`: The master repository of high-resolution sculpture images (28 verified assets).
- `inventory_final.json`: The source of truth for all gemstone sculpture metadata, prices, and energetic pairings.
- `*.jfif`: Key layout/branding images (1-4) used for specific site sections.
- `orig folder/`: Contains original raw source data and images.

## Key Features & Sections
- **The Grove (Gallery):** A high-aesthetic dynamic grid displaying the full collection. Features a **staggered layout** (alternating name placement) and **neon-glow graphic typography** for sculpture names. Includes price filtering and stone energy descriptions.
- **The Process:** Highlights the "Root-to-Canopy" technique and the hand-wiring of gemstone leaflets.
- **Dynamic Inquiries:** Form pre-population allowing users to inquire about specific sculptures directly from the gallery.

## Usage & Development
- **Inventory Updates**: To add or edit sculptures, update the `inventory` object in both `gallery.html` and `inquiry.html` (or modify `inventory_final.json` and sync).
- **Image Management**: New images should be added to `namedpics/` using the `Name_Number.ext` convention for SEO and system compatibility.
- **Styling**: All pages use a shared design language of glassmorphism panels, blurry radial backgrounds, and Playfair Display typography. The gallery uses a specialized `.graphic-text` class for high-impact neon-glow headers.

## Development Conventions
- **Self-Documenting Code**: All functions, classes, and scripts MUST include detailed comments explaining *what* the code is doing and *why* it exists.
- **Visual Consistency**: Maintain the high-contrast dark theme and pink accentuation throughout all new components.
- **Naming Protocol**: Gemstone sculpture imagery must retain descriptive naming for clarity and search engine optimization.

## Collaboration & Task Management
- **One Task at a Time**: Complete the current objective fully before moving to a new one.
- **Focus Protocol**: If a new task is suggested mid-flight, kindly remind the user and make a note to address it immediately after the current task is finalized.
- **Approval Protocol**: Only make changes that have been explicitly discussed and approved. If a better approach or improvement is identified, inform the user and allow them to decide on implementation before proceeding.
