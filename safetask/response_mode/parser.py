import uuid
from datetime import datetime, timezone
from safetask.models.incident import IncidentDraft

def parse_incident_text(text: str) -> IncidentDraft:
    # A simple keyword-based parser for the MVP.
    text_lower = text.lower()
    
    incident_type = None
    if any(word in text_lower for word in ["leak", "spill", "release", "odor", "vapor", "gas", "fume"]):
        incident_type = "chemical_release"
    elif any(word in text_lower for word in ["fire", "smoke", "burn"]):
        incident_type = "fire"
    
    substance = None
    if "methyl isocyanate" in text_lower:
        substance = "Methyl isocyanate"
    elif "chlorine" in text_lower:
        substance = "Chlorine"
        
    location = None
    if "building 3" in text_lower:
        location = "Building 3"
        if "first floor" in text_lower:
            location += ", first floor"
        if "northwest corner" in text_lower:
            location += ", northwest corner"
            
    asset = None
    if "tank" in text_lower:
        asset = "tank"
    elif "valve" in text_lower:
        asset = "valve"

    injury_keywords = [word for word in ["hospitalized", "amputation", "injury", "hurt"] if word in text_lower]
    evacuation_keywords = [word for word in ["evacuate", "evacuation", "clear the area"] if word in text_lower]

    return IncidentDraft(
        incident_id=str(uuid.uuid4()),
        original_text=text,
        incident_type=incident_type,
        parsed_substance=substance,
        parsed_location=location,
        parsed_asset=asset,
        injury_keywords=injury_keywords,
        evacuation_keywords=evacuation_keywords,
        created_at=datetime.now(timezone.utc).isoformat()
    )
