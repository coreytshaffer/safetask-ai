import streamlit as st
from pitlens.database import init_db
from pitlens.ui_components.session_ui import render_session_manager, get_active_session_id
from pitlens.ui_components.active_bet_ui import render_active_bet_ui
from pitlens.ui_components.wager_ui import render_wager_ui
from pitlens.ui_components.decision_ui import render_decision_ui
from pitlens.review.timeline import render_timeline
from pitlens.db_ops import get_rounds_for_session

def main():
    st.set_page_config(page_title="PitLens MVP", layout="wide")
    
    # Initialize DB on start
    init_db()
    
    st.sidebar.title("PitLens Navigation")
    
    render_session_manager()
    
    session_id = get_active_session_id()
    if session_id and session_id != "New Session":
        st.divider()
        rounds = get_rounds_for_session(session_id)
        if rounds:
            # Select round to view/edit
            round_opts = {r.round_id: f"Round {r.round_number}" for r in rounds}
            selected_round_id = st.selectbox("Select Round to Review", options=list(round_opts.keys()), format_func=lambda x: round_opts[x])
            
            if selected_round_id:
                selected_round = next(r for r in rounds if r.round_id == selected_round_id)
                col1, col2, col3 = st.columns(3)
                with col1:
                    render_active_bet_ui(selected_round.round_id, selected_round.round_number)
                with col2:
                    render_wager_ui(selected_round.round_id, selected_round.round_number)
                with col3:
                    render_decision_ui(selected_round.round_id, selected_round.round_number, session_id)
                    
        st.divider()
        render_timeline(session_id)

if __name__ == "__main__":
    main()

