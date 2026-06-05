import datetime

def create_dispatch_entry(officer_id: str, location: str, task: str) -> dict:
    dispatch_entry = {
        'officer_id': officer_id,
        'location': location,
        'task': task,
        'timestamp': datetime.datetime.now().isoformat(),
        'status': 'dispatched'
    }
    return dispatch_entry