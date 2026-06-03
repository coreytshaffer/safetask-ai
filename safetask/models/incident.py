from pydantic import BaseModel
from typing import Optional, List

class IncidentDraft(BaseModel):
    incident_id: str
    original_text: str
    incident_type: Optional[str] = None
    parsed_substance: Optional[str] = None
    parsed_location: Optional[str] = None
    parsed_asset: Optional[str] = None
    injury_keywords: List[str] = []
    evacuation_keywords: List[str] = []
    created_at: str
    status: str = "draft"
