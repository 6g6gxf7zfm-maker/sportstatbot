"""Momentum tracking and swing calculation engine"""

import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

from app.models import Game, PlayByPlay


class MomentumEngine:
    """Calculate and track game momentum in real-time"""

    def __init__(self, window_seconds: int = 300):
        """
        Initialize momentum engine

        Args:
            window_seconds: Time window for momentum calculation (default 5 minutes)
        """
        self.window_seconds = window_seconds

    async def calculate_momentum(
        self,
        game: Game,
        play: PlayByPlay,
        win_probs: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate momentum for a given play

        Returns:
            dict with momentum metrics:
                - home_momentum: -1 to 1
                - away_momentum: -1 to 1
                - swing_magnitude: absolute change
                - swing_direction: 'home' or 'away'
                - excitement_index: 0 to 100
        """

        # Calculate score-based momentum
        score_diff = game.home_score - game.away_score
        score_momentum = self._calculate_score_momentum(score_diff)

        # Calculate win probability change momentum
        wp_momentum = self._calculate_wp_momentum(win_probs)

        # Calculate recency-weighted momentum (recent plays matter more)
        time_weight = self._calculate_time_weight(play.time_elapsed)

        # Combine factors
        home_momentum = (
            0.4 * score_momentum["home"] +
            0.5 * wp_momentum["home"] +
            0.1 * time_weight
        )

        away_momentum = (
            0.4 * score_momentum["away"] +
            0.5 * wp_momentum["away"] +
            0.1 * (1 - time_weight)
        )

        # Normalize to -1 to 1 range
        home_momentum = np.clip(home_momentum, -1, 1)
        away_momentum = np.clip(away_momentum, -1, 1)

        # Calculate swing
        swing_magnitude = abs(home_momentum - away_momentum)
        swing_direction = "home" if home_momentum > away_momentum else "away"

        # Calculate excitement index
        excitement_index = self._calculate_excitement(
            score_diff, win_probs, swing_magnitude
        )

        return {
            "home_momentum": float(home_momentum),
            "away_momentum": float(away_momentum),
            "swing_magnitude": float(swing_magnitude),
            "swing_direction": swing_direction,
            "excitement_index": float(excitement_index),
        }

    def _calculate_score_momentum(self, score_diff: int) -> Dict[str, float]:
        """Calculate momentum based on score differential"""
        # Use sigmoid function to map score difference to momentum
        # Close games have more volatile momentum
        max_diff = 20  # Maximum meaningful score difference

        normalized_diff = score_diff / max_diff
        sigmoid = 1 / (1 + np.exp(-3 * normalized_diff))  # Steeper curve

        return {
            "home": sigmoid,
            "away": 1 - sigmoid
        }

    def _calculate_wp_momentum(self, win_probs: Dict[str, float]) -> Dict[str, float]:
        """Calculate momentum based on win probability"""
        home_wp = win_probs.get("home", 0.5)
        away_wp = win_probs.get("away", 0.5)

        # Convert probability to momentum (-1 to 1)
        home_momentum = (home_wp - 0.5) * 2
        away_momentum = (away_wp - 0.5) * 2

        return {
            "home": home_momentum,
            "away": away_momentum
        }

    def _calculate_time_weight(self, time_elapsed: float) -> float:
        """Calculate time-based weight (later plays matter more)"""
        # Simple linear weight - could be more sophisticated
        # Assuming 48 minutes (2880 seconds) for basketball
        total_time = 2880
        return min(time_elapsed / total_time, 1.0)

    def _calculate_excitement(
        self,
        score_diff: int,
        win_probs: Dict[str, float],
        swing_magnitude: float
    ) -> float:
        """
        Calculate excitement index (0-100)

        Close games with big swings = high excitement
        """
        # Close game factor (smaller diff = more exciting)
        closeness = max(0, 1 - abs(score_diff) / 20)

        # Uncertainty factor (close to 50% win prob = more exciting)
        uncertainty = 1 - abs(win_probs.get("home", 0.5) - 0.5) * 2

        # Swing factor
        swing_factor = swing_magnitude

        # Combine factors
        excitement = (
            0.4 * closeness +
            0.4 * uncertainty +
            0.2 * swing_factor
        ) * 100

        return np.clip(excitement, 0, 100)

    def detect_momentum_shift(
        self,
        current_momentum: float,
        previous_momentum: float,
        threshold: float = 0.3
    ) -> bool:
        """
        Detect if there was a significant momentum shift

        Args:
            current_momentum: Current momentum value
            previous_momentum: Previous momentum value
            threshold: Minimum change to count as shift

        Returns:
            True if shift detected
        """
        change = abs(current_momentum - previous_momentum)
        return change >= threshold
