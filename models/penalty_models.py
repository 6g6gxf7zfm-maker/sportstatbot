"""
Expected Penalty Value Models

6. Expected penalty value model in football and hockey
"""

import numpy as np
from typing import Dict, List, Optional


class ExpectedPenaltyValue:
    """
    Expected penalty value model for football and hockey.

    Calculates expected point value from penalty situations based on
    historical conversion rates, game context, and player quality.
    """

    def __init__(self, sport: str = 'soccer'):
        """
        Initialize expected penalty value model.

        Args:
            sport: Sport type ('soccer', 'hockey', 'american_football')
        """
        self.sport = sport

        # Historical conversion rates by sport
        self.base_conversion_rates = {
            'soccer': {
                'penalty_kick': 0.79,
                'free_kick_direct': 0.06,
                'free_kick_dangerous': 0.12
            },
            'hockey': {
                'penalty_shot': 0.33,
                'power_play_minor': 0.20,
                'power_play_major': 0.45,
                '5_on_3': 0.55
            },
            'american_football': {
                'field_goal_20': 0.95,
                'field_goal_30': 0.90,
                'field_goal_40': 0.75,
                'field_goal_50': 0.60,
                'extra_point': 0.94
            }
        }

        # Point values
        self.point_values = {
            'soccer': {'goal': 1},
            'hockey': {'goal': 1},
            'american_football': {
                'field_goal': 3,
                'extra_point': 1,
                'two_point_conversion': 2
            }
        }

    def calculate_expected_value(
        self,
        penalty_type: str,
        kicker_skill: Optional[float] = None,
        game_context: Optional[Dict] = None
    ) -> float:
        """
        Calculate expected value of a penalty situation.

        Args:
            penalty_type: Type of penalty (e.g., 'penalty_kick', 'power_play_minor')
            kicker_skill: Taker skill modifier (0.8-1.2, 1.0 = average)
            game_context: Dict with 'time_remaining', 'score_diff', 'pressure'

        Returns:
            Expected point value
        """
        # Get base conversion rate
        base_rate = self.base_conversion_rates.get(self.sport, {}).get(
            penalty_type, 0.5
        )

        # Adjust for player skill
        if kicker_skill is not None:
            conversion_rate = base_rate * kicker_skill
        else:
            conversion_rate = base_rate

        # Adjust for game context
        if game_context:
            conversion_rate = self._apply_context_adjustments(
                conversion_rate,
                game_context
            )

        # Clip to valid probability range
        conversion_rate = np.clip(conversion_rate, 0, 1)

        # Calculate expected value
        if self.sport in ['soccer', 'hockey']:
            expected_value = conversion_rate * 1.0  # 1 point per goal
        elif self.sport == 'american_football':
            if 'field_goal' in penalty_type:
                expected_value = conversion_rate * 3.0
            elif penalty_type == 'extra_point':
                expected_value = conversion_rate * 1.0
            elif penalty_type == 'two_point_conversion':
                expected_value = conversion_rate * 2.0
            else:
                expected_value = 0.0
        else:
            expected_value = conversion_rate

        return expected_value

    def _apply_context_adjustments(
        self,
        base_rate: float,
        context: Dict
    ) -> float:
        """
        Apply game context adjustments to conversion rate.

        Args:
            base_rate: Base conversion probability
            context: Game context dict

        Returns:
            Adjusted conversion rate
        """
        adjusted_rate = base_rate

        # Time pressure (late in game)
        time_remaining = context.get('time_remaining', 1.0)  # 0-1 normalized
        if time_remaining < 0.1:
            # High pressure in final moments
            pressure_modifier = 0.95
        else:
            pressure_modifier = 1.0

        adjusted_rate *= pressure_modifier

        # Score differential pressure
        score_diff = abs(context.get('score_diff', 0))
        if score_diff <= 1:
            # Close game = more pressure
            close_game_modifier = 0.97
        else:
            close_game_modifier = 1.0

        adjusted_rate *= close_game_modifier

        # Explicit pressure rating
        pressure = context.get('pressure', 0.5)  # 0-1 scale
        pressure_impact = 1.0 - (pressure * 0.1)  # Max 10% reduction

        adjusted_rate *= pressure_impact

        return adjusted_rate

    def calculate_power_play_value(
        self,
        pp_type: str,
        duration: float,
        team_pp_pct: Optional[float] = None
    ) -> float:
        """
        Calculate expected value of hockey power play.

        Args:
            pp_type: Power play type ('minor', 'major', '5_on_3')
            duration: Duration in minutes
            team_pp_pct: Team's power play conversion %

        Returns:
            Expected goals from power play
        """
        if self.sport != 'hockey':
            return 0.0

        # Base goals per minute rates
        goals_per_minute = {
            'minor': 0.10,   # ~20% conversion on 2-min PP
            'major': 0.09,   # ~45% on 5-min PP
            '5_on_3': 0.275  # ~55% on 2-min 5-on-3
        }

        base_rate = goals_per_minute.get(pp_type, 0.10)

        # Adjust for team skill
        if team_pp_pct is not None:
            # League average is typically ~20%
            skill_multiplier = team_pp_pct / 0.20
            base_rate *= skill_multiplier

        expected_goals = base_rate * duration

        return expected_goals

    def calculate_pk_win_prob_impact(
        self,
        expected_value: float,
        current_score_diff: int
    ) -> float:
        """
        Calculate win probability swing from penalty situation.

        Args:
            expected_value: Expected points from penalty
            current_score_diff: Current score differential

        Returns:
            Change in win probability (percentage points)
        """
        # Leverage factor: penalties worth more in close games
        if abs(current_score_diff) <= 1:
            leverage = 1.5
        elif abs(current_score_diff) <= 3:
            leverage = 1.2
        else:
            leverage = 0.8

        # Base impact: 1 expected goal typically worth ~8-10% win prob in soccer
        base_impact_per_goal = 0.09

        win_prob_delta = expected_value * base_impact_per_goal * leverage

        return win_prob_delta

    def simulate_penalty_shootout(
        self,
        team_a_skill: float,
        team_b_skill: float,
        num_rounds: int = 5
    ) -> Dict:
        """
        Simulate penalty shootout (soccer) or shootout (hockey).

        Args:
            team_a_skill: Team A penalty skill (0.7-0.9 range)
            team_b_skill: Team B penalty skill
            num_rounds: Number of penalty rounds

        Returns:
            Simulation results with win probabilities
        """
        simulations = 10000
        team_a_wins = 0
        team_b_wins = 0

        for _ in range(simulations):
            score_a = 0
            score_b = 0

            # Regular rounds
            for _ in range(num_rounds):
                if np.random.random() < team_a_skill:
                    score_a += 1
                if np.random.random() < team_b_skill:
                    score_b += 1

            # Sudden death if tied
            round_num = num_rounds
            while score_a == score_b and round_num < 15:
                a_scores = np.random.random() < team_a_skill
                b_scores = np.random.random() < team_b_skill

                if a_scores and not b_scores:
                    score_a += 1
                elif b_scores and not a_scores:
                    score_b += 1
                elif a_scores and b_scores:
                    score_a += 1
                    score_b += 1

                round_num += 1

            if score_a > score_b:
                team_a_wins += 1
            elif score_b > score_a:
                team_b_wins += 1

        return {
            'team_a_win_prob': team_a_wins / simulations,
            'team_b_win_prob': team_b_wins / simulations,
            'expected_rounds': num_rounds + 1.5
        }
