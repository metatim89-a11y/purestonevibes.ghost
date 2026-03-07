/**
 * analyze_gems.js - Pure CommonJS version (no ESM)
 * Analyzes each namedpics image with Gemini Vision AI
 * to identify gemstone types and wire specialties from scratch.
 */

const fs = require("fs");
const path = require("path");

// Load .env manually (avoid ESM import issues)
try {
    const envFile = fs.readFileSync(path.join(__dirname, ".env"), "utf8");
    envFile.split(/\r?\n/).forEach((line) => {
        const [key, ...val] = line.split("=");
        if (key && val.length) process.env[key.trim()] = val.join("=").trim();
    });
} catch (e) {
    console.error("Could not read .env:", e.message);
}

const { GoogleGenerativeAI } = require("@google/generative-ai");

const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
    console.error("ERROR: GEMINI_API_KEY not found in .env file.");
    process.exit(1);
}

const genAI = new GoogleGenerativeAI(API_KEY);
// gemini-1.5-flash has a separate free-tier quota from gemini-2.0-flash
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const PICS_DIR = path.join(__dirname, "namedpics");
const OUTPUT_FILE = path.join(__dirname, "inventory_ai_analyzed.json");
const SUPPORTED = [".jpg", ".jpeg", ".png", ".jfif"];

function toInlinePart(filePath) {
    const ext = path.extname(filePath).toLowerCase().replace(".", "");
    const mimeMap = { jpg: "image/jpeg", jpeg: "image/jpeg", png: "image/png", jfif: "image/jpeg" };
    return {
        inlineData: {
            data: fs.readFileSync(filePath).toString("base64"),
            mimeType: mimeMap[ext] || "image/jpeg",
        },
    };
}

/**
 * Retries a function with exponential backoff if it fails with a 429 rate limit error.
 * @param {Function} fn - Async function to retry.
 * @param {number} maxRetries - Maximum number of retries.
 * @returns {Promise<any>}
 */
async function withRetry(fn, maxRetries = 5) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (err) {
            const is429 = err.message && err.message.includes("429");
            if (is429 && attempt < maxRetries) {
                const waitMs = Math.pow(2, attempt) * 5000; // 10s, 20s, 40s, 80s
                process.stdout.write(`\n      ⏳ Rate limited. Waiting ${waitMs / 1000}s before retry ${attempt}/${maxRetries}... `);
                await new Promise((r) => setTimeout(r, waitMs));
            } else {
                throw err;
            }
        }
    }
}

async function analyzeImage(filePath, name) {
    const prompt = `You are an expert gemologist. Look at this handcrafted wire-wrapped gemstone sculpture tree.
Identify the following purely from visual inspection. Do NOT guess from names.
Return ONLY valid JSON, no markdown:
{
  "leaflet_gemstone": "The gemstone making up the leaves/canopy (e.g. Amethyst, Rose Quartz, Green Aventurine, Tiger Eye, Malachite). Be specific based on color, luster, transparency.",
  "base_material": "The stone or material the tree sits on (e.g. Raw Amethyst Geode, Clear Quartz Cluster, Polished Agate Slice, Driftwood).",
  "wire_specialty": "Wire color and probable material (e.g. Raw Copper, Tarnish-Resistant Copper, Silver-Plated Copper, Gold-Plated Copper).",
  "color_palette": "2-3 dominant colors in the sculpture (e.g. Deep Purple, Warm Gold, Emerald Green).",
  "notes": "Any other visually distinctive feature worth recording."
}`;

    const result = await withRetry(() => model.generateContent([prompt, toInlinePart(filePath)]));
    const raw = result.response.text().replace(/```json|```/g, "").trim();
    try {
        return JSON.parse(raw);
    } catch {
        return { leaflet_gemstone: "Parse Error", base_material: "Unknown", wire_specialty: "Unknown", color_palette: "", notes: raw };
    }
}

async function main() {
    const files = fs
        .readdirSync(PICS_DIR)
        .filter((f) => SUPPORTED.includes(path.extname(f).toLowerCase()))
        .sort();

    console.log(`\n🔍 Found ${files.length} images in namedpics/`);
    console.log(`📡 Starting Gemini Vision AI analysis...\n`);

    const inventory = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const filePath = path.join(PICS_DIR, file);
        process.stdout.write(`  [${i + 1}/${files.length}] ${file} ... `);

        try {
            const data = await analyzeImage(filePath, file);
            console.log(`✅ ${data.leaflet_gemstone} | ${data.base_material} | ${data.wire_specialty}`);

            inventory.push({
                id: `item-${i + 1}`,
                name: `Sculpture ${i + 1}`,
                slug: `sculpture-${i + 1}`,
                primary_image: `namedpics/${file}`,
                leaflet_gemstone: data.leaflet_gemstone,
                base_material: data.base_material,
                wire_specialty: data.wire_specialty,
                color_palette: data.color_palette,
                notes: data.notes,
                price: 150,
                status: "available",
            });
        } catch (err) {
            console.log(`❌ Error: ${err.message}`);
            inventory.push({
                id: `item-${i + 1}`,
                name: `Sculpture ${i + 1}`,
                slug: `sculpture-${i + 1}`,
                primary_image: `namedpics/${file}`,
                leaflet_gemstone: "Error",
                base_material: "Error",
                wire_specialty: "Error",
                color_palette: "",
                notes: err.message,
                price: 150,
                status: "available",
            });
        }

        // 2s delay between requests to stay well within free-tier rate limits
        await new Promise((r) => setTimeout(r, 2000));
    }

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(inventory, null, 2));
    console.log(`\n✨ Done! ${inventory.length} sculptures analyzed.`);
    console.log(`📄 Saved to: ${OUTPUT_FILE}`);
}

main().catch(console.error);
