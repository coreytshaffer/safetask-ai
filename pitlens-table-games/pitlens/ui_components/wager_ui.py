import streamlit as st
import uuid
from pitlens.models import Wager
from pitlens.db_ops import save_wager, get_wagers_for_round, get_active_bet_shots_for_round

def render_wager_ui(round_id: str, round_number: int):
    st.subheader(f"Wagers for Round {round_number}")
    
    existing_wagers = get_wagers_for_round(round_id)
    if existing_wagers:
        for w in existing_wagers:
            st.success(f"Seat {w.seat_number}: ${w.main_bet_amount} (Source: {w.source})")

    active_shots = get_active_bet_shots_for_round(round_id)
    seats_with_shots = {shot.seat_number: shot for shot in active_shots if shot.usable}
    
    with st.form(f"wager_form_{round_id}"):
        st.write("Enter Wager")
        seat_number = st.number_input("Seat Number", min_value=1, max_value=7, value=1, key=f"wager_seat_{round_id}")
        main_bet = st.number_input("Main Bet Amount ($)", min_value=0.0, step=5.0)
        side_bet = st.number_input("Side Bet Amount ($)", min_value=0.0, step=1.0)
        
        # Determine source based on active bet shot
        if seat_number in seats_with_shots:
            default_source = "reviewer_confirmed_active_bet_shot" if seats_with_shots[seat_number].reviewer_confirmed else "system_estimate"
        else:
            default_source = "manual_entry"
            st.warning("No usable active bet shot found for this seat. Entry will be marked as manual/uncertain.")
            
        source = st.selectbox("Source", ["reviewer_confirmed_active_bet_shot", "system_estimate", "manual_entry", "no_usable_shot"], index=["reviewer_confirmed_active_bet_shot", "system_estimate", "manual_entry", "no_usable_shot"].index(default_source))
        reviewer_confirmed = st.checkbox("Reviewer Confirmed Wager", value=True)
        notes = st.text_input("Notes")
        
        submitted = st.form_submit_button("Save Wager")
        if submitted:
            wager = Wager(
                wager_id=str(uuid.uuid4()),
                round_id=round_id,
                seat_number=seat_number,
                main_bet_amount=main_bet,
                side_bet_amount_optional=side_bet if side_bet > 0 else None,
                source=source,
                reviewer_confirmed=reviewer_confirmed,
                notes=notes or None
            )
            save_wager(wager)
            st.success("Wager saved!")
            st.rerun()
