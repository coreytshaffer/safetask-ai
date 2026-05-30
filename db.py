import sqlite3
import os
import json

DB_FILE = "safetask.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
            reasoning TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_incident(incident):
    conn = sqlite3.connect(DB_FILE)
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
    conn.commit()
    conn.close()

def get_incidents():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM incidents ORDER BY date DESC')
    rows = c.fetchall()
    conn.close()
    
    incidents = []
    for row in rows:
        d = dict(row)
        d['contact_slate'] = json.loads(d['contact_slate']) if d['contact_slate'] else []
        if d['type'] == 'jha':
            d['formatted_narrative'] = d['narrative']
        incidents.append(d)
    return incidents

def get_incident(incident_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM incidents WHERE id = ?', (incident_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        d = dict(row)
        d['contact_slate'] = json.loads(d['contact_slate']) if d['contact_slate'] else []
        if d['type'] == 'jha':
            d['formatted_narrative'] = d['narrative']
        return d
    return None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
