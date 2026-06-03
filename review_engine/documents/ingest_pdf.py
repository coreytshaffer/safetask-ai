import fitz  # PyMuPDF
import hashlib
from typing import List, Tuple

def extract_text_from_pdf(filepath: str) -> Tuple[str, List[dict]]:
    # Extracts text and returns full document hash + list of page dicts
    doc = fitz.open(filepath)
    pages = []
    
    hasher = hashlib.sha256()
    
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text")
        pages.append({
            "page_number": i + 1,
            "text": text
        })
        hasher.update(text.encode('utf-8'))
        
    return hasher.hexdigest(), pages
