"""
Injury Impact Models

8. Injury-impact elasticity curve (points lost per absence day)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class InjuryImpactElasticity:
    """
    Injury-impact elasticity curve - points lost per absence day.

    Models the relationship between player absence duration and team
    performance decline, with diminishing/accelerating returns.
    """

    def __init__(self):
        """Initialize injury impact model."""
        # Player value tiers
        self.value_tiers = {
            'superstar': 1.5,
            'star': 1.2,
            'starter': 1.0,
            'rotation': 0.6,
            'bench': 0.3
        }

    def calculate_impact_curve(
        self,
        player_tier: str,
        games_missed: int,
        team_depth: float = 1.0
    ) -> Dict:
        """
        Calculate injury impact over time.

        Args:
            player_tier: Player value tier (superstar, star, starter, rotation, bench)
            games_missed: Number of games player has missed
            team_depth: Team depth quality (0.5-1.5, 1.0=average)

        Returns:
            Impact analysis over time
        """
        player_value = self.value_tiers.get(player_tier, 1.0)

        # Points per game impact follows a curve
        # Initial impact is high, but team adjusts over time
        impacts_per_game = []
        cumulative_impact = 0.0

        for game_num in range(1, games_missed + 1):
            # Base impact per game
            base_impact = player_value * 3.0  # Superstar worth ~4.5 ppg

            # Adjustment factor (team adapts over time)
            # Impact decreases as team adjusts, but never fully compensates
            adaptation_factor = self._calculate_adaptation(game_num, team_depth)

            # Current game impact
            game_impact = base_impact * adaptation_factor

            impacts_per_game.append(game_impact)
            cumulative_impact += game_impact

        # Calculate elasticity (rate of change)
        if len(impacts_per_game) >= 2:
            early_avg = np.mean(impacts_per_game[:3])
            late_avg = np.mean(impacts_per_game[-3:]) if len(impacts_per_game) > 3 else early_avg
            elasticity = (late_avg - early_avg) / early_avg if early_avg > 0 else 0
        else:
            elasticity = 0.0

        return {
            'total_points_lost': cumulative_impact,
            'avg_points_per_game_lost': cumulative_impact / max(games_missed, 1),
            'initial_impact': impacts_per_game[0] if impacts_per_game else 0,
            'current_impact': impacts_per_game[-1] if impacts_per_game else 0,
            'elasticity': elasticity,
            'impacts_by_game': impacts_per_game
        }

    def _calculate_adaptation(self, game_num: int, team_depth: float) -> float:
        """
        Calculate team adaptation factor.

        Args:
            game_num: Games into injury absence
            team_depth: Team depth quality

        Returns:
            Adaptation multiplier (1.0 = no adaptation, 0.5 = 50% adapted)
        """
        # Better depth = faster adaptation
        adaptation_rate = 0.05 * team_depth

        # Adaptation follows exponential decay toward minimum impact
        # Team never fully replaces star player (minimum 60% of initial impact)
        min_impact = 0.60
        adaptation = min_impact + (1.0 - min_impact) * np.exp(-adaptation_rate * game_num)

        return adaptation

    def estimate_replacement_value(
        self,
        injured_player_stats: Dict[str, float],
        replacement_player_stats: Dict[str, float]
    ) -> Dict:
        """
        Estimate value difference between injured and replacement player.

        Args:
            injured_player_stats: Injured player's per-game stats
            replacement_player_stats: Replacement player's per-game stats

        Returns:
            Replacement value analysis
        """
        # Key stats to compare
        important_stats = ['points', 'assists', 'rebounds', 'steals', 'blocks']

        value_differences = {}
        total_value_lost = 0.0

        for stat in important_stats:
            injured_value = injured_player_stats.get(stat, 0)
            replacement_value = replacement_player_stats.get(stat, 0)

            difference = injured_value - replacement_value
            value_differences[stat] = difference

            # Weight different stats
            weights = {
                'points': 1.0,
                'assists': 0.8,
                'rebounds': 0.7,
                'steals': 0.6,
                'blocks': 0.5
            }

            total_value_lost += difference * weights.get(stat, 0.5)

        return {
            'total_value_lost': total_value_lost,
            'stat_differences': value_differences,
            'replacement_level': replacement_player_stats.get('points', 0) / max(injured_player_stats.get('points', 1), 1),
            'estimated_win_impact': total_value_lost * 0.03  # Rough conversion to wins
        }

    def predict_recovery_curve(
        self,
        injury_type: str,
        severity: str,
        player_age: int
    ) -> Dict:
        """
        Predict performance recovery after injury return.

        Args:
            injury_type: Type of injury (e.g., 'knee', 'ankle', 'hamstring')
            severity: 'minor', 'moderate', 'severe'
            player_age: Player age in years

        Returns:
            Recovery timeline and performance curve
        """
        # Base recovery times (in games)
        recovery_times = {
            ('minor', 'ankle'): 3,
            ('minor', 'knee'): 4,
            ('minor', 'hamstring'): 5,
            ('moderate', 'ankle'): 8,
            ('moderate', 'knee'): 12,
            ('moderate', 'hamstring'): 10,
            ('severe', 'ankle'): 20,
            ('severe', 'knee'): 30,
            ('severe', 'hamstring'): 25,
        }

        base_recovery = recovery_times.get((severity, injury_type), 10)

        # Age adjustment
        if player_age > 32:
            age_multiplier = 1.3
        elif player_age > 28:
            age_multiplier = 1.15
        elif player_age < 25:
            age_multiplier = 0.9
        else:
            age_multiplier = 1.0

        recovery_games = int(base_recovery * age_multiplier)

        # Performance curve after return
        performance_curve = []
        for game in range(recovery_games):
            # Gradual return to full performance
            progress = game / recovery_games
            # Use sigmoid-like curve
            performance_pct = 1 / (1 + np.exp(-8 * (progress - 0.5)))
            performance_curve.append(performance_pct)

        return {
            'estimated_recovery_games': recovery_games,
            'performance_at_return': performance_curve[0] if performance_curve else 0.5,
            'games_to_80_pct': int(recovery_games * 0.3),
            'games_to_95_pct': int(recovery_games * 0.7),
            'performance_curve': performance_curve,
            'long_term_impact': self._estimate_long_term_impact(injury_type, severity, player_age)
        }

    def _estimate_long_term_impact(
        self,
        injury_type: str,
        severity: str,
        age: int
    ) -> str:
        """Estimate long-term career impact."""
        if severity == 'severe' and injury_type in ['knee', 'achilles'] and age > 30:
            return "Significant - may not return to previous level"
        elif severity == 'severe':
            return "Moderate - extended recovery needed"
        elif severity == 'moderate' and age > 32:
            return "Minor to moderate - some lingering effects possible"
        else:
            return "Minimal - expected full recovery"

    def calculate_cumulative_injury_burden(
        self,
        injuries: List[Dict]
    ) -> Dict:
        """
        Calculate cumulative burden from multiple injuries.

        Args:
            injuries: List of injury dicts with 'player_tier', 'games_missed'

        Returns:
            Cumulative impact analysis
        """
        total_impact = 0.0
        player_impacts = []

        for injury in injuries:
            impact_result = self.calculate_impact_curve(
                injury['player_tier'],
                injury['games_missed'],
                injury.get('team_depth', 1.0)
            )

            total_impact += impact_result['total_points_lost']
            player_impacts.append(impact_result)

        # Interaction effect: multiple injuries compound
        if len(injuries) > 1:
            # 10% compound effect for each additional injury
            compound_factor = 1.0 + (len(injuries) - 1) * 0.10
            total_impact *= compound_factor

        return {
            'total_cumulative_impact': total_impact,
            'num_injuries': len(injuries),
            'avg_impact_per_injury': total_impact / max(len(injuries), 1),
            'estimated_wins_lost': total_impact / 10.0,  # Rough conversion
            'individual_impacts': player_impacts
        }
