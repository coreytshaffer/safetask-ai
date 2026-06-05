from typing import Dict
from .safety_schema import FieldSafetyEvent

def draft_jha(event: FieldSafetyEvent) -> Dict[str, str]:
    hazards_identified = f"Potential {event.hazard_type} hazard identified."
    controls_recommended = ""
    
    if event.severity == "low":
        controls_recommended = "No immediate controls required. Monitor the situation."
    elif event.severity == "medium":
        controls_recommended = "Implement basic safety measures and monitor closely."
    elif event.severity == "high":
        controls_recommended = "Implement all safety protocols and evacuate if necessary."
    
    return {
        'hazards_identified': hazards_identified,
        'controls_recommended': controls_recommended
    }