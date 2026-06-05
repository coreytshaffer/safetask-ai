from typing import List, Dict, Any
from pitlens.models import Wager, ReviewFlag
import uuid

def calculate_bet_spread(wagers: List[Wager]) -> Dict[str, Any]:
    """Calculates bet spread metrics for a list of wagers (ordered by round)."""
    if not wagers:
        return {}

    confirmed_wagers = [w for w in wagers if w.reviewer_confirmed and w.source != "no_usable_shot"]
    unconfirmed_wagers = [w for w in wagers if not w.reviewer_confirmed or w.source == "no_usable_shot"]
    
    if not confirmed_wagers:
        return {
            "unconfirmed_count": len(unconfirmed_wagers),
            "status": "No confirmed wagers available for spread analysis."
        }
        
    main_bets = [w.main_bet_amount for w in confirmed_wagers]
    
    min_bet = min(main_bets)
    max_bet = max(main_bets)
    spread_ratio = f"{int(max_bet/min_bet)}:1" if min_bet > 0 else "N/A"
    
    largest_increase = 0.0
    largest_decrease = 0.0
    increases_count = 0
    decreases_count = 0
    
    for i in range(1, len(confirmed_wagers)):
        prev_bet = confirmed_wagers[i-1].main_bet_amount
        curr_bet = confirmed_wagers[i].main_bet_amount
        
        diff = curr_bet - prev_bet
        if diff > 0:
            increases_count += 1
            if diff > largest_increase:
                largest_increase = diff
        elif diff < 0:
            decreases_count += 1
            if abs(diff) > largest_decrease:
                largest_decrease = abs(diff)

    return {
        "min_bet": min_bet,
        "max_bet": max_bet,
        "spread_ratio": spread_ratio,
        "largest_increase": largest_increase,
        "largest_decrease": largest_decrease,
        "increases_count": increases_count,
        "decreases_count": decreases_count,
        "unconfirmed_count": len(unconfirmed_wagers)
    }

def generate_wager_review_flags(session_id: str, wagers: List[Wager]) -> List[ReviewFlag]:
    """Generates neutral review flags for wager patterns."""
    flags = []
    
    # Sort wagers by round_id conceptually (assuming they are passed in order)
    # We will assume wagers list is for a specific seat across the session.
    
    for i in range(len(wagers)):
        curr_wager = wagers[i]
        
        # 1. Wager estimate requires human review (Confidence-gated)
        if not curr_wager.reviewer_confirmed:
            flags.append(ReviewFlag(
                flag_id=str(uuid.uuid4()),
                session_id=session_id,
                round_id_optional=curr_wager.round_id,
                seat_number_optional=curr_wager.seat_number,
                flag_type="Wager Estimate Requires Review",
                severity="medium",
                system_generated=True,
                reviewer_confirmed=False,
                description="Wager source is unconfirmed or from system estimate. Human review required."
            ))
            
        if curr_wager.source == "no_usable_shot":
            flags.append(ReviewFlag(
                flag_id=str(uuid.uuid4()),
                session_id=session_id,
                round_id_optional=curr_wager.round_id,
                seat_number_optional=curr_wager.seat_number,
                flag_type="Missing Active Bet Shot",
                severity="medium",
                system_generated=True,
                reviewer_confirmed=False,
                description="Missing or obstructed active bet shot for this round."
            ))

        if i > 0:
            prev_wager = wagers[i-1]
            prev_bet = prev_wager.main_bet_amount
            curr_bet = curr_wager.main_bet_amount
            
            # Sudden wager increase (e.g., > 3x)
            if prev_bet > 0 and curr_bet >= prev_bet * 3:
                flags.append(ReviewFlag(
                    flag_id=str(uuid.uuid4()),
                    session_id=session_id,
                    round_id_optional=curr_wager.round_id,
                    seat_number_optional=curr_wager.seat_number,
                    flag_type="Sudden Wager Increase",
                    severity="high",
                    system_generated=True,
                    reviewer_confirmed=False,
                    description=f"Review-relevant wager pattern: sudden increase from ${prev_bet} to ${curr_bet}."
                ))
            
            # Sudden wager decrease (e.g., > 75% drop)
            if prev_bet > 0 and curr_bet <= prev_bet * 0.25:
                flags.append(ReviewFlag(
                    flag_id=str(uuid.uuid4()),
                    session_id=session_id,
                    round_id_optional=curr_wager.round_id,
                    seat_number_optional=curr_wager.seat_number,
                    flag_type="Sudden Wager Decrease",
                    severity="medium",
                    system_generated=True,
                    reviewer_confirmed=False,
                    description=f"Review-relevant wager pattern: sudden decrease from ${prev_bet} to ${curr_bet}."
                ))
            
            # Side bet appears at high wager
            # Assuming 'high wager' is anything > 100 for this generic rule
            if not prev_wager.side_bet_amount_optional and curr_wager.side_bet_amount_optional:
                if curr_bet >= 100:
                    flags.append(ReviewFlag(
                        flag_id=str(uuid.uuid4()),
                        session_id=session_id,
                        round_id_optional=curr_wager.round_id,
                        seat_number_optional=curr_wager.seat_number,
                        flag_type="Side Bet at High Wager",
                        severity="medium",
                        system_generated=True,
                        reviewer_confirmed=False,
                        description="Side bet appeared alongside a high main wager."
                    ))
                    
    return flags
