import hashlib
from datetime import datetime
import re
from .safety_schema import FieldSafetyEvent

def anonymize_event(event: FieldSafetyEvent) -> dict:
    anonymized_data = {}
    event_dict = event.model_dump()
    
    # Anonymize reporter IDs using SHA-256
    if 'reporter_id' in event_dict and event_dict['reporter_id']:
        anonymized_data['reporter_id'] = hashlib.sha256(event_dict['reporter_id'].encode()).hexdigest()
    
    # Round down timestamp to the nearest hour
    if 'timestamp' in event_dict and event_dict['timestamp']:
        dt = event_dict['timestamp']
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        rounded_dt = dt.replace(minute=0, second=0, microsecond=0)
        anonymized_data['timestamp'] = rounded_dt.isoformat()
    
    # Scrub phone numbers and emails from free-text string fields
    for key, value in event_dict.items():
        if key in ['reporter_id', 'timestamp']:
            continue
        if isinstance(value, str):
            # Scrub phone numbers
            scrubbed = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'XXX-XXX-XXXX', value)
            # Scrub emails
            scrubbed = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', scrubbed)
            anonymized_data[key] = scrubbed
        else:
            anonymized_data[key] = value
            
    return anonymized_data