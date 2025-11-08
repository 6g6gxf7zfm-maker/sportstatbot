"""API v1 router"""

from fastapi import APIRouter
from app.api.v1 import teams, players, games, analytics, metrics

api_router = APIRouter()

# Include sub-routers
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
