import csv
import json
import os

input_file = r'c:\Users\Customer\Desktop\purestonevibes.ghost\orig folder\renamed\tree_data_updated.csv'
pics_dir = r'c:\Users\Customer\Desktop\purestonevibes.ghost\namedpics'

inventory = {}

# Get all filenames in namedpics to determine extension
pic_files = os.listdir(pics_dir)
pic_map = {}
for f in pic_files:
    if '.' in f:
        name_no_ext = f.rsplit('.', 1)[0]
        ext = f.rsplit('.', 1)[1]
        pic_map[name_no_ext] = ext

with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['NameOfTree']
        id_key = name.replace(' ', '_')
        
        # Determine extension from pic_map or default to jpg
        ext = pic_map.get(id_key, 'jpg')
        
        # Get base and leaf stones for short display if needed, but the user wants the full combined energy
        base = row['BaseStone (v)']
        leaf = row['LeafStone (v)']
        energy = row['Combined together energy use']
        price = int(row['PurchasePrice'].replace('$', ''))
        
        inventory[id_key] = {
            "base": base,
            "leaf": leaf,
            "energy": energy,
            "price": price,
            "ext": ext
        }

print(json.dumps(inventory, indent=4))
