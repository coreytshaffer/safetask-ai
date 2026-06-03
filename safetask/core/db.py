import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime, timezone

DB_DIR = Path("data")
DB_FILE = DB_DIR / "safetask.db"

def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            type TEXT,
            date TEXT,
            inc_date TEXT,
            location TEXT,
            hash TEXT,
            incident_title TEXT,
            task_desc TEXT,
            category TEXT,
            severity TEXT,
            narrative TEXT,
            radio_script TEXT,
            contact_slate TEXT,
            reasoning TEXT,
            status TEXT DEFAULT 'draft'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT,
            camera_id TEXT,
            timestamp TEXT,
            location TEXT,
            text TEXT,
            confidence TEXT,
            evidence_quality TEXT,
            FOREIGN KEY(incident_id) REFERENCES incidents(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            name TEXT,
            aliases TEXT,
            status TEXT,
            risk_level TEXT,
            notes TEXT,
            facial_hash TEXT,
            gait_profile TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS release_authorizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT,
            commission_rep_name TEXT,
            commission_uid TEXT,
            secure_room_reviewed INTEGER,
            signature_b64 TEXT,
            timestamp TEXT,
            auth_type TEXT DEFAULT 'physical',
            call_time TEXT,
            FOREIGN KEY(incident_id) REFERENCES incidents(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS evidence_links (
            token TEXT PRIMARY KEY,
            incident_id TEXT,
            pin TEXT,
            created_at TEXT,
            views INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS dispatch_tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            officer TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            timestamp TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS lost_and_found (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            location_found TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'logged',
            timestamp TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS evidence_registry (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS evacuation_roster (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Unknown'
        )
    ''')
    
    # Insert mock data if empty
    c.execute('SELECT COUNT(*) FROM subjects')
    if c.fetchone()[0] == 0:
        c.executemany('''
            INSERT INTO subjects (id, name, aliases, status, risk_level, notes, facial_hash, gait_profile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('SUBJ-001', 'John "The Count" Doe', 'Johnny D', 'Banned', 'High', 'Known blackjack advantage player. Do not allow on floor.', '1a2b3c', 'G-8812'),
            ('SUBJ-002', 'Jane Smith', 'J-Smitty', 'VIP', 'Low', 'High roller. Notify host upon entry.', '4d5e6f', 'G-9923'),
            ('SUBJ-003', 'Unknown Subject X', 'Red Hat', 'Banned', 'Medium', 'Suspected of slot ticket theft.', 'None', 'G-3314')
        ])

    conn.commit()
    
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS incidents_fts USING fts5(
            id UNINDEXED, 
            incident_title, 
            narrative, 
            location, 
            category, 
            content='incidents', 
            content_rowid='rowid'
        )
    ''')
    
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS incidents_ai AFTER INSERT ON incidents BEGIN
            INSERT INTO incidents_fts(rowid, id, incident_title, narrative, location, category)
            VALUES (new.rowid, new.id, new.incident_title, new.narrative, new.location, new.category);
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS incidents_ad AFTER DELETE ON incidents BEGIN
            INSERT INTO incidents_fts(incidents_fts, rowid, id, incident_title, narrative, location, category)
            VALUES('delete', old.rowid, old.id, old.incident_title, old.narrative, old.location, old.category);
        END;
    ''')
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS incidents_au AFTER UPDATE ON incidents BEGIN
            INSERT INTO incidents_fts(incidents_fts, rowid, id, incident_title, narrative, location, category)
            VALUES('delete', old.rowid, old.id, old.incident_title, old.narrative, old.location, old.category);
            INSERT INTO incidents_fts(rowid, id, incident_title, narrative, location, category)
            VALUES (new.rowid, new.id, new.incident_title, new.narrative, new.location, new.category);
        END;
    ''')

    conn.commit()
    conn.close()
    
    seed_users()

def seed_users():
    conn = get_connection()
    c = conn.cursor()
    users = [
        ("admin", "password123", "ADMIN"),
        ("operator", "password123", "OPERATOR"),
        ("guard", "password123", "GUARD")
    ]
    for u in users:
        c.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", u)
    conn.commit()
    conn.close()

def save_incident(incident):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO incidents 
        (id, type, date, inc_date, location, hash, incident_title, task_desc, category, severity, narrative, radio_script, contact_slate, reasoning) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        incident.get('id', ''),
        incident.get('type', ''),
        incident.get('date', ''),
        incident.get('inc_date', ''),
        incident.get('location', ''),
        incident.get('hash', ''),
        incident.get('incident_title', ''),
        incident.get('task_desc', ''),
        incident.get('category', ''),
        incident.get('severity', ''),
        incident.get('narrative', incident.get('formatted_narrative', '')),
        incident.get('radio_script', ''),
        json.dumps(incident.get('contact_slate', [])),
        incident.get('reasoning', '')
    ))

    if 'observations' in incident:
        c.execute('DELETE FROM observations WHERE incident_id = ?', (incident.get('id'),))
        for obs in incident['observations']:
            c.execute('''
                INSERT INTO observations (incident_id, camera_id, timestamp, location, text, confidence, evidence_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.get('id'),
                obs.get('camera_id', ''),
                obs.get('timestamp', ''),
                obs.get('location', ''),
                obs.get('text', ''),
                obs.get('confidence', ''),
                obs.get('evidence_quality', '')
            ))
    conn.commit()
    conn.close()

def get_incidents():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM incidents ORDER BY date DESC')
    rows = c.fetchall()
    
    c.execute('SELECT incident_id FROM release_authorizations')
    auth_rows = c.fetchall()
    auth_set = set(row['incident_id'] for row in auth_rows)
    
    conn.close()
    
    incidents = []
    for row in rows:
        d = dict(row)
        d['contact_slate'] = json.loads(d['contact_slate']) if d['contact_slate'] else []
        if d['type'] == 'jha':
            d['formatted_narrative'] = d['narrative']
        d['authorized'] = d['id'] in auth_set
        incidents.append(d)
    return incidents

def get_incident(incident_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM incidents WHERE id = ?', (incident_id,))
    row = c.fetchone()
    
    if row:
        d = dict(row)
        d['contact_slate'] = json.loads(d['contact_slate']) if d['contact_slate'] else []
        if d['type'] == 'jha':
            d['formatted_narrative'] = d['narrative']

        c.execute('SELECT * FROM observations WHERE incident_id = ?', (incident_id,))
        obs_rows = c.fetchall()
        d['observations'] = [dict(obs) for obs in obs_rows]
        
        c.execute('SELECT * FROM release_authorizations WHERE incident_id = ? ORDER BY id DESC LIMIT 1', (incident_id,))
        auth_row = c.fetchone()
        if auth_row:
            d['authorization'] = dict(auth_row)
            
        conn.close()
        return d
    conn.close()
    return None

def save_authorization(auth_data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO release_authorizations (incident_id, commission_rep_name, commission_uid, secure_room_reviewed, signature_b64, timestamp, auth_type, call_time)
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?, ?)
    ''', (
        auth_data.get('incident_id'),
        auth_data.get('commission_rep_name'),
        auth_data.get('commission_uid'),
        auth_data.get('secure_room_reviewed', 0),
        auth_data.get('signature_b64', ''),
        auth_data.get('auth_type', 'physical'),
        auth_data.get('call_time', '')
    ))
    conn.commit()
    conn.close()

def save_evidence_link(incident_id, token, pin):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO evidence_links (token, incident_id, pin, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (token, incident_id, pin))
    conn.commit()
    conn.close()

def get_evidence_link(token):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM evidence_links WHERE token = ?', (token,))
    row = c.fetchone()
    
    if row and row['views'] < 1:
        c.execute('UPDATE evidence_links SET views = views + 1 WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        return dict(row)
    
    conn.close()
    return None

def search_incidents(query_string):
    conn = get_connection()
    c = conn.cursor()
    
    words = [w for w in query_string.replace('"', '').split() if w.strip()]
    if not words:
        return []
    clean_query = " AND ".join([f'"{word}"*' for word in words])
    
    try:
        c.execute('''
            SELECT incidents.*, snippet(incidents_fts, -1, '<b>', '</b>', '...', 64) as snippet
            FROM incidents_fts
            JOIN incidents ON incidents.rowid = incidents_fts.rowid
            WHERE incidents_fts MATCH ?
            ORDER BY rank
            LIMIT 20
        ''', (clean_query,))
        rows = c.fetchall()
    except sqlite3.OperationalError as e:
        print("FTS Error:", e)
        rows = []
    finally:
        conn.close()
        
    results = []
    for row in rows:
        d = dict(row)
        d['contact_slate'] = json.loads(d['contact_slate']) if d['contact_slate'] else []
        results.append(d)
    return results

def get_subjects():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM subjects')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_by_username(username: str) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    return dict(res) if res else None

def get_dispatch_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM dispatch_tasks ORDER BY timestamp DESC")
    tasks = [dict(row) for row in c.fetchall()]
    conn.close()
    return tasks

def create_dispatch_task(task_id: str, title: str, officer: str):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    c.execute('''
        INSERT INTO dispatch_tasks (id, title, officer, status, timestamp)
        VALUES (?, ?, ?, 'active', ?)
    ''', (task_id, title, officer, timestamp))
    conn.commit()
    conn.close()
    return {
        "id": task_id, "title": title, "officer": officer, 
        "status": "active", "timestamp": timestamp
    }

def complete_dispatch_task(task_id: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE dispatch_tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True

def get_lost_and_found_items():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM lost_and_found ORDER BY timestamp DESC")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def log_lost_and_found_item(item_id: str, description: str, location_found: str):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    c.execute('''
        INSERT INTO lost_and_found (id, description, location_found, status, timestamp)
        VALUES (?, ?, ?, 'logged', ?)
    ''', (item_id, description, location_found, timestamp))
    conn.commit()
    conn.close()
    return {
        "id": item_id, "description": description, 
        "location_found": location_found, "status": "logged", "timestamp": timestamp
    }

def get_evidence_log():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM evidence_registry ORDER BY timestamp DESC")
    evidence = [dict(row) for row in c.fetchall()]
    conn.close()
    return evidence

def log_evidence(evidence_id: str, incident_id: str, filename: str, file_hash: str, uploaded_by: str):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    c.execute('''
        INSERT INTO evidence_registry (id, incident_id, filename, file_hash, uploaded_by, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (evidence_id, incident_id, filename, file_hash, uploaded_by, timestamp))
    conn.commit()
    conn.close()
    return {
        "id": evidence_id, "incident_id": incident_id, "filename": filename,
        "file_hash": file_hash, "uploaded_by": uploaded_by, "timestamp": timestamp
    }

def get_evacuation_roster():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM evacuation_roster ORDER BY department, name")
    roster = [dict(row) for row in c.fetchall()]
    conn.close()
    return roster

def update_evacuation_status(person_id: str, new_status: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE evacuation_roster SET status = ? WHERE id = ?", (new_status, person_id))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def seed_dummy_roster():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM evacuation_roster") 
    
    import uuid
    import random
    
    departments = ["Engineering", "Security", "Operations", "Custodial", "Management"]
    names = ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Eve Adams", 
             "Frank Castle", "Grace Hopper", "Hank Pym", "Ivy Pepper", "Jack Bauer"]
    
    for name in names:
        person_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        dept = random.choice(departments)
        c.execute('''
            INSERT INTO evacuation_roster (id, name, department, status)
            VALUES (?, ?, ?, 'Unknown')
        ''', (person_id, name, dept))
        
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
