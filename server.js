const express = require('express');
const path = require('path');
const cors = require('cors');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from the 'netlify' folder (our web root)
// This keeps the directory structure lean and compatible with past work.
app.use(express.static(path.join(__dirname, 'netlify')));

// --- API Endpoints ---

/**
 * GET /api/inventory
 * Serves the master list of gemstone sculptures.
 * Why: Centralizing this makes global updates instant.
 */
app.get('/api/inventory', (req, res) => {
    const inventoryPath = path.join(__dirname, 'inventory_final.json');
    fs.readFile(inventoryPath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading inventory:', err);
            return res.status(500).json({ error: 'Failed to load inventory' });
        }
        res.json(JSON.parse(data));
    });
});

/**
 * POST /api/inquiry
 * Handles new gemstone inquiries from the user.
 */
app.post('/api/inquiry', (req, res) => {
    const inquiryData = req.body;
    console.log('New Inquiry Received:', inquiryData);

    // In a real production app, we would save this to a database or send an email.
    // For now, we simulate success for the demo.
    res.status(200).json({
        message: 'Inquiry received successfully! Fish will connect with you soon.',
        reference: `PSV-${Math.floor(Math.random() * 10000)}`
    });
});

// Fallback to index.html for SPA-like behavior (optional, but good for cleanliness)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'netlify', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`
🚀 Pure Stone Vibes Backend Running
📡 API: http://localhost:${PORT}/api/inventory
🌐 Web: http://localhost:${PORT}
    `);
});
