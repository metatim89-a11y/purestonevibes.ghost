import json
import re

txt_file = 'fishestones (1).txt'
json_file = 'inventory_final.json'

mapping = {}
with open(txt_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines[2:]:
        parts = line.strip().split(',')
        if len(parts) >= 6:
            name = parts[0]
            base = parts[1]
            leaf = parts[3]
            purpose = parts[5]
            mapping[name] = {
                'base': base,
                'leaf': leaf,
                'energy': f"{purpose} Pairing: {leaf} for {purpose.lower()} + {base} for grounding."
            }

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for key, item in data.items():
    # extract base name: e.g. "Amethyst_Moon_Bonsai_1" -> "Amethyst_Moon_Bonsai"
    base_name = re.sub(r'_\d+$', '', key)
    
    if base_name in mapping:
        item['base'] = mapping[base_name]['base']
        item['leaf'] = mapping[base_name]['leaf']
        item['energy'] = mapping[base_name]['energy']
    else:
        # manual fixes for the ones not in the fishestones txt
        if base_name == "Amethyst_Moon_Bonsai":
            item['leaf'] = "Amethyst (med)"
            item['base'] = "Moonstone (high)"
            item['energy'] = "Harmonic Pairing: Amethyst for intuition + Moonstone for new beginnings."
        elif base_name == "Midnight_Shadow_Spire":
            item['leaf'] = "Black Tourmaline (high)"
            item['base'] = "Obsidian (high)"
            item['energy'] = "Stability Pairing: Black Tourmaline for protection + Obsidian for grounding."
        elif base_name == "Rose_Passion_Petite":
            item['leaf'] = "Rose Quartz (low)"
            item['base'] = "Pink Wire Root (low)"
            item['energy'] = "Heart Pairing: Rose Quartz for compassion."
        # make sure ALL trees have the primary gem in the leaf, not just randomly swapped
        elif "Rose" in base_name and "Rose" not in item['leaf']:
            item['leaf'] = "Rose Quartz"
        elif "Jade" in base_name and "Jade" not in item['leaf']:
            item['leaf'] = "Jade"
        elif "Turquoise" in base_name and "Turquoise" not in item['leaf']:
            item['leaf'] = "Turquoise"
            
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Successfully updated inventory_final.json!")
