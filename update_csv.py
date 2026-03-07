import csv
import re

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
    
    # Wrapping complexity to labor description
    if "(low)" in wrapping_raw.lower():
        labor = "Standard root-wrap"
    elif "(med)" in wrapping_raw.lower():
        labor = "Intricate root-wrap"
    elif "(high)" in wrapping_raw.lower():
        labor = "Masterwork high-labor wrap"
    else:
        labor = "Root-wrap"

    # Construct the description
    # Example: "Abundance Pairing: Malachite for change + Jade for luck. High labor root-wrap on raw stone."
    
    # Determine a theme based on the combo (simple heuristic)
    theme = "Harmonic Pairing"
    if "Love" in leaf_meaning or "Heart" in leaf_meaning:
        theme = "Heart Pairing"
    elif "Prosperity" in leaf_meaning or "Abundance" in leaf_meaning:
        theme = "Abundance Pairing"
    elif "Intuition" in leaf_meaning or "Wisdom" in leaf_meaning:
        theme = "Insight Pairing"
    elif "Protection" in base_meaning or "Grounding" in base_meaning:
        theme = "Grounding Pairing"

    description = f"{theme}: {base_stone} for {base_meaning} + {leaf_stone} for {leaf_meaning}. {labor} on raw stone."
    return description

input_file = 'orig folder/renamed/tree_data.csv'
output_file = 'orig folder/renamed/tree_data_updated.csv'

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, 
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    # Update the header name for the energy column
    if "Combined together energy use" in fieldnames:
        # We will keep the old column name for the writer but change the content
        pass
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        base = row['BaseStone (v)']
        leaf = row['LeafStone (v)']
        wrapping = row['Wrapping (v)']
        
        new_desc = get_energy_desc(base, leaf, wrapping)
        row['Combined together energy use'] = new_desc
        writer.writerow(row)

print("CSV update complete.")
