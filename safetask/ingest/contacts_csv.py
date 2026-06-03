import pandas as pd
from typing import List
from safetask.models.contacts import ContactRecord

def load_contacts_csv(filepath: str) -> List[ContactRecord]:
    df = pd.read_csv(filepath)
    records = []
    for _, row in df.iterrows():
        record = ContactRecord(
            role=row['role'],
            name=row['name'],
            phone=row.get('phone'),
            email=row.get('email'),
            escalation_order=row.get('escalation_order'),
            incident_type=row.get('incident_type'),
            location_scope=row.get('location_scope')
        )
        records.append(record)
    return records
