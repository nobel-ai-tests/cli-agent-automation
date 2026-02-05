import os
import json
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
MANIFEST_FILE = os.path.join(BASE_DIR, 'projects_manifest.json')

def atomic_write(file_path, content):
    """Write content to a file atomically using a temporary file."""
    dir_name = os.path.dirname(file_path)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, text=True)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def generate_manifest():
    manifest = []
    
    if os.path.exists(PROJECTS_DIR):
        for item in sorted(os.listdir(PROJECTS_DIR)):
            item_path = os.path.join(PROJECTS_DIR, item)
            if os.path.isdir(item_path):
                # Get sub-items for each project
                sub_items = sorted(os.listdir(item_path))
                manifest.append({
                    "name": item,
                    "files": sub_items
                })
    
    content = json.dumps(manifest, indent=2)
    atomic_write(MANIFEST_FILE, content)

if __name__ == "__main__":
    generate_manifest()
