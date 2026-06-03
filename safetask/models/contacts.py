from pydantic import BaseModel
from typing import Optional

class ContactRecord(BaseModel):
    role: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    escalation_order: Optional[int] = None
    incident_type: Optional[str] = None
    location_scope: Optional[str] = None
