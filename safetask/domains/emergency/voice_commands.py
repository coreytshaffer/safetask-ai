import re

def parse_evacuation_command(command_text: str) -> dict:
    # Define a pattern to identify evacuation commands and extract the target zone
    pattern = r'\b(evacuate|evacuate now|exit|get out)\b.*\b(zone \d+|main floor|upper level|lower level)\b'
    match = re.search(pattern, command_text, re.IGNORECASE)
    
    if match:
        return {
            'is_evacuation': True,
            'target_zone': match.group(2).strip()
        }
    else:
        return {
            'is_evacuation': False,
            'target_zone': None
        }