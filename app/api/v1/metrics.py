"""Metrics API endpoints"""

from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import TeamMetrics, PlayerMetrics
from app.services.analytics.metrics_engine import MetricsEngine
from app.schemas.analytics import TeamMetricsResponse, PlayerMetricsResponse

router = APIRouter()


@router.get("/team/{team_id}", response_model=List[TeamMetricsResponse])
async def get_team_metrics(
    team_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get team metrics for specified time period"""
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(TeamMetrics)
        .where(
            TeamMetrics.team_id == team_id,
            TeamMetrics.date >= start_date
        )
        .order_by(TeamMetrics.date.desc())
    )

    metrics = result.scalars().all()

    return metrics


@router.post("/team/{team_id}/calculate")
async def calculate_team_metrics(
    team_id: int,
    game_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Calculate advanced metrics for a team"""
    engine = MetricsEngine(db)

    try:
        metrics = await engine.calculate_team_metrics(
            team_id, game_id
        )

        return {
            "team_id": metrics.team_id,
            "date": metrics.date,
            "offensive_rating": metrics.offensive_rating,
            "defensive_rating": metrics.defensive_rating,
            "expected_points_added": metrics.expected_points_added,
            "success_rate": metrics.success_rate,
            "expected_goals": metrics.expected_goals,
            "pythagorean_wins": metrics.pythagorean_wins,
            "luck_index": metrics.luck_index,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/player/{player_id}", response_model=List[PlayerMetricsResponse])
async def get_player_metrics(
    player_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get player metrics for specified time period"""
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(PlayerMetrics)
        .where(
            PlayerMetrics.player_id == player_id,
            PlayerMetrics.date >= start_date
        )
        .order_by(PlayerMetrics.date.desc())
    )

    metrics = result.scalars().all()

    return metrics


@router.post("/player/{player_id}/calculate")
async def calculate_player_metrics(
    player_id: int,
    game_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Calculate advanced metrics for a player"""
    engine = MetricsEngine(db)

    try:
        metrics = await engine.calculate_player_metrics(
            player_id, game_id
        )

        return {
            "player_id": metrics.player_id,
            "date": metrics.date,
            "plus_minus": metrics.plus_minus,
            "offensive_rating": metrics.offensive_rating,
            "defensive_rating": metrics.defensive_rating,
            "usage_rate": metrics.usage_rate,
            "clutch_index": metrics.clutch_index,
            "expected_goals": metrics.expected_goals,
            "performance_vs_average": metrics.performance_vs_average,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/team/{team_id}/advanced")
async def get_advanced_team_metrics(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive advanced metrics for a team"""
    result = await db.execute(
        select(TeamMetrics)
        .where(TeamMetrics.team_id == team_id)
        .order_by(TeamMetrics.date.desc())
        .limit(1)
    )

    latest_metrics = result.scalar_one_or_none()

    if not latest_metrics:
        raise HTTPException(
            status_code=404,
            detail="No metrics found for this team"
        )

    return {
        "team_id": team_id,
        "latest_metrics": {
            "offensive_rating": latest_metrics.offensive_rating,
            "defensive_rating": latest_metrics.defensive_rating,
            "net_rating": (
                latest_metrics.offensive_rating - latest_metrics.defensive_rating
                if latest_metrics.offensive_rating and latest_metrics.defensive_rating
                else None
            ),
            "expected_points_added": latest_metrics.expected_points_added,
            "success_rate": latest_metrics.success_rate,
            "expected_goals": latest_metrics.expected_goals,
            "cpoe": latest_metrics.completion_percentage_over_expected,
            "pace": latest_metrics.pace,
            "turnover_rate": latest_metrics.turnover_rate,
        },
        "luck_metrics": {
            "pythagorean_wins": latest_metrics.pythagorean_wins,
            "pythagorean_losses": latest_metrics.pythagorean_losses,
            "luck_index": latest_metrics.luck_index,
        },
        "strength_of_schedule": latest_metrics.opponent_strength,
    }


@router.get("/player/{player_id}/advanced")
async def get_advanced_player_metrics(
    player_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive advanced metrics for a player"""
    result = await db.execute(
        select(PlayerMetrics)
        .where(PlayerMetrics.player_id == player_id)
        .order_by(PlayerMetrics.date.desc())
        .limit(10)
    )

    metrics = result.scalars().all()

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="No metrics found for this player"
        )

    # Calculate averages
    avg_plus_minus = sum(m.plus_minus or 0 for m in metrics) / len(metrics)
    avg_off_rating = sum(m.offensive_rating or 0 for m in metrics) / len(metrics)
    avg_def_rating = sum(m.defensive_rating or 0 for m in metrics) / len(metrics)
    avg_usage = sum(m.usage_rate or 0 for m in metrics) / len(metrics)
    avg_clutch = sum(m.clutch_index or 1 for m in metrics) / len(metrics)

    return {
        "player_id": player_id,
        "recent_averages": {
            "plus_minus": avg_plus_minus,
            "offensive_rating": avg_off_rating,
            "defensive_rating": avg_def_rating,
            "net_rating": avg_off_rating - avg_def_rating,
            "usage_rate": avg_usage,
        },
        "clutch_performance": {
            "clutch_index": avg_clutch,
            "clutch_points": sum(m.clutch_points or 0 for m in metrics) / len(metrics),
        },
        "shot_quality": {
            "expected_goals": sum(m.expected_goals or 0 for m in metrics) / len(metrics),
            "goals_above_expected": sum(m.goals_above_expected or 0 for m in metrics) / len(metrics),
        },
        "contract_year_performance": {
            "is_contract_year": metrics[0].is_contract_year if metrics else False,
            "performance_vs_average": metrics[0].performance_vs_average if metrics else None,
        }
    }
