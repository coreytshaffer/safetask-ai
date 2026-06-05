from pitlens.models import BlackjackRulePreset, StrategyRecommendation

def get_hard_total_action(player_total: int, dealer_upcard_val: int) -> str:
    if player_total >= 17:
        return "stand"
    elif player_total >= 13 and player_total <= 16:
        if 2 <= dealer_upcard_val <= 6:
            return "stand"
        else:
            return "hit"
    elif player_total == 12:
        if 4 <= dealer_upcard_val <= 6:
            return "stand"
        else:
            return "hit"
    elif player_total == 11:
        return "double"
    elif player_total == 10:
        if 2 <= dealer_upcard_val <= 9:
            return "double"
        else:
            return "hit"
    elif player_total == 9:
        if 3 <= dealer_upcard_val <= 6:
            return "double"
        else:
            return "hit"
    else:
        return "hit"

def get_soft_total_action(player_other_card: int, dealer_upcard_val: int) -> str:
    # player_other_card is the card besides the Ace (e.g., A,7 -> 7)
    if player_other_card >= 8:
        return "stand"
    elif player_other_card == 7:
        if 2 <= dealer_upcard_val <= 6:
            return "double"
        elif 7 <= dealer_upcard_val <= 8:
            return "stand"
        else:
            return "hit"
    elif 4 <= player_other_card <= 6:
        if 4 <= dealer_upcard_val <= 6:
            return "double"
        else:
            return "hit"
    elif 2 <= player_other_card <= 3:
        if 5 <= dealer_upcard_val <= 6:
            return "double"
        else:
            return "hit"
    return "hit"

def get_pair_action(pair_val: int, dealer_upcard_val: int, das_allowed: bool) -> str:
    if pair_val == 11 or pair_val == 8: # Aces or 8s
        return "split"
    elif pair_val == 10:
        return "stand"
    elif pair_val == 9:
        if dealer_upcard_val in [7, 10, 11]:
            return "stand"
        return "split"
    elif pair_val == 7:
        if 2 <= dealer_upcard_val <= 7:
            return "split"
        return "hit"
    elif pair_val == 6:
        if 2 <= dealer_upcard_val <= 6:
            return "split"
        return "hit"
    elif pair_val == 5:
        if 2 <= dealer_upcard_val <= 9:
            return "double"
        return "hit"
    elif pair_val == 4:
        if 5 <= dealer_upcard_val <= 6 and das_allowed:
            return "split"
        return "hit"
    elif pair_val in [2, 3]:
        if 2 <= dealer_upcard_val <= 7:
            return "split"
        return "hit"
    return "hit"

def parse_card_val(card_str: str) -> int:
    card_str = card_str.upper().strip()
    if card_str in ['J', 'Q', 'K', '10']:
        return 10
    elif card_str == 'A':
        return 11
    else:
        try:
            return int(card_str)
        except:
            return 0

def get_basic_strategy(player_hand: str, dealer_upcard: str, preset: BlackjackRulePreset) -> StrategyRecommendation:
    """
    player_hand format: "16", "Soft 17", "Pair 8"
    dealer_upcard format: "10", "A", "5"
    """
    dealer_val = parse_card_val(dealer_upcard)
    
    player_hand = player_hand.lower().strip()
    
    # Check Surrender first if applicable
    if preset.surrender_type == "late":
        if player_hand == "16" and dealer_val in [9, 10, 11]:
            return StrategyRecommendation(recommended_action="surrender", explanation="16 vs 9, 10, A is late surrender.")
        if player_hand == "15" and dealer_val == 10:
            return StrategyRecommendation(recommended_action="surrender", explanation="15 vs 10 is late surrender.")
    
    action = "hit"
    explanation = ""
    
    if player_hand.startswith("pair"):
        val_str = player_hand.replace("pair", "").strip()
        pair_val = parse_card_val(val_str)
        action = get_pair_action(pair_val, dealer_val, preset.double_after_split_allowed)
        explanation = f"Pair of {val_str}s vs {dealer_upcard}: {action.capitalize()}"
    elif player_hand.startswith("soft"):
        total_str = player_hand.replace("soft", "").strip()
        total = int(total_str)
        other_card = total - 11
        action = get_soft_total_action(other_card, dealer_val)
        explanation = f"Soft {total} vs {dealer_upcard}: {action.capitalize()}"
    else:
        total = int(player_hand)
        action = get_hard_total_action(total, dealer_val)
        explanation = f"Hard {total} vs {dealer_upcard}: {action.capitalize()}"

    # If action is double but we can't double (e.g. some presets might restrict it, though generally allowed on first two cards)
    # We will assume double is allowed. If not, fallback to hit/stand.
    
    return StrategyRecommendation(recommended_action=action, explanation=explanation)
