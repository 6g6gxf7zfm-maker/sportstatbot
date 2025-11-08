"""Team database model"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Team(Base):
    """Team entity model"""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    abbreviation: Mapped[str] = mapped_column(String(10))
    city: Mapped[str] = mapped_column(String)
    league: Mapped[str] = mapped_column(String, index=True)
    conference: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    division: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Stadium/Arena information
    venue_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    venue_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    venue_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # indoor, outdoor
    venue_surface: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # grass, turf, court
    altitude_feet: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Current season stats
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    ties: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    win_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    # Metadata
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    colors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    players: Mapped[list["Player"]] = relationship(
        "Player", back_populates="team", lazy="selectin"
    )
    home_games: Mapped[list["Game"]] = relationship(
        "Game", foreign_keys="Game.home_team_id", back_populates="home_team"
    )
    away_games: Mapped[list["Game"]] = relationship(
        "Game", foreign_keys="Game.away_team_id", back_populates="away_team"
    )
    metrics: Mapped[list["TeamMetrics"]] = relationship(
        "TeamMetrics", back_populates="team", lazy="selectin"
    )
    identity: Mapped[Optional["TeamIdentity"]] = relationship(
        "TeamIdentity", back_populates="team", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Team {self.name} ({self.abbreviation})>"
