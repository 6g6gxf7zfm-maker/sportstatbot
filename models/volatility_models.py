"""
Volatility Models

23. Game volatility index (standard deviation of score differential)
"""

import numpy as np
from typing import Dict, List, Optional


class GameVolatilityIndex:
    """
    Game volatility index - standard deviation of score differential.

    Measures game flow volatility and predictability using score
    differential variance over time.
    """

    def __init__(self):
        """Initialize game volatility model."""
        self.game_volatility_profiles = {}

    def calculate_game_volatility(
        self,
        game_id: str,
        score_timeline: List[Dict]
    ) -> Dict:
        """
        Calculate volatility index for a game.

        Args:
            game_id: Game identifier
            score_timeline: Timeline of scores with 'minute', 'score_diff'

        Returns:
            Volatility analysis
        """
        if not score_timeline:
            return {
                'volatility_index': 0,
                'volatility_rating': 'Unknown'
            }

        # Extract score differentials over time
        score_diffs = [point.get('score_diff', 0) for point in score_timeline]

        # Calculate volatility metrics
        volatility_std = np.std(score_diffs)
        volatility_range = max(score_diffs) - min(score_diffs)
        mean_diff = np.mean(np.abs(score_diffs))

        # Lead changes
        lead_changes = self._count_lead_changes(score_diffs)

        # Momentum swings (large score diff changes)
        momentum_swings = self._count_momentum_swings(score_diffs)

        # Normalize volatility index
        # Higher = more volatile/exciting
        volatility_index = (
            0.4 * (volatility_std / 10.0) +
            0.3 * (lead_changes / 10.0) +
            0.3 * (momentum_swings / 5.0)
        )

        volatility_index = min(volatility_index, 1.0) * 100  # Scale to 0-100

        self.game_volatility_profiles[game_id] = {
            'volatility_index': volatility_index,
            'volatility_rating': self._index_to_rating(volatility_index),
            'std_deviation': volatility_std,
            'score_range': volatility_range,
            'lead_changes': lead_changes,
            'momentum_swings': momentum_swings,
            'mean_margin': mean_diff,
            'game_flow': self._classify_game_flow(score_diffs)
        }

        return self.game_volatility_profiles[game_id]

    def _count_lead_changes(self, score_diffs: List[float]) -> int:
        """Count number of lead changes."""
        lead_changes = 0

        for i in range(1, len(score_diffs)):
            # Check if sign changed (lead changed hands)
            if (score_diffs[i] > 0 and score_diffs[i-1] < 0) or \
               (score_diffs[i] < 0 and score_diffs[i-1] > 0):
                lead_changes += 1

        return lead_changes

    def _count_momentum_swings(
        self,
        score_diffs: List[float],
        threshold: float = 6.0
    ) -> int:
        """Count momentum swings (large differential changes)."""
        swings = 0

        for i in range(1, len(score_diffs)):
            diff_change = abs(score_diffs[i] - score_diffs[i-1])
            if diff_change >= threshold:
                swings += 1

        return swings

    def _index_to_rating(self, index: float) -> str:
        """Convert volatility index to rating."""
        if index > 75:
            return "Extremely Volatile (Chaotic)"
        elif index > 60:
            return "Highly Volatile (Back-and-forth)"
        elif index > 40:
            return "Moderately Volatile"
        elif index > 20:
            return "Low Volatility (Stable)"
        else:
            return "Very Low Volatility (Blowout)"

    def _classify_game_flow(self, score_diffs: List[float]) -> str:
        """Classify overall game flow pattern."""
        if not score_diffs:
            return "Unknown"

        # Check for patterns
        lead_changes = self._count_lead_changes(score_diffs)
        final_margin = abs(score_diffs[-1]) if score_diffs else 0
        max_margin = max(np.abs(score_diffs))

        if lead_changes >= 8:
            return "Seesaw battle"
        elif final_margin < 5 and lead_changes >= 3:
            return "Close throughout"
        elif max_margin > 20 and final_margin < 10:
            return "Comeback game"
        elif max_margin > 20 and final_margin > 15:
            return "Wire-to-wire blowout"
        elif final_margin < 5:
            return "Close finish"
        elif final_margin > 15:
            return "Blowout"
        else:
            return "Competitive game"

    def predict_game_volatility(
        self,
        team_a_stats: Dict,
        team_b_stats: Dict
    ) -> Dict:
        """
        Predict expected game volatility from team profiles.

        Args:
            team_a_stats: Team A's season stats
            team_b_stats: Team B's season stats

        Returns:
            Predicted volatility
        """
        # Factors that increase volatility
        pace_diff = abs(
            team_a_stats.get('pace', 100) -
            team_b_stats.get('pace', 100)
        )

        # Three-point shooting variance
        three_pt_volume = (
            team_a_stats.get('three_point_attempts', 30) +
            team_b_stats.get('three_point_attempts', 30)
        ) / 2

        # Turnover rates
        turnover_rate = (
            team_a_stats.get('turnover_rate', 0.14) +
            team_b_stats.get('turnover_rate', 0.14)
        ) / 2

        # Defensive pressure
        defensive_pressure = (
            team_a_stats.get('steals_per_game', 7) +
            team_b_stats.get('steals_per_game', 7)
        ) / 2

        # Calculate predicted volatility
        volatility_factors = {
            'pace_mismatch': pace_diff / 10.0,
            'three_point_variance': three_pt_volume / 40.0,
            'turnover_factor': turnover_rate / 0.15,
            'defensive_pressure': defensive_pressure / 10.0
        }

        predicted_volatility = sum(volatility_factors.values()) / len(volatility_factors)
        predicted_volatility = min(predicted_volatility, 1.0) * 100

        return {
            'predicted_volatility_index': predicted_volatility,
            'predicted_rating': self._index_to_rating(predicted_volatility),
            'contributing_factors': volatility_factors,
            'primary_driver': max(volatility_factors.items(), key=lambda x: x[1])[0]
        }

    def team_volatility_profile(
        self,
        team_id: str,
        games: List[Dict]
    ) -> Dict:
        """
        Build team's volatility profile over multiple games.

        Args:
            team_id: Team identifier
            games: List of games with volatility data

        Returns:
            Team volatility profile
        """
        if not games:
            return {'avg_volatility': 0, 'consistency': 'Unknown'}

        volatilities = [g.get('volatility_index', 50) for g in games]

        avg_volatility = np.mean(volatilities)
        std_volatility = np.std(volatilities)

        # Consistency = how consistent is their game volatility
        consistency = "Consistent" if std_volatility < 15 else "Variable"

        # Game type distribution
        high_volatility_games = sum(1 for v in volatilities if v > 60)
        low_volatility_games = sum(1 for v in volatilities if v < 40)

        return {
            'avg_volatility': avg_volatility,
            'volatility_std': std_volatility,
            'consistency': consistency,
            'volatility_rating': self._index_to_rating(avg_volatility),
            'pct_high_volatility_games': (high_volatility_games / len(games)) * 100,
            'pct_low_volatility_games': (low_volatility_games / len(games)) * 100,
            'game_style': self._determine_game_style(avg_volatility)
        }

    def _determine_game_style(self, avg_volatility: float) -> str:
        """Determine team's game style from volatility."""
        if avg_volatility > 65:
            return "Chaotic/unpredictable"
        elif avg_volatility > 50:
            return "Up-tempo/exciting"
        elif avg_volatility > 35:
            return "Competitive/standard"
        else:
            return "Controlled/methodical"

    def entertainment_value(
        self,
        game_id: str
    ) -> Dict:
        """
        Calculate entertainment value of game.

        Args:
            game_id: Game identifier

        Returns:
            Entertainment metrics
        """
        if game_id not in self.game_volatility_profiles:
            return {'entertainment_score': 50}

        profile = self.game_volatility_profiles[game_id]

        # Entertainment factors
        volatility_score = profile['volatility_index']
        lead_change_score = min(profile['lead_changes'] * 10, 100)
        close_game_bonus = 20 if profile['mean_margin'] < 5 else 0

        entertainment_score = (
            0.5 * volatility_score +
            0.3 * lead_change_score +
            0.2 * close_game_bonus
        )

        return {
            'entertainment_score': entertainment_score,
            'entertainment_rating': self._entertainment_rating(entertainment_score),
            'factors': {
                'volatility': volatility_score,
                'lead_changes': lead_change_score,
                'closeness': close_game_bonus
            }
        }

    def _entertainment_rating(self, score: float) -> str:
        """Convert entertainment score to rating."""
        if score > 80:
            return "Instant Classic"
        elif score > 65:
            return "Highly Entertaining"
        elif score > 50:
            return "Good Game"
        elif score > 35:
            return "Average"
        else:
            return "Dull/One-sided"
