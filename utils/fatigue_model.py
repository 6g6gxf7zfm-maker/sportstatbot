"""Fatigue decay curve model for rest impact analysis."""
from typing import Dict
from datetime import datetime, timedelta
import math


class FatigueDecayCurve:
    """
    Models player/team fatigue and performance decay based on rest.

    Calculates expected performance impact from back-to-back games,
    three-in-four scenarios, etc.
    """

    def __init__(self):
        """Initialize fatigue decay model."""
        self.sport_recovery_rates = self._get_recovery_rates()

    def calculate_fatigue_impact(
        self,
        days_rest: int,
        sport: str,
        back_to_back: bool = False,
        three_in_four: bool = False
    ) -> Dict:
        """
        Calculate fatigue impact on performance.

        Args:
            days_rest: Days since last game
            sport: Sport type
            back_to_back: Whether this is back-to-back game
            three_in_four: Whether this is 3rd game in 4 days

        Returns:
            Dictionary with fatigue analysis
        """
        recovery_rate = self.sport_recovery_rates.get(sport, 1.0)

        # Calculate base fatigue penalty
        if back_to_back:
            base_penalty = self._get_back_to_back_penalty(sport)
            fatigue_level = "HIGH"
        elif three_in_four:
            base_penalty = self._get_three_in_four_penalty(sport)
            fatigue_level = "MODERATE-HIGH"
        elif days_rest == 1:
            base_penalty = 0.05
            fatigue_level = "MODERATE"
        elif days_rest >= 7:
            base_penalty = -0.02  # Actually rested (slight bonus)
            fatigue_level = "NONE"
        else:
            # Normal rest (2-6 days)
            base_penalty = max(0, 0.03 - (days_rest * 0.01))
            fatigue_level = "LOW"

        # Apply recovery rate
        adjusted_penalty = base_penalty * recovery_rate

        # Calculate performance multiplier
        performance_multiplier = 1 - adjusted_penalty

        return {
            'days_rest': days_rest,
            'fatigue_level': fatigue_level,
            'performance_penalty_pct': round(adjusted_penalty * 100, 1),
            'performance_multiplier': round(performance_multiplier, 3),
            'expected_scoring_impact': self._calculate_scoring_impact(
                adjusted_penalty, sport
            ),
            'injury_risk_increase': self._calculate_injury_risk(
                back_to_back, three_in_four
            ),
            'recommendation': self._generate_rest_recommendation(
                fatigue_level, back_to_back
            ),
            'sport': sport
        }

    def calculate_cumulative_fatigue(
        self,
        game_schedule: List[datetime],
        current_date: datetime,
        sport: str
    ) -> Dict:
        """
        Calculate cumulative fatigue over a stretch of games.

        Args:
            game_schedule: List of game dates
            current_date: Current date
            sport: Sport type

        Returns:
            Dictionary with cumulative fatigue analysis
        """
        if not game_schedule:
            return {'cumulative_fatigue': 0, 'note': 'No games scheduled'}

        # Sort games chronologically
        sorted_games = sorted([g for g in game_schedule if g <= current_date])

        if not sorted_games:
            return {'cumulative_fatigue': 0, 'note': 'No games played yet'}

        # Calculate fatigue accumulation
        total_fatigue = 0
        back_to_backs = 0
        three_in_fours = 0

        for i in range(len(sorted_games)):
            if i > 0:
                days_between = (sorted_games[i] - sorted_games[i-1]).days

                if days_between == 1:
                    back_to_backs += 1
                    total_fatigue += self._get_back_to_back_penalty(sport)

                # Check for 3-in-4
                if i >= 2:
                    days_span = (sorted_games[i] - sorted_games[i-2]).days
                    if days_span <= 4:
                        three_in_fours += 1
                        total_fatigue += 0.03

        # Calculate fatigue level
        avg_fatigue = total_fatigue / len(sorted_games) if sorted_games else 0

        return {
            'total_games': len(sorted_games),
            'back_to_back_games': back_to_backs,
            'three_in_four_games': three_in_fours,
            'cumulative_fatigue_score': round(total_fatigue, 2),
            'average_fatigue_per_game': round(avg_fatigue, 3),
            'schedule_difficulty': self._rate_schedule_difficulty(
                back_to_backs, three_in_fours, len(sorted_games)
            ),
            'sport': sport
        }

    def _get_back_to_back_penalty(self, sport: str) -> float:
        """Get performance penalty for back-to-back games."""
        penalties = {
            'nba': 0.08,  # 8% performance decrease
            'nhl': 0.06,  # 6% decrease
            'mlb': 0.02,  # Pitching rotation mitigates
            'nfl': 0.00,  # N/A - NFL doesn't do back-to-backs
            'mls': 0.07,
            'soccer': 0.07
        }
        return penalties.get(sport, 0.05)

    def _get_three_in_four_penalty(self, sport: str) -> float:
        """Get performance penalty for 3 games in 4 days."""
        penalties = {
            'nba': 0.06,
            'nhl': 0.05,
            'mlb': 0.03,
            'mls': 0.06,
            'soccer': 0.06
        }
        return penalties.get(sport, 0.04)

    def _get_recovery_rates(self) -> Dict[str, float]:
        """Get sport-specific recovery rates (1.0 = normal)."""
        return {
            'nba': 1.0,
            'nhl': 0.9,   # Hockey players recover slightly faster
            'mlb': 0.5,   # Rotation system helps
            'nfl': 1.2,   # More physical, slower recovery
            'mls': 1.0,
            'soccer': 1.0
        }

    def _calculate_scoring_impact(self, penalty: float, sport: str) -> float:
        """Convert fatigue penalty to expected scoring impact."""
        base_scoring = {
            'nba': 110,
            'nfl': 24,
            'nhl': 3,
            'mls': 1.5,
            'soccer': 1.8,
            'mlb': 4.5
        }

        base = base_scoring.get(sport, 100)
        impact = base * penalty

        return round(impact, 1)

    def _calculate_injury_risk(
        self,
        back_to_back: bool,
        three_in_four: bool
    ) -> str:
        """Calculate increased injury risk."""
        if back_to_back and three_in_four:
            return "HIGH (+35%)"
        elif back_to_back:
            return "MODERATE (+20%)"
        elif three_in_four:
            return "MODERATE (+15%)"
        else:
            return "NORMAL (baseline)"

    def _generate_rest_recommendation(
        self,
        fatigue_level: str,
        back_to_back: bool
    ) -> str:
        """Generate recommendation based on fatigue."""
        if fatigue_level == "HIGH":
            return "Consider resting key players or reducing minutes"
        elif fatigue_level == "MODERATE-HIGH":
            return "Monitor player conditioning closely"
        elif fatigue_level == "MODERATE":
            return "Normal rotation should suffice"
        else:
            return "Team well-rested"

    def _rate_schedule_difficulty(
        self,
        back_to_backs: int,
        three_in_fours: int,
        total_games: int
    ) -> str:
        """Rate overall schedule difficulty."""
        difficulty_score = (back_to_backs * 2) + three_in_fours
        avg_difficulty = difficulty_score / total_games if total_games > 0 else 0

        if avg_difficulty >= 0.3:
            return "BRUTAL"
        elif avg_difficulty >= 0.2:
            return "DIFFICULT"
        elif avg_difficulty >= 0.1:
            return "MODERATE"
        else:
            return "EASY"
