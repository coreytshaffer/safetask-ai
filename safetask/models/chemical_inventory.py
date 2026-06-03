from pydantic import BaseModel
from typing import Optional, List

class ChemicalInventoryRecord(BaseModel):
    chemical_name: str
    product_name: Optional[str] = None
    cas_number: Optional[str] = None
    location: str
    asset_id: Optional[str] = None
    last_reported_amount: Optional[float] = None
    amount_units: Optional[str] = None
    last_verified_at: Optional[str] = None
    chemical_age_days: Optional[int] = None
    sds_file_name: Optional[str] = None
    responsible_person: Optional[str] = None
    source: str = "inventory_csv"
