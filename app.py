import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import db
import pdf_engine

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

LM_STUDIO_URL = "http://127.0.0.1:1234/v1"

# Initialize Database
if not os.path.exists(db.DB_FILE):
    db.init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

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

import doc_processor
import tempfile

@app.route('/api/policies/upload', methods=['POST'])
def upload_policy():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    code = request.form.get('code')
    title = request.form.get('title')

    if file.filename == '' or not code or not title:
        return jsonify({"error": "Missing file, code, or title"}), 400

    try:
        # Save temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Process deterministically
        new_policy = doc_processor.process_upload(tmp_path, code, title)
        os.remove(tmp_path)

        return jsonify({"status": "success", "policy": new_policy}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting SafeTask AI Server on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)
