import streamlit as st
import pandas as pd
from pitlens.db_ops import get_rounds_for_session, get_wagers_for_round, get_player_decisions_for_round, get_review_flags_for_session, get_active_bet_shots_for_round

def render_timeline(session_id: str):
    st.header("Session Timeline")
    
    rounds = get_rounds_for_session(session_id)
    if not rounds:
        st.info("No rounds recorded yet.")
        return
        
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    with col1:
        show_wagers = st.checkbox("Show Wagers", value=True)
        show_decisions = st.checkbox("Show Decisions", value=True)
    with col2:
        show_flags = st.checkbox("Show Review Flags", value=True)
        only_deviations = st.checkbox("Only Strategy Deviations", value=False)
    with col3:
        only_unconfirmed = st.checkbox("Only Unconfirmed Items", value=False)
        
    timeline_data = []
    
    for r in rounds:
        wagers = get_wagers_for_round(r.round_id)
        decisions = get_player_decisions_for_round(r.round_id)
        shots = get_active_bet_shots_for_round(r.round_id)
        
        # We index things by seat for easier merging
        seats = set([w.seat_number for w in wagers] + [d.seat_number for d in decisions] + [s.seat_number for s in shots])
        
        for seat in seats:
            w = next((x for x in wagers if x.seat_number == seat), None)
            d = next((x for x in decisions if x.seat_number == seat), None)
            s = next((x for x in shots if x.seat_number == seat), None)
            
            # Filter logic
            if only_unconfirmed:
                w_unconf = w and not w.reviewer_confirmed
                d_unconf = False # Decisions don't have confirmed flag yet in UI
                s_unconf = s and not s.reviewer_confirmed
                if not (w_unconf or s_unconf):
                    continue
                    
            if only_deviations and (not d or not d.deviation_flag):
                continue
                
            entry = {
                "Round": r.round_number,
                "Seat": seat,
            }
            
            if show_wagers:
                if w:
                    entry["Wager"] = f"${w.main_bet_amount}" + (f" (+${w.side_bet_amount_optional})" if w.side_bet_amount_optional else "")
                    entry["Wager Source"] = w.source
                else:
                    entry["Wager"] = "-"
                    entry["Wager Source"] = "-"
                    
                if s:
                    entry["Active Bet Shot"] = "Confirmed" if s.reviewer_confirmed else "Unconfirmed"
                else:
                    entry["Active Bet Shot"] = "Missing"
                    
            if show_decisions:
                if d:
                    entry["Decision"] = f"{d.player_total} vs {d.dealer_upcard}: {d.observed_action.upper()}"
                    entry["Strategy"] = f"Expected {d.recommended_action.upper()}"
                    entry["Deviation"] = "Yes" if d.deviation_flag else "No"
                else:
                    entry["Decision"] = "-"
                    entry["Strategy"] = "-"
                    entry["Deviation"] = "-"
                    
            timeline_data.append(entry)
            
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No data matches current filters.")
        
    if show_flags:
        st.subheader("Review Flags")
        flags = get_review_flags_for_session(session_id)
        if flags:
            for f in flags:
                st.warning(f"**{f.flag_type}** ({f.severity.upper()}): {f.description}")
        else:
            st.success("No review flags generated for this session.")
