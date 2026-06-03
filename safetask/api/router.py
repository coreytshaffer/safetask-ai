import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime

# We will rely on field-aware's existing rag module, if it can be imported.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from rag.retriever import DocumentRetriever
    retriever = DocumentRetriever()
except Exception as e:
    retriever = None
    print(f"Warning: SafeTask couldn't load DocumentRetriever: {e}")

router = APIRouter()

class IncidentReport(BaseModel):
    title: str
    description: str
    reporter: str
    location: str
    equipment_involved: Optional[str] = ""

@router.post("/incident")
async def report_incident(report: IncidentReport):
    """
    Submit an incident report.
    This will process the incident, use RAG to find relevant policies, 
    and return an incident review packet.
    """
    # 1. Save incident locally (for MVP, we just return it as part of the packet)
    incident_id = f"INC-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 2. Use RAG to fetch relevant safety guidelines based on description
    policies = []
    if retriever:
        try:
            # We construct a query based on the incident description
            query = f"Safety policy, reporting criteria, or procedure for: {report.description} {report.equipment_involved}"
            rag_results = retriever.search(query, n_results=3)
            for res in rag_results:
                policies.append({
                    "title": res.get("title", "Unknown Policy"),
                    "excerpt": res.get("snippet", ""),
                    "source": res.get("source", ""),
                    "page": res.get("page", 1)
                })
        except Exception as e:
            print(f"RAG search failed: {e}")

    # Fallback/mock policies if RAG is empty or failed
    if not policies:
        policies.append({
            "title": "OSHA Severe Injury Reporting",
            "excerpt": "Employers must report any worker fatality within 8 hours and any amputation, loss of an eye, or hospitalization of a worker within 24 hours.",
            "source": "OSHA 1904.39",
            "page": 1
        })

    packet = {
        "incident_id": incident_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "Awaiting Safety Officer Review",
        "details": report.dict(),
        "recommended_review": policies,
        "escalation_prompt": "Does this incident involve hospitalization, amputation, or eye loss? If so, review OSHA reporting criteria immediately."
    }

    # Optional: Save to a local JSON file or DB
    save_dir = Path("data/safetask_incidents")
    save_dir.mkdir(parents=True, exist_ok=True)
    import json
    with open(save_dir / f"{incident_id}.json", "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=4)

    return {"status": "success", "packet": packet}
