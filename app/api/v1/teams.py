"""Team API endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Team
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse

router = APIRouter()


@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    skip: int = 0,
    limit: int = 100,
    league: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all teams"""
    query = select(Team)

    if league:
        query = query.where(Team.league == league)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    teams = result.scalars().all()

    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific team"""
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new team"""
    db_team = Team(**team.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)

    return db_team


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_update: TeamUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a team"""
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Update fields
    update_data = team_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    return team


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a team"""
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    await db.delete(team)
    await db.commit()

    return None
