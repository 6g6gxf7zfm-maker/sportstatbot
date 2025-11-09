"""
Referee Analysis Models

10. Referee decision-entropy metric
"""

import numpy as np
from typing import Dict, List, Optional
from collections import Counter
from scipy.stats import entropy


class RefereeDecisionEntropy:
    """
    Referee decision-entropy metric.

    Measures consistency/unpredictability of referee decisions using
    information entropy. Higher entropy = more unpredictable calls.
    """

    def __init__(self):
        """Initialize referee decision entropy model."""
        self.referee_profiles = {}

    def calculate_decision_entropy(
        self,
        referee_id: str,
        decision_history: List[Dict]
    ) -> Dict:
        """
        Calculate entropy of referee's decision patterns.

        Args:
            referee_id: Referee identifier
            decision_history: List of decisions with 'type', 'home_team', 'called'

        Returns:
            Entropy analysis
        """
        # Categorize decisions by type
        decision_types = {}

        for decision in decision_history:
            dec_type = decision.get('type', 'unknown')
            called = decision.get('called', False)
            favors_home = decision.get('home_team', False)

            if dec_type not in decision_types:
                decision_types[dec_type] = {
                    'called': 0,
                    'not_called': 0,
                    'favors_home': 0,
                    'favors_away': 0
                }

            if called:
                decision_types[dec_type]['called'] += 1
                if favors_home:
                    decision_types[dec_type]['favors_home'] += 1
                else:
                    decision_types[dec_type]['favors_away'] += 1
            else:
                decision_types[dec_type]['not_called'] += 1

        # Calculate entropy for each decision type
        entropies = {}
        for dec_type, counts in decision_types.items():
            # Call rate entropy
            total = counts['called'] + counts['not_called']
            if total > 0:
                probs = [counts['called'] / total, counts['not_called'] / total]
                call_entropy = entropy(probs, base=2)
            else:
                call_entropy = 0.0

            # Home bias entropy
            total_calls = counts['favors_home'] + counts['favors_away']
            if total_calls > 0:
                bias_probs = [
                    counts['favors_home'] / total_calls,
                    counts['favors_away'] / total_calls
                ]
                bias_entropy = entropy(bias_probs, base=2)
            else:
                bias_entropy = 0.0

            entropies[dec_type] = {
                'call_entropy': call_entropy,
                'bias_entropy': bias_entropy,
                'total_entropy': call_entropy + bias_entropy
            }

        # Overall entropy
        if entropies:
            overall_entropy = np.mean([e['total_entropy'] for e in entropies.values()])
        else:
            overall_entropy = 0.0

        # Store profile
        self.referee_profiles[referee_id] = {
            'overall_entropy': overall_entropy,
            'decision_entropies': entropies,
            'total_decisions': len(decision_history)
        }

        return {
            'overall_entropy': overall_entropy,
            'consistency_rating': self._entropy_to_consistency(overall_entropy),
            'decision_type_entropies': entropies,
            'total_decisions_analyzed': len(decision_history)
        }

    def _entropy_to_consistency(self, entropy_value: float) -> str:
        """Convert entropy to consistency rating."""
        # Lower entropy = more consistent/predictable
        if entropy_value < 0.5:
            return "Very Consistent"
        elif entropy_value < 1.0:
            return "Consistent"
        elif entropy_value < 1.5:
            return "Moderate"
        elif entropy_value < 2.0:
            return "Inconsistent"
        else:
            return "Very Inconsistent"

    def calculate_home_bias(
        self,
        referee_id: str,
        games: List[Dict]
    ) -> Dict:
        """
        Calculate referee's home team bias.

        Args:
            referee_id: Referee identifier
            games: List of games with 'penalties_home', 'penalties_away'

        Returns:
            Bias analysis
        """
        total_home_calls = 0
        total_away_calls = 0

        for game in games:
            total_home_calls += game.get('penalties_home', 0)
            total_away_calls += game.get('penalties_away', 0)

        total_calls = total_home_calls + total_away_calls

        if total_calls == 0:
            return {
                'home_bias_pct': 0.0,
                'bias_rating': "Insufficient data",
                'total_calls': 0
            }

        home_pct = total_home_calls / total_calls
        # Expected is 50/50, but slight home bias (52-53%) is normal
        expected_home_pct = 0.525

        bias = home_pct - expected_home_pct

        return {
            'home_call_pct': home_pct * 100,
            'expected_pct': expected_home_pct * 100,
            'bias_pct': bias * 100,
            'bias_rating': self._bias_to_rating(bias),
            'total_calls': total_calls,
            'statistically_significant': total_calls > 100 and abs(bias) > 0.05
        }

    def _bias_to_rating(self, bias: float) -> str:
        """Convert bias value to rating."""
        if abs(bias) < 0.03:
            return "Neutral"
        elif bias > 0.08:
            return "Strong Home Bias"
        elif bias > 0.05:
            return "Moderate Home Bias"
        elif bias < -0.05:
            return "Away Bias (unusual)"
        else:
            return "Slight Home Bias (normal)"

    def predict_penalty_total(
        self,
        referee_id: str,
        game_context: Dict
    ) -> Dict:
        """
        Predict total penalties for a game based on referee tendencies.

        Args:
            referee_id: Referee identifier
            game_context: Game context with 'sport', 'league'

        Returns:
            Penalty prediction
        """
        if referee_id not in self.referee_profiles:
            return {
                'predicted_total': 10,  # League average guess
                'confidence': 'Low'
            }

        profile = self.referee_profiles[referee_id]

        # Calculate average call rate
        decision_counts = [
            e['total_entropy'] for e in profile['decision_entropies'].values()
        ]

        # Higher entropy = more calls (less letting things go)
        avg_entropy = profile['overall_entropy']

        # Base prediction (sport-dependent)
        sport = game_context.get('sport', 'unknown')
        base_totals = {
            'football': 12,
            'basketball': 22,
            'hockey': 8,
            'soccer': 3
        }

        base_total = base_totals.get(sport, 10)

        # Adjust based on referee tendency
        # Higher entropy refs call more penalties
        adjustment_factor = 1.0 + ((avg_entropy - 1.0) * 0.2)

        predicted_total = base_total * adjustment_factor

        return {
            'predicted_total': round(predicted_total),
            'base_total': base_total,
            'referee_adjustment': adjustment_factor,
            'confidence': 'High' if profile['total_decisions'] > 50 else 'Moderate'
        }

    def compare_referees(
        self,
        referee_a_id: str,
        referee_b_id: str
    ) -> Dict:
        """
        Compare two referees' tendencies.

        Args:
            referee_a_id: First referee
            referee_b_id: Second referee

        Returns:
            Comparison analysis
        """
        if referee_a_id not in self.referee_profiles or referee_b_id not in self.referee_profiles:
            return {'error': 'One or both referees not in database'}

        profile_a = self.referee_profiles[referee_a_id]
        profile_b = self.referee_profiles[referee_b_id]

        entropy_diff = profile_a['overall_entropy'] - profile_b['overall_entropy']

        return {
            'referee_a_entropy': profile_a['overall_entropy'],
            'referee_b_entropy': profile_b['overall_entropy'],
            'entropy_difference': entropy_diff,
            'more_consistent': referee_a_id if entropy_diff < 0 else referee_b_id,
            'more_calls_expected': referee_a_id if entropy_diff > 0 else referee_b_id,
            'difference_magnitude': abs(entropy_diff)
        }
