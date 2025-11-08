"""Player Pydantic schemas"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
    """Base player schema"""
    first_name: str
    last_name: str
    full_name: str
    position: Optional[str] = None
    jersey_number: Optional[int] = None


class PlayerCreate(PlayerBase):
    """Schema for creating a new player"""
    external_id: str
    team_id: Optional[int] = None
    height_inches: Optional[int] = None
    weight_pounds: Optional[int] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    draft_year: Optional[int] = None
    draft_round: Optional[int] = None
    draft_pick: Optional[int] = None
    years_pro: Optional[int] = None
    college: Optional[str] = None
    is_rookie: bool = False


class PlayerUpdate(BaseModel):
    """Schema for updating a player"""
    team_id: Optional[int] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    is_active: Optional[bool] = None
    is_injured: Optional[bool] = None
    injury_status: Optional[str] = None
    injury_return_date: Optional[date] = None
    contract_year: Optional[bool] = None
    games_played: Optional[int] = None
    games_started: Optional[int] = None
    minutes_played: Optional[float] = None


class PlayerResponse(PlayerBase):
    """Schema for player response"""
    id: int
    external_id: str
    team_id: Optional[int] = None
    height_inches: Optional[int] = None
    weight_pounds: Optional[int] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    draft_year: Optional[int] = None
    years_pro: Optional[int] = None
    college: Optional[str] = None
    is_active: bool
    is_injured: bool
    injury_status: Optional[str] = None
    is_rookie: bool
    contract_year: bool
    games_played: int
    games_started: int
    minutes_played: float
    headshot_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
