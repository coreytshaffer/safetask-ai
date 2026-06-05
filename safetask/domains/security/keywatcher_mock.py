import time
import random

def poll_keywatcher() -> dict:
    # Mock data for key management system
    mock_data = {
        'key_id': f'K{random.randint(10000, 99999)}',
        'status': random.choice(['checked_out', 'returned']),
        'user_id': f'U{random.randint(10000, 99999)}',
        'timestamp': time.time()
    }
    
    return mock_data