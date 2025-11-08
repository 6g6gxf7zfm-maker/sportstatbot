"""Game and play-by-play database models"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Float, Boolean, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from app.core.database import Base


class GameStatus(str, Enum):
    """Game status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    HALFTIME = "halftime"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Game(Base):
    """Game entity model"""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)

    # Teams
    home_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )
    away_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )

    # Game info
    league: Mapped[str] = mapped_column(String, index=True)
    season: Mapped[str] = mapped_column(String, index=True)
    season_type: Mapped[str] = mapped_column(String)  # regular, playoffs, preseason
    week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    game_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    venue: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(GameStatus, native_enum=False),
        default=GameStatus.SCHEDULED,
        index=True
    )
    current_period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_remaining: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Scores
    home_score: Mapped[int] = mapped_column(Integer, default=0)
    away_score: Mapped[int] = mapped_column(Integer, default=0)
    period_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Environmental conditions
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weather_condition: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_indoor: Mapped[bool] = mapped_column(Boolean, default=True)

    # Officials
    referee_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    officials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Context
    is_rivalry: Mapped[bool] = mapped_column(Boolean, default=False)
    is_playoff: Mapped[bool] = mapped_column(Boolean, default=False)
    playoff_round: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attendance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Rest days
    home_rest_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_rest_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    broadcast_network: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    game_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    home_team: Mapped["Team"] = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_games"
    )
    away_team: Mapped["Team"] = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_games"
    )
    events: Mapped[list["GameEvent"]] = relationship(
        "GameEvent", back_populates="game", cascade="all, delete-orphan"
    )
    play_by_play: Mapped[list["PlayByPlay"]] = relationship(
        "PlayByPlay", back_populates="game", cascade="all, delete-orphan"
    )
    momentum_events: Mapped[list["MomentumEvent"]] = relationship(
        "MomentumEvent", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game {self.away_team_id} @ {self.home_team_id} on {self.game_date}>"


class GameEvent(Base):
    """Game events (goals, touchdowns, major plays)"""

    __tablename__ = "game_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id"), index=True
    )

    # Event details
    event_type: Mapped[str] = mapped_column(String, index=True)  # goal, touchdown, penalty, etc.
    period: Mapped[int] = mapped_column(Integer)
    time_elapsed: Mapped[float] = mapped_column(Float)  # seconds
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )
    player_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id"), nullable=True, index=True
    )

    # Event data
    description: Mapped[str] = mapped_column(Text)
    score_value: Mapped[int] = mapped_column(Integer, default=0)
    home_score_after: Mapped[int] = mapped_column(Integer)
    away_score_after: Mapped[int] = mapped_column(Integer)

    # Additional context
    coordinates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # x, y position
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="events")

    def __repr__(self) -> str:
        return f"<GameEvent {self.event_type} at {self.time_elapsed}s>"


class PlayByPlay(Base):
    """Detailed play-by-play tracking (second-by-second)"""

    __tablename__ = "play_by_play"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id"), index=True
    )

    # Play details
    sequence_number: Mapped[int] = mapped_column(Integer, index=True)
    period: Mapped[int] = mapped_column(Integer)
    time_elapsed: Mapped[float] = mapped_column(Float, index=True)  # seconds
    time_remaining: Mapped[float] = mapped_column(Float)  # seconds

    # Team and players
    offensive_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=True
    )
    defensive_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=True
    )
    players_involved: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Play info
    play_type: Mapped[str] = mapped_column(String, index=True)
    play_description: Mapped[str] = mapped_column(Text)
    is_scoring_play: Mapped[bool] = mapped_column(Boolean, default=False)

    # Position/field data
    start_position: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    end_position: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Advanced metrics (calculated)
    expected_points: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    win_probability_home: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    win_probability_away: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    leverage_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Sport-specific data
    sport_specific_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="play_by_play")

    def __repr__(self) -> str:
        return f"<PlayByPlay #{self.sequence_number} - {self.play_type}>"
