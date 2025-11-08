"""Team Pydantic schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    """Base team schema"""
    name: str = Field(..., description="Team name")
    abbreviation: str = Field(..., max_length=10, description="Team abbreviation")
    city: str = Field(..., description="City")
    league: str = Field(..., description="League name")
    conference: Optional[str] = Field(None, description="Conference")
    division: Optional[str] = Field(None, description="Division")


class TeamCreate(TeamBase):
    """Schema for creating a new team"""
    external_id: str = Field(..., description="External API ID")
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    venue_type: Optional[str] = None
    venue_surface: Optional[str] = None
    altitude_feet: Optional[int] = None
    logo_url: Optional[str] = None
    colors: Optional[dict] = None
    founded_year: Optional[int] = None


class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    city: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    ties: Optional[int] = None
    win_percentage: Optional[float] = None


class TeamResponse(TeamBase):
    """Schema for team response"""
    id: int
    external_id: str
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    venue_type: Optional[str] = None
    venue_surface: Optional[str] = None
    altitude_feet: Optional[int] = None
    wins: int
    losses: int
    ties: Optional[int] = None
    win_percentage: float
    logo_url: Optional[str] = None
    colors: Optional[dict] = None
    founded_year: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
