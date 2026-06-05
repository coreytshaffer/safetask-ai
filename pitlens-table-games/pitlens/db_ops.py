import sqlite3
from typing import List, Optional
from pitlens.database import get_db_connection
from pitlens.models import GameSession, Round, ActiveBetShot, Wager, PlayerDecision, ReviewFlag, Report

def save_game_session(session: GameSession) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO game_sessions 
            (session_id, game_type, property_name_optional, table_id_optional, reviewer_name_optional, started_at, ended_at, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id, session.game_type.value, session.property_name_optional, session.table_id_optional,
            session.reviewer_name_optional, session.started_at.isoformat() if session.started_at else None,
            session.ended_at.isoformat() if session.ended_at else None, session.notes,
            session.created_at.isoformat(), session.updated_at.isoformat()
        ))

def get_game_sessions() -> List[GameSession]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM game_sessions ORDER BY created_at DESC').fetchall()
        # Note: mapping enum correctly
        sessions = []
        for r in rows:
            d = dict(r)
            sessions.append(GameSession(**d))
        return sessions

def save_round(r: Round) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO rounds
            (round_id, session_id, round_number, timestamp_optional, shoe_round_number_optional, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            r.round_id, r.session_id, r.round_number, r.timestamp_optional, r.shoe_round_number_optional, r.notes
        ))

def get_rounds_for_session(session_id: str) -> List[Round]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM rounds WHERE session_id = ? ORDER BY round_number ASC', (session_id,)).fetchall()
        return [Round(**dict(r)) for r in rows]

def save_active_bet_shot(abs: ActiveBetShot) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO active_bet_shots
            (active_bet_shot_id, round_id, seat_number, source_type, frame_timestamp_optional, file_reference_optional, reviewer_confirmed, usable, obstruction_notes, confidence_label, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            abs.active_bet_shot_id, abs.round_id, abs.seat_number, abs.source_type, abs.frame_timestamp_optional,
            abs.file_reference_optional, abs.reviewer_confirmed, abs.usable, abs.obstruction_notes, abs.confidence_label,
            abs.created_at.isoformat()
        ))

def get_active_bet_shots_for_round(round_id: str) -> List[ActiveBetShot]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM active_bet_shots WHERE round_id = ?', (round_id,)).fetchall()
        return [ActiveBetShot(**dict(r)) for r in rows]

def save_wager(w: Wager) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO wagers
            (wager_id, round_id, seat_number, main_bet_amount, side_bet_amount_optional, source, confidence_score_optional, reviewer_confirmed, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            w.wager_id, w.round_id, w.seat_number, w.main_bet_amount, w.side_bet_amount_optional,
            w.source, w.confidence_score_optional, w.reviewer_confirmed, w.notes
        ))

def get_wagers_for_round(round_id: str) -> List[Wager]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM wagers WHERE round_id = ?', (round_id,)).fetchall()
        return [Wager(**dict(r)) for r in rows]

def save_player_decision(pd: PlayerDecision) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO player_decisions
            (decision_id, round_id, seat_number, player_total, dealer_upcard, hand_type, observed_action, recommended_action, deviation_flag, deviation_severity, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pd.decision_id, pd.round_id, pd.seat_number, pd.player_total, pd.dealer_upcard,
            pd.hand_type, pd.observed_action, pd.recommended_action, pd.deviation_flag, pd.deviation_severity, pd.notes
        ))

def get_player_decisions_for_round(round_id: str) -> List[PlayerDecision]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM player_decisions WHERE round_id = ?', (round_id,)).fetchall()
        return [PlayerDecision(**dict(r)) for r in rows]

def save_review_flag(f: ReviewFlag) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO review_flags
            (flag_id, session_id, round_id_optional, seat_number_optional, flag_type, severity, system_generated, reviewer_confirmed, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f.flag_id, f.session_id, f.round_id_optional, f.seat_number_optional, f.flag_type,
            f.severity, f.system_generated, f.reviewer_confirmed, f.description, f.created_at.isoformat()
        ))

def get_review_flags_for_session(session_id: str) -> List[ReviewFlag]:
    with get_db_connection() as conn:
        rows = conn.execute('SELECT * FROM review_flags WHERE session_id = ? ORDER BY created_at ASC', (session_id,)).fetchall()
        return [ReviewFlag(**dict(r)) for r in rows]
