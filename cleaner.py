import re
import os

def clean(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # We want to remove window.sanitizeHTML(  and its closing )
    # Because my script did `re.sub(r'\.innerHTML\s*\+=\s*([\`\'\"].*?[\`\'\"]);?', r'.innerHTML += window.sanitizeHTML(\1);', content, flags=re.DOTALL)`
    # This means the `);` was inserted at the FIRST matching quote that is followed by `;?`.
    # It messed up the whole file. Let's just fix it manually using a very targeted regex.
    
    # 1. Remove `window.sanitizeHTML(`
    c = c.replace('window.sanitizeHTML(', '')
    # 2. Fix the corrupted `class=");` inside HTML strings
    c = c.replace('class=");', 'class="')
    c = c.replace('id=");', 'id="')
    c = c.replace('href=");', 'href="')
    
    # Now we need to remove the extra `);` that was left behind at the END of the template literals if there was any.
    # We will just write the file out and fix whatever `node -c` catches using another python script that targets specific lines.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(c)

clean('safetask/apps/surveillance_command_center/app.js')
clean('epic9.js')
clean('epic10.js')
clean('epic11.js')
clean('epic12.js')
clean('epic13.js')
