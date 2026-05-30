import os

filepath = 'safetask/apps/surveillance_command_center/app.js'
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the incorrectly escaped backticks
    content = content.replace('\\`\\${', '`${')
    content = content.replace('\\`', '`')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
