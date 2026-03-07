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

const sqlite3 = require('sqlite3').verbose();

// Initialize DB
const dbPath = path.join(__dirname, 'inquiries.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error('Could not connect to database:', err);
    else console.log('Connected to SQLite database.');
});

// Create inquiries table if it doesn't exist
db.run(`
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        sculpture TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
`);

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
 * Handles new gemstone inquiries from the user and saves to DB.
 */
app.post('/api/inquiry', (req, res) => {
    const { name, email, sculpture, message } = req.body;
    console.log('New Inquiry Received:', { name, email, sculpture });

    db.run(
        `INSERT INTO inquiries (name, email, sculpture, message) VALUES (?, ?, ?, ?)`,
        [name, email, sculpture, message],
        function (err) {
            if (err) {
                console.error("Database error:", err);
                return res.status(500).json({ error: "Failed to save inquiry." });
            }
            res.status(200).json({
                message: 'Inquiry received successfully! Fish will connect with you soon.',
                reference: `PSV-${this.lastID}-${Math.floor(Math.random() * 1000)}`
            });
        }
    );
});

/**
 * GET /api/inquiries
 * Returns all inquiries for the dashboard.
 * In a real app we would protect this with JWT auth.
 */
app.get('/api/inquiries', (req, res) => {
    // For demo simplicity, we just rely on the frontend login check 
    // (though real security needs backend token verification)
    db.all(`SELECT * FROM inquiries ORDER BY created_at DESC`, [], (err, rows) => {
        if (err) {
            console.error("Database error:", err);
            return res.status(500).json({ error: "Failed to fetch inquiries." });
        }
        res.json(rows);
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
