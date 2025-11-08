"""Player API endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Player
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse

router = APIRouter()


@router.get("/", response_model=List[PlayerResponse])
async def get_players(
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[int] = None,
    position: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all players with optional filters"""
    query = select(Player).where(Player.is_active == is_active)

    if team_id:
        query = query.where(Player.team_id == team_id)

    if position:
        query = query.where(Player.position == position)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    players = result.scalars().all()

    return players


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific player"""
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@router.post("/", response_model=PlayerResponse, status_code=201)
async def create_player(
    player: PlayerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new player"""
    db_player = Player(**player.model_dump())
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)

    return db_player


@router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a player"""
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = player_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)

    await db.commit()
    await db.refresh(player)

    return player


@router.get("/{player_id}/injury-status")
async def get_player_injury_status(
    player_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get player injury status"""
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return {
        "player_id": player.id,
        "name": player.full_name,
        "is_injured": player.is_injured,
        "injury_status": player.injury_status,
        "injury_return_date": player.injury_return_date,
    }
