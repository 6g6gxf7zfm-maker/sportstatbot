"""
Ball Possession Simulator (Soccer/Hockey).

Simulates expected possession sequences and scoring chances.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class PossessionSimulation:
    """Result of possession simulation."""
    team: str
    opponent: str
    expected_possession_pct: float
    expected_shots: float
    expected_shots_on_target: float
    expected_goals: float
    expected_corners: float
    expected_xG: float  # Expected goals metric
    dominant_periods: List[str]


class PossessionSimulator:
    """Simulates possession-based sports (soccer, hockey)."""

    def __init__(self):
        """Initialize possession simulator."""
        pass

    def simulate_possession(
        self,
        team: str,
        opponent: str,
        team_possession_avg: float,
        opponent_possession_avg: float,
        team_efficiency: float,
        opponent_efficiency: float
    ) -> PossessionSimulation:
        """
        Simulate possession and expected outcomes.

        Args:
            team: Team name
            opponent: Opponent name
            team_possession_avg: Team's avg possession %
            opponent_possession_avg: Opponent's avg possession %
            team_efficiency: Team's shooting efficiency
            opponent_efficiency: Opponent's efficiency

        Returns:
            PossessionSimulation with results
        """
        # Normalize possession percentages
        total_poss = team_possession_avg + opponent_possession_avg
        team_poss_pct = (team_possession_avg / total_poss) * 100

        # Expected shots based on possession
        expected_shots = (team_poss_pct / 10) * 1.2

        # Expected goals from xG
        expected_xG = expected_shots * team_efficiency * 0.12

        return PossessionSimulation(
            team=team,
            opponent=opponent,
            expected_possession_pct=round(team_poss_pct, 1),
            expected_shots=round(expected_shots, 1),
            expected_shots_on_target=round(expected_shots * 0.35, 1),
            expected_goals=round(expected_xG, 2),
            expected_corners=round(expected_shots * 0.4, 1),
            expected_xG=round(expected_xG, 2),
            dominant_periods=["First half"] if team_poss_pct > 55 else []
        )


