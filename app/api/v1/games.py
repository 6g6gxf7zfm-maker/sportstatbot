"""Game API endpoints"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.models import Game
from app.schemas.game import GameCreate, GameUpdate, GameResponse

router = APIRouter()


@router.get("/", response_model=List[GameResponse])
async def get_games(
    skip: int = 0,
    limit: int = 100,
    league: Optional[str] = None,
    season: Optional[str] = None,
    status: Optional[str] = None,
    team_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all games with optional filters"""
    query = select(Game)

    filters = []
    if league:
        filters.append(Game.league == league)
    if season:
        filters.append(Game.season == season)
    if status:
        filters.append(Game.status == status)
    if team_id:
        filters.append(
            (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
        )

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Game.game_date.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    games = result.scalars().all()

    return games


@router.get("/live", response_model=List[GameResponse])
async def get_live_games(
    db: AsyncSession = Depends(get_db)
):
    """Get all live games"""
    result = await db.execute(
        select(Game).where(Game.status == "in_progress")
    )
    games = result.scalars().all()

    return games


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific game"""
    result = await db.execute(
        select(Game).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return game


@router.post("/", response_model=GameResponse, status_code=201)
async def create_game(
    game: GameCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new game"""
    db_game = Game(**game.model_dump())
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)

    return db_game


@router.patch("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    game_update: GameUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a game (e.g., score, status)"""
    result = await db.execute(
        select(Game).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    update_data = game_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)

    await db.commit()
    await db.refresh(game)

    return game


@router.get("/{game_id}/boxscore")
async def get_game_boxscore(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed boxscore for a game"""
    result = await db.execute(
        select(Game).where(Game.id == game_id)
    )
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return {
        "game_id": game.id,
        "home_team_id": game.home_team_id,
        "away_team_id": game.away_team_id,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "period_scores": game.period_scores,
        "status": game.status,
        "current_period": game.current_period,
        "time_remaining": game.time_remaining,
    }
