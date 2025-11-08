"""Advanced metrics calculation engine"""

import numpy as np
from typing import Dict, List, Optional, Any
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Team, Player, Game, PlayByPlay, TeamMetrics, PlayerMetrics


class MetricsEngine:
    """Calculate advanced team and player metrics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_team_metrics(
        self,
        team_id: int,
        game_id: Optional[int] = None,
        calculation_date: Optional[date] = None
    ) -> TeamMetrics:
        """Calculate advanced team metrics"""

        if calculation_date is None:
            calculation_date = date.today()

        # Get team's recent games for calculations
        games = await self._get_team_games(team_id, limit=10)

        if not games:
            raise ValueError(f"No games found for team {team_id}")

        # Calculate offensive metrics
        offensive_rating = await self._calculate_offensive_rating(team_id, games)
        epa = await self._calculate_expected_points_added(team_id, games)
        success_rate = await self._calculate_success_rate(team_id, games)
        xg = await self._calculate_expected_goals(team_id, games)
        cpoe = await self._calculate_cpoe(team_id, games)

        # Calculate defensive metrics
        defensive_rating = await self._calculate_defensive_rating(team_id, games)
        epa_allowed = await self._calculate_epa_allowed(team_id, games)
        defensive_success_rate = await self._calculate_defensive_success_rate(team_id, games)

        # Calculate efficiency metrics
        pace = await self._calculate_pace(team_id, games)
        turnover_rate = await self._calculate_turnover_rate(team_id, games)

        # Calculate luck metrics
        pythagorean_record = await self._calculate_pythagorean_record(team_id, games)

        # Calculate strength of schedule
        sos = await self._calculate_strength_of_schedule(team_id)

        metrics = TeamMetrics(
            team_id=team_id,
            game_id=game_id,
            date=calculation_date,
            offensive_rating=offensive_rating,
            expected_points_added=epa,
            success_rate=success_rate,
            expected_goals=xg,
            completion_percentage_over_expected=cpoe,
            defensive_rating=defensive_rating,
            expected_points_allowed=epa_allowed,
            defensive_success_rate=defensive_success_rate,
            pace=pace,
            turnover_rate=turnover_rate,
            pythagorean_wins=pythagorean_record["wins"],
            pythagorean_losses=pythagorean_record["losses"],
            luck_index=pythagorean_record["luck_index"],
            opponent_strength=sos,
        )

        self.db.add(metrics)
        await self.db.commit()
        return metrics

    async def calculate_player_metrics(
        self,
        player_id: int,
        game_id: Optional[int] = None,
        calculation_date: Optional[date] = None
    ) -> PlayerMetrics:
        """Calculate advanced player metrics"""

        if calculation_date is None:
            calculation_date = date.today()

        # Get player data
        player_result = await self.db.execute(
            select(Player).where(Player.id == player_id)
        )
        player = player_result.scalar_one_or_none()

        if not player:
            raise ValueError(f"Player {player_id} not found")

        # Calculate performance metrics
        plus_minus = await self._calculate_plus_minus(player_id, game_id)
        offensive_rating = await self._calculate_player_offensive_rating(player_id)
        defensive_rating = await self._calculate_player_defensive_rating(player_id)
        usage_rate = await self._calculate_usage_rate(player_id, game_id)

        # Calculate clutch performance
        clutch_metrics = await self._calculate_clutch_metrics(player_id)

        # Calculate shot quality
        shot_quality = await self._calculate_shot_quality(player_id)

        # Check contract year performance
        performance_vs_avg = None
        if player.contract_year:
            performance_vs_avg = await self._calculate_contract_year_boost(player_id)

        metrics = PlayerMetrics(
            player_id=player_id,
            game_id=game_id,
            date=calculation_date,
            plus_minus=plus_minus,
            offensive_rating=offensive_rating,
            defensive_rating=defensive_rating,
            usage_rate=usage_rate,
            clutch_points=clutch_metrics.get("points"),
            clutch_efficiency=clutch_metrics.get("efficiency"),
            clutch_index=clutch_metrics.get("index"),
            expected_goals=shot_quality.get("expected_goals"),
            goals_above_expected=shot_quality.get("goals_above_expected"),
            shot_quality_avg=shot_quality.get("average_quality"),
            is_contract_year=player.contract_year,
            performance_vs_average=performance_vs_avg,
        )

        self.db.add(metrics)
        await self.db.commit()
        return metrics

    # Helper methods for calculations

    async def _get_team_games(self, team_id: int, limit: int = 10) -> List[Game]:
        """Get recent games for a team"""
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

    async def _calculate_offensive_rating(self, team_id: int, games: List[Game]) -> float:
        """Calculate offensive rating (points per 100 possessions)"""
        # Simplified calculation - would be more complex in production
        if not games:
            return 100.0

        total_points = 0
        total_possessions = 0

        for game in games:
            if game.home_team_id == team_id:
                total_points += game.home_score
            else:
                total_points += game.away_score
            total_possessions += 100  # Placeholder

        return (total_points / total_possessions) * 100 if total_possessions > 0 else 100.0

    async def _calculate_expected_points_added(self, team_id: int, games: List[Game]) -> float:
        """Calculate EPA (Expected Points Added)"""
        # Would implement proper EPA calculation based on play-by-play data
        # This is a placeholder
        return 0.15  # Average EPA per play

    async def _calculate_success_rate(self, team_id: int, games: List[Game]) -> float:
        """Calculate success rate (% of plays that gain expected value)"""
        # Placeholder - would analyze play-by-play data
        return 0.45

    async def _calculate_expected_goals(self, team_id: int, games: List[Game]) -> float:
        """Calculate xG (Expected Goals) based on shot quality"""
        # Placeholder for shot quality model
        return 2.3

    async def _calculate_cpoe(self, team_id: int, games: List[Game]) -> float:
        """Calculate CPOE (Completion Percentage Over Expected)"""
        # Placeholder - would compare actual vs expected completion %
        return 2.5

    async def _calculate_defensive_rating(self, team_id: int, games: List[Game]) -> float:
        """Calculate defensive rating (points allowed per 100 possessions)"""
        if not games:
            return 100.0

        total_points_allowed = 0
        total_possessions = 0

        for game in games:
            if game.home_team_id == team_id:
                total_points_allowed += game.away_score
            else:
                total_points_allowed += game.home_score
            total_possessions += 100  # Placeholder

        return (total_points_allowed / total_possessions) * 100 if total_possessions > 0 else 100.0

    async def _calculate_epa_allowed(self, team_id: int, games: List[Game]) -> float:
        """Calculate EPA allowed on defense"""
        return -0.10  # Placeholder

    async def _calculate_defensive_success_rate(self, team_id: int, games: List[Game]) -> float:
        """Calculate defensive success rate"""
        return 0.48  # Placeholder

    async def _calculate_pace(self, team_id: int, games: List[Game]) -> float:
        """Calculate team pace (possessions per game)"""
        return 100.0  # Placeholder

    async def _calculate_turnover_rate(self, team_id: int, games: List[Game]) -> float:
        """Calculate turnover rate"""
        return 12.5  # Placeholder percentage

    async def _calculate_pythagorean_record(self, team_id: int, games: List[Game]) -> Dict[str, float]:
        """Calculate Pythagorean win expectation"""
        if not games:
            return {"wins": 0, "losses": 0, "luck_index": 0}

        points_for = 0
        points_against = 0
        actual_wins = 0

        for game in games:
            is_home = game.home_team_id == team_id
            if is_home:
                points_for += game.home_score
                points_against += game.away_score
                if game.home_score > game.away_score:
                    actual_wins += 1
            else:
                points_for += game.away_score
                points_against += game.home_score
                if game.away_score > game.home_score:
                    actual_wins += 1

        # Pythagorean expectation formula (exponent = 2.37 for basketball, varies by sport)
        exponent = 2.37
        if points_for > 0 and points_against > 0:
            pythag_win_pct = points_for ** exponent / (
                points_for ** exponent + points_against ** exponent
            )
        else:
            pythag_win_pct = 0.5

        pythag_wins = pythag_win_pct * len(games)
        pythag_losses = len(games) - pythag_wins
        luck_index = actual_wins - pythag_wins

        return {
            "wins": pythag_wins,
            "losses": pythag_losses,
            "luck_index": luck_index
        }

    async def _calculate_strength_of_schedule(self, team_id: int) -> float:
        """Calculate strength of schedule (weighted by recency)"""
        # Placeholder - would calculate based on opponent quality
        return 0.520  # Above .500 = tough schedule

    async def _calculate_plus_minus(self, player_id: int, game_id: Optional[int]) -> float:
        """Calculate player plus/minus"""
        # Placeholder
        return 5.5

    async def _calculate_player_offensive_rating(self, player_id: int) -> float:
        """Calculate player offensive rating"""
        return 112.0  # Placeholder

    async def _calculate_player_defensive_rating(self, player_id: int) -> float:
        """Calculate player defensive rating"""
        return 105.0  # Placeholder

    async def _calculate_usage_rate(self, player_id: int, game_id: Optional[int]) -> float:
        """Calculate player usage rate"""
        return 25.0  # Placeholder percentage

    async def _calculate_clutch_metrics(self, player_id: int) -> Dict[str, float]:
        """Calculate clutch performance metrics (4th quarter/overtime)"""
        return {
            "points": 8.5,
            "efficiency": 0.65,
            "index": 1.25  # > 1.0 means above average in clutch
        }

    async def _calculate_shot_quality(self, player_id: int) -> Dict[str, float]:
        """Calculate shot quality metrics"""
        return {
            "expected_goals": 0.35,
            "goals_above_expected": 0.08,
            "average_quality": 0.42
        }

    async def _calculate_contract_year_boost(self, player_id: int) -> float:
        """Calculate performance boost in contract year"""
        # Compare current season to career average
        return 1.15  # 15% above average (placeholder)
