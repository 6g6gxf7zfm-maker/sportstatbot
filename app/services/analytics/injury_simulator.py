"""Injury impact simulation and analysis"""

import numpy as np
from typing import Dict, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Player, Team, InjuryImpact, PlayerMetrics


class InjuryImpactSimulator:
    """Simulate and analyze impact of player injuries on team performance"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def simulate_injury_impact(
        self,
        player_id: int,
        injury_type: str,
        expected_games_missed: int,
        replacement_player_id: Optional[int] = None
    ) -> InjuryImpact:
        """
        Simulate the impact of a player injury

        Args:
            player_id: Injured player
            injury_type: Type of injury
            expected_games_missed: Number of games expected to miss
            replacement_player_id: Player who will replace them

        Returns:
            InjuryImpact analysis
        """

        # Get player and team
        player_result = await self.db.execute(
            select(Player).where(Player.id == player_id)
        )
        player = player_result.scalar_one_or_none()

        if not player or not player.team_id:
            raise ValueError(f"Player {player_id} not found or not on a team")

        team_result = await self.db.execute(
            select(Team).where(Team.id == player.team_id)
        )
        team = team_result.scalar_one_or_none()

        if not team:
            raise ValueError(f"Team {player.team_id} not found")

        # Calculate player value
        player_value = await self._calculate_player_value(player_id)

        # Calculate team performance before injury
        team_win_pct_before = team.win_percentage

        # Simulate team performance with injury
        impact_analysis = await self._simulate_team_impact(
            team.id, player_id, player_value, replacement_player_id
        )

        # Calculate offensive/defensive impact
        offensive_impact = await self._calculate_offensive_impact(player_id)
        defensive_impact = await self._calculate_defensive_impact(player_id)

        # Calculate injury severity score
        severity = self._calculate_severity(
            injury_type, expected_games_missed, player_value
        )

        # Create impact record
        injury_impact = InjuryImpact(
            player_id=player_id,
            team_id=team.id,
            injury_date=date.today(),
            injury_type=injury_type,
            expected_return_date=None,  # Would calculate based on injury type
            games_missed=expected_games_missed,
            player_value_lost=player_value,
            team_win_pct_before=team_win_pct_before,
            team_win_pct_projected=impact_analysis["projected_win_pct"],
            win_pct_change=impact_analysis["win_pct_change"],
            replacement_player_id=replacement_player_id,
            replacement_efficiency=impact_analysis.get("replacement_efficiency"),
            offensive_impact=offensive_impact,
            defensive_impact=defensive_impact,
            severity_score=severity,
        )

        self.db.add(injury_impact)
        await self.db.commit()
        return injury_impact

    async def _calculate_player_value(self, player_id: int) -> float:
        """
        Calculate player value (similar to WAR in baseball)

        Returns:
            Player value above replacement (0-10 scale)
        """

        # Get player metrics
        result = await self.db.execute(
            select(PlayerMetrics)
            .where(PlayerMetrics.player_id == player_id)
            .order_by(PlayerMetrics.date.desc())
            .limit(10)
        )
        metrics = list(result.scalars().all())

        if not metrics:
            return 2.0  # Default replacement level

        # Calculate value from various metrics
        # This is simplified - would be more sophisticated in production

        avg_plus_minus = np.mean([m.plus_minus or 0 for m in metrics])
        avg_offensive_rating = np.mean([m.offensive_rating or 100 for m in metrics])
        avg_defensive_rating = np.mean([m.defensive_rating or 100 for m in metrics])
        avg_usage = np.mean([m.usage_rate or 20 for m in metrics])

        # Normalize and combine
        # Higher offensive rating, lower defensive rating = better
        value = (
            avg_plus_minus / 10 * 2 +  # Plus/minus contribution
            (avg_offensive_rating - 100) / 10 +  # Offensive value
            (100 - avg_defensive_rating) / 10 +  # Defensive value
            (avg_usage - 20) / 5  # Usage value
        )

        return np.clip(value, 0, 10)

    async def _simulate_team_impact(
        self,
        team_id: int,
        injured_player_id: int,
        player_value: float,
        replacement_player_id: Optional[int]
    ) -> Dict:
        """Simulate team performance with injured player out"""

        # Get current team stats
        team_result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        team = team_result.scalar_one_or_none()

        current_win_pct = team.win_percentage if team else 0.5

        # Calculate replacement value
        if replacement_player_id:
            replacement_value = await self._calculate_player_value(replacement_player_id)
        else:
            replacement_value = 2.0  # Replacement level

        # Value lost
        value_lost = player_value - replacement_value

        # Convert value lost to win percentage impact
        # Rule of thumb: 1 point of value ≈ 0.02 win percentage
        win_pct_impact = value_lost * 0.02

        projected_win_pct = max(0.0, min(1.0, current_win_pct - win_pct_impact))

        return {
            "projected_win_pct": projected_win_pct,
            "win_pct_change": -win_pct_impact,
            "replacement_efficiency": replacement_value / player_value if player_value > 0 else 1.0
        }

    async def _calculate_offensive_impact(self, player_id: int) -> float:
        """Calculate offensive impact of injury (0-10)"""

        # Get recent offensive metrics
        result = await self.db.execute(
            select(PlayerMetrics.offensive_rating, PlayerMetrics.usage_rate)
            .where(PlayerMetrics.player_id == player_id)
            .order_by(PlayerMetrics.date.desc())
            .limit(10)
        )

        metrics = result.all()

        if not metrics:
            return 3.0

        avg_off_rating = np.mean([m.offensive_rating or 100 for m in metrics])
        avg_usage = np.mean([m.usage_rate or 20 for m in metrics])

        # Impact based on how much offense they provided
        impact = (
            (avg_off_rating - 100) / 10 +  # Efficiency impact
            (avg_usage - 20) / 10  # Volume impact
        )

        return np.clip(impact, 0, 10)

    async def _calculate_defensive_impact(self, player_id: int) -> float:
        """Calculate defensive impact of injury (0-10)"""

        result = await self.db.execute(
            select(PlayerMetrics.defensive_rating)
            .where(PlayerMetrics.player_id == player_id)
            .order_by(PlayerMetrics.date.desc())
            .limit(10)
        )

        metrics = result.scalars().all()

        if not metrics:
            return 3.0

        avg_def_rating = np.mean([m or 100 for m in metrics])

        # Lower defensive rating = better defense
        # Impact is how much worse the defense will be
        impact = (100 - avg_def_rating) / 10

        return np.clip(impact, 0, 10)

    def _calculate_severity(
        self,
        injury_type: str,
        games_missed: int,
        player_value: float
    ) -> float:
        """
        Calculate injury severity score (0-10)

        Based on:
        - Type of injury
        - Games missed
        - Player value
        """

        # Injury type severity multiplier
        severity_multipliers = {
            "ankle": 1.0,
            "knee": 1.5,
            "hamstring": 1.2,
            "concussion": 1.3,
            "shoulder": 1.1,
            "back": 1.4,
            "achilles": 2.0,
            "acl": 2.5,
        }

        injury_multiplier = severity_multipliers.get(
            injury_type.lower(), 1.0
        )

        # Combine factors
        severity = (
            (games_missed / 20) * 3 +  # Games missed component (0-3)
            (player_value / 10) * 4 +  # Player value component (0-4)
            injury_multiplier  # Injury type (0-2.5)
        )

        return np.clip(severity, 0, 10)

    async def get_team_injury_report(self, team_id: int) -> Dict:
        """Get comprehensive injury report for a team"""

        result = await self.db.execute(
            select(InjuryImpact)
            .where(InjuryImpact.team_id == team_id)
            .order_by(InjuryImpact.injury_date.desc())
            .limit(20)
        )

        injuries = list(result.scalars().all())

        total_value_lost = sum(inj.player_value_lost for inj in injuries)
        total_win_pct_impact = sum(inj.win_pct_change for inj in injuries)

        return {
            "active_injuries": len([inj for inj in injuries if inj.games_missed > 0]),
            "total_value_lost": total_value_lost,
            "total_win_pct_impact": total_win_pct_impact,
            "injuries": injuries
        }
