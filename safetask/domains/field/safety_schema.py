from datetime import datetime
from pydantic import BaseModel

class FieldSafetyEvent(BaseModel):
    event_id: str
    timestamp: datetime
    location: str
    hazard_type: str
    reporter_id: str
    severity: str