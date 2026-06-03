import pandas as pd
from typing import List
from safetask.models.chemical_inventory import ChemicalInventoryRecord

def load_inventory_csv(filepath: str) -> List[ChemicalInventoryRecord]:
    df = pd.read_csv(filepath)
    records = []
    for _, row in df.iterrows():
        record = ChemicalInventoryRecord(
            chemical_name=row['chemical_name'],
            product_name=row.get('product_name'),
            cas_number=row.get('cas_number'),
            location=row['location'],
            asset_id=row.get('asset_id'),
            last_reported_amount=row.get('last_reported_amount'),
            amount_units=row.get('amount_units'),
            last_verified_at=row.get('last_verified_at'),
            chemical_age_days=row.get('chemical_age_days'),
            sds_file_name=row.get('sds_file_name'),
            responsible_person=row.get('responsible_person')
        )
        records.append(record)
    return records
