from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class GameType(str, Enum):
    BLACKJACK = "blackjack"
    PAI_GOW = "pai_gow_poker"
    BACCARAT = "baccarat"

class Reviewer(BaseModel):
    reviewer_id: str
    name: str

class GameSession(BaseModel):
    session_id: str
    game_type: GameType
    property_name_optional: Optional[str] = None
    table_id_optional: Optional[str] = None
    reviewer_name_optional: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BlackjackRulePreset(BaseModel):
    preset_id: str
    name: str
    deck_count: int
    dealer_hits_soft_17: bool
    double_after_split_allowed: bool
    surrender_type: str  # "late", "early", "none"
    resplit_aces_allowed: bool
    blackjack_payout: str  # "3:2", "6:5"
    side_bets: List[str]
    notes: Optional[str] = None

class Round(BaseModel):
    round_id: str
    session_id: str
    round_number: int
    timestamp_optional: Optional[str] = None
    shoe_round_number_optional: Optional[int] = None
    notes: Optional[str] = None

class ActiveBetShot(BaseModel):
    active_bet_shot_id: str
    round_id: str
    seat_number: int
    source_type: str  # "video_frame", "screenshot", "manual_only"
    frame_timestamp_optional: Optional[str] = None
    file_reference_optional: Optional[str] = None
    reviewer_confirmed: bool
    usable: bool
    obstruction_notes: Optional[str] = None
    confidence_label: str  # "high", "medium", "low", "not_applicable"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Wager(BaseModel):
    wager_id: str
    round_id: str
    seat_number: int
    main_bet_amount: float
    side_bet_amount_optional: Optional[float] = None
    source: str  # "reviewer_confirmed_active_bet_shot", "system_estimate", "manual_entry", "no_usable_shot"
    confidence_score_optional: Optional[float] = None
    reviewer_confirmed: bool
    notes: Optional[str] = None

class PlayerDecision(BaseModel):
    decision_id: str
    round_id: str
    seat_number: int
    player_total: str  # e.g., "16", "Soft 17", "Pair of 8s"
    dealer_upcard: str # e.g., "10", "A"
    hand_type: str  # "hard", "soft", "pair"
    observed_action: str  # "hit", "stand", "double", "split", "surrender", "insurance", "unknown"
    recommended_action: str
    deviation_flag: bool
    deviation_severity: str  # "low", "medium", "high", "none"
    notes: Optional[str] = None

class StrategyRecommendation(BaseModel):
    recommended_action: str
    explanation: str

class ReviewFlag(BaseModel):
    flag_id: str
    session_id: str
    round_id_optional: Optional[str] = None
    seat_number_optional: Optional[int] = None
    flag_type: str
    severity: str
    system_generated: bool
    reviewer_confirmed: bool
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Report(BaseModel):
    report_id: str
    session_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    content: str  # HTML content
