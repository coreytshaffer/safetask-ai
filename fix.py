import re

with open('safetask/apps/surveillance_command_center/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The first issue is `</main> </div>` right above `<!-- 4. SETTINGS`
html = html.replace('</main>\n    </div>\n  \n          <!-- 4. SETTINGS', '<!-- 4. SETTINGS')

# The second issue is the leftover old tabAdmin:
# <!-- 4. ADMIN POLICY DEPLOYMENT TAB --> ...
# We want to remove it.
old_tab_start = html.find('<!-- 4. ADMIN POLICY DEPLOYMENT TAB -->')
if old_tab_start != -1:
    old_tab_end = html.find('<!-- 4. SETTINGS & SERVER CONFIG TAB -->')
    if old_tab_end != -1:
        html = html[:old_tab_start] + html[old_tab_end:]

# We need to add `</main> </div>` back at the very bottom right before script tags
if '</main>' not in html[old_tab_start:]:
    # Find the end of settings tab
    idx = html.find('<!-- FOOTER -->')
    if idx != -1:
        html = html[:idx] + '</main></div>\n' + html[idx:]

with open('safetask/apps/surveillance_command_center/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
