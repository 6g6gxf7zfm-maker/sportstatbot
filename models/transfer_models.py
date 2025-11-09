"""
Cross-League Transfer Models

4. Cross-league skill transfer estimator
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class CrossLeagueSkillTransfer:
    """
    Cross-league skill transfer estimator.

    Estimates how player/team performance translates across different leagues
    with varying competitive levels.
    """

    def __init__(self):
        """Initialize cross-league transfer estimator."""
        # League strength ratings (1.0 = baseline, higher = stronger)
        self.league_strength = {
            'premier_league': 1.15,
            'la_liga': 1.12,
            'bundesliga': 1.08,
            'serie_a': 1.10,
            'ligue_1': 1.05,
            'mls': 0.85,
            'championship': 0.92,
            'eredivisie': 0.95,
            'liga_mx': 0.88,
            'nba': 1.0,
            'euroleague': 0.92,
            'nhl': 1.0,
            'khl': 0.88,
            'nfl': 1.0,
            'cfl': 0.75
        }

        # Skill translation factors by metric type
        self.skill_translation = {}

    def set_league_strength(self, league_id: str, strength: float):
        """
        Set or update league strength rating.

        Args:
            league_id: League identifier
            strength: Strength rating (1.0 = baseline)
        """
        self.league_strength[league_id] = strength

    def estimate_transferred_performance(
        self,
        player_stats: Dict[str, float],
        from_league: str,
        to_league: str,
        position: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Estimate performance after league transfer.

        Args:
            player_stats: Current stats in origin league
            from_league: Origin league identifier
            to_league: Destination league identifier
            position: Player position (affects translation)

        Returns:
            Estimated stats in new league
        """
        from_strength = self.league_strength.get(from_league, 1.0)
        to_strength = self.league_strength.get(to_league, 1.0)

        # Calculate difficulty adjustment ratio
        difficulty_ratio = to_strength / from_strength

        transferred_stats = {}

        for stat_name, stat_value in player_stats.items():
            # Different stats translate differently
            translation_factor = self._get_translation_factor(
                stat_name,
                position,
                difficulty_ratio
            )

            # Apply translation
            transferred_stats[stat_name] = stat_value * translation_factor

        return transferred_stats

    def _get_translation_factor(
        self,
        stat_name: str,
        position: Optional[str],
        difficulty_ratio: float
    ) -> float:
        """
        Get translation factor for a specific stat.

        Args:
            stat_name: Name of the statistic
            position: Player position
            difficulty_ratio: Ratio of league difficulties

        Returns:
            Translation multiplier
        """
        # Base translation (inverse of difficulty)
        # Moving to harder league = stats decrease
        base_factor = 1.0 / difficulty_ratio

        # Skill-based adjustments
        # Some skills translate better than others
        skill_multipliers = {
            'goals': 0.85,  # Goal-scoring heavily impacted by league quality
            'assists': 0.90,
            'points': 0.88,
            'shots': 0.95,  # Shot volume less impacted
            'passes': 0.98,  # Passing relatively consistent
            'pass_completion': 0.92,
            'tackles': 0.96,
            'interceptions': 0.94,
            'saves': 0.90,
            'rebounds': 0.96,
            'steals': 0.93,
            'blocks': 0.95
        }

        skill_mult = skill_multipliers.get(stat_name, 0.93)

        # Position-specific adjustments
        position_adjustment = 1.0
        if position in ['striker', 'forward', 'center']:
            # Offensive positions more impacted by competition level
            position_adjustment = 0.90
        elif position in ['midfielder', 'guard']:
            position_adjustment = 0.95
        elif position in ['defender', 'defenseman']:
            # Defensive skills translate better
            position_adjustment = 1.00

        # Combine factors
        final_factor = base_factor * skill_mult * position_adjustment

        # Ensure reasonable bounds
        return np.clip(final_factor, 0.5, 1.5)

    def calculate_transfer_risk(
        self,
        player_stats: Dict[str, float],
        from_league: str,
        to_league: str,
        age: int,
        experience_years: int
    ) -> Dict:
        """
        Calculate risk factors for league transfer.

        Args:
            player_stats: Current performance stats
            from_league: Origin league
            to_league: Destination league
            age: Player age
            experience_years: Years of professional experience

        Returns:
            Risk assessment dict
        """
        from_strength = self.league_strength.get(from_league, 1.0)
        to_strength = self.league_strength.get(to_league, 1.0)

        # Base risk from league difference
        league_diff = abs(to_strength - from_strength)
        base_risk = league_diff / 0.5  # Normalize

        # Age factor (younger = lower risk)
        age_risk = 0.0
        if age > 30:
            age_risk = 0.3
        elif age > 27:
            age_risk = 0.15
        elif age < 22:
            age_risk = 0.2  # Very young also risky

        # Experience factor
        experience_risk = max(0, (5 - experience_years) / 10.0)

        # Direction factor (moving to stronger league = higher risk)
        direction_risk = 0.0
        if to_strength > from_strength:
            direction_risk = (to_strength - from_strength) * 0.5
        else:
            direction_risk = -0.1  # Bonus for moving to weaker league

        # Total risk
        total_risk = np.clip(
            base_risk + age_risk + experience_risk + direction_risk,
            0, 1
        )

        return {
            'total_risk': total_risk,
            'risk_level': self._risk_to_category(total_risk),
            'factors': {
                'league_difference': base_risk,
                'age': age_risk,
                'experience': experience_risk,
                'direction': direction_risk
            },
            'confidence_interval': (
                0.7 - total_risk * 0.4,  # Lower bound
                1.0 - total_risk * 0.1   # Upper bound
            )
        }

    def _risk_to_category(self, risk: float) -> str:
        """Convert risk score to category."""
        if risk < 0.25:
            return "Low"
        elif risk < 0.5:
            return "Moderate"
        elif risk < 0.75:
            return "High"
        else:
            return "Very High"

    def estimate_adaptation_time(
        self,
        from_league: str,
        to_league: str,
        age: int,
        previous_transfers: int
    ) -> int:
        """
        Estimate games needed to adapt to new league.

        Args:
            from_league: Origin league
            to_league: Destination league
            age: Player age
            previous_transfers: Number of previous league changes

        Returns:
            Estimated games to adapt
        """
        from_strength = self.league_strength.get(from_league, 1.0)
        to_strength = self.league_strength.get(to_league, 1.0)

        # Base adaptation time
        base_games = 10

        # Increase if moving to much stronger league
        if to_strength > from_strength:
            strength_diff = to_strength - from_strength
            base_games += int(strength_diff * 20)

        # Age factor
        if age > 30:
            base_games += 5
        elif age < 23:
            base_games += 3

        # Experience with transfers reduces adaptation time
        transfer_reduction = min(previous_transfers * 2, 8)
        base_games -= transfer_reduction

        return max(base_games, 3)  # Minimum 3 games
