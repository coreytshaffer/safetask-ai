import pytest
from pitlens.blackjack.strategy import get_basic_strategy
from pitlens.models import BlackjackRulePreset

@pytest.fixture
def preset_6d_h17():
    return BlackjackRulePreset(
        preset_id="test", name="test", deck_count=6, dealer_hits_soft_17=True,
        double_after_split_allowed=True, surrender_type="late", resplit_aces_allowed=False,
        blackjack_payout="3:2", side_bets=[]
    )

def test_hard_total_stand(preset_6d_h17):
    rec = get_basic_strategy("17", "10", preset_6d_h17)
    assert rec.recommended_action == "stand"

def test_hard_total_hit(preset_6d_h17):
    rec = get_basic_strategy("15", "10", preset_6d_h17)
    assert rec.recommended_action == "surrender" # 15 vs 10 is surrender in H17 late surrender

def test_hard_total_double(preset_6d_h17):
    rec = get_basic_strategy("11", "5", preset_6d_h17)
    assert rec.recommended_action == "double"

def test_soft_total(preset_6d_h17):
    rec = get_basic_strategy("Soft 18", "9", preset_6d_h17)
    assert rec.recommended_action == "hit"

def test_pair_split(preset_6d_h17):
    rec = get_basic_strategy("Pair 8", "10", preset_6d_h17)
    assert rec.recommended_action == "split"

def test_late_surrender(preset_6d_h17):
    rec = get_basic_strategy("16", "10", preset_6d_h17)
    assert rec.recommended_action == "surrender"
