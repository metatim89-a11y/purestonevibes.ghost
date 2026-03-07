import csv
import re
import os

# Stone Energy Mapping
stone_meanings = {
    "Amethyst": "Intuition, Calm",
    "Moonstone": "New Beginnings",
    "Rose Quartz": "Love, Compassion",
    "Clear Quartz": "Amplification, Clarity",
    "Green Jade": "Luck, Prosperity",
    "Jade": "Luck, Prosperity",
    "Green Aventurine": "Opportunity, Optimism",
    "Aventurine": "Opportunity",
    "Malachite": "Transformation",
    "Obsidian": "Protection, Grounding",
    "Black Tourmaline": "Protection",
    "Purple Fluorite": "Focus, Order",
    "Jasper": "Nurturing, Grounding",
    "Red Jasper": "Endurance, Grounding",
    "Turquoise": "Wholeness, Truth",
    "Wire Root": "Grounding Stability",
    "Selenite": "Cleansing, Peace",
    "Lapis Lazuli": "Wisdom, Truth",
    "Tiger's Eye": "Protection, Willpower",
    "Pink Agate": "Stability, Composure",
    "Citrine": "Abundance, Joy",
    "Rhodonite": "Emotional Healing",
    "Calcite": "Energy, Cleansing",
    "Carnelian": "Creativity, Motivation",
    "Unakite": "Vision, Balance",
    "Apatite": "Manifestation, Service",
    "Sodalite": "Insight, Clarity"
}

def get_stone_name(text):
    # Extract stone name from "Stone Name (value)" format
    match = re.match(r"^(.*?)\s*\(", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def get_energy_desc(base_raw, leaf_raw, wrapping_raw):
    base_stone = get_stone_name(base_raw)
    leaf_stone = get_stone_name(leaf_raw)

    base_meaning = stone_meanings.get(base_stone, "Grounding")
    leaf_meaning = stone_meanings.get(leaf_stone, "Growth")

    # Wrapping complexity map to labor/craftsmanship description
    # Based on the user's manual example: "High labor root-wrap on raw stone."
    if "(low)" in wrapping_raw.lower():
        labor = "Standard root-wrap"
    elif "(med)" in wrapping_raw.lower():
        labor = "Intricate root-wrap"
    elif "(high)" in wrapping_raw.lower():
        labor = "Masterwork high-labor wrap"
    else:
        labor = "Root-wrap"

    # Pairing logic (themes)
    theme = "Harmonic Pairing"
    if any(m in leaf_meaning for m in ["Love", "Compassion"]):
        theme = "Heart Pairing"
    elif any(m in leaf_meaning for m in ["Luck", "Prosperity", "Abundance"]):
        theme = "Abundance Pairing"
    elif any(m in leaf_meaning for m in ["Intuition", "Wisdom", "Focus"]):
        theme = "Insight Pairing"
    elif any(m in base_meaning for m in ["Protection", "Grounding"]):
        theme = "Stability Pairing"

    # Construction of the final description
    description = f"{theme}: {leaf_stone} for {leaf_meaning.lower()} + {base_stone} for {base_meaning.lower()}. {labor} on raw stone."
    return description

input_file = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\orig folder\renamed\tree_data.csv'
output_file = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\orig folder\renamed\tree_data_updated.csv'

try:
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            base = row['BaseStone (v)']
            leaf = row['LeafStone (v)']
            wrapping = row['Wrapping (v)']

            new_desc = get_energy_desc(base, leaf, wrapping)
            row['Combined together energy use'] = new_desc
            writer.writerow(row)

    print(f"CSV update complete. Saved to {output_file}")
    
    # Optional: Replace the original file if requested, but for now we keep the updated one separate for verification
    # os.replace(output_file, input_file)

except Exception as e:
    print(f"Error: {e}")
