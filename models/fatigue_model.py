"""
Fatigue Decay Curve Model.

Models expected performance decline due to fatigue.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class FatigueAssessment:
    """Fatigue assessment for a team."""
    team: str
    fatigue_level: float  # 0-100 (0=fresh, 100=exhausted)
    performance_multiplier: float  # Expected performance relative to baseline
    games_in_last_7_days: int
    travel_miles_last_week: float
    recovery_status: str  # 'optimal', 'adequate', 'suboptimal', 'poor'
    expected_impact: Dict[str, float]


class FatigueDecayModel:
    """Models fatigue impact on team performance."""

    def __init__(self):
        """Initialize fatigue model."""
        self.base_recovery_rate = 10  # Fatigue points recovered per day

    def assess_fatigue(
        self,
        team: str,
        games_last_7_days: int,
        days_since_last_game: int,
        travel_miles_last_week: float,
        back_to_back_games: bool = False,
        overtime_game_recent: bool = False
    ) -> FatigueAssessment:
        """
        Assess team's fatigue level.

        Args:
            team: Team name
            games_last_7_days: Games played in last week
            days_since_last_game: Days of rest
            travel_miles_last_week: Travel distance
            back_to_back_games: Playing back-to-back
            overtime_game_recent: Recent OT game

        Returns:
            FatigueAssessment with fatigue metrics
        """
        # Base fatigue from game density
        base_fatigue = games_last_7_days * 15

        # Back-to-back penalty
        if back_to_back_games:
            base_fatigue += 25

        # Overtime penalty
        if overtime_game_recent:
            base_fatigue += 10

        # Travel fatigue
        travel_fatigue = min(15, travel_miles_last_week / 200)

        # Total fatigue before recovery
        total_fatigue = min(100, base_fatigue + travel_fatigue)

        # Recovery from rest
        recovery = days_since_last_game * self.base_recovery_rate
        final_fatigue = max(0, total_fatigue - recovery)

        # Performance multiplier (inverse of fatigue)
        performance_mult = 1.0 - (final_fatigue / 200)  # Max 50% decline

        # Recovery status
        if final_fatigue <= 20:
            recovery_status = 'optimal'
        elif final_fatigue <= 40:
            recovery_status = 'adequate'
        elif final_fatigue <= 65:
            recovery_status = 'suboptimal'
        else:
            recovery_status = 'poor'

        # Expected impacts
        expected_impact = {
            'shooting_accuracy': -final_fatigue * 0.003,
            'turnovers': final_fatigue * 0.002,
            'defensive_intensity': -final_fatigue * 0.004
        }

        return FatigueAssessment(
            team=team,
            fatigue_level=round(final_fatigue, 1),
            performance_multiplier=round(performance_mult, 3),
            games_in_last_7_days=games_last_7_days,
            travel_miles_last_week=round(travel_miles_last_week, 1),
            recovery_status=recovery_status,
            expected_impact=expected_impact
        )


