import os
import re

def fix(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Undo the bad regex
    content = re.sub(r'window\.sanitizeHTML\(([\`\'\"])(.*?)([\`\'\"])\);', r'\1\2\3', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix('safetask/apps/surveillance_command_center/app.js')
fix('epic9.js')
fix('epic10.js')
fix('epic11.js')
fix('epic12.js')
fix('epic13.js')
