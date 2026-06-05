import os
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
import hashlib
from pydantic import BaseModel
from typing import List, Optional
import datetime
import uuid
from safetask.core import db
db.init_db()

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

async def require_auth(authorization: str = Header(None)):
    """Minimal token gate — checks that the mock-jwt token is present."""
    if not authorization or not authorization.startswith("mock-jwt-"):
        raise HTTPException(status_code=401, detail="Unauthorized")


def _safe_filename(filename: str) -> str:
    """Strip path components and replace unsafe characters to prevent path traversal."""
    return re.sub(r"[^\w.\-]", "_", Path(filename).name)

class IncidentReport(BaseModel):
    title: str
    description: str
    reporter: str
    location: str
    equipment_involved: Optional[str] = ""

@router.post("/incident", dependencies=[Depends(require_auth)])
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

# Epic 16: Security Dispatch Console
class DispatchTask(BaseModel):
    title: str
    officer: str

@router.get("/dispatch", dependencies=[Depends(require_auth)])
async def get_dispatch_log():
    tasks = db.get_dispatch_tasks()
    return {"tasks": tasks}

@router.post("/dispatch", dependencies=[Depends(require_auth)])
async def dispatch_officer(task: DispatchTask):
    task_id = f"TSK-{uuid.uuid4().hex[:6].upper()}"
    new_task = db.create_dispatch_task(task_id, task.title, task.officer)
    return {"status": "success", "task": new_task}

@router.patch("/dispatch/{task_id}/complete", dependencies=[Depends(require_auth)])
async def complete_task(task_id: str):
    success = db.complete_dispatch_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": f"Task {task_id} completed."}

class LostItem(BaseModel):
    description: str
    location_found: str

@router.get("/lostandfound", dependencies=[Depends(require_auth)])
async def get_lost_items():
    items = db.get_lost_and_found_items()
    return {"items": items}

@router.post("/lostandfound", dependencies=[Depends(require_auth)])
async def log_lost_item(item: LostItem):
    item_id = f"LNF-{uuid.uuid4().hex[:6].upper()}"
    new_item = db.log_lost_and_found_item(item_id, item.description, item.location_found)
    return {"status": "success", "item": new_item}

# Epic 7: Evidence Locker
@router.get("/evidence", dependencies=[Depends(require_auth)])
async def get_evidence():
    evidence = db.get_evidence_log()
    return {"evidence": evidence}

@router.post("/evidence/upload", dependencies=[Depends(require_auth)])
async def upload_evidence(
    incident_id: str = Form(...),
    officer: str = Form(...),
    file: UploadFile = File(...)
):
    evidence_dir = Path("data/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    file_bytes = await file.read()
    
    # Generate cryptographic SHA-256 hash for chain of custody
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Save the file to disk
    evidence_id = f"EVD-{uuid.uuid4().hex[:6].upper()}"
    safe_filename = f"{evidence_id}_{_safe_filename(file.filename)}"
    file_path = evidence_dir / safe_filename
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    new_evidence = db.log_evidence(
        evidence_id=evidence_id,
        incident_id=incident_id,
        filename=file.filename,
        file_hash=file_hash,
        uploaded_by=officer
    )
    
    return {"status": "success", "evidence": new_evidence}

# Epic 11: Evacuation Accountability Board
class StatusUpdate(BaseModel):
    status: str

@router.get("/evacuation/roster", dependencies=[Depends(require_auth)])
async def get_evacuation_roster():
    roster = db.get_evacuation_roster()
    return {"roster": roster}

@router.patch("/evacuation/roster/{person_id}/status", dependencies=[Depends(require_auth)])
async def update_person_status(person_id: str, payload: StatusUpdate):
    if payload.status not in ["Unknown", "Safe", "Missing", "Injured"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    success = db.update_evacuation_status(person_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
        
    return {"status": "success"}

@router.post("/evacuation/seed")
async def seed_evacuation_roster():
    db.seed_dummy_roster()
    return {"status": "success", "message": "Dummy roster seeded"}

# Epic 17: Training Mode & LM Studio Integration
import json
import urllib.request
import urllib.error

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

@router.post("/training/chat")
async def training_chat(payload: ChatRequest):
    # System prompt to define the AI Advisor's persona
    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly, highly intelligent Training Advisor for a high-security facility command center. "
            "Your job is to train new operators on facility SOPs, camera control, and radio etiquette. "
            "Speak clearly, be encouraging, and use spaced repetition concepts (ask quizzes). "
            "Keep your responses concise and professional."
        )
    }
    
    # Prepend the system prompt to the user's message history
    messages = [system_prompt] + [msg.model_dump() for msg in payload.messages]
    
    lm_studio_url = os.environ.get("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
    data = json.dumps({
        "model": "local-model", # LM Studio usually ignores this or uses whatever is loaded
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }).encode('utf-8')
    
    req = urllib.request.Request(lm_studio_url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            ai_message = result['choices'][0]['message']['content']
            return {"status": "success", "response": ai_message}
    except urllib.error.URLError as e:
        # Fallback if LM Studio is offline or unreachable
        return {
            "status": "error", 
            "response": f"[SYSTEM OFFLINE] Unable to reach LM Studio at {lm_studio_url}. Ensure the local server is running. Error: {str(e)}"
        }

# Epic 18: Authentication
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
async def login(payload: LoginRequest):
    user = db.get_user_by_username(payload.username)
    candidate_hash = hashlib.sha256(payload.password.encode()).hexdigest()
    if user and user['password_hash'] == candidate_hash:
        return {"status": "success", "token": f"mock-jwt-{user['id']}", "role": user['role'], "username": user['username']}
    else:
        return {"status": "error", "message": "Invalid username or password"}

# Epic 19: Safety Vision Analytics Simulation
import random
import time

@router.get("/vision/events")
async def get_vision_events():
    """Simulates a computer vision pipeline returning tracked objects and events."""
    # Simulate some tracked workers with random coordinates on a 100x100 grid percentage
    tracked_objects = []
    for i in range(1, 4): # Track 3 people
        x = random.uniform(10, 80)
        y = random.uniform(20, 70)
        tracked_objects.append({
            "id": f"worker_{i}",
            "x": x,
            "y": y,
            "width": 10,
            "height": 20,
            "status": "safe" if random.random() > 0.3 else "violation"
        })
        
    # Occasionally generate an event
    events = []
    if random.random() > 0.7:
        event_types = [
            {"type": "PPE_VIOLATION", "desc": "Missing Hardhat Detected", "color": "var(--danger)"},
            {"type": "ZONE_BREACH", "desc": "Unauthorized Entry: Exclusion Zone B", "color": "var(--warning)"},
            {"type": "ERGONOMIC", "desc": "Improper lifting posture detected", "color": "var(--accent)"}
        ]
        evt = random.choice(event_types)
        events.append({
            "timestamp": int(time.time() * 1000),
            "type": evt["type"],
            "description": evt["desc"],
            "color": evt["color"],
            "confidence": round(random.uniform(0.75, 0.98), 2)
        })
        
    return {
        "status": "success",
        "timestamp": int(time.time() * 1000),
        "tracked_objects": tracked_objects,
        "events": events
    }
