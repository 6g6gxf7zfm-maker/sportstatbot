"""Analytics API endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics.player_chemistry import PlayerChemistryAnalyzer
from app.services.analytics.form_trajectory import FormTrajectoryPredictor
from app.services.analytics.injury_simulator import InjuryImpactSimulator
from app.schemas.analytics import (
    PlayerChemistryResponse,
    FormTrajectoryResponse,
    InjuryImpactResponse,
    TeamIdentityResponse,
    ScheduleDifficultyResponse,
    ClutchPerformanceResponse
)

router = APIRouter()


@router.get("/chemistry/{player_id}", response_model=List[PlayerChemistryResponse])
async def get_player_chemistry(
    player_id: int,
    season: str,
    db: AsyncSession = Depends(get_db)
):
    """Get player chemistry scores with teammates"""
    analyzer = PlayerChemistryAnalyzer(db)

    # Would retrieve existing chemistry records
    # This is a placeholder
    return []


@router.post("/chemistry/calculate")
async def calculate_chemistry(
    player_id: int,
    teammate_id: int,
    season: str,
    db: AsyncSession = Depends(get_db)
):
    """Calculate chemistry between two players"""
    analyzer = PlayerChemistryAnalyzer(db)

    try:
        chemistry = await analyzer.calculate_chemistry(
            player_id, teammate_id, season
        )
        return {
            "player_id": chemistry.player_id,
            "teammate_id": chemistry.teammate_id,
            "chemistry_score": chemistry.chemistry_score,
            "synergy_rating": chemistry.synergy_rating
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lineup/best-combinations")
async def get_best_lineups(
    team_id: int,
    lineup_size: int = 5,
    min_minutes: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get best performing lineup combinations for a team"""
    analyzer = PlayerChemistryAnalyzer(db)

    lineups = await analyzer.find_best_lineups(
        team_id, lineup_size, min_minutes
    )

    return {"lineups": lineups}


@router.get("/player-similarity/{player_id}")
async def get_similar_players(
    player_id: int,
    n_similar: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Find players similar to the given player"""
    analyzer = PlayerChemistryAnalyzer(db)

    similar_players = await analyzer.get_player_similarity(
        player_id, n_similar
    )

    return {"similar_players": similar_players}


@router.get("/form-trajectory/{team_id}", response_model=FormTrajectoryResponse)
async def get_form_trajectory(
    team_id: int,
    forecast_games: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """Get team form trajectory and forecast"""
    predictor = FormTrajectoryPredictor(db)

    try:
        trajectory = await predictor.calculate_form_trajectory(
            team_id, forecast_games
        )
        return trajectory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/injury-impact/simulate")
async def simulate_injury(
    player_id: int,
    injury_type: str,
    expected_games_missed: int,
    replacement_player_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Simulate the impact of a player injury"""
    simulator = InjuryImpactSimulator(db)

    try:
        impact = await simulator.simulate_injury_impact(
            player_id,
            injury_type,
            expected_games_missed,
            replacement_player_id
        )

        return {
            "player_id": impact.player_id,
            "team_id": impact.team_id,
            "injury_type": impact.injury_type,
            "games_missed": impact.games_missed,
            "win_pct_change": impact.win_pct_change,
            "severity_score": impact.severity_score,
            "offensive_impact": impact.offensive_impact,
            "defensive_impact": impact.defensive_impact,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/injury-report/{team_id}")
async def get_injury_report(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive injury report for a team"""
    simulator = InjuryImpactSimulator(db)

    report = await simulator.get_team_injury_report(team_id)

    return report


@router.get("/momentum/{game_id}")
async def get_game_momentum(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time momentum data for a game"""
    from sqlalchemy import select
    from app.models import MomentumEvent

    result = await db.execute(
        select(MomentumEvent)
        .where(MomentumEvent.game_id == game_id)
        .order_by(MomentumEvent.timestamp.desc())
        .limit(100)
    )

    momentum_events = result.scalars().all()

    if not momentum_events:
        return {"game_id": game_id, "events": []}

    return {
        "game_id": game_id,
        "current_momentum": {
            "home": momentum_events[0].home_momentum,
            "away": momentum_events[0].away_momentum,
            "excitement_index": momentum_events[0].excitement_index,
        },
        "events": [
            {
                "timestamp": event.timestamp,
                "home_momentum": event.home_momentum,
                "away_momentum": event.away_momentum,
                "swing_magnitude": event.momentum_swing,
                "swing_direction": event.swing_direction,
            }
            for event in momentum_events[:20]
        ]
    }


@router.get("/schedule-difficulty/{team_id}")
async def get_schedule_difficulty(
    team_id: int,
    upcoming_games: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Analyze upcoming schedule difficulty"""
    # Placeholder implementation
    return {
        "team_id": team_id,
        "upcoming_games": upcoming_games,
        "avg_opponent_rating": 0.520,
        "difficulty_score": 6.5,
        "expected_wins": 6.2,
        "expected_losses": 3.8,
        "toughest_stretch": {
            "games": "15-20",
            "avg_opponent_rating": 0.650
        }
    }


@router.get("/clutch-performance/{player_id}")
async def get_clutch_performance(
    player_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get player clutch performance statistics"""
    from sqlalchemy import select
    from app.models import Player, PlayerMetrics

    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Get recent clutch metrics
    metrics_result = await db.execute(
        select(PlayerMetrics)
        .where(PlayerMetrics.player_id == player_id)
        .order_by(PlayerMetrics.date.desc())
        .limit(10)
    )

    metrics = metrics_result.scalars().all()

    if not metrics:
        return {
            "player_id": player_id,
            "player_name": player.full_name,
            "clutch_situations": 0,
            "clutch_success_rate": 0,
            "clutch_points": 0,
            "clutch_index": 1.0,
            "pressure_rating": 50.0
        }

    avg_clutch_index = sum(m.clutch_index or 1.0 for m in metrics) / len(metrics)
    avg_clutch_points = sum(m.clutch_points or 0 for m in metrics) / len(metrics)

    return {
        "player_id": player_id,
        "player_name": player.full_name,
        "clutch_situations": len(metrics) * 5,  # Placeholder
        "clutch_success_rate": 0.45,
        "clutch_points": avg_clutch_points,
        "clutch_index": avg_clutch_index,
        "pressure_rating": (avg_clutch_index - 1.0) * 50 + 50
    }
