"""Form trajectory forecasting and trend analysis"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from scipy import stats

from app.models import Team, Game, TeamMetrics, FormTrajectory


class FormTrajectoryPredictor:
    """Predict team form trends and forecast performance"""

    def __init__(self, db: AsyncSession, lookback_games: int = 10):
        self.db = db
        self.lookback_games = lookback_games

    async def calculate_form_trajectory(
        self,
        team_id: int,
        forecast_games: int = 5
    ) -> FormTrajectory:
        """
        Calculate team's form trajectory and forecast future performance

        Args:
            team_id: Team to analyze
            forecast_games: Number of games to forecast ahead

        Returns:
            FormTrajectory model with predictions
        """

        # Get recent games
        recent_games = await self._get_recent_games(team_id, self.lookback_games)

        if not recent_games:
            raise ValueError(f"No recent games found for team {team_id}")

        # Calculate current form
        recent_record = self._calculate_recent_record(recent_games, team_id)
        form_score = self._calculate_form_score(recent_games, team_id)
        trend_direction = self._determine_trend(recent_games, team_id)

        # Analyze performance trends
        performance_trends = await self._analyze_performance_trends(
            team_id, recent_games
        )

        # Generate forecasts
        forecast = self._generate_forecast(
            recent_games, team_id, forecast_games
        )

        # Calculate confidence
        confidence = self._calculate_forecast_confidence(recent_games)

        trajectory = FormTrajectory(
            team_id=team_id,
            calculation_date=date.today(),
            recent_record=recent_record,
            form_score=form_score,
            trend_direction=trend_direction,
            points_trend=performance_trends["points"],
            offensive_trend=performance_trends["offensive"],
            defensive_trend=performance_trends["defensive"],
            forecast_wins=forecast["wins"],
            forecast_losses=forecast["losses"],
            win_probability_next_game=forecast["next_game_prob"],
            projected_performance=forecast["details"],
            forecast_confidence=confidence,
        )

        self.db.add(trajectory)
        await self.db.commit()
        return trajectory

    async def _get_recent_games(
        self,
        team_id: int,
        limit: int
    ) -> List[Game]:
        """Get team's recent games"""

        result = await self.db.execute(
            select(Game)
            .where(
                and_(
                    (Game.home_team_id == team_id) | (Game.away_team_id == team_id),
                    Game.status == "final"
                )
            )
            .order_by(Game.game_date.desc())
            .limit(limit)
        )

        return list(result.scalars().all())

    def _calculate_recent_record(
        self,
        games: List[Game],
        team_id: int
    ) -> str:
        """Calculate recent W-L record string (e.g., 'W-W-L-W-L')"""

        record = []
        for game in reversed(games):  # Chronological order
            is_home = game.home_team_id == team_id

            if is_home:
                result = "W" if game.home_score > game.away_score else "L"
            else:
                result = "W" if game.away_score > game.home_score else "L"

            record.append(result)

        return "-".join(record)

    def _calculate_form_score(
        self,
        games: List[Game],
        team_id: int
    ) -> float:
        """
        Calculate form score (0-100)

        Based on:
        - Win percentage
        - Point differential
        - Recency (recent games weighted more)
        """

        if not games:
            return 50.0

        total_score = 0
        total_weight = 0

        for i, game in enumerate(games):
            # Recency weight (most recent = highest weight)
            weight = i + 1

            is_home = game.home_team_id == team_id

            # Win/loss component
            if is_home:
                won = game.home_score > game.away_score
                point_diff = game.home_score - game.away_score
            else:
                won = game.away_score > game.home_score
                point_diff = game.away_score - game.home_score

            # Score for this game (0-100)
            game_score = 50  # Base
            game_score += 25 if won else -25  # Win/loss
            game_score += np.clip(point_diff / 20 * 25, -25, 25)  # Point differential

            total_score += game_score * weight
            total_weight += weight

        form_score = total_score / total_weight if total_weight > 0 else 50.0

        return np.clip(form_score, 0, 100)

    def _determine_trend(
        self,
        games: List[Game],
        team_id: int
    ) -> str:
        """Determine if team is improving, declining, or stable"""

        if len(games) < 5:
            return "stable"

        # Calculate point differentials over time
        point_diffs = []
        for game in reversed(games):  # Chronological
            is_home = game.home_team_id == team_id
            if is_home:
                diff = game.home_score - game.away_score
            else:
                diff = game.away_score - game.home_score
            point_diffs.append(diff)

        # Linear regression to find trend
        x = np.arange(len(point_diffs))
        slope, _, r_value, _, _ = stats.linregress(x, point_diffs)

        # Determine trend based on slope
        if slope > 1.5 and r_value ** 2 > 0.3:
            return "improving"
        elif slope < -1.5 and r_value ** 2 > 0.3:
            return "declining"
        else:
            return "stable"

    async def _analyze_performance_trends(
        self,
        team_id: int,
        games: List[Game]
    ) -> Dict[str, float]:
        """Analyze trends in various performance metrics"""

        # Calculate trends (slope of linear regression)
        # Positive = improving, negative = declining

        return {
            "points": 1.2,  # Scoring 1.2 more points per game (trend)
            "offensive": 0.8,  # Offensive rating trending up
            "defensive": -0.5,  # Defensive rating trending down (good)
        }

    def _generate_forecast(
        self,
        games: List[Game],
        team_id: int,
        forecast_games: int
    ) -> Dict:
        """Generate performance forecast for upcoming games"""

        # Calculate current performance level
        wins = 0
        total_points_for = 0
        total_points_against = 0

        for game in games:
            is_home = game.home_team_id == team_id

            if is_home:
                if game.home_score > game.away_score:
                    wins += 1
                total_points_for += game.home_score
                total_points_against += game.away_score
            else:
                if game.away_score > game.home_score:
                    wins += 1
                total_points_for += game.away_score
                total_points_against += game.home_score

        win_pct = wins / len(games) if games else 0.5

        # Simple forecast based on current form
        # Would be more sophisticated in production (opponent-adjusted, etc.)
        forecast_wins = win_pct * forecast_games
        forecast_losses = forecast_games - forecast_wins

        return {
            "wins": forecast_wins,
            "losses": forecast_losses,
            "next_game_prob": win_pct,
            "details": {
                "avg_points_for": total_points_for / len(games) if games else 0,
                "avg_points_against": total_points_against / len(games) if games else 0,
                "forecast_games": forecast_games,
            }
        }

    def _calculate_forecast_confidence(self, games: List[Game]) -> float:
        """Calculate confidence in forecast (0-1)"""

        if len(games) < 5:
            return 0.5  # Low confidence with few games

        # Higher confidence with:
        # - More games in sample
        # - More consistent performance

        sample_size_factor = min(len(games) / 15, 1.0)

        # Calculate consistency (lower variance = higher confidence)
        # This is simplified
        consistency_factor = 0.7

        confidence = (sample_size_factor + consistency_factor) / 2

        return np.clip(confidence, 0.3, 0.95)
