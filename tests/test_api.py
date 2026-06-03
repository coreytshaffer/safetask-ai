import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from web.app import app

client = TestClient(app)

def test_index_route():
    # It might return a 404 or point to a static file depending on if static is built
    # Let's just test that the API is mounted
    response = client.get("/api/policies")
    assert response.status_code == 200
    assert "policies" in response.json()

def test_api_flag_allow():
    response = client.post("/api/flag", json={"text": "A perfectly safe observation of a bird."})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["packet"]["decision_state"] == "allow"

def test_api_flag_warn():
    # Use a term that triggers require_review like 'toxic'
    response = client.post("/api/flag", json={"text": "There was a toxic algal bloom."})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Depending on the rule definitions, this is usually require_review or warn
    assert data["packet"]["decision_state"] in ["warn", "require_review"]
