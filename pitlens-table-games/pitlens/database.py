import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pitlens.db")

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # GameSession
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id TEXT PRIMARY KEY,
                game_type TEXT NOT NULL,
                property_name_optional TEXT,
                table_id_optional TEXT,
                reviewer_name_optional TEXT,
                started_at TEXT,
                ended_at TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Round
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rounds (
                round_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                timestamp_optional TEXT,
                shoe_round_number_optional INTEGER,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES game_sessions (session_id)
            )
        ''')

        # ActiveBetShot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_bet_shots (
                active_bet_shot_id TEXT PRIMARY KEY,
                round_id TEXT NOT NULL,
                seat_number INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                frame_timestamp_optional TEXT,
                file_reference_optional TEXT,
                reviewer_confirmed BOOLEAN NOT NULL,
                usable BOOLEAN NOT NULL,
                obstruction_notes TEXT,
                confidence_label TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (round_id) REFERENCES rounds (round_id)
            )
        ''')

        # Wager
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wagers (
                wager_id TEXT PRIMARY KEY,
                round_id TEXT NOT NULL,
                seat_number INTEGER NOT NULL,
                main_bet_amount REAL NOT NULL,
                side_bet_amount_optional REAL,
                source TEXT NOT NULL,
                confidence_score_optional REAL,
                reviewer_confirmed BOOLEAN NOT NULL,
                notes TEXT,
                FOREIGN KEY (round_id) REFERENCES rounds (round_id)
            )
        ''')

        # PlayerDecision
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_decisions (
                decision_id TEXT PRIMARY KEY,
                round_id TEXT NOT NULL,
                seat_number INTEGER NOT NULL,
                player_total TEXT NOT NULL,
                dealer_upcard TEXT NOT NULL,
                hand_type TEXT NOT NULL,
                observed_action TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                deviation_flag BOOLEAN NOT NULL,
                deviation_severity TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (round_id) REFERENCES rounds (round_id)
            )
        ''')

        # ReviewFlag
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS review_flags (
                flag_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                round_id_optional TEXT,
                seat_number_optional INTEGER,
                flag_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                system_generated BOOLEAN NOT NULL,
                reviewer_confirmed BOOLEAN NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES game_sessions (session_id),
                FOREIGN KEY (round_id_optional) REFERENCES rounds (round_id)
            )
        ''')

        # Report
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES game_sessions (session_id)
            )
        ''')

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
