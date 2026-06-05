import streamlit as st
import uuid
from pitlens.models import PlayerDecision
from pitlens.db_ops import save_player_decision, get_player_decisions_for_round, get_game_sessions
from pitlens.blackjack.presets import load_all_presets
from pitlens.blackjack.strategy import get_basic_strategy
import re

def render_decision_ui(round_id: str, round_number: int, session_id: str):
    st.subheader(f"Player Decisions for Round {round_number}")
    
    existing_decisions = get_player_decisions_for_round(round_id)
    if existing_decisions:
        for d in existing_decisions:
            color = "red" if d.deviation_flag else "green"
            st.markdown(f"**Seat {d.seat_number}:** {d.player_total} vs {d.dealer_upcard} -> Observed: {d.observed_action.upper()} | Expected: {d.recommended_action.upper()} :{color}[({'Deviation' if d.deviation_flag else 'Match'})]")

    with st.form(f"decision_form_{round_id}"):
        st.write("Enter Player Decision")
        seat_number = st.number_input("Seat Number", min_value=1, max_value=7, value=1, key=f"dec_seat_{round_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            hand_type = st.selectbox("Hand Type", ["hard", "soft", "pair"])
            player_total = st.text_input("Player Hand (e.g., '16', 'Soft 17', 'Pair 8')")
        with col2:
            dealer_upcard = st.text_input("Dealer Upcard (e.g., '10', 'A', '5')")
            observed_action = st.selectbox("Observed Action", ["hit", "stand", "double", "split", "surrender", "insurance", "unknown"])
            
        notes = st.text_input("Notes", key=f"dec_notes_{round_id}")
        
        submitted = st.form_submit_button("Save Decision")
        if submitted:
            # We need the active preset for this session
            sessions = get_game_sessions()
            session = next(s for s in sessions if s.session_id == session_id)
            
            # Extract preset_id from notes (Hacky for MVP, normally in DB col)
            preset_id = "6d_h17_das_ls" # fallback
            match = re.search(r'\[Preset: (.*?)\]', session.notes or "")
            if match:
                preset_id = match.group(1)
                
            presets = load_all_presets()
            preset = next((p for p in presets if p.preset_id == preset_id), presets[0])
            
            recommendation = get_basic_strategy(player_total, dealer_upcard, preset)
            
            is_deviation = recommendation.recommended_action.lower() != observed_action.lower()
            severity = "medium" if is_deviation else "none" # simplified severity logic
            
            decision = PlayerDecision(
                decision_id=str(uuid.uuid4()),
                round_id=round_id,
                seat_number=seat_number,
                player_total=player_total,
                dealer_upcard=dealer_upcard,
                hand_type=hand_type,
                observed_action=observed_action,
                recommended_action=recommendation.recommended_action,
                deviation_flag=is_deviation,
                deviation_severity=severity,
                notes=notes or None
            )
            save_player_decision(decision)
            
            if is_deviation:
                st.error(f"Deviation logged! Expected {recommendation.recommended_action}, got {observed_action}.")
            else:
                st.success("Decision matches basic strategy.")
            st.rerun()
