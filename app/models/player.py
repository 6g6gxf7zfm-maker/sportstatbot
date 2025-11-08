"""Player database model"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Player(Base):
    """Player entity model"""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String, index=True)
    full_name: Mapped[str] = mapped_column(String, index=True)

    # Team association
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=True, index=True
    )

    # Personal info
    jersey_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    height_inches: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_pounds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Career info
    draft_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    draft_round: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    draft_pick: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    years_pro: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    college: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Contract info
    contract_year: Mapped[bool] = mapped_column(Boolean, default=False)
    contract_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contract_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Current season stats (basic - sport-specific stats in PlayerMetrics)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    games_started: Mapped[int] = mapped_column(Integer, default=0)
    minutes_played: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_injured: Mapped[bool] = mapped_column(Boolean, default=False)
    injury_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    injury_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_rookie: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    headshot_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    additional_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    team: Mapped[Optional["Team"]] = relationship(
        "Team", back_populates="players"
    )
    metrics: Mapped[list["PlayerMetrics"]] = relationship(
        "PlayerMetrics", back_populates="player", lazy="selectin"
    )
    chemistry_scores: Mapped[list["PlayerChemistry"]] = relationship(
        "PlayerChemistry",
        foreign_keys="PlayerChemistry.player_id",
        back_populates="player"
    )

    def __repr__(self) -> str:
        return f"<Player {self.full_name} (#{self.jersey_number})>"
