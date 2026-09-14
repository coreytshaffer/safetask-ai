import os
import json
import tempfile
import requests
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from safetask.core import db
from safetask.core.regulation_pack import policy_response
from safetask.core import pdf_engine

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", "..", ".."))
DOMAIN_PACKS_DIR = os.path.join(PROJECT_ROOT, "safetask", "domains")

app = Flask(__name__, static_folder=APP_DIR, static_url_path='')
CORS(app)

LM_STUDIO_URL = "http://127.0.0.1:1234/v1"

# Initialize Database
if not os.path.exists(db.DB_FILE):
    db.init_db()

def is_safe_pack_name(pack_name: str) -> bool:
    return pack_name.replace("-", "").replace("_", "").isalnum()

@app.route('/')
def index():
    return send_from_directory(APP_DIR, 'index.html')

@app.route('/policy-packs/<domain>/regulations.json')
def regulation_pack(domain):
    status, payload = policy_response(domain, domain_root=DOMAIN_PACKS_DIR)
    return jsonify(payload), status, {"Cache-Control": "no-store"}

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(APP_DIR, path)

@app.route('/api/models', methods=['GET'])
def get_models():
    try:
        resp = requests.get(f"{LM_STUDIO_URL}/models")
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/completions', methods=['POST'])
def proxy_chat():
    try:
        resp = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            json=request.json,
            headers={"Content-Type": "application/json"}
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    incidents = db.get_incidents()
    return jsonify(incidents)

# Epic 11: Authorization Route
@app.route('/api/incidents/<incident_id>/authorize', methods=['POST'])
def authorize_incident(incident_id):
    data = request.json
    data['incident_id'] = incident_id
    db.save_authorization(data)
    return jsonify({"status": "success", "message": "Incident authorized successfully"})

# Epic 11: Get single incident for PDF auth
@app.route('/api/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    inc = db.get_incident(incident_id)
    if inc:
        return jsonify(inc)
    return jsonify({"error": "Not found"}), 404

# Epic 12: Generate Evidence Link
import random
import string

@app.route('/api/incidents/<incident_id>/link', methods=['POST'])
def generate_evidence_link(incident_id):
    # Check if authorized
    inc = db.get_incident(incident_id)
    if not inc or 'authorization' not in inc:
        return jsonify({"error": "Incident not authorized for release"}), 403
    
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    pin = ''.join(random.choices(string.digits, k=6))
    
    db.save_evidence_link(incident_id, token, pin)
    
    return jsonify({
        "status": "success",
        "link": f"/portal/{token}",
        "pin": pin
    })

@app.route('/portal/<token>', methods=['GET'])
def portal_page(token):
    # Just return the HTML file for the portal
    return send_file('portal.html')

@app.route('/api/portal/verify', methods=['POST'])
def verify_portal_pin():
    data = request.json
    token = data.get('token')
    pin = data.get('pin')
    
    link_data = db.get_evidence_link(token)
    if not link_data:
        return jsonify({"error": "Link invalid or expired (maximum views reached)"}), 404
        
    if link_data['pin'] != pin:
        return jsonify({"error": "Invalid PIN"}), 403
        
    inc = db.get_incident(link_data['incident_id'])
    return jsonify({"status": "success", "incident": inc})

# Epic 13: Subject Profile Management & Biometrics
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = db.get_subjects()
    return jsonify({"subjects": subjects})

@app.route('/api/biometrics/scan', methods=['POST'])
def run_biometric_scan():
    # Simulate a 1-5 second process finding a subject
    subjects = db.get_subjects()
    if not subjects:
        return jsonify({"error": "No subjects in database"}), 404
        
    # We'll just randomly pick a subject to "match"
    import random
    match = random.choice(subjects)
    confidence = round(random.uniform(82.5, 99.8), 1)
    
    return jsonify({
        "status": "success",
        "match": match,
        "confidence": confidence,
        "scan_type": "Facial & Gait Fusion"
    })

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    results = db.search_incidents(query)
    return jsonify(results)

@app.route('/api/incidents', methods=['POST'])
def save_incident():
    data = request.json
    if not data or 'id' not in data:
        return jsonify({"error": "Invalid incident data"}), 400
    db.save_incident(data)
    return jsonify({"status": "success", "id": data['id']})

@app.route('/api/export/pdf/<incident_id>', methods=['GET'])
def export_pdf(incident_id):
    output_dir = "exports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"Incident_{incident_id}.pdf")
    
    success = pdf_engine.generate_incident_pdf(incident_id, output_path)
    if success and os.path.exists(output_path):
        return send_file(output_path, as_attachment=True, download_name=f"Incident_{incident_id}.pdf")
    else:
        return jsonify({"error": "Failed to generate PDF or incident not found"}), 404

@app.route('/api/policies/upload', methods=['POST'])
def upload_policy():
    return jsonify({"status": "publication_disabled", "entries": [],
                    "message": "Uploads cannot publish reviewed policy"}), 410, {"Cache-Control": "no-store"}

if __name__ == '__main__':
    print("Starting SafeTask AI Server on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)
