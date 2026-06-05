from pydantic import BaseModel
import json
from .safety_schema import FieldSafetyEvent
import uuid

def handoff_to_scc(event: FieldSafetyEvent) -> dict:
    serialized_event = event.model_dump()
    # Serialize datetime if needed, or let json handle it via default=str
    return {
        'scc_alert_id': str(uuid.uuid4()),
        'status': 'routed_to_scc',
        'event_data': json.dumps(serialized_event, default=str)
    }