import streamlit as st
import uuid
from datetime import datetime
from pitlens.models import GameSession, GameType, Round
from pitlens.db_ops import save_game_session, get_game_sessions, save_round, get_rounds_for_session
from pitlens.blackjack.presets import load_all_presets
from pitlens.exports.html_report import generate_html_report
from pitlens.exports.json_export import generate_json_export
from pitlens.db_ops import save_game_session, get_game_sessions, save_round, get_rounds_for_session
from pitlens.blackjack.presets import load_all_presets

def render_session_manager():
    st.header("Session Management")
    
    # Load existing sessions
    existing_sessions = get_game_sessions()
    
    if existing_sessions:
        session_opts = {s.session_id: f"{s.created_at.strftime('%Y-%m-%d %H:%M')} - {s.game_type.value}" for s in existing_sessions}
        selected_session_id = st.selectbox("Select Session", options=["New Session"] + list(session_opts.keys()), format_func=lambda x: "Create New Session" if x == "New Session" else session_opts[x])
    else:
        selected_session_id = "New Session"
        st.info("No existing sessions found. Create a new one.")

    if selected_session_id == "New Session":
        with st.form("new_session_form"):
            game_type = st.selectbox("Game Type", [GameType.BLACKJACK.value])
            property_name = st.text_input("Property Name (Optional)")
            table_id = st.text_input("Table ID (Optional)")
            reviewer_name = st.text_input("Reviewer Name (Optional)")
            notes = st.text_area("Notes")
            
            # Blackjack specific settings
            presets = load_all_presets()
            preset_opts = {p.preset_id: p.name for p in presets}
            selected_preset_id = st.selectbox("Blackjack Preset", options=list(preset_opts.keys()), format_func=lambda x: preset_opts[x])
            
            submitted = st.form_submit_button("Create Session")
            if submitted:
                new_session_id = str(uuid.uuid4())
                session = GameSession(
                    session_id=new_session_id,
                    game_type=GameType(game_type),
                    property_name_optional=property_name or None,
                    table_id_optional=table_id or None,
                    reviewer_name_optional=reviewer_name or None,
                    notes=notes or None,
                    started_at=datetime.utcnow()
                )
                save_game_session(session)
                # Store preset selection in session notes for MVP (or ideally in a config table, but notes is easy)
                session.notes = f"{session.notes or ''}\n[Preset: {selected_preset_id}]"
                save_game_session(session)
                
                st.session_state['active_session_id'] = new_session_id
                st.success("Session created successfully!")
                st.rerun()
    else:
        st.session_state['active_session_id'] = selected_session_id
        session = next(s for s in existing_sessions if s.session_id == selected_session_id)
        st.write(f"**Active Session:** {session.session_id}")
        st.write(f"**Game Type:** {session.game_type.value}")
        
        # Round management
        st.subheader("Rounds")
        rounds = get_rounds_for_session(session.session_id)
        if rounds:
            st.write(f"Total Rounds: {len(rounds)}")
            for r in rounds:
                st.write(f"Round {r.round_number} (ID: {r.round_id})")
        
        if st.button("Add Next Round"):
            next_round_num = len(rounds) + 1
            new_round = Round(
                round_id=str(uuid.uuid4()),
                session_id=session.session_id,
                round_number=next_round_num
            )
            save_round(new_round)
            st.success(f"Round {next_round_num} added!")
            st.rerun()
            
        st.subheader("Exports")
        colA, colB = st.columns(2)
        with colA:
            html_data = generate_html_report(session.session_id)
            st.download_button("Download HTML Report", data=html_data, file_name=f"pitlens_report_{session.session_id}.html", mime="text/html")
        with colB:
            json_data = generate_json_export(session.session_id)
            st.download_button("Download JSON Packet", data=json_data, file_name=f"pitlens_export_{session.session_id}.json", mime="application/json")

def get_active_session_id():
    return st.session_state.get('active_session_id')
