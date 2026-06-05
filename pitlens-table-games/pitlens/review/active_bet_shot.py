from pitlens.models import ActiveBetShot
from typing import Optional

def validate_active_bet_shot(shot: ActiveBetShot) -> tuple[bool, Optional[str]]:
    """
    Validates if an active bet shot meets criteria for wager analysis.
    Returns (is_valid, reason_if_invalid)
    """
    if not shot.usable:
        return False, "Shot marked as unusable."
    
    if not shot.reviewer_confirmed:
        if shot.confidence_label in ["low", "not_applicable"]:
            return False, "Unconfirmed shot with low confidence."
            
    if shot.obstruction_notes:
        # Just a warning flag, could still be usable
        pass

    return True, None
