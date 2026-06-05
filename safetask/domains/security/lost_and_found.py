import uuid

def register_item(item_type: str, description: str, location_found: str) -> dict:
    item_id = str(uuid.uuid4())
    return {
        'item_id': item_id,
        'item_type': item_type,
        'description': description,
        'location_found': location_found,
        'status': 'logged'
    }