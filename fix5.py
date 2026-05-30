import os

def remove_sanitize(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find `window.sanitizeHTML(`
    while 'window.sanitizeHTML(' in content:
        start_idx = content.find('window.sanitizeHTML(')
        # Find the matching closing `);`
        # We assume it's the first `);` after the start_idx that is at the end of the statement.
        # But wait, `window.sanitizeHTML(` itself is a function call. It has a closing `)`.
        # We can find the matching parenthesis for `window.sanitizeHTML(`
        paren_count = 0
        in_string = False
        string_char = ''
        escape = False
        
        idx = start_idx + len('window.sanitizeHTML')
        end_idx = -1
        
        for i in range(idx, len(content)):
            char = content[i]
            
            if escape:
                escape = False
                continue
                
            if char == '\\':
                escape = True
                continue
                
            if in_string:
                if char == string_char:
                    in_string = False
                continue
                
            if char in ["'", '"', '`']:
                in_string = True
                string_char = char
                continue
                
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    end_idx = i
                    break
                    
        if end_idx != -1:
            # We found the matching `)`. 
            # We need to remove `window.sanitizeHTML(` and `)`
            inner_content = content[start_idx + len('window.sanitizeHTML('):end_idx]
            
            # Check if there is a `;` after `)`
            replace_end = end_idx + 1
            if replace_end < len(content) and content[replace_end] == ';':
                pass # don't remove the semicolon
                
            content = content[:start_idx] + inner_content + content[replace_end:]
        else:
            print(f"Error parsing at {start_idx}")
            break

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

remove_sanitize('safetask/apps/surveillance_command_center/app.js')
remove_sanitize('epic9.js')
remove_sanitize('epic10.js')
remove_sanitize('epic11.js')
remove_sanitize('epic12.js')
remove_sanitize('epic13.js')
