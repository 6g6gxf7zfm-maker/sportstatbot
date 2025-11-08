"""
Heat Surge Alert System.

Flags teams significantly outperforming their expected metrics.
"""

from typing import Dict, List
from typing import Optional
from dataclasses import dataclass


@dataclass
class HeatSurgeAlert:
    """Alert for team with heat surge."""
    team: str
    sport: str
    surge_score: float  # 0-100
    metrics_outperforming: List[str]
    expected_vs_actual: Dict[str, tuple]  # metric -> (expected, actual)
    sustainability_rating: str  # 'sustainable', 'moderate', 'unlikely'
    alert_level: str  # 'hot', 'very_hot', 'extreme'


class HeatSurgeDetector:
    """Detects teams on unsustainable hot streaks."""

    def __init__(self):
        """Initialize heat surge detector."""
        pass

    def detect_surge(
        self,
        team: str,
        sport: str,
        expected_metrics: Dict[str, float],
        actual_metrics: Dict[str, float]
    ) -> Optional[HeatSurgeAlert]:
        """
        Detect if team is experiencing a heat surge.

        Args:
            team: Team name
            sport: Sport type
            expected_metrics: Expected performance metrics
            actual_metrics: Actual performance metrics

        Returns:
            HeatSurgeAlert if surge detected, None otherwise
        """
        outperforming = []
        expected_vs_actual = {}
        surge_points = 0

        for metric, expected in expected_metrics.items():
            actual = actual_metrics.get(metric, expected)
            
            # Calculate outperformance
            if expected > 0:
                pct_diff = ((actual - expected) / expected) * 100
                
                if pct_diff > 10:  # Outperforming by 10%+
                    outperforming.append(metric)
                    expected_vs_actual[metric] = (expected, actual)
                    surge_points += min(30, pct_diff)

        if surge_points < 20:
            return None  # Not a significant surge

        # Sustainability assessment
        if surge_points >= 60:
            sustainability = 'unlikely'
            alert_level = 'extreme'
        elif surge_points >= 40:
            sustainability = 'moderate'
            alert_level = 'very_hot'
        else:
            sustainability = 'sustainable'
            alert_level = 'hot'

        return HeatSurgeAlert(
            team=team,
            sport=sport,
            surge_score=round(min(100, surge_points), 1),
            metrics_outperforming=outperforming,
            expected_vs_actual=expected_vs_actual,
            sustainability_rating=sustainability,
            alert_level=alert_level
        )


