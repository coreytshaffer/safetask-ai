import glob
import json
import os
import sys
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv()

import datetime

from analysis.sandbox import AnalysisSandbox
from export_engine import ExportEngine
from review_engine.harness.checker import CyberneticHarness
from notebook.db import NotebookDB
from notebook.parser import DictationParser
from qgis_runner.runner import QGISRunner
from rag.retriever import DocumentRetriever
from safetask.api.router import router as safetask_router

app = FastAPI(title="FieldAware Dashboard")

app.include_router(safetask_router, prefix="/api/safetask", tags=["safetask"])

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

safetask_ui_dir = Path(__file__).parent.parent.parent / "safetask" / "web_ui"
app.mount("/safetask/static", StaticFiles(directory=str(safetask_ui_dir)), name="safetask_static")

db = NotebookDB()
harness = CyberneticHarness("policy")
retriever = DocumentRetriever()

from analysis.vision import VisionAnalyzer
# Initialize global analyzer once
try:
    vision_analyzer = VisionAnalyzer()
except Exception as e:
    vision_analyzer = None
    print(f"Failed to load vision analyzer: {e}")


class DictateRequest(BaseModel):
    text: str


class SearchRequest(BaseModel):
    query: str


class ChatRequest(BaseModel):
    messages: list


class FlagRequest(BaseModel):
    text: str


@app.get("/")
async def serve_index():
    """Serve the main index.html file for the Web Dashboard."""
    return FileResponse(str(static_dir / "index.html"))

@app.get("/safetask")
async def serve_safetask_index():
    """Serve the SafeTask UI index.html"""
    return FileResponse(str(safetask_ui_dir / "index.html"))


@app.get("/api/notes")
async def get_notes():
    """Retrieve all field notes from the local database, sorted by most recent first."""
    notes = db.get_all_notes()
    # sort by timestamp desc
    notes.sort(key=lambda x: x.timestamp, reverse=True)
    return {"notes": notes}


@app.post("/api/dictate")
async def process_dictation(req: DictateRequest):
    """
    Process a raw text dictation.
    Evaluates the dictation against the Cybernetic Harness before saving.
    """
    try:
        # Note: in real use, we'd pass the actual LM Studio URL
        parser = DictationParser()
        note = parser.parse(req.text)

        packet = harness.evaluate(note.notes, artifact_name="dashboard_dictation")

        if packet.decision_state in ["require_review", "block"]:
            return {"status": "blocked", "packet": packet}

        db.insert_note(note)
        return {"status": "saved", "note": note, "packet": packet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_docs(req: SearchRequest):
    try:
        cards = retriever.search(req.query, n_results=3)
        return {"results": cards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/flag")
async def check_flag(req: FlagRequest):
    try:
        packet = harness.evaluate(req.text, artifact_name="api_flag_request")
        return {"status": "success", "packet": packet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/identify")
async def identify_specimen(file: UploadFile = File(...)):
    if not vision_analyzer:
        raise HTTPException(status_code=500, detail="Vision analyzer not loaded.")
    
    try:
        # Save uploaded file temporarily
        temp_path = f"data/samples/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        results = vision_analyzer.identify_species(temp_path)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from ingestion.clear_lake import ClearLakeWatchIngestor

@app.post("/api/sync/clearlake")
async def sync_clearlake():
    success = ClearLakeWatchIngestor.sync()
    if success:
        return {"status": "success", "message": "Pre-departure sync complete. Data cached locally."}
    else:
        raise HTTPException(status_code=500, detail="Failed to sync Clear Lake Watch data. Check network connection.")

@app.get("/api/sensors/clearlake")
async def get_clearlake_sensors():
    data = ClearLakeWatchIngestor.get_cached_data()
    if not data:
        raise HTTPException(status_code=404, detail="No cached sensor data found. Please run pre-departure sync.")
    return data

class ActionRequest(BaseModel):
    arg: str = ""

class PreprocessRequest(BaseModel):
    input_file: str
    output_file: str
    tolerance: float = 0.001

@app.post("/api/actions/preprocess-spatial")
async def action_preprocess_spatial(req: PreprocessRequest):
    try:
        from analysis.spatial_preprocessor import SpatialPreprocessor
        out_path = SpatialPreprocessor.process_pipeline(req.input_file, req.output_file, req.tolerance)
        return {"status": "success", "message": f"Preprocessed spatial data saved to {out_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/analyze")
async def action_analyze(req: ActionRequest):
    try:
        sandbox = AnalysisSandbox()
        # Default to the example script if none provided
        script = req.arg if req.arg else "scripts/example_analysis.py"
        result = sandbox.run_script(script)
        return {"status": "success", "message": "Analysis complete", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/export")
async def action_export(req: ActionRequest):
    try:
        engine = ExportEngine()
        base_name = (
            req.arg
            if req.arg
            else f"dashboard_export_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )
        recent_notes = db.get_all_notes()[-20:]
        zip_path = engine.generate_export_bundle(base_name, "Dashboard", recent_notes)
        return {"status": "success", "message": f"Export bundled to {zip_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/map")
async def action_map(req: ActionRequest):
    try:
        runner = QGISRunner()
        recipe = req.arg if req.arg else "clear_lake_context"

        # We need a context block to run harness
        context_block = f"Map Request for recipe: {recipe}"
        packet = harness.evaluate(context_block, "dashboard_map")
        if packet.decision_state in ["require_review", "block"]:
            return {"status": "blocked", "packet": packet}

        runner.generate_map(recipe)
        return {"status": "success", "message": f"Map generated for {recipe}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/folium")
async def action_folium(req: ActionRequest):
    try:
        from qgis_runner.folium_map import FoliumMapGenerator

        generator = FoliumMapGenerator()
        output_path = generator.generate_interactive_map()
        return {
            "status": "success",
            "message": f"Interactive map generated at {output_path}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/index")
async def action_index(req: ActionRequest):
    try:
        from rag.indexer import DocumentIndexer
        indexer = DocumentIndexer()
        # Note: the indexer currently doesn't return the count, but it logs it.
        # We can just call index_directory.
        indexer.index_directory()
        return {"status": "success", "message": "Document repository indexing complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import requests


@app.post("/api/chat")
async def chat_with_model(req: ChatRequest):
    try:
        # Connect to the local LM Studio model
        api_url = os.environ.get("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
        payload = {"messages": req.messages, "temperature": 0.7, "max_tokens": 500}
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"reply": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maps")
async def get_maps():
    # Read all map metadata JSONs in data/exports
    exports_dir = Path("data/exports")
    maps = []
    if exports_dir.exists():
        for meta_file in exports_dir.glob("*_meta.json"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Convert absolute paths to relative URLs or base64.
                    # For a local prototype, we can serve images directly if we mount the export dir
                    # But for now we just return the metadata. We'll mount the exports dir to serve the images.
                    png_path = meta_file.with_name(
                        meta_file.stem.replace("_meta", "") + ".png"
                    )
                    if png_path.exists():
                        data["image_url"] = f"/exports/{png_path.name}"
                        maps.append(data)
            except Exception:
                continue
    # Sort maps by timestamp descending
    maps.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"maps": maps}


exports_dir = Path("data/exports")
exports_dir.mkdir(parents=True, exist_ok=True)
app.mount("/exports", StaticFiles(directory=str(exports_dir)), name="exports")


@app.get("/api/policies")
async def get_policies():
    policies = []
    policy_dir = Path("policy")
    if policy_dir.exists():
        for pfile in policy_dir.glob("*.yaml"):
            try:
                with open(pfile, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "rules" in data:
                        for rule in data["rules"]:
                            policies.append(
                                {
                                    "id": rule.get("id", "Unknown"),
                                    "description": rule.get("description", ""),
                                    "decision": rule.get("decision", "info"),
                                }
                            )
            except Exception:
                continue
    return {"policies": policies}


@app.get("/api/weather")
async def get_weather():
    # In a real app, this would fetch from NOAA while online and cache it locally for offline use.
    return {
        "location": "Clear Lake, CA",
        "cached_time": "2026-06-01T08:00:00Z",
        "current": {"temp": 82, "condition": "Sunny", "wind": "12 mph NW"},
        "hazards": [
            {
                "type": "Heat Advisory",
                "severity": "high",
                "description": "Temperatures expected to exceed 95°F by afternoon.",
            },
            {
                "type": "Harmful Algal Bloom",
                "severity": "medium",
                "description": "Caution advisory in effect for North Shore.",
            },
        ],
    }
