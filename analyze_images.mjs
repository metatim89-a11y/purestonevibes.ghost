/**
 * analyze_images.mjs
 * 
 * Script to analyze each gemstone sculpture image using the Gemini AI vision API.
 * For each image it identifies:
 *  1. The gemstone type forming the leaflets/canopy
 *  2. The base material
 *  3. The wire type/specialty
 *
 * Usage: node analyze_images.mjs
 * Requires: GEMINI_API_KEY environment variable or a .env file.
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import { readFileSync, readdirSync, writeFileSync } from "fs";
import { join, extname, basename } from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";
import * as dotenv from "dotenv";
dotenv.config();

// --- Configuration ---
const PICS_DIR = "namedpics";
const OUTPUT_FILE = "inventory_ai_analyzed.json";
const API_KEY = process.env.GEMINI_API_KEY;

if (!API_KEY) {
    console.error("❌ ERROR: GEMINI_API_KEY not found in environment or .env file.");
    console.error("   Please add GEMINI_API_KEY=your_key_here to your .env file and re-run.");
    process.exit(1);
}

// --- Gemini Client Setup ---
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

/**
 * Converts a local image file to a Gemini-compatible inline data part.
 * @param {string} filePath - Absolute path to the image file.
 * @returns {{ inlineData: { data: string, mimeType: string } }}
 */
function imageToGenerativePart(filePath) {
    const ext = extname(filePath).toLowerCase().replace(".", "");
    const mimeMap = {
        jpg: "image/jpeg",
        jpeg: "image/jpeg",
        png: "image/png",
        jfif: "image/jpeg",
        webp: "image/webp",
    };
    const mimeType = mimeMap[ext] || "image/jpeg";
    const data = readFileSync(filePath).toString("base64");
    return { inlineData: { data, mimeType } };
}

/**
 * Analyzes a single image through the Gemini Vision API to extract gemstone data.
 * @param {string} imagePath - Full path to the image file.
 * @param {string} imageName - Just the filename for metadata.
 * @param {number} index - 1-based index for this sculpture.
 * @returns {Promise<object>} - Parsed JSON result from Gemini.
 */
async function analyzeImage(imagePath, imageName, index) {
    const imagePart = imageToGenerativePart(imagePath);

    const prompt = `
You are an expert gemologist analyzing a handcrafted wire-wrapped gemstone sculpture tree.
Examine this image carefully and identify the following details purely from what you can visually observe.
Do not guess based on any name. Use only what you can see.

Return ONLY a valid JSON object in this exact format (no markdown, no explanation):
{
  "leaflet_gemstone": "Name of the primary gemstone forming the leaves or canopy of the tree. Be specific about the type based on color, transparency, luster, and crystal structure visible (e.g. Amethyst, Rose Quartz, Green Aventurine, Tiger Eye, Malachite, Labradorite).",
  "base_material": "Description of the base material or stone the tree is anchored in (e.g. Raw Amethyst Geode, Clear Quartz Cluster, Polished Agate Slice, Natural Driftwood, Polished Malachite Sphere).",  
  "wire_specialty": "Identify the wire material by its visible color and finish (e.g. Raw Copper, Tarnish-Resistant Copper, Silver-Plated Copper, 18k Gold-Plated Copper).",
  "color_palette": "2-3 dominant colors you can see in the sculpture (e.g. Deep Purple, Soft Pink, Forest Green).",
  "notes": "Any other visually distinctive detail about this sculpture worth noting."
}
`;

    const result = await model.generateContent([prompt, imagePart]);
    const responseText = result.response.text().replace(/```json|```/g, "").trim();

    try {
        return JSON.parse(responseText);
    } catch (e) {
        console.warn(`  ⚠️  Could not parse JSON for ${imageName}, raw response:\n${responseText}`);
        return {
            leaflet_gemstone: "Unknown",
            base_material: "Unknown",
            wire_specialty: "Unknown",
            color_palette: "",
            notes: responseText,
        };
    }
}

// --- Main ---
async function main() {
    const SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".jfif"];

    // Get all image files, sorted
    const allFiles = readdirSync(PICS_DIR)
        .filter((f) => SUPPORTED_EXTS.includes(extname(f).toLowerCase()))
        .sort();

    console.log(`\n🔍 Found ${allFiles.length} images in ${PICS_DIR}/`);
    console.log("📡 Starting AI analysis via Gemini Vision...\n");

    const inventory = [];
    let counter = 1;

    for (const fileName of allFiles) {
        const filePath = join(PICS_DIR, fileName);
        process.stdout.write(`  [${counter}/${allFiles.length}] Analyzing ${fileName}... `);

        try {
            const data = await analyzeImage(filePath, fileName, counter);

            inventory.push({
                id: `item-${counter}`,
                name: `Sculpture ${counter}`,
                slug: `sculpture-${counter}`,
                primary_image: `namedpics/${fileName}`,
                leaflet_gemstone: data.leaflet_gemstone,
                base_material: data.base_material,
                wire_specialty: data.wire_specialty,
                color_palette: data.color_palette,
                notes: data.notes,
                price: 150,
                status: "available",
            });

            console.log(`✅ ${data.leaflet_gemstone} / ${data.base_material} / ${data.wire_specialty}`);
        } catch (err) {
            console.error(`❌ Error: ${err.message}`);
            inventory.push({
                id: `item-${counter}`,
                name: `Sculpture ${counter}`,
                slug: `sculpture-${counter}`,
                primary_image: `namedpics/${fileName}`,
                leaflet_gemstone: "Error",
                base_material: "Error",
                wire_specialty: "Error",
                color_palette: "",
                notes: err.message,
                price: 150,
                status: "available",
            });
        }

        counter++;

        // Small delay to avoid rate limits
        await new Promise((res) => setTimeout(res, 500));
    }

    writeFileSync(OUTPUT_FILE, JSON.stringify(inventory, null, 2));
    console.log(`\n✨ Analysis complete! ${inventory.length} sculptures catalogued.`);
    console.log(`📄 Results saved to: ${OUTPUT_FILE}`);
}

main().catch(console.error);
