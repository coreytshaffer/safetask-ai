import uuid
from datetime import datetime, timedelta
from pitlens.models import GameSession, GameType, Round, ActiveBetShot, Wager, PlayerDecision
from pitlens.db_ops import save_game_session, save_round, save_active_bet_shot, save_wager, save_player_decision

def generate_demo_session():
    """Generates a demo blackjack session with 12 rounds."""
    session_id = "demo_session_" + str(uuid.uuid4())[:8]
    
    session = GameSession(
        session_id=session_id,
        game_type=GameType.BLACKJACK,
        property_name_optional="Demo Casino",
        table_id_optional="BJ-04",
        reviewer_name_optional="Demo Reviewer",
        started_at=datetime.utcnow() - timedelta(minutes=45),
        notes="Demo session for testing.\n[Preset: 6d_h17_das_ls]"
    )
    save_game_session(session)
    
    # 12 rounds
    wagers = [25.0, 25.0, 25.0, 50.0, 50.0, 50.0, 200.0, 200.0, 250.0, 300.0, 25.0, 25.0]
    
    # Decisions (player total, dealer upcard, hand_type, observed, recommended, deviation)
    # We'll just fake them mostly matching, with a couple deviations
    decisions = [
        ("15", "7", "hard", "hit", "hit", False),
        ("14", "6", "hard", "stand", "stand", False),
        ("12", "4", "hard", "stand", "stand", False),
        ("11", "6", "hard", "double", "double", False),
        ("Soft 18", "9", "soft", "hit", "hit", False),
        ("Pair 8", "10", "pair", "split", "split", False),
        
        # Deviation 1: Stand on 16 vs 10 (High wager)
        ("16", "10", "hard", "stand", "surrender", True), 
        
        # Deviation 2: Double 9 vs 7
        ("9", "7", "hard", "double", "hit", True),
        
        ("20", "5", "hard", "stand", "stand", False),
        ("19", "A", "hard", "stand", "stand", False),
        ("13", "2", "hard", "stand", "stand", False),
        ("14", "10", "hard", "hit", "hit", False)
    ]
    
    for i in range(12):
        round_id = str(uuid.uuid4())
        r = Round(
            round_id=round_id,
            session_id=session_id,
            round_number=i+1
        )
        save_round(r)
        
        # Active bet shot (missing for round 8)
        if i != 7:
            shot = ActiveBetShot(
                active_bet_shot_id=str(uuid.uuid4()),
                round_id=round_id,
                seat_number=1,
                source_type="video_frame",
                reviewer_confirmed=True,
                usable=True,
                confidence_label="high"
            )
            save_active_bet_shot(shot)
            
        # Wager
        w = Wager(
            wager_id=str(uuid.uuid4()),
            round_id=round_id,
            seat_number=1,
            main_bet_amount=wagers[i],
            source="reviewer_confirmed_active_bet_shot" if i != 7 else "no_usable_shot",
            reviewer_confirmed=(i != 7)
        )
        save_wager(w)
        
        # Decision
        d = decisions[i]
        pd = PlayerDecision(
            decision_id=str(uuid.uuid4()),
            round_id=round_id,
            seat_number=1,
            player_total=d[0],
            dealer_upcard=d[1],
            hand_type=d[2],
            observed_action=d[3],
            recommended_action=d[4],
            deviation_flag=d[5],
            deviation_severity="medium" if d[5] else "none"
        )
        save_player_decision(pd)

if __name__ == "__main__":
    from pitlens.database import init_db
    init_db()
    generate_demo_session()
    print("Demo session generated successfully.")
