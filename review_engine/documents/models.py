from pydantic import BaseModel
from typing import Optional

class DocumentRecord(BaseModel):
    document_id: str
    title: str
    file_name: str
    file_path: str
    document_type: str  # SDS, EAP, policy, equipment_manual, regulation, other
    source_owner: Optional[str] = None
    revision_date: Optional[str] = None
    uploaded_at: str
    checksum_sha256: str

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    section_heading: Optional[str] = None
    text: str
    page_link: Optional[str] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
