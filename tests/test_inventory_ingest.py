import pytest
from safetask.ingest.inventory_csv import load_inventory_csv
import tempfile
import os

def test_inventory_ingest():
    csv_content = "chemical_name,location\nMethyl Isocyanate,Building 3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name
        
    try:
        records = load_inventory_csv(tmp_path)
        assert len(records) == 1
        assert records[0].chemical_name == "Methyl Isocyanate"
        assert records[0].location == "Building 3"
    finally:
        os.remove(tmp_path)
