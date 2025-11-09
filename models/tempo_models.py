"""
Tempo Models

18. Expected tempo estimator from early-game sequences
"""

import numpy as np
from typing import Dict, List, Optional


class ExpectedTempoEstimator:
    """
    Expected tempo estimator from early-game sequences.

    Predicts full-game tempo based on early possession patterns
    and team tendencies.
    """

    def __init__(self, sport: str = 'basketball'):
        """
        Initialize tempo estimator.

        Args:
            sport: Sport type
        """
        self.sport = sport

    def estimate_game_tempo(
        self,
        early_possessions: List[Dict],
        team_a_avg_pace: float,
        team_b_avg_pace: float,
        minutes_elapsed: float
    ) -> Dict:
        """
        Estimate full-game tempo from early data.

        Args:
            early_possessions: List of possession data with 'duration', 'team'
            team_a_avg_pace: Team A's season average pace
            team_b_avg_pace: Team B's season average pace
            minutes_elapsed: Minutes of game elapsed

        Returns:
            Tempo estimation
        """
        if not early_possessions or minutes_elapsed == 0:
            # Use average of team paces
            expected_pace = (team_a_avg_pace + team_b_avg_pace) / 2
            return {
                'estimated_game_pace': expected_pace,
                'confidence': 'Low',
                'adjustment_from_average': 0.0
            }

        # Calculate observed pace so far
        total_possessions = len(early_possessions)
        possessions_per_minute = total_possessions / minutes_elapsed

        # Estimate 48-minute pace (or game length)
        if self.sport == 'basketball':
            game_length = 48.0
        elif self.sport == 'football':
            game_length = 60.0
        else:
            game_length = 90.0

        observed_pace = possessions_per_minute * game_length

        # Weight observed vs expected based on sample size
        confidence_weight = min(minutes_elapsed / 12.0, 0.8)  # Max 80% weight to observed

        expected_avg = (team_a_avg_pace + team_b_avg_pace) / 2

        # Blend observed and expected
        estimated_pace = (
            confidence_weight * observed_pace +
            (1 - confidence_weight) * expected_avg
        )

        # Calculate possession duration statistics
        durations = [p.get('duration', 15) for p in early_possessions]
        avg_duration = np.mean(durations)
        std_duration = np.std(durations)

        return {
            'estimated_game_pace': estimated_pace,
            'observed_pace': observed_pace,
            'expected_avg_pace': expected_avg,
            'confidence': self._minutes_to_confidence(minutes_elapsed),
            'adjustment_from_average': estimated_pace - expected_avg,
            'avg_possession_duration': avg_duration,
            'possession_duration_std': std_duration,
            'tempo_variance': self._classify_tempo_variance(std_duration)
        }

    def _minutes_to_confidence(self, minutes: float) -> str:
        """Convert minutes elapsed to confidence level."""
        if minutes < 5:
            return "Very Low"
        elif minutes < 10:
            return "Low"
        elif minutes < 15:
            return "Moderate"
        elif minutes < 24:
            return "High"
        else:
            return "Very High"

    def _classify_tempo_variance(self, std_dev: float) -> str:
        """Classify tempo variance."""
        if std_dev < 3:
            return "Very Consistent"
        elif std_dev < 5:
            return "Consistent"
        elif std_dev < 7:
            return "Variable"
        else:
            return "Highly Variable"

    def predict_total_possessions(
        self,
        estimated_pace: float,
        game_minutes: Optional[float] = None
    ) -> int:
        """
        Predict total possessions for game.

        Args:
            estimated_pace: Estimated pace (possessions per 48 min)
            game_minutes: Expected game length

        Returns:
            Predicted total possessions
        """
        if game_minutes is None:
            if self.sport == 'basketball':
                game_minutes = 48.0
            elif self.sport == 'football':
                game_minutes = 60.0
            else:
                game_minutes = 90.0

        total_possessions = int((estimated_pace / 48.0) * game_minutes)

        return total_possessions

    def adjust_predictions_for_tempo(
        self,
        base_predictions: Dict[str, float],
        estimated_pace: float,
        league_avg_pace: float
    ) -> Dict[str, float]:
        """
        Adjust stat predictions based on tempo.

        Args:
            base_predictions: Base statistical predictions
            estimated_pace: Estimated game pace
            league_avg_pace: League average pace

        Returns:
            Tempo-adjusted predictions
        """
        # Calculate pace adjustment factor
        pace_factor = estimated_pace / league_avg_pace

        adjusted = {}

        # Stats that scale with pace
        pace_dependent_stats = [
            'points', 'field_goals', 'rebounds', 'assists',
            'turnovers', 'possessions'
        ]

        # Stats less dependent on pace
        percentage_stats = [
            'fg_pct', 'three_pct', 'ft_pct'
        ]

        for stat, value in base_predictions.items():
            if stat in pace_dependent_stats:
                # Scale with pace
                adjusted[stat] = value * pace_factor
            elif stat in percentage_stats:
                # Percentage stats don't change with pace
                adjusted[stat] = value
            else:
                # Moderate scaling for other stats
                adjusted[stat] = value * ((pace_factor + 1.0) / 2)

        return adjusted

    def identify_tempo_drivers(
        self,
        early_possessions: List[Dict]
    ) -> Dict:
        """
        Identify what's driving the tempo.

        Args:
            early_possessions: Early possession data

        Returns:
            Tempo driver analysis
        """
        if not early_possessions:
            return {'primary_driver': 'Unknown'}

        # Analyze possession types
        fast_breaks = sum(1 for p in early_possessions if p.get('type') == 'fast_break')
        half_court = sum(1 for p in early_possessions if p.get('type') == 'half_court')
        turnovers = sum(1 for p in early_possessions if p.get('type') == 'turnover')

        # Analyze durations
        quick_possessions = sum(1 for p in early_possessions if p.get('duration', 15) < 10)
        slow_possessions = sum(1 for p in early_possessions if p.get('duration', 15) > 20)

        total = len(early_possessions)

        drivers = []

        if fast_breaks / total > 0.25:
            drivers.append("Transition offense")

        if turnovers / total > 0.18:
            drivers.append("High turnover rate")

        if quick_possessions / total > 0.40:
            drivers.append("Quick shots/decisions")

        if slow_possessions / total > 0.40:
            drivers.append("Deliberate half-court sets")

        if not drivers:
            drivers.append("Standard pace factors")

        return {
            'primary_drivers': drivers,
            'fast_break_rate': fast_breaks / total if total > 0 else 0,
            'quick_possession_rate': quick_possessions / total if total > 0 else 0,
            'slow_possession_rate': slow_possessions / total if total > 0 else 0
        }

    def tempo_matchup_prediction(
        self,
        team_a_pace: float,
        team_b_pace: float,
        team_a_def_pace: float,
        team_b_def_pace: float
    ) -> Dict:
        """
        Predict game tempo from team matchup.

        Args:
            team_a_pace: Team A's offensive pace
            team_b_pace: Team B's offensive pace
            team_a_def_pace: Pace allowed by Team A defense
            team_b_def_pace: Pace allowed by Team B defense

        Returns:
            Tempo prediction
        """
        # Weighted average of offensive and defensive paces
        # 60% offense, 40% defense
        team_a_contribution = 0.6 * team_a_pace + 0.4 * team_b_def_pace
        team_b_contribution = 0.6 * team_b_pace + 0.4 * team_a_def_pace

        predicted_pace = (team_a_contribution + team_b_contribution) / 2

        # Determine pace category
        if predicted_pace > 105:
            pace_category = "Very Fast"
        elif predicted_pace > 100:
            pace_category = "Fast"
        elif predicted_pace > 96:
            pace_category = "Average"
        elif predicted_pace > 92:
            pace_category = "Slow"
        else:
            pace_category = "Very Slow"

        return {
            'predicted_pace': predicted_pace,
            'pace_category': pace_category,
            'team_a_preferred_pace': team_a_pace,
            'team_b_preferred_pace': team_b_pace,
            'pace_advantage': 'Team A' if abs(team_a_pace - predicted_pace) < abs(team_b_pace - predicted_pace) else 'Team B'
        }
