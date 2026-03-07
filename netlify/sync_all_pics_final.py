import csv
import json
import os
import shutil

input_file = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\orig folder\renamed\tree_data_updated.csv'
source_pics_dir = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\orig folder\renamed'
target_pics_dir = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\namedpics'
price_file = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\fishestones (1).txt'

inventory = {}

# Load prices from fishesstones (1).txt
# Format: Tree Name,Base Gem,Base Value,Leaflet Gem,Leaf Value,Purpose & Energy,Price
prices_map = {}
with open(price_file, mode='r', encoding='utf-8') as f:
    text = f.read()
    # Find the table part
    if "Tree Name,Base Gem" in text:
        content = text.split("Tree Name,Base Gem")[1]
        lines = content.strip().split('\n')
        for line in lines:
            if ',' in line:
                parts = line.strip().split(',')
                if len(parts) >= 7:
                    tree_name = parts[0].strip().lower().replace('_', ' ')
                    price_str = parts[6].strip().replace('$', '')
                    try:
                        prices_map[tree_name] = int(float(price_str))
                    except:
                        pass

# Process the updated tree data
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        num = row['TreeNumber']
        name = row['NameOfTree']
        
        clean_name = name.replace(' ', '_')
        id_key = f"{clean_name}_{num}"
        
        # Check for image and copy
        source_file = None
        for f_name in os.listdir(source_pics_dir):
            if f_name.startswith(f"{num}."):
                source_file = f_name
                break
        
        if source_file:
            ext = source_file.rsplit('.', 1)[1]
            target_file = f"{id_key}.{ext}"
            shutil.copy2(os.path.join(source_pics_dir, source_file), os.path.join(target_pics_dir, target_file))
            
            energy = row['Combined together energy use']
            
            # Case-insensitive lookup for price
            lookup_name = name.strip().lower()
            original_price = int(row['PurchasePrice'].replace('$', ''))
            price = prices_map.get(lookup_name, original_price)
            
            inventory[id_key] = {
                "base": row['BaseStone (v)'],
                "leaf": row['LeafStone (v)'],
                "energy": energy,
                "price": price,
                "ext": ext,
                "displayName": name
            }

target_json = r'c:\Users\Customer\Desktop\fishesstonevibeexample10mins\inventory_full.json'
with open(target_json, 'w', encoding='utf-8') as f:
    json.dump(inventory, f, indent=4)

print(f"Update successful. {len(inventory)} items processed. {len(prices_map)} prices found in text file.")
