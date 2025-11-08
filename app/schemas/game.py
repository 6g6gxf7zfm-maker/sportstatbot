"""Game Pydantic schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GameBase(BaseModel):
    """Base game schema"""
    home_team_id: int
    away_team_id: int
    league: str
    season: str
    season_type: str
    game_date: datetime


class GameCreate(GameBase):
    """Schema for creating a new game"""
    external_id: str
    week: Optional[int] = None
    venue: Optional[str] = None
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    wind_speed: Optional[float] = None
    humidity: Optional[float] = None
    is_indoor: bool = True
    is_rivalry: bool = False
    is_playoff: bool = False
    playoff_round: Optional[str] = None


class GameUpdate(BaseModel):
    """Schema for updating a game"""
    status: Optional[str] = None
    current_period: Optional[int] = None
    time_remaining: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    period_scores: Optional[dict] = None
    home_rest_days: Optional[int] = None
    away_rest_days: Optional[int] = None
    attendance: Optional[int] = None


class GameResponse(GameBase):
    """Schema for game response"""
    id: int
    external_id: str
    week: Optional[int] = None
    venue: Optional[str] = None
    status: str
    current_period: Optional[int] = None
    time_remaining: Optional[str] = None
    home_score: int
    away_score: int
    period_scores: Optional[dict] = None
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    wind_speed: Optional[float] = None
    humidity: Optional[float] = None
    is_indoor: bool
    is_rivalry: bool
    is_playoff: bool
    playoff_round: Optional[str] = None
    home_rest_days: Optional[int] = None
    away_rest_days: Optional[int] = None
    attendance: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayByPlayEvent(BaseModel):
    """Schema for play-by-play event"""
    sequence_number: int
    period: int
    time_elapsed: float
    play_type: str
    play_description: str
    is_scoring_play: bool = False
    expected_points: Optional[float] = None
    win_probability_home: Optional[float] = None
    win_probability_away: Optional[float] = None

    class Config:
        from_attributes = True
