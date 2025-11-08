"""Analytics and metrics database models"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Date, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TeamMetrics(Base):
    """Advanced team metrics per game or time period"""

    __tablename__ = "team_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )
    game_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("games.id"), nullable=True, index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)

    # Offensive metrics
    offensive_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_points_added: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # EPA
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_goals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # xG
    completion_percentage_over_expected: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # CPOE

    # Defensive metrics
    defensive_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_points_allowed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    defensive_success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Efficiency metrics
    pace: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    possessions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    turnover_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effective_field_goal_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Luck metrics
    pythagorean_wins: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pythagorean_losses: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    luck_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Strength of schedule
    opponent_strength: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sos_weighted: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Sport-specific metrics
    sport_specific_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="metrics")

    def __repr__(self) -> str:
        return f"<TeamMetrics team_id={self.team_id} date={self.date}>"


class PlayerMetrics(Base):
    """Advanced player metrics per game or time period"""

    __tablename__ = "player_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id"), index=True
    )
    game_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("games.id"), nullable=True, index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)

    # Performance metrics
    plus_minus: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    offensive_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    defensive_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    usage_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    true_shooting_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Clutch performance (4th quarter/overtime)
    clutch_points: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clutch_efficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clutch_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Shot quality
    expected_goals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    goals_above_expected: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shot_quality_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Contract year boost
    is_contract_year: Mapped[bool] = mapped_column(Float, default=False)
    performance_vs_average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Sport-specific stats
    sport_specific_stats: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="metrics")

    def __repr__(self) -> str:
        return f"<PlayerMetrics player_id={self.player_id} date={self.date}>"


class PlayerChemistry(Base):
    """Player chemistry and synergy scores"""

    __tablename__ = "player_chemistry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id"), index=True
    )
    teammate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id"), index=True
    )
    season: Mapped[str] = mapped_column(String, index=True)

    # Chemistry metrics
    chemistry_score: Mapped[float] = mapped_column(Float)
    shared_minutes: Mapped[float] = mapped_column(Float)
    plus_minus_together: Mapped[float] = mapped_column(Float)
    offensive_synergy: Mapped[float] = mapped_column(Float)
    defensive_synergy: Mapped[float] = mapped_column(Float)

    # Additional analysis
    games_together: Mapped[int] = mapped_column(Integer)
    assist_connection: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    synergy_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    player: Mapped["Player"] = relationship(
        "Player",
        foreign_keys=[player_id],
        back_populates="chemistry_scores"
    )

    def __repr__(self) -> str:
        return f"<PlayerChemistry player_id={self.player_id} teammate_id={self.teammate_id}>"


class MomentumEvent(Base):
    """Real-time momentum swing tracking"""

    __tablename__ = "momentum_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id"), index=True
    )

    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    game_time_elapsed: Mapped[float] = mapped_column(Float)
    period: Mapped[int] = mapped_column(Integer)

    # Momentum data
    home_momentum: Mapped[float] = mapped_column(Float)  # -1 to 1
    away_momentum: Mapped[float] = mapped_column(Float)  # -1 to 1
    momentum_swing: Mapped[float] = mapped_column(Float)  # magnitude of change
    swing_direction: Mapped[str] = mapped_column(String)  # home, away

    # Contributing factors
    trigger_event_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    trigger_event_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score_differential: Mapped[int] = mapped_column(Integer)

    # Calculated metrics
    win_probability_home: Mapped[float] = mapped_column(Float)
    win_probability_away: Mapped[float] = mapped_column(Float)
    excitement_index: Mapped[float] = mapped_column(Float)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="momentum_events")

    def __repr__(self) -> str:
        return f"<MomentumEvent game_id={self.game_id} swing={self.momentum_swing}>"


class FormTrajectory(Base):
    """Form trajectory and trend forecasting"""

    __tablename__ = "form_trajectories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )
    calculation_date: Mapped[date] = mapped_column(Date, index=True)

    # Current form (last N games)
    recent_record: Mapped[str] = mapped_column(String)  # e.g., "W-W-L-W-L"
    form_score: Mapped[float] = mapped_column(Float)  # 0-100
    trend_direction: Mapped[str] = mapped_column(String)  # improving, declining, stable

    # Performance trends
    points_trend: Mapped[float] = mapped_column(Float)
    offensive_trend: Mapped[float] = mapped_column(Float)
    defensive_trend: Mapped[float] = mapped_column(Float)

    # Forecasts (next 5 games)
    forecast_wins: Mapped[float] = mapped_column(Float)
    forecast_losses: Mapped[float] = mapped_column(Float)
    win_probability_next_game: Mapped[float] = mapped_column(Float)
    projected_performance: Mapped[dict] = mapped_column(JSON)

    # Confidence
    forecast_confidence: Mapped[float] = mapped_column(Float)
    model_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<FormTrajectory team_id={self.team_id} trend={self.trend_direction}>"


class InjuryImpact(Base):
    """Injury impact simulation and analysis"""

    __tablename__ = "injury_impacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id"), index=True
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )

    # Injury details
    injury_date: Mapped[date] = mapped_column(Date)
    injury_type: Mapped[str] = mapped_column(String)
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    games_missed: Mapped[int] = mapped_column(Integer, default=0)

    # Impact analysis
    player_value_lost: Mapped[float] = mapped_column(Float)  # WAR or similar
    team_win_pct_before: Mapped[float] = mapped_column(Float)
    team_win_pct_projected: Mapped[float] = mapped_column(Float)
    win_pct_change: Mapped[float] = mapped_column(Float)

    # Replacement analysis
    replacement_player_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id"), nullable=True
    )
    replacement_efficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Offensive/defensive impact
    offensive_impact: Mapped[float] = mapped_column(Float)
    defensive_impact: Mapped[float] = mapped_column(Float)

    # Additional context
    severity_score: Mapped[float] = mapped_column(Float)  # 0-10
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<InjuryImpact player_id={self.player_id} impact={self.win_pct_change}>"


class RefereeStats(Base):
    """Referee bias and statistics tracking"""

    __tablename__ = "referee_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    referee_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    referee_name: Mapped[str] = mapped_column(String)
    season: Mapped[str] = mapped_column(String, index=True)

    # Games officiated
    games_officiated: Mapped[int] = mapped_column(Integer)

    # Foul/penalty metrics
    avg_fouls_per_game: Mapped[float] = mapped_column(Float)
    avg_penalties_per_game: Mapped[float] = mapped_column(Float)
    home_team_foul_rate: Mapped[float] = mapped_column(Float)
    away_team_foul_rate: Mapped[float] = mapped_column(Float)
    foul_differential: Mapped[float] = mapped_column(Float)

    # Bias indicators
    home_team_win_pct: Mapped[float] = mapped_column(Float)
    away_team_win_pct: Mapped[float] = mapped_column(Float)
    home_bias_score: Mapped[float] = mapped_column(Float)  # statistical deviation

    # Technical calls
    technical_fouls_called: Mapped[int] = mapped_column(Integer, default=0)
    ejections: Mapped[int] = mapped_column(Integer, default=0)

    # Additional stats
    avg_game_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    controversial_calls: Mapped[int] = mapped_column(Integer, default=0)
    additional_stats: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<RefereeStats {self.referee_name} ({self.season})>"


class CoachingProfile(Base):
    """Coaching style profiles and analytics"""

    __tablename__ = "coaching_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coach_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    coach_name: Mapped[str] = mapped_column(String, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), index=True
    )
    season: Mapped[str] = mapped_column(String, index=True)

    # Coaching style
    tempo_preference: Mapped[float] = mapped_column(Float)  # 0-100, slow to fast
    aggressiveness: Mapped[float] = mapped_column(Float)  # 0-100
    risk_tolerance: Mapped[float] = mapped_column(Float)  # 0-100

    # Strategy metrics
    offensive_scheme: Mapped[str] = mapped_column(String)
    defensive_scheme: Mapped[str] = mapped_column(String)
    avg_substitutions_per_game: Mapped[float] = mapped_column(Float)
    rotation_size: Mapped[int] = mapped_column(Integer)

    # Decision-making
    fourth_down_aggression: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timeout_usage_efficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    challenge_success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Results
    win_percentage: Mapped[float] = mapped_column(Float)
    playoff_record: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    years_experience: Mapped[int] = mapped_column(Integer)

    # Situational coaching
    close_game_record: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    halftime_adjustment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Additional data
    coaching_tree: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    additional_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<CoachingProfile {self.coach_name}>"


class TeamIdentity(Base):
    """Team identity and playing style analysis"""

    __tablename__ = "team_identities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), unique=True, index=True
    )
    season: Mapped[str] = mapped_column(String, index=True)

    # Identity classification
    identity_type: Mapped[str] = mapped_column(String)  # e.g., "pace & space", "grind & defend"
    identity_score: Mapped[float] = mapped_column(Float)  # confidence in classification

    # Style metrics
    pace_rating: Mapped[float] = mapped_column(Float)  # 0-100
    offensive_style: Mapped[str] = mapped_column(String)
    defensive_style: Mapped[str] = mapped_column(String)

    # Tendencies
    three_point_reliance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    paint_presence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ball_movement: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    defensive_pressure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Strengths & weaknesses
    primary_strengths: Mapped[list] = mapped_column(JSON)
    primary_weaknesses: Mapped[list] = mapped_column(JSON)

    # Matchup analysis
    best_against: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    worst_against: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Consistency
    style_consistency: Mapped[float] = mapped_column(Float)  # how consistent is their identity
    adaptability_score: Mapped[float] = mapped_column(Float)  # how much they adjust

    # Additional analysis
    identity_evolution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    additional_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="identity")

    def __repr__(self) -> str:
        return f"<TeamIdentity team_id={self.team_id} type={self.identity_type}>"
