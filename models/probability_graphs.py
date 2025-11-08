"""
Real-time Probability Graph Generator.

Generates win probability data over time for visualization.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProbabilityPoint:
    """Single point in probability graph."""
    time_elapsed: float  # Minutes or percentage
    home_win_prob: float
    away_win_prob: float
    score_home: int
    score_away: int
    key_event: Optional[str] = None


class ProbabilityGraphGenerator:
    """Generates win probability graphs for games."""

    def __init__(self):
        """Initialize probability graph generator."""
        pass

    def generate_live_probability_curve(
        self,
        game_events: List[Dict],
        initial_home_prob: float,
        initial_away_prob: float
    ) -> List[ProbabilityPoint]:
        """
        Generate probability curve from game events.

        Args:
            game_events: List of game events with timestamps and scores
            initial_home_prob: Starting home win probability
            initial_away_prob: Starting away win probability

        Returns:
            List of ProbabilityPoint objects for graphing
        """
        curve = []

        # Initial point
        curve.append(ProbabilityPoint(
            time_elapsed=0,
            home_win_prob=initial_home_prob,
            away_win_prob=initial_away_prob,
            score_home=0,
            score_away=0
        ))

        # Process each event
        for event in game_events:
            time = event.get('time_elapsed', 0)
            score_home = event.get('score_home', 0)
            score_away = event.get('score_away', 0)
            event_type = event.get('type', '')

            # Recalculate probability based on score and time
            home_prob, away_prob = self._calculate_win_probability(
                score_home, score_away, time, event.get('time_remaining', 100)
            )

            curve.append(ProbabilityPoint(
                time_elapsed=time,
                home_win_prob=home_prob,
                away_win_prob=away_prob,
                score_home=score_home,
                score_away=score_away,
                key_event=event_type if event_type in ['touchdown', 'field_goal', 'turnover'] else None
            ))

        return curve

    def _calculate_win_probability(
        self,
        score_home: int,
        score_away: int,
        time_elapsed: float,
        time_remaining: float
    ) -> Tuple[float, float]:
        """Calculate current win probability."""
        score_diff = score_home - score_away
        time_factor = time_remaining / 100

        # Simple model: more time = more uncertainty
        if score_diff > 0:
            home_prob = 0.50 + (score_diff / 20) * (1 - time_factor * 0.3)
        else:
            home_prob = 0.50 + (score_diff / 20) * (1 - time_factor * 0.3)

        home_prob = max(0.01, min(0.99, home_prob))
        away_prob = 1 - home_prob

        return home_prob, away_prob
