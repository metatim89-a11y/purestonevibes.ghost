import json
import os

def sync_inventory():
    # Load Master Dictionary and Current Inventory
    with open("stones_master.json", "r") as f:
        master = json.load(f)
    
    with open("inventory_final.json", "r") as f:
        inventory = json.load(f)

    updated_count = 0
    missing_stones = set()

    for key, item in inventory.items():
        # 1. Clean Stone Names (remove "(high)", "(low)", etc.)
        base_raw = item.get("base", "Unknown").split("(")[0].strip()
        leaf_raw = item.get("leaf", "Unknown").split("(")[0].strip()

        # 2. Get Properties from Master
        base_props = master.get(base_raw, {}).get("properties", "grounding")
        leaf_props = master.get(leaf_raw, {}).get("properties", "balance")

        # Track missing stones for a final report
        if base_raw not in master: missing_stones.add(base_raw)
        if leaf_raw not in master: missing_stones.add(leaf_raw)

        # 3. Determine Pairing Type
        # "Heart" if they are the same, "Harmonic" if different
        pairing_type = "Heart" if base_raw == leaf_raw else "Harmonic"
        
        # 4. Reconstruct the Energy String (The "Reprogramming")
        # Standard Format: {Type} Pairing: {Leaf} for {Props} + {Base} for {Props}.
        new_energy = f"{pairing_type} Pairing: {leaf_raw} for {leaf_props} + {base_raw} for {base_props}."
        
        # Ensure it ends with a period and has proper spacing
        new_energy = new_energy.replace(" + ", " + ").replace("  ", " ").strip()

        # 5. Update Inventory Item
        item["energy"] = new_energy
        item["base"] = base_raw # Cleaned name
        item["leaf"] = leaf_raw # Cleaned name
        
        # 6. Verify Image Existence
        img_path = f"namedpics/{key}.{item.get('ext', 'jpg')}"
        if not os.path.exists(img_path):
            print(f"Warning: Image missing for {key} at {img_path}")

        updated_count += 1

    # Save the synchronized inventory
    with open("inventory_final.json", "w") as f:
        json.dump(inventory, f, indent=4)

    print(f"\n--- SYNC COMPLETE ---")
    print(f"Successfully reprogrammed {updated_count} items.")
    if missing_stones:
        print(f"Missing from Master Dictionary: {', '.join(missing_stones)}")
    print(f"Inventory saved to inventory_final.json")

if __name__ == "__main__":
    sync_inventory()
