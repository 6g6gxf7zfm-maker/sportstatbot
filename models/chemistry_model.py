"""
Team Chemistry Model.

Measures optimal lineup combinations and player synergies.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LineupRating:
    """Rating for a specific lineup."""
    lineup: List[str]
    chemistry_score: float  # 0-100
    offensive_rating: float
    defensive_rating: float
    synergy_factors: List[str]
    weaknesses: List[str]


class TeamChemistryModel:
    """Models team chemistry and optimal lineups."""

    def __init__(self):
        """Initialize chemistry model."""
        pass

    def evaluate_lineup(
        self,
        players: List[str],
        player_ratings: Dict[str, float],
        historical_performance: Optional[Dict] = None
    ) -> LineupRating:
        """
        Evaluate a lineup's chemistry and effectiveness.

        Args:
            players: List of player names in lineup
            player_ratings: Individual player ratings
            historical_performance: Past performance data for this combo

        Returns:
            LineupRating with evaluation
        """
        # Calculate base rating
        avg_rating = sum(player_ratings.get(p, 50) for p in players) / len(players)

        # Synergy bonus (players who play well together)
        synergy = self._calculate_synergy(players, historical_performance)

        chemistry_score = min(100, avg_rating + synergy)

        return LineupRating(
            lineup=players,
            chemistry_score=chemistry_score,
            offensive_rating=chemistry_score * 1.1,
            defensive_rating=chemistry_score * 0.9,
            synergy_factors=["Good spacing", "Complementary skills"],
            weaknesses=[]
        )

    def _calculate_synergy(
        self,
        players: List[str],
        historical_performance: Optional[Dict]
    ) -> float:
        """Calculate synergy bonus for lineup."""
        if not historical_performance:
            return 0

        # Check win rate with this combo
        combo_key = "_".join(sorted(players))
        combo_data = historical_performance.get(combo_key, {})
        win_pct = combo_data.get('win_pct', 0.5)

        # Above .500 = positive synergy
        return (win_pct - 0.5) * 20  # Max ±10 points


