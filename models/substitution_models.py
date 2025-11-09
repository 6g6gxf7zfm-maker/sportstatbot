"""
Substitution Impact Models

21. Substitution impact regression per minute played
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class SubstitutionImpactRegression:
    """
    Substitution impact regression per minute played.

    Models the impact of player substitutions on team performance
    using regression analysis per minute of playing time.
    """

    def __init__(self):
        """Initialize substitution impact model."""
        self.player_impacts = {}
        self.lineup_impacts = {}

    def calculate_player_impact(
        self,
        player_id: str,
        on_court_stats: Dict[str, float],
        off_court_stats: Dict[str, float],
        minutes_played: float
    ) -> Dict:
        """
        Calculate individual player's impact.

        Args:
            player_id: Player identifier
            on_court_stats: Team stats when player is on court
            off_court_stats: Team stats when player is off court
            minutes_played: Minutes player has played

        Returns:
            Player impact analysis
        """
        # Calculate per-minute impact
        impact_metrics = {}

        key_stats = ['points', 'offensive_rating', 'defensive_rating', 'net_rating']

        for stat in key_stats:
            on_value = on_court_stats.get(stat, 0)
            off_value = off_court_stats.get(stat, 0)

            # Plus-minus impact
            impact = on_value - off_value
            impact_per_minute = impact / max(minutes_played, 1)

            impact_metrics[f'{stat}_impact'] = impact
            impact_per_minute[f'{stat}_per_min'] = impact_per_minute

        # Overall impact score (weighted combination)
        overall_impact = (
            0.5 * impact_metrics.get('net_rating_impact', 0) +
            0.3 * impact_metrics.get('offensive_rating_impact', 0) +
            0.2 * (-impact_metrics.get('defensive_rating_impact', 0))  # Lower def rating is better
        )

        self.player_impacts[player_id] = {
            'overall_impact': overall_impact,
            'impact_per_minute': overall_impact / max(minutes_played, 1),
            'minutes_played': minutes_played,
            'detailed_impacts': impact_metrics
        }

        return self.player_impacts[player_id]

    def optimal_substitution_time(
        self,
        player_id: str,
        fatigue_curve: List[float],
        replacement_quality: float
    ) -> int:
        """
        Determine optimal substitution timing.

        Args:
            player_id: Player to sub out
            fatigue_curve: Fatigue impact by minute (0-1 scale)
            replacement_quality: Replacement player quality (0-1)

        Returns:
            Optimal minute to substitute
        """
        if player_id not in self.player_impacts:
            return 6  # Default: sub at 6 minutes

        player_impact = self.player_impacts[player_id]['impact_per_minute']

        # Find minute where fatigued starter < fresh replacement
        for minute in range(len(fatigue_curve)):
            fatigue_factor = fatigue_curve[minute]

            # Player's fatigued impact
            fatigued_impact = player_impact * fatigue_factor

            # Replacement impact (fresh)
            replacement_impact = player_impact * replacement_quality

            # Sub when replacement becomes better
            if replacement_impact > fatigued_impact:
                return minute

        # If never crosses, use 2/3 through fatigue curve
        return int(len(fatigue_curve) * 0.67)

    def evaluate_substitution_pattern(
        self,
        substitutions: List[Dict],
        game_flow: List[Dict]
    ) -> Dict:
        """
        Evaluate effectiveness of substitution pattern.

        Args:
            substitutions: List of subs with 'minute', 'player_out', 'player_in'
            game_flow: Game stats by minute

        Returns:
            Pattern evaluation
        """
        sub_impacts = []

        for i, sub in enumerate(substitutions):
            minute = sub.get('minute', 0)
            player_out = sub.get('player_out', '')
            player_in = sub.get('player_in', '')

            # Get performance before and after sub
            if minute + 3 < len(game_flow):
                before_stats = self._aggregate_stats(game_flow[max(0, minute-3):minute])
                after_stats = self._aggregate_stats(game_flow[minute:minute+3])

                impact = {
                    'minute': minute,
                    'player_out': player_out,
                    'player_in': player_in,
                    'point_diff_before': before_stats.get('point_diff', 0),
                    'point_diff_after': after_stats.get('point_diff', 0),
                    'impact': after_stats.get('point_diff', 0) - before_stats.get('point_diff', 0)
                }

                sub_impacts.append(impact)

        # Overall pattern quality
        avg_impact = np.mean([s['impact'] for s in sub_impacts]) if sub_impacts else 0

        return {
            'num_substitutions': len(substitutions),
            'substitution_impacts': sub_impacts,
            'avg_impact': avg_impact,
            'pattern_quality': self._impact_to_quality(avg_impact)
        }

    def _aggregate_stats(self, time_window: List[Dict]) -> Dict:
        """Aggregate stats over time window."""
        if not time_window:
            return {'point_diff': 0}

        total_points_for = sum(m.get('points_for', 0) for m in time_window)
        total_points_against = sum(m.get('points_against', 0) for m in time_window)

        return {
            'point_diff': total_points_for - total_points_against,
            'points_for': total_points_for,
            'points_against': total_points_against
        }

    def _impact_to_quality(self, impact: float) -> str:
        """Convert impact to quality rating."""
        if impact > 2:
            return "Excellent"
        elif impact > 0.5:
            return "Good"
        elif impact > -0.5:
            return "Neutral"
        elif impact > -2:
            return "Poor"
        else:
            return "Very Poor"

    def lineup_combination_impact(
        self,
        lineup: List[str],
        lineup_stats: Dict[str, float],
        minutes_played: float
    ) -> Dict:
        """
        Calculate impact of specific lineup combination.

        Args:
            lineup: List of player IDs in lineup
            lineup_stats: Stats for this lineup combination
            minutes_played: Minutes this lineup played together

        Returns:
            Lineup combination analysis
        """
        lineup_key = '_'.join(sorted(lineup))

        # Calculate per-minute metrics
        net_rating = lineup_stats.get('net_rating', 0)
        offensive_rating = lineup_stats.get('offensive_rating', 100)
        defensive_rating = lineup_stats.get('defensive_rating', 100)

        # Chemistry score (based on performance vs expected)
        expected_net_rating = 0  # Would calculate from individual player ratings
        chemistry_bonus = net_rating - expected_net_rating

        self.lineup_impacts[lineup_key] = {
            'lineup': lineup,
            'minutes_played': minutes_played,
            'net_rating': net_rating,
            'offensive_rating': offensive_rating,
            'defensive_rating': defensive_rating,
            'chemistry_bonus': chemistry_bonus,
            'effectiveness': self._rating_to_effectiveness(net_rating)
        }

        return self.lineup_impacts[lineup_key]

    def _rating_to_effectiveness(self, net_rating: float) -> str:
        """Convert net rating to effectiveness category."""
        if net_rating > 10:
            return "Elite"
        elif net_rating > 5:
            return "Very Good"
        elif net_rating > 0:
            return "Above Average"
        elif net_rating > -5:
            return "Below Average"
        else:
            return "Poor"

    def recommend_substitution(
        self,
        current_lineup: List[str],
        available_subs: List[str],
        game_situation: Dict
    ) -> Dict:
        """
        Recommend substitution based on game situation.

        Args:
            current_lineup: Current players on court
            available_subs: Available substitutes
            game_situation: Game context (score, time, fatigue)

        Returns:
            Substitution recommendation
        """
        score_diff = game_situation.get('score_diff', 0)
        time_remaining = game_situation.get('time_remaining', 24)
        current_fatigue = game_situation.get('avg_fatigue', 0.5)

        # Determine priority (offense vs defense vs rest)
        if abs(score_diff) > 10 and time_remaining > 10:
            # Blowout - rest starters
            priority = 'rest'
        elif score_diff < -5:
            # Losing - need offense
            priority = 'offense'
        elif score_diff > 5:
            # Winning - protect lead with defense
            priority = 'defense'
        else:
            # Close game - balance
            priority = 'balanced'

        recommendations = []

        for starter in current_lineup:
            for sub in available_subs:
                if starter in self.player_impacts and sub in self.player_impacts:
                    starter_impact = self.player_impacts[starter]
                    sub_impact = self.player_impacts[sub]

                    # Adjust for fatigue
                    adj_starter_impact = starter_impact['overall_impact'] * (1 - current_fatigue)

                    if priority == 'rest' or adj_starter_impact < sub_impact['overall_impact']:
                        recommendations.append({
                            'player_out': starter,
                            'player_in': sub,
                            'impact_change': sub_impact['overall_impact'] - adj_starter_impact,
                            'reason': priority
                        })

        # Sort by impact
        recommendations.sort(key=lambda x: x['impact_change'], reverse=True)

        return {
            'top_recommendation': recommendations[0] if recommendations else None,
            'all_recommendations': recommendations,
            'priority': priority
        }
