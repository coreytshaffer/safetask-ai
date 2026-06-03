import pytest
from safetask.ingest.contacts_csv import load_contacts_csv
import tempfile
import os

def test_contact_ingest():
    csv_content = "role,name,escalation_order\nSafety Officer,Jane Safety,1"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name
        
    try:
        records = load_contacts_csv(tmp_path)
        assert len(records) == 1
        assert records[0].role == "Safety Officer"
        assert records[0].name == "Jane Safety"
        assert records[0].escalation_order == 1
    finally:
        os.remove(tmp_path)
