from typing import Dict, Optional
from .acs_mock import BadgeReadEvent

def acs_handoff_to_scc(event: BadgeReadEvent) -> Optional[Dict]:
    if event.status == 'denied':
        return {
            'alert_type': 'acs_denied',
            'event_data': event.model_dump()
        }
    else:
        return None