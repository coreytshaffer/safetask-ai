import json
import os
from typing import List, Optional
from pitlens.models import BlackjackRulePreset

PRESETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "presets", "blackjack_presets.json"
)
CUSTOM_PRESETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "presets", "custom_blackjack_presets.json"
)

def load_default_presets() -> List[BlackjackRulePreset]:
    if not os.path.exists(PRESETS_PATH):
        return []
    with open(PRESETS_PATH, 'r') as f:
        data = json.load(f)
        return [BlackjackRulePreset(**item) for item in data]

def load_custom_presets() -> List[BlackjackRulePreset]:
    if not os.path.exists(CUSTOM_PRESETS_PATH):
        return []
    with open(CUSTOM_PRESETS_PATH, 'r') as f:
        data = json.load(f)
        return [BlackjackRulePreset(**item) for item in data]

def load_all_presets() -> List[BlackjackRulePreset]:
    return load_default_presets() + load_custom_presets()

def save_custom_preset(preset: BlackjackRulePreset) -> None:
    custom_presets = load_custom_presets()
    # Replace if ID exists, else append
    existing_idx = next((i for i, p in enumerate(custom_presets) if p.preset_id == preset.preset_id), None)
    if existing_idx is not None:
        custom_presets[existing_idx] = preset
    else:
        custom_presets.append(preset)
    
    with open(CUSTOM_PRESETS_PATH, 'w') as f:
        json.dump([p.model_dump() for p in custom_presets], f, indent=2)

def get_preset_by_id(preset_id: str) -> Optional[BlackjackRulePreset]:
    all_presets = load_all_presets()
    return next((p for p in all_presets if p.preset_id == preset_id), None)
