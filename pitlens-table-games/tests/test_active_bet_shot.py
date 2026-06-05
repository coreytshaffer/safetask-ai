import pytest
from pitlens.review.active_bet_shot import validate_active_bet_shot
from pitlens.models import ActiveBetShot

def test_active_bet_shot_valid():
    shot = ActiveBetShot(
        active_bet_shot_id="1", round_id="r1", seat_number=1, source_type="video",
        reviewer_confirmed=True, usable=True, confidence_label="high"
    )
    valid, reason = validate_active_bet_shot(shot)
    assert valid is True
    assert reason is None

def test_active_bet_shot_unusable():
    shot = ActiveBetShot(
        active_bet_shot_id="2", round_id="r1", seat_number=1, source_type="video",
        reviewer_confirmed=True, usable=False, confidence_label="high"
    )
    valid, reason = validate_active_bet_shot(shot)
    assert valid is False
    assert "unusable" in reason.lower()

def test_active_bet_shot_unconfirmed_low_conf():
    shot = ActiveBetShot(
        active_bet_shot_id="3", round_id="r1", seat_number=1, source_type="video",
        reviewer_confirmed=False, usable=True, confidence_label="low"
    )
    valid, reason = validate_active_bet_shot(shot)
    assert valid is False
    assert "unconfirmed" in reason.lower()
