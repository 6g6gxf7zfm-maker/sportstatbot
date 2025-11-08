"""Win probability calculation engine"""

import numpy as np
from typing import Dict, Any
from app.models import Game


class WinProbabilityCalculator:
    """Calculate live win probabilities during games"""

    def __init__(self):
        # Model parameters (would be trained on historical data in production)
        self.score_weight = 0.4
        self.time_weight = 0.3
        self.momentum_weight = 0.2
        self.context_weight = 0.1

    async def calculate(
        self,
        game: Game,
        play_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate win probabilities for both teams

        Returns:
            dict with:
                - home: home team win probability (0-1)
                - away: away team win probability (0-1)
                - leverage_index: game leverage (how important this moment is)
        """

        # Get game state
        score_diff = game.home_score - game.away_score
        time_remaining = play_data.get("time_remaining", 0)
        total_time = 2880  # 48 minutes in seconds (basketball example)
        time_elapsed_pct = 1 - (time_remaining / total_time)

        # Calculate score-based probability
        score_prob = self._score_to_probability(score_diff, time_remaining)

        # Calculate time-based adjustment
        time_factor = self._time_factor(time_elapsed_pct)

        # Calculate context-based adjustments
        context_adj = self._context_adjustment(game, play_data)

        # Combine factors
        base_home_prob = (
            self.score_weight * score_prob +
            self.time_weight * time_factor +
            self.context_weight * context_adj
        )

        # Apply bounds
        home_prob = np.clip(base_home_prob, 0.01, 0.99)
        away_prob = 1 - home_prob

        # Calculate leverage index
        leverage = self._calculate_leverage(home_prob, time_remaining)

        return {
            "home": float(home_prob),
            "away": float(away_prob),
            "leverage_index": float(leverage)
        }

    def _score_to_probability(self, score_diff: int, time_remaining: float) -> float:
        """Convert score differential to win probability"""
        # More time = less certain
        # Uses logistic regression-style conversion

        # Adjust for time remaining (larger differences matter more late)
        time_factor = 1 + (1 - time_remaining / 2880) * 2

        # Calculate probability using sigmoid
        z = (score_diff * time_factor) / 10
        prob = 1 / (1 + np.exp(-z))

        return prob

    def _time_factor(self, time_elapsed_pct: float) -> float:
        """Calculate time-based factor"""
        # Early game: more uncertain (favor 0.5)
        # Late game: more certain (favor current state)

        if time_elapsed_pct < 0.25:
            return 0.5  # Very uncertain
        elif time_elapsed_pct < 0.50:
            return 0.5 + (time_elapsed_pct - 0.25) * 0.5
        else:
            return 0.625 + (time_elapsed_pct - 0.50) * 0.75

    def _context_adjustment(self, game: Game, play_data: Dict[str, Any]) -> float:
        """Adjust for game context (home court, playoff, etc.)"""
        adjustment = 0.5  # Neutral

        # Home court advantage (typically 55-60% in basketball)
        adjustment += 0.05

        # Playoff intensity (typically tighter)
        if game.is_playoff:
            adjustment += 0.02

        # Rest advantage
        if game.home_rest_days and game.away_rest_days:
            rest_diff = game.home_rest_days - game.away_rest_days
            adjustment += rest_diff * 0.01  # Small advantage per day

        return adjustment

    def _calculate_leverage(self, win_prob: float, time_remaining: float) -> float:
        """
        Calculate leverage index

        High leverage = close game + meaningful time remaining
        Leverage Index: 1.0 = average, >1.0 = high leverage
        """

        # Closeness factor (50% = max leverage)
        closeness = 1 - abs(win_prob - 0.5) * 2

        # Time factor (middle of game = higher leverage)
        time_pct = 1 - (time_remaining / 2880)
        if time_pct < 0.25:
            time_factor = 0.5
        elif time_pct > 0.85:
            time_factor = 1.5  # Crunch time
        else:
            time_factor = 1.0

        leverage = closeness * time_factor * 2

        return max(0.1, leverage)
