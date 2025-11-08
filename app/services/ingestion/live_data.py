"""Live play-by-play data ingestion service"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Game, PlayByPlay, GameEvent, MomentumEvent
from app.core.cache import cache
from app.services.analytics.momentum_engine import MomentumEngine
from app.services.analytics.win_probability import WinProbabilityCalculator

logger = logging.getLogger(__name__)


class LiveDataIngestion:
    """Service for ingesting live play-by-play data"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.momentum_engine = MomentumEngine()
        self.win_prob_calculator = WinProbabilityCalculator()
        self._active_games: Dict[int, bool] = {}

    async def start_game_tracking(self, game_id: int):
        """Start tracking a live game"""
        if game_id in self._active_games:
            logger.warning(f"Game {game_id} is already being tracked")
            return

        self._active_games[game_id] = True
        logger.info(f"Started tracking game {game_id}")

        # In production, this would connect to a live data feed
        # For now, it's a placeholder for the architecture
        await cache.set(f"game:{game_id}:tracking", True, ttl=14400)  # 4 hours

    async def stop_game_tracking(self, game_id: int):
        """Stop tracking a live game"""
        if game_id in self._active_games:
            del self._active_games[game_id]
            await cache.delete(f"game:{game_id}:tracking")
            logger.info(f"Stopped tracking game {game_id}")

    async def ingest_play(
        self,
        game_id: int,
        play_data: Dict[str, Any]
    ) -> PlayByPlay:
        """Ingest a single play-by-play event"""

        # Get game
        result = await self.db.execute(
            select(Game).where(Game.id == game_id)
        )
        game = result.scalar_one_or_none()

        if not game:
            raise ValueError(f"Game {game_id} not found")

        # Calculate advanced metrics for the play
        expected_points = await self._calculate_expected_points(play_data, game)
        win_probs = await self.win_prob_calculator.calculate(
            game, play_data
        )

        # Create play-by-play record
        play = PlayByPlay(
            game_id=game_id,
            sequence_number=play_data.get("sequence_number"),
            period=play_data.get("period"),
            time_elapsed=play_data.get("time_elapsed"),
            time_remaining=play_data.get("time_remaining"),
            offensive_team_id=play_data.get("offensive_team_id"),
            defensive_team_id=play_data.get("defensive_team_id"),
            players_involved=play_data.get("players_involved"),
            play_type=play_data.get("play_type"),
            play_description=play_data.get("description"),
            is_scoring_play=play_data.get("is_scoring_play", False),
            start_position=play_data.get("start_position"),
            end_position=play_data.get("end_position"),
            expected_points=expected_points,
            win_probability_home=win_probs.get("home"),
            win_probability_away=win_probs.get("away"),
            leverage_index=win_probs.get("leverage_index"),
            sport_specific_data=play_data.get("sport_specific_data"),
        )

        self.db.add(play)
        await self.db.flush()

        # Update momentum if significant play
        if self._is_significant_play(play_data):
            await self._update_momentum(game, play, win_probs)

        # Cache the latest play for real-time access
        await cache.set(
            f"game:{game_id}:latest_play",
            {
                "sequence": play.sequence_number,
                "description": play.play_description,
                "time": play.time_elapsed,
            },
            ttl=60
        )

        await self.db.commit()
        return play

    async def ingest_game_event(
        self,
        game_id: int,
        event_data: Dict[str, Any]
    ) -> GameEvent:
        """Ingest a significant game event (goal, touchdown, etc.)"""

        event = GameEvent(
            game_id=game_id,
            event_type=event_data.get("event_type"),
            period=event_data.get("period"),
            time_elapsed=event_data.get("time_elapsed"),
            team_id=event_data.get("team_id"),
            player_id=event_data.get("player_id"),
            description=event_data.get("description"),
            score_value=event_data.get("score_value", 0),
            home_score_after=event_data.get("home_score_after"),
            away_score_after=event_data.get("away_score_after"),
            coordinates=event_data.get("coordinates"),
            event_data=event_data.get("additional_data"),
        )

        self.db.add(event)
        await self.db.commit()

        # Invalidate cache
        await cache.delete(f"game:{game_id}:events")

        return event

    async def update_game_score(
        self,
        game_id: int,
        home_score: int,
        away_score: int,
        current_period: int,
        time_remaining: str
    ):
        """Update live game score"""

        result = await self.db.execute(
            select(Game).where(Game.id == game_id)
        )
        game = result.scalar_one_or_none()

        if not game:
            raise ValueError(f"Game {game_id} not found")

        game.home_score = home_score
        game.away_score = away_score
        game.current_period = current_period
        game.time_remaining = time_remaining

        await self.db.commit()

        # Update cache
        await cache.set(
            f"game:{game_id}:score",
            {
                "home": home_score,
                "away": away_score,
                "period": current_period,
                "time_remaining": time_remaining,
            },
            ttl=10  # Very short TTL for live scores
        )

    async def _calculate_expected_points(
        self,
        play_data: Dict[str, Any],
        game: Game
    ) -> Optional[float]:
        """Calculate expected points for a play"""
        # Placeholder - would implement sport-specific EP calculation
        # based on game situation, field position, down & distance, etc.
        return 0.0

    def _is_significant_play(self, play_data: Dict[str, Any]) -> bool:
        """Determine if a play is significant for momentum tracking"""
        return (
            play_data.get("is_scoring_play", False) or
            play_data.get("is_turnover", False) or
            play_data.get("is_big_play", False)
        )

    async def _update_momentum(
        self,
        game: Game,
        play: PlayByPlay,
        win_probs: Dict[str, float]
    ):
        """Update game momentum based on play"""
        momentum_data = await self.momentum_engine.calculate_momentum(
            game, play, win_probs
        )

        momentum_event = MomentumEvent(
            game_id=game.id,
            timestamp=datetime.utcnow(),
            game_time_elapsed=play.time_elapsed,
            period=play.period,
            home_momentum=momentum_data["home_momentum"],
            away_momentum=momentum_data["away_momentum"],
            momentum_swing=momentum_data["swing_magnitude"],
            swing_direction=momentum_data["swing_direction"],
            score_differential=game.home_score - game.away_score,
            win_probability_home=win_probs["home"],
            win_probability_away=win_probs["away"],
            excitement_index=momentum_data["excitement_index"],
        )

        self.db.add(momentum_event)
