import json
import os
import shutil

# Master file
MASTER_JSON = 'netlify/inventory_final.json'
with open(MASTER_JSON, 'r') as f:
    inventory = json.load(f)

DIRECTORIES = ['.', 'local_deployment', 'netlify']

for dir_path in DIRECTORIES:
    print(f"Processing directory: {dir_path}")
    
    # 1. Sync JSON files
    for json_file in ['inventory_final.json', 'inventory_full.json', 'inventory.json']:
        dest = os.path.join(dir_path, json_file)
        # For simplicity, we make them all identical to inventory_final.json
        with open(dest, 'w') as f:
            json.dump(inventory, f, indent=4)
    
    # 2. Sync Images
    # We want images to be named both by number (1.jpg) and by display name or id?
    # User said: "every pic to have the same name"
    # Looking at gallery.html, it expects namedpics/ID.EXT or namedpics/NUMBER.EXT
    # Let's ensure BOTH exist or standardise on one.
    # netlify/gallery.html uses item.id (which is the key)
    # root gallery.html uses item.number
    
    # To be safe, let's make sure BOTH number.jpg and ID.jpg exist in namedpics/
    namedpics_dir = os.path.join(dir_path, 'namedpics')
    if not os.path.exists(namedpics_dir):
        os.makedirs(namedpics_dir)
        
    for key, item in inventory.items():
        number = item.get('number', key)
        ext = item.get('ext', 'jpg')
        
        # Source could be in any of the namedpics dirs, we look for it
        src_image = None
        for search_dir in DIRECTORIES:
            potential_src = os.path.join(search_dir, 'namedpics', f"{number}.{ext}")
            if os.path.exists(potential_src):
                src_image = potential_src
                break
        
        if src_image:
            # Copy to current dir's namedpics as NUMBER.EXT
            dest_number = os.path.join(namedpics_dir, f"{number}.{ext}")
            if src_image != dest_number:
                shutil.copy2(src_image, dest_number)
            
            # ALSO copy as KEY.EXT (if different from number) to support different code versions
            if key != str(number):
                dest_key = os.path.join(namedpics_dir, f"{key}.{ext}")
                shutil.copy2(src_image, dest_key)
        else:
            print(f"Warning: Could not find source image for item {number}")

print("Sync complete.")
