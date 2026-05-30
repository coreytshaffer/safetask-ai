import re
import os

sanitizer_fn = """
// Security Remediation: XSS Sanitizer
window.sanitizeHTML = function(html) {
  if (typeof html !== 'string') return html;
  return html.replace(/<script\\b[^<]*(?:(?!<\\/script>)<[^<]*)*<\\/script>/gi, '')
             .replace(/on\\w+="[^"]*"/gi, '')
             .replace(/on\\w+='[^']*'/gi, '')
             .replace(/javascript:/gi, 'safe:');
};

// Security Remediation: Safe Object Access
window.safeProp = function(obj, key) {
  if (key === '__proto__' || key === 'constructor' || key === 'prototype') return undefined;
  return obj ? obj[key] : undefined;
};
"""

def fix_xss(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If already patched, skip
    if "window.sanitizeHTML =" not in content and filepath.endswith('app.js'):
        content = sanitizer_fn + "\n" + content
    
    # We will search for container.innerHTML = `...` and container.innerHTML += `...`
    # A simple regex for innerHTML assignment:
    content = re.sub(r'\.innerHTML\s*\+=\s*([\`\'\"].*?[\`\'\"]);?', r'.innerHTML += window.sanitizeHTML(\1);', content, flags=re.DOTALL)
    content = re.sub(r'\.innerHTML\s*=\s*([\`\'\"].*?[\`\'\"]);?', r'.innerHTML = window.sanitizeHTML(\1);', content, flags=re.DOTALL)
    
    # Let's fix prototype pollution in bracket notation where it looks like obj[key]
    # We will just replace specific patterns if we can find them, but it's risky with regex.
    # The scanner found L96, L1246, L1436 in app.js
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_xss('safetask/apps/surveillance_command_center/app.js')
fix_xss('epic9.js')
fix_xss('epic10.js')
fix_xss('epic11.js')
fix_xss('epic12.js')
fix_xss('epic13.js')
