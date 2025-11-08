"""Analytics Pydantic schemas"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class TeamMetricsResponse(BaseModel):
    """Schema for team metrics response"""
    id: int
    team_id: int
    game_id: Optional[int] = None
    date: date
    offensive_rating: Optional[float] = None
    expected_points_added: Optional[float] = None
    success_rate: Optional[float] = None
    expected_goals: Optional[float] = None
    completion_percentage_over_expected: Optional[float] = None
    defensive_rating: Optional[float] = None
    pace: Optional[float] = None
    pythagorean_wins: Optional[float] = None
    luck_index: Optional[float] = None
    opponent_strength: Optional[float] = None
    sport_specific_metrics: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerMetricsResponse(BaseModel):
    """Schema for player metrics response"""
    id: int
    player_id: int
    game_id: Optional[int] = None
    date: date
    plus_minus: Optional[float] = None
    offensive_rating: Optional[float] = None
    defensive_rating: Optional[float] = None
    usage_rate: Optional[float] = None
    clutch_index: Optional[float] = None
    expected_goals: Optional[float] = None
    goals_above_expected: Optional[float] = None
    performance_vs_average: Optional[float] = None
    sport_specific_stats: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerChemistryResponse(BaseModel):
    """Schema for player chemistry response"""
    id: int
    player_id: int
    teammate_id: int
    season: str
    chemistry_score: float
    shared_minutes: float
    plus_minus_together: float
    offensive_synergy: float
    defensive_synergy: float
    games_together: int
    synergy_rating: Optional[float] = None

    class Config:
        from_attributes = True


class MomentumEventResponse(BaseModel):
    """Schema for momentum event response"""
    id: int
    game_id: int
    timestamp: datetime
    game_time_elapsed: float
    period: int
    home_momentum: float
    away_momentum: float
    momentum_swing: float
    swing_direction: str
    score_differential: int
    win_probability_home: float
    win_probability_away: float
    excitement_index: float

    class Config:
        from_attributes = True


class FormTrajectoryResponse(BaseModel):
    """Schema for form trajectory response"""
    id: int
    team_id: int
    calculation_date: date
    recent_record: str
    form_score: float
    trend_direction: str
    points_trend: float
    offensive_trend: float
    defensive_trend: float
    forecast_wins: float
    forecast_losses: float
    win_probability_next_game: float
    projected_performance: dict
    forecast_confidence: float

    class Config:
        from_attributes = True


class InjuryImpactResponse(BaseModel):
    """Schema for injury impact response"""
    id: int
    player_id: int
    team_id: int
    injury_date: date
    injury_type: str
    expected_return_date: Optional[date] = None
    games_missed: int
    player_value_lost: float
    team_win_pct_before: float
    team_win_pct_projected: float
    win_pct_change: float
    offensive_impact: float
    defensive_impact: float
    severity_score: float

    class Config:
        from_attributes = True


class TeamIdentityResponse(BaseModel):
    """Schema for team identity response"""
    id: int
    team_id: int
    season: str
    identity_type: str
    identity_score: float
    pace_rating: float
    offensive_style: str
    defensive_style: str
    primary_strengths: List[str]
    primary_weaknesses: List[str]
    style_consistency: float
    adaptability_score: float

    class Config:
        from_attributes = True


class ScheduleDifficultyResponse(BaseModel):
    """Schema for schedule difficulty analysis"""
    team_id: int
    upcoming_games: int
    avg_opponent_rating: float
    difficulty_score: float
    expected_wins: float
    expected_losses: float
    toughest_stretch: dict


class ClutchPerformanceResponse(BaseModel):
    """Schema for clutch performance stats"""
    player_id: int
    player_name: str
    clutch_situations: int
    clutch_success_rate: float
    clutch_points: float
    clutch_index: float
    pressure_rating: float
