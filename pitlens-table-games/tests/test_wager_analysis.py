import pytest
from pitlens.blackjack.wager_analysis import calculate_bet_spread, generate_wager_review_flags
from pitlens.models import Wager

def test_calculate_bet_spread():
    wagers = [
        Wager(wager_id="1", round_id="r1", seat_number=1, main_bet_amount=25.0, source="system", reviewer_confirmed=True),
        Wager(wager_id="2", round_id="r2", seat_number=1, main_bet_amount=50.0, source="system", reviewer_confirmed=True),
        Wager(wager_id="3", round_id="r3", seat_number=1, main_bet_amount=200.0, source="system", reviewer_confirmed=True),
    ]
    
    spread = calculate_bet_spread(wagers)
    assert spread["min_bet"] == 25.0
    assert spread["max_bet"] == 200.0
    assert spread["spread_ratio"] == "8:1"
    assert spread["largest_increase"] == 150.0
    assert spread["increases_count"] == 2
    assert spread["decreases_count"] == 0

def test_unconfirmed_wagers_excluded():
    wagers = [
        Wager(wager_id="1", round_id="r1", seat_number=1, main_bet_amount=25.0, source="system", reviewer_confirmed=True),
        Wager(wager_id="2", round_id="r2", seat_number=1, main_bet_amount=1000.0, source="system", reviewer_confirmed=False),
    ]
    spread = calculate_bet_spread(wagers)
    assert spread["max_bet"] == 25.0
    assert spread["unconfirmed_count"] == 1

def test_wager_review_flags():
    wagers = [
        Wager(wager_id="1", round_id="r1", seat_number=1, main_bet_amount=25.0, source="system", reviewer_confirmed=True),
        Wager(wager_id="2", round_id="r2", seat_number=1, main_bet_amount=250.0, source="system", reviewer_confirmed=True), # 10x increase
    ]
    flags = generate_wager_review_flags("session1", wagers)
    
    # Should flag sudden wager increase
    assert len(flags) > 0
    assert any(f.flag_type == "Sudden Wager Increase" for f in flags)
