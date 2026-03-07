const fs = require('fs');
const path = require('path');

const versionFile = path.join(__dirname, 'netlify', 'version.json');

let data = { version: "1.000" };
if (fs.existsSync(versionFile)) {
    try {
        data = JSON.parse(fs.readFileSync(versionFile, 'utf8'));
    } catch (e) {
        console.error("Error parsing version.json", e);
    }
}

let currentVersion = parseFloat(data.version);
if (isNaN(currentVersion)) currentVersion = 1.000;

// Increment by 0.001
currentVersion += 0.001;

// Format to 3 decimal places
data.version = currentVersion.toFixed(3);

fs.writeFileSync(versionFile, JSON.stringify(data, null, 2));
console.log(`Version incremented to ${data.version}`);
