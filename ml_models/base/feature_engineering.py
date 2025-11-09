"""
Feature engineering utilities for sports data
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class FeatureEngineer:
    """Utility class for common feature engineering tasks"""

    @staticmethod
    def calculate_rolling_average(values: List[float], window: int = 5) -> List[float]:
        """
        Calculate rolling average over a window

        Args:
            values: List of numeric values
            window: Rolling window size

        Returns:
            List of rolling averages
        """
        if len(values) < window:
            return [np.mean(values)] * len(values)

        result = []
        for i in range(len(values)):
            if i < window - 1:
                result.append(np.mean(values[:i+1]))
            else:
                result.append(np.mean(values[i-window+1:i+1]))
        return result

    @staticmethod
    def calculate_momentum(values: List[float], window: int = 3) -> float:
        """
        Calculate momentum (trend direction)

        Args:
            values: Recent performance values
            window: Number of recent games to consider

        Returns:
            Momentum score (positive = improving, negative = declining)
        """
        if len(values) < 2:
            return 0.0

        recent = values[-window:] if len(values) >= window else values
        # Simple linear trend
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]
        return float(slope)

    @staticmethod
    def days_since(date_str: str, reference_date: Optional[datetime] = None) -> int:
        """
        Calculate days since a date

        Args:
            date_str: Date string (YYYY-MM-DD format)
            reference_date: Reference date (default: today)

        Returns:
            Number of days
        """
        if reference_date is None:
            reference_date = datetime.now()

        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        return (reference_date - target_date).days

    @staticmethod
    def encode_position(position: str, sport: str) -> Dict[str, int]:
        """
        One-hot encode player position

        Args:
            position: Player position string
            sport: Sport type (nba, nfl, mlb, etc.)

        Returns:
            Dict with position encodings
        """
        positions = {
            'nba': ['PG', 'SG', 'SF', 'PF', 'C'],
            'nfl': ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'DB', 'K', 'P'],
            'mlb': ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH'],
            'nhl': ['C', 'LW', 'RW', 'D', 'G']
        }

        sport_positions = positions.get(sport.lower(), [])
        encoding = {f'pos_{p}': 0 for p in sport_positions}

        if position in sport_positions:
            encoding[f'pos_{position}'] = 1

        return encoding

    @staticmethod
    def calculate_age_curve_adjustment(age: int, peak_age: int = 27) -> float:
        """
        Calculate performance adjustment based on age curve

        Args:
            age: Player's age
            peak_age: Sport-specific peak age

        Returns:
            Multiplier for performance (1.0 = peak, <1.0 = decline)
        """
        # Simplified age curve (peak at 27, decline after)
        if age <= peak_age:
            # Pre-peak: gradual improvement
            return 0.85 + (age - 22) * 0.03
        else:
            # Post-peak: gradual decline
            years_past_peak = age - peak_age
            decline = years_past_peak * 0.02
            return max(0.7, 1.0 - decline)

    @staticmethod
    def normalize_stats(stats: Dict[str, float], league_averages: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize stats relative to league average

        Args:
            stats: Player stats
            league_averages: League-wide averages

        Returns:
            Normalized stats (percentage above/below average)
        """
        normalized = {}
        for stat, value in stats.items():
            avg = league_averages.get(stat)
            if avg and avg > 0:
                normalized[f'{stat}_norm'] = (value / avg - 1.0) * 100
            else:
                normalized[f'{stat}_norm'] = 0.0
        return normalized

    @staticmethod
    def create_interaction_features(stats: Dict[str, float]) -> Dict[str, float]:
        """
        Create interaction features (useful for non-linear relationships)

        Args:
            stats: Base statistics

        Returns:
            Dict with interaction features
        """
        interactions = {}

        # Example basketball interactions
        if 'points' in stats and 'minutes' in stats:
            interactions['points_per_minute'] = stats['points'] / max(stats['minutes'], 1)

        if 'assists' in stats and 'turnovers' in stats:
            interactions['ast_to_ratio'] = stats['assists'] / max(stats['turnovers'], 1)

        if 'field_goals_made' in stats and 'field_goals_attempted' in stats:
            interactions['fg_pct'] = stats['field_goals_made'] / max(stats['field_goals_attempted'], 1)

        return interactions

    @staticmethod
    def calculate_variance_metrics(values: List[float]) -> Dict[str, float]:
        """
        Calculate variance and stability metrics

        Args:
            values: List of performance values

        Returns:
            Dict with variance metrics
        """
        if not values:
            return {
                'mean': 0.0,
                'std': 0.0,
                'cv': 0.0,
                'range': 0.0,
                'iqr': 0.0
            }

        arr = np.array(values)
        mean_val = np.mean(arr)

        return {
            'mean': float(mean_val),
            'std': float(np.std(arr)),
            'cv': float(np.std(arr) / mean_val) if mean_val > 0 else 0.0,
            'range': float(np.max(arr) - np.min(arr)),
            'iqr': float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            'median': float(np.median(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr))
        }

    @staticmethod
    def detect_outliers(values: List[float], method: str = 'iqr') -> List[bool]:
        """
        Detect outlier values

        Args:
            values: List of values
            method: 'iqr' or 'zscore'

        Returns:
            List of booleans (True = outlier)
        """
        arr = np.array(values)

        if method == 'iqr':
            q1 = np.percentile(arr, 25)
            q3 = np.percentile(arr, 75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            return [v < lower or v > upper for v in values]

        elif method == 'zscore':
            mean = np.mean(arr)
            std = np.std(arr)
            z_scores = [(v - mean) / std for v in values]
            return [abs(z) > 3 for z in z_scores]

        return [False] * len(values)
