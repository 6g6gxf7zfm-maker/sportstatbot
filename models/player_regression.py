"""
Player Regression Model.

Identifies players likely to bounce back or regress.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import statistics


@dataclass
class RegressionPrediction:
    """Regression prediction for a player."""
    player_name: str
    team: str
    current_performance: float
    expected_performance: float
    regression_direction: str  # 'bounce_back', 'regression', 'stable'
    regression_magnitude: float  # Expected change
    confidence: float  # 0-100
    key_factors: List[str]


class PlayerRegressionModel:
    """Predicts player performance regression/progression."""

    def __init__(self):
        """Initialize regression model."""
        pass

    def predict_regression(
        self,
        player_name: str,
        team: str,
        current_season_stats: Dict[str, float],
        career_averages: Dict[str, float],
        recent_form: List[float],
        age: int,
        injury_history: Optional[List] = None
    ) -> RegressionPrediction:
        """
        Predict if player will regress or bounce back.

        Args:
            player_name: Player name
            team: Team name
            current_season_stats: Current season statistics
            career_averages: Career average stats
            recent_form: Recent game performances
            age: Player age
            injury_history: Recent injuries

        Returns:
            RegressionPrediction
        """
        # Get primary stat (points, goals, etc.)
        primary_stat = self._get_primary_stat(current_season_stats)
        current_value = current_season_stats.get(primary_stat, 0)
        career_value = career_averages.get(primary_stat, current_value)

        # Calculate deviation from career norm
        deviation = current_value - career_value
        deviation_pct = (deviation / career_value * 100) if career_value > 0 else 0

        # Variance in recent performances (consistency)
        variance = statistics.variance(recent_form) if len(recent_form) > 1 else 0

        # Age factor (players >30 may decline, <25 may improve)
        age_factor = 0
        if age > 32:
            age_factor = -0.05  # Slight decline expected
        elif age < 24:
            age_factor = 0.05  # Slight improvement expected

        # Expected performance (regression to mean)
        expected_value = career_value * (1 + age_factor)

        # Regression calculation
        if abs(deviation_pct) < 10:
            direction = 'stable'
            magnitude = 0
        elif deviation_pct < -15:
            # Underperforming - likely to bounce back
            direction = 'bounce_back'
            magnitude = abs(deviation) * 0.6  # Expect 60% recovery
        elif deviation_pct > 15:
            # Overperforming - likely to regress
            direction = 'regression'
            magnitude = deviation * 0.4  # Expect 40% decline

        else:
            direction = 'stable'
            magnitude = 0

        # Confidence based on variance
        if variance < 10:
            confidence = 80  # Consistent performance
        elif variance < 25:
            confidence = 60
        else:
            confidence = 40  # High variance = low confidence

        # Key factors
        factors = []
        if abs(deviation_pct) > 20:
            factors.append(f"Significantly {'under' if deviation < 0 else 'over'}performing career average")
        if age > 32:
            factors.append("Age-related decline possible")
        if variance > 25:
            factors.append("High performance variance")
        if injury_history:
            factors.append("Recent injury concerns")

        return RegressionPrediction(
            player_name=player_name,
            team=team,
            current_performance=round(current_value, 1),
            expected_performance=round(expected_value, 1),
            regression_direction=direction,
            regression_magnitude=round(magnitude, 1),
            confidence=round(confidence, 1),
            key_factors=factors
        )

    def _get_primary_stat(self, stats: Dict) -> str:
        """Get primary stat from dictionary."""
        # Priority order
        priorities = ['points', 'goals', 'yards', 'hits', 'strikeouts']
        
        for stat in priorities:
            if stat in stats:
                return stat
        
        # Return first stat if none match
        return list(stats.keys())[0] if stats else 'value'


