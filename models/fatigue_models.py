"""
Fatigue and Rest Models

7. Fatigue-adjusted pace model for back-to-backs
15. Rest differential predictor for win-prob shifts
20. Travel-fatigue penalty parameter per time zone crossed
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class FatigueAdjustedPace:
    """
    Fatigue-adjusted pace model for back-to-back games.

    Adjusts team pace and performance expectations based on rest and schedule.
    """

    def __init__(self, sport: str = 'basketball'):
        """
        Initialize fatigue-adjusted pace model.

        Args:
            sport: Sport type (affects fatigue parameters)
        """
        self.sport = sport

        # Fatigue coefficients by rest days
        self.fatigue_factors = {
            0: 0.92,   # Back-to-back (8% reduction)
            1: 0.96,   # 1 day rest (4% reduction)
            2: 1.00,   # 2 days rest (normal)
            3: 1.01,   # 3 days (slight boost)
            4: 1.00,   # 4+ days (diminishing returns)
        }

    def calculate_adjusted_pace(
        self,
        base_pace: float,
        days_rest: int,
        overtime_in_last: bool = False,
        travel_distance: float = 0.0
    ) -> float:
        """
        Calculate fatigue-adjusted pace.

        Args:
            base_pace: Team's baseline pace (possessions per game)
            days_rest: Days since last game
            overtime_in_last: Whether last game went to OT
            travel_distance: Travel distance in miles

        Returns:
            Adjusted pace
        """
        # Base fatigue factor
        rest_days_capped = min(days_rest, 4)
        fatigue_factor = self.fatigue_factors.get(rest_days_capped, 1.0)

        # Overtime penalty
        if overtime_in_last and days_rest < 2:
            fatigue_factor *= 0.97

        # Travel fatigue (more than 500 miles)
        if travel_distance > 500:
            travel_penalty = 1.0 - min((travel_distance - 500) / 5000, 0.05)
            fatigue_factor *= travel_penalty

        adjusted_pace = base_pace * fatigue_factor

        return adjusted_pace

    def predict_performance_drop(
        self,
        days_rest: int,
        game_sequence: List[Dict]
    ) -> Dict:
        """
        Predict performance drop from fatigue.

        Args:
            days_rest: Days of rest before upcoming game
            game_sequence: Recent game history with 'date', 'minutes_played', 'overtime'

        Returns:
            Predicted performance impact
        """
        # Cumulative fatigue from recent games
        cumulative_fatigue = 0.0

        for i, game in enumerate(reversed(game_sequence[:5])):
            # Decay factor for older games
            decay = 0.8 ** i

            # Fatigue from game
            game_fatigue = 1.0
            if game.get('overtime', False):
                game_fatigue = 1.2

            # Minutes played factor
            minutes = game.get('minutes_played', 240)  # Default 48 min game
            if minutes > 250:  # Overtime
                game_fatigue *= (minutes / 240)

            cumulative_fatigue += game_fatigue * decay

        # Normalize cumulative fatigue
        fatigue_index = cumulative_fatigue / 5.0

        # Calculate performance drops
        pace_drop_pct = 0.0
        shooting_drop_pct = 0.0
        defensive_drop_pct = 0.0

        if days_rest == 0:
            pace_drop_pct = 8 + fatigue_index * 4
            shooting_drop_pct = 3 + fatigue_index * 2
            defensive_drop_pct = 5 + fatigue_index * 3
        elif days_rest == 1:
            pace_drop_pct = 4 + fatigue_index * 2
            shooting_drop_pct = 1.5 + fatigue_index * 1
            defensive_drop_pct = 2.5 + fatigue_index * 1.5

        return {
            'fatigue_index': fatigue_index,
            'pace_drop_percentage': pace_drop_pct,
            'shooting_drop_percentage': shooting_drop_pct,
            'defensive_drop_percentage': defensive_drop_pct,
            'overall_performance_multiplier': 1.0 - (pace_drop_pct / 100)
        }


class RestDifferentialPredictor:
    """
    Rest differential predictor for win probability shifts.

    Predicts impact of rest advantage/disadvantage on game outcome.
    """

    def __init__(self):
        """Initialize rest differential predictor."""
        # Win probability modifiers per day of rest advantage
        self.rest_advantage_impact = 0.015  # 1.5% per day

    def calculate_rest_advantage(
        self,
        team_a_rest: int,
        team_b_rest: int
    ) -> Dict:
        """
        Calculate rest advantage between teams.

        Args:
            team_a_rest: Team A's days of rest
            team_b_rest: Team B's days of rest

        Returns:
            Rest advantage analysis
        """
        rest_diff = team_a_rest - team_b_rest

        # Calculate win probability impact
        win_prob_shift = rest_diff * self.rest_advantage_impact

        # Cap at reasonable bounds
        win_prob_shift = np.clip(win_prob_shift, -0.10, 0.10)

        # Determine advantage magnitude
        if abs(rest_diff) >= 2:
            magnitude = "Significant"
        elif abs(rest_diff) == 1:
            magnitude = "Moderate"
        else:
            magnitude = "None"

        return {
            'rest_differential': rest_diff,
            'advantage_team': 'team_a' if rest_diff > 0 else 'team_b' if rest_diff < 0 else 'none',
            'win_prob_shift': win_prob_shift,
            'magnitude': magnitude,
            'back_to_back_disadvantage': team_a_rest == 0 or team_b_rest == 0
        }

    def predict_rest_impact_on_spread(
        self,
        rest_differential: int,
        base_spread: float
    ) -> float:
        """
        Predict impact of rest on point spread.

        Args:
            rest_differential: Difference in days rest (positive favors team A)
            base_spread: Current point spread

        Returns:
            Adjusted point spread
        """
        # Each day of rest advantage worth approximately 1-1.5 points
        spread_impact = rest_differential * 1.2

        # More pronounced for back-to-back situations
        if abs(rest_differential) >= 2:
            spread_impact *= 1.3

        adjusted_spread = base_spread + spread_impact

        return adjusted_spread


class TravelFatiguePenalty:
    """
    Travel-fatigue penalty parameter per time zone crossed.

    Calculates performance penalty based on travel distance and time zones.
    """

    def __init__(self):
        """Initialize travel fatigue model."""
        # Performance penalty per time zone
        self.penalty_per_timezone = 0.012  # 1.2% per zone

        # Additional penalty for direction
        self.eastward_multiplier = 1.3  # Eastward travel worse
        self.westward_multiplier = 0.9  # Westward travel easier

    def calculate_travel_penalty(
        self,
        time_zones_crossed: int,
        direction: str,
        travel_distance: float,
        arrival_time_before_game: float
    ) -> Dict:
        """
        Calculate travel fatigue penalty.

        Args:
            time_zones_crossed: Number of time zones crossed
            direction: 'east' or 'west'
            travel_distance: Distance in miles
            arrival_time_before_game: Hours between arrival and game

        Returns:
            Travel penalty analysis
        """
        # Base penalty from time zones
        base_penalty = time_zones_crossed * self.penalty_per_timezone

        # Direction modifier
        if direction == 'east':
            direction_mult = self.eastward_multiplier
        elif direction == 'west':
            direction_mult = self.westward_multiplier
        else:
            direction_mult = 1.0

        # Distance modifier (very long flights)
        distance_penalty = 0.0
        if travel_distance > 2000:
            distance_penalty = (travel_distance - 2000) / 10000  # Max 0.05

        # Recovery time modifier
        if arrival_time_before_game < 24:
            recovery_mult = 0.8  # Worse if arrived recently
        elif arrival_time_before_game < 48:
            recovery_mult = 0.95
        else:
            recovery_mult = 1.0

        # Total penalty
        total_penalty = (base_penalty * direction_mult + distance_penalty) / recovery_mult

        # Cap at reasonable maximum
        total_penalty = min(total_penalty, 0.15)

        return {
            'total_penalty_pct': total_penalty * 100,
            'performance_multiplier': 1.0 - total_penalty,
            'time_zones_crossed': time_zones_crossed,
            'direction_impact': direction_mult,
            'distance_penalty': distance_penalty,
            'recovery_factor': recovery_mult,
            'severity': self._penalty_to_severity(total_penalty)
        }

    def _penalty_to_severity(self, penalty: float) -> str:
        """Convert penalty to severity category."""
        if penalty < 0.02:
            return "Minimal"
        elif penalty < 0.05:
            return "Moderate"
        elif penalty < 0.10:
            return "Significant"
        else:
            return "Severe"

    def calculate_timezone_shift_impact(
        self,
        time_zones: int,
        game_time_local: str,
        direction: str
    ) -> Dict:
        """
        Calculate impact of time zone shift on circadian rhythm.

        Args:
            time_zones: Number of zones crossed
            game_time_local: Local game time (e.g., "19:00")
            direction: 'east' or 'west'

        Returns:
            Circadian impact analysis
        """
        # Parse game time
        hour = int(game_time_local.split(':')[0])

        # Body clock adjustment needed
        if direction == 'east':
            body_clock_hour = (hour + time_zones) % 24
        else:
            body_clock_hour = (hour - time_zones) % 24

        # Performance varies by time of day
        # Peak performance: 18:00-22:00 local time
        # Worst performance: 2:00-6:00 local time
        if 18 <= body_clock_hour <= 22:
            circadian_penalty = 0.0  # Optimal time
        elif 14 <= body_clock_hour < 18 or 22 < body_clock_hour <= 24:
            circadian_penalty = 0.02  # Slight sub-optimal
        elif 10 <= body_clock_hour < 14:
            circadian_penalty = 0.04  # Moderate penalty
        elif 6 <= body_clock_hour < 10:
            circadian_penalty = 0.06  # Significant penalty
        else:  # 0-6 hours (middle of night)
            circadian_penalty = 0.10  # Severe penalty

        return {
            'body_clock_game_time': f"{body_clock_hour:02d}:00",
            'circadian_penalty_pct': circadian_penalty * 100,
            'optimal_timing': circadian_penalty < 0.03,
            'performance_multiplier': 1.0 - circadian_penalty
        }
