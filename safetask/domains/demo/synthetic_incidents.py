import random

def generate_incidents(count: int) -> list[dict]:
    incidents = []
    for _ in range(count):
        incident_type = random.choice(['slip and fall', 'suspicious activity', 'theft', 'fight'])
        location = random.choice(['lobby', 'casino floor', 'bathroom', 'security office'])
        description = f"A {incident_type} occurred in the {location}."
        incidents.append({
            'id': random.randint(1000, 9999),
            'type': incident_type,
            'location': location,
            'description': description
        })
    return incidents