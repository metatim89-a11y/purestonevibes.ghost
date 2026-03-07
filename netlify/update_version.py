import json
import os
import re

VERSION_FILE = 'version.json'
THEME_JS = 'theme.js'
HTML_FILES = [f for f in os.listdir('.') if f.endswith('.html')]

def update_version():
    # 1. Read and increment version
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            data = json.load(f)
            current_version = float(data['version'])
    else:
        current_version = 1.000
    
    new_version = round(current_version + 0.001, 3)
    version_str = f"v{new_version:.3f}"
    
    with open(VERSION_FILE, 'w') as f:
        json.dump({"version": new_version}, f, indent=4)
    
    print(f"Incrementing version: {current_version:.3f} -> {new_version:.3f}")

    # 2. Update VERSION in theme.js
    if os.path.exists(THEME_JS):
        with open(THEME_JS, 'r') as f:
            content = f.read()
        
        # Check if VERSION constant exists, otherwise prepend it
        if 'const APP_VERSION =' in content:
            new_content = re.sub(r'const APP_VERSION = ".*?";', f'const APP_VERSION = "{version_str}";', content)
        else:
            new_content = f'const APP_VERSION = "{version_str}";\n' + content
            
        with open(THEME_JS, 'w') as f:
            f.write(new_content)

    # 3. Update footer/meta in HTML files
    for html_file in HTML_FILES:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update version in footer (looking for Vibes &copy; 2026)
        version_display = f'Pure Stone Vibes &copy; 2026 | <span class="opacity-50">{version_str}</span>'
        new_content = re.sub(r'Pure Stone Vibes &copy; 2026( \| <span.*?>v.*?</span>)?', version_display, content)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    print(f"Updated {len(HTML_FILES)} HTML files and {THEME_JS}")

if __name__ == "__main__":
    update_version()
