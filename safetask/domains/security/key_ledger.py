def append_audit_ledger(key_event: dict) -> bool:
    # Format the key event into a secure audit log entry string
    audit_log_entry = f"Key ID: {key_event['key_id']}, Status: {key_event['status']}, User ID: {key_event['user_id']}, Timestamp: {key_event['timestamp']}"
    
    # Print the audit log entry to the console (simulating an append to an immutable ledger)
    print(audit_log_entry)
    
    # Return True to indicate successful appending
    return True