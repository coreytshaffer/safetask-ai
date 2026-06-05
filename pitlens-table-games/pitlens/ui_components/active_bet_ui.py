import streamlit as st
import uuid
from datetime import datetime
from pitlens.models import ActiveBetShot
from pitlens.db_ops import save_active_bet_shot, get_active_bet_shots_for_round

def render_active_bet_ui(round_id: str, round_number: int):
    st.subheader(f"Active Bet Shot for Round {round_number}")
    
    existing_shots = get_active_bet_shots_for_round(round_id)
    
    if existing_shots:
        st.write("Existing Active Bet Shots:")
        for shot in existing_shots:
            st.info(f"Seat {shot.seat_number}: {shot.confidence_label.upper()} confidence. Usable: {shot.usable}")
    
    with st.form(f"active_bet_form_{round_id}"):
        st.write("Add / Update Active Bet Shot")
        seat_number = st.number_input("Seat Number", min_value=1, max_value=7, value=1)
        source_type = st.selectbox("Source Type", ["video_frame", "screenshot", "manual_only"])
        usable = st.checkbox("Usable Shot?", value=True)
        reviewer_confirmed = st.checkbox("Reviewer Confirmed?", value=True)
        confidence = st.selectbox("Confidence Label", ["high", "medium", "low", "not_applicable"])
        notes = st.text_area("Obstruction Notes")
        
        submitted = st.form_submit_button("Save Active Bet Shot")
        if submitted:
            shot = ActiveBetShot(
                active_bet_shot_id=str(uuid.uuid4()),
                round_id=round_id,
                seat_number=seat_number,
                source_type=source_type,
                usable=usable,
                reviewer_confirmed=reviewer_confirmed,
                confidence_label=confidence,
                obstruction_notes=notes or None
            )
            save_active_bet_shot(shot)
            st.success("Active bet shot saved!")
            st.rerun()
