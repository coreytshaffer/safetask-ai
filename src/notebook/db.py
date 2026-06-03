import sqlite3
import yaml
from pathlib import Path

from .schema import FieldNote
from .git_sync import GitSync
from logger import logger

class NotebookDB:
    def __init__(self, db_path: str = "data/field_notes.db", notes_dir: str = "data/notes"):
        self.db_path = Path(db_path)
        self.notes_dir = Path(notes_dir)
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
        self.git_sync = GitSync(notes_dir=str(self.notes_dir))
        self.sync_from_markdown()

    def _get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS field_notes (
                    id TEXT PRIMARY KEY,
                    site_id TEXT,
                    timestamp TEXT,
                    observer TEXT,
                    coordinates TEXT,
                    notes TEXT,
                    confidence_level TEXT,
                    evidence_type TEXT
                )
            """)
            conn.commit()

    def _write_markdown(self, note: FieldNote) -> Path:
        """Writes a FieldNote to a Markdown file with YAML frontmatter."""
        filepath = self.notes_dir / f"{note.id}.md"
        
        frontmatter = {
            "id": note.id,
            "site_id": note.site_id,
            "timestamp": note.timestamp,
            "observer": note.observer,
            "coordinates": note.coordinates,
            "confidence_level": note.confidence_level,
            "evidence_type": note.evidence_type
        }
        
        content = f"---\n{yaml.dump(frontmatter)}---\n\n{note.notes}\n"
        filepath.write_text(content, encoding="utf-8")
        return filepath

    def sync_from_markdown(self):
        """Reads all Markdown files and upserts them into the SQLite cache."""
        logger.info("Syncing SQLite cache from Markdown files...")
        count = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clear existing cache
            cursor.execute("DELETE FROM field_notes")
            
            for md_file in self.notes_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    if content.startswith("---"):
                        _, fm, body = content.split("---", 2)
                        meta = yaml.safe_load(fm)
                        note = FieldNote(
                            id=meta.get("id"),
                            site_id=meta.get("site_id"),
                            timestamp=meta.get("timestamp"),
                            observer=meta.get("observer"),
                            coordinates=meta.get("coordinates"),
                            confidence_level=meta.get("confidence_level"),
                            evidence_type=meta.get("evidence_type"),
                            notes=body.strip()
                        )
                        cursor.execute(
                            """
                            INSERT INTO field_notes 
                            (id, site_id, timestamp, observer, coordinates, notes, confidence_level, evidence_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                note.id, note.site_id, note.timestamp, note.observer, 
                                note.coordinates, note.notes, note.confidence_level, note.evidence_type
                            )
                        )
                        count += 1
                except Exception as e:
                    logger.error(f"Failed to sync markdown note {md_file.name}: {e}")
            conn.commit()
        logger.info(f"Synced {count} notes into SQLite cache.")

    def insert_note(self, note: FieldNote):
        """Saves note to Markdown, commits to Git, and updates SQLite cache."""
        # 1. Save to Markdown (Source of Truth)
        filepath = self._write_markdown(note)
        
        # 2. Version with Git
        self.git_sync.commit_note(filepath, message=f"Add note {note.id}")
        
        # 3. Update SQLite cache
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO field_notes 
                (id, site_id, timestamp, observer, coordinates, notes, confidence_level, evidence_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    note.id,
                    note.site_id,
                    note.timestamp,
                    note.observer,
                    note.coordinates,
                    note.notes,
                    note.confidence_level,
                    note.evidence_type,
                ),
            )
            conn.commit()

    def get_all_notes(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM field_notes")
            rows = cursor.fetchall()
            return [
                FieldNote(
                    id=r[0],
                    site_id=r[1],
                    timestamp=r[2],
                    observer=r[3],
                    coordinates=r[4],
                    notes=r[5],
                    confidence_level=r[6],
                    evidence_type=r[7],
                )
                for r in rows
            ]
