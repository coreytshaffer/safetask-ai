from pydantic import BaseModel
import random
import time

class BadgeReadEvent(BaseModel):
    badge_id: str
    door_id: str
    timestamp: float
    status: str

def poll_acs() -> BadgeReadEvent:
    badge_ids = ['B123', 'B456', 'B789']
    door_ids = ['D1', 'D2']
    statuses = ['granted', 'denied']
    
    return BadgeReadEvent(
        badge_id=random.choice(badge_ids),
        door_id=random.choice(door_ids),
        timestamp=time.time(),
        status=random.choice(statuses)
    )