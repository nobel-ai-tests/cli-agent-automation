import os
import json

def generate_manifest():
    projects_dir = 'projects'
    manifest = []
    
    if os.path.exists(projects_dir):
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path):
                # Get sub-items for each project
                sub_items = os.listdir(item_path)
                manifest.append({
                    "name": item,
                    "files": sub_items
                })
    
    with open('projects_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    generate_manifest()
