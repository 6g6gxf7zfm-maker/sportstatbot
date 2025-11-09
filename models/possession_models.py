"""
Possession Value Models

16. Possession value network using Markov transitions
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class PossessionValueNetwork:
    """
    Possession value network using Markov transitions.

    Models possession value using Markov chain of possible states
    and transition probabilities to calculate expected points.
    """

    def __init__(self, sport: str = 'basketball'):
        """
        Initialize possession value network.

        Args:
            sport: Sport type
        """
        self.sport = sport

        # Define possession states and transitions
        self.states = self._define_states()
        self.transition_matrix = None
        self.state_values = {}

    def _define_states(self) -> List[str]:
        """Define possession states based on sport."""
        if self.sport == 'basketball':
            return [
                'start',
                'paint_attempt',
                'mid_range_attempt',
                'three_point_attempt',
                'free_throw',
                'offensive_rebound',
                'turnover',
                'made_2pt',
                'made_3pt',
                'made_ft',
                'miss_end'
            ]
        elif self.sport == 'football':
            return [
                'start',
                'run',
                'short_pass',
                'long_pass',
                'touchdown',
                'field_goal',
                'turnover',
                'punt',
                'incomplete'
            ]
        else:
            return ['start', 'shot', 'turnover', 'goal', 'miss']

    def build_transition_matrix(
        self,
        team_data: Dict[str, float]
    ) -> np.ndarray:
        """
        Build Markov transition matrix from team tendencies.

        Args:
            team_data: Team statistical tendencies

        Returns:
            Transition probability matrix
        """
        n_states = len(self.states)
        matrix = np.zeros((n_states, n_states))

        if self.sport == 'basketball':
            matrix = self._build_basketball_transitions(team_data)
        elif self.sport == 'football':
            matrix = self._build_football_transitions(team_data)

        self.transition_matrix = matrix
        return matrix

    def _build_basketball_transitions(
        self,
        team_data: Dict[str, float]
    ) -> np.ndarray:
        """Build basketball-specific transition matrix."""
        state_idx = {state: i for i, state in enumerate(self.states)}
        n = len(self.states)
        matrix = np.zeros((n, n))

        # Extract team tendencies
        paint_rate = team_data.get('paint_attempt_rate', 0.35)
        mid_rate = team_data.get('mid_range_rate', 0.20)
        three_rate = team_data.get('three_point_rate', 0.35)
        tov_rate = team_data.get('turnover_rate', 0.10)

        paint_fg = team_data.get('paint_fg_pct', 0.55)
        mid_fg = team_data.get('mid_range_fg_pct', 0.40)
        three_fg = team_data.get('three_point_fg_pct', 0.35)
        oreb_rate = team_data.get('offensive_rebound_rate', 0.25)
        ft_rate = team_data.get('free_throw_rate', 0.25)

        # From start state
        start_idx = state_idx['start']
        matrix[start_idx, state_idx['paint_attempt']] = paint_rate
        matrix[start_idx, state_idx['mid_range_attempt']] = mid_rate
        matrix[start_idx, state_idx['three_point_attempt']] = three_rate
        matrix[start_idx, state_idx['turnover']] = tov_rate

        # From shot attempts
        paint_idx = state_idx['paint_attempt']
        matrix[paint_idx, state_idx['made_2pt']] = paint_fg
        matrix[paint_idx, state_idx['free_throw']] = ft_rate * (1 - paint_fg)
        matrix[paint_idx, state_idx['offensive_rebound']] = oreb_rate * (1 - paint_fg) * (1 - ft_rate)
        matrix[paint_idx, state_idx['miss_end']] = (1 - paint_fg) * (1 - ft_rate) * (1 - oreb_rate)

        mid_idx = state_idx['mid_range_attempt']
        matrix[mid_idx, state_idx['made_2pt']] = mid_fg
        matrix[mid_idx, state_idx['offensive_rebound']] = oreb_rate * (1 - mid_fg)
        matrix[mid_idx, state_idx['miss_end']] = (1 - mid_fg) * (1 - oreb_rate)

        three_idx = state_idx['three_point_attempt']
        matrix[three_idx, state_idx['made_3pt']] = three_fg
        matrix[three_idx, state_idx['offensive_rebound']] = oreb_rate * (1 - three_fg)
        matrix[three_idx, state_idx['miss_end']] = (1 - three_fg) * (1 - oreb_rate)

        # From offensive rebound (restart possession with lower rates)
        oreb_idx = state_idx['offensive_rebound']
        matrix[oreb_idx, state_idx['paint_attempt']] = 0.50
        matrix[oreb_idx, state_idx['three_point_attempt']] = 0.30
        matrix[oreb_idx, state_idx['turnover']] = 0.20

        # Terminal states (absorbing)
        for terminal in ['made_2pt', 'made_3pt', 'miss_end', 'turnover']:
            idx = state_idx[terminal]
            matrix[idx, idx] = 1.0

        return matrix

    def _build_football_transitions(
        self,
        team_data: Dict[str, float]
    ) -> np.ndarray:
        """Build football-specific transition matrix."""
        # Simplified football model
        state_idx = {state: i for i, state in enumerate(self.states)}
        n = len(self.states)
        matrix = np.zeros((n, n))

        # From start
        start_idx = state_idx['start']
        matrix[start_idx, state_idx['run']] = team_data.get('run_rate', 0.45)
        matrix[start_idx, state_idx['short_pass']] = team_data.get('short_pass_rate', 0.35)
        matrix[start_idx, state_idx['long_pass']] = team_data.get('long_pass_rate', 0.20)

        # Terminal states
        for terminal in ['touchdown', 'field_goal', 'turnover', 'punt']:
            idx = state_idx[terminal]
            matrix[idx, idx] = 1.0

        return matrix

    def calculate_possession_value(
        self,
        start_state: str = 'start',
        max_steps: int = 10
    ) -> float:
        """
        Calculate expected points from a possession.

        Args:
            start_state: Starting state
            max_steps: Maximum transition steps

        Returns:
            Expected points
        """
        if self.transition_matrix is None:
            return 0.0

        # Define terminal state values
        terminal_values = {
            'made_2pt': 2.0,
            'made_3pt': 3.0,
            'made_ft': 1.0,
            'touchdown': 7.0,
            'field_goal': 3.0,
            'goal': 1.0,
            'turnover': 0.0,
            'miss_end': 0.0,
            'punt': 0.0
        }

        state_idx = {state: i for i, state in enumerate(self.states)}
        start_idx = state_idx.get(start_state, 0)

        # Initialize state probability distribution
        current_dist = np.zeros(len(self.states))
        current_dist[start_idx] = 1.0

        total_value = 0.0

        # Iterate transitions
        for step in range(max_steps):
            # Accumulate value from terminal states
            for state, value in terminal_values.items():
                if state in state_idx:
                    idx = state_idx[state]
                    total_value += current_dist[idx] * value

            # Transition to next state
            current_dist = current_dist @ self.transition_matrix

            # Check for convergence (all probability in terminal states)
            if np.sum(current_dist) < 0.01:
                break

        return total_value

    def expected_points_per_possession(
        self,
        team_data: Dict[str, float]
    ) -> float:
        """
        Calculate team's expected points per possession.

        Args:
            team_data: Team statistical profile

        Returns:
            Expected PPP (points per possession)
        """
        self.build_transition_matrix(team_data)
        expected_value = self.calculate_possession_value()

        return expected_value

    def possession_efficiency_breakdown(
        self,
        team_data: Dict[str, float]
    ) -> Dict:
        """
        Break down possession efficiency by component.

        Args:
            team_data: Team data

        Returns:
            Efficiency breakdown
        """
        self.build_transition_matrix(team_data)

        # Calculate values from different starting points
        if self.sport == 'basketball':
            components = {
                'paint_possession': self.calculate_possession_value('paint_attempt'),
                'mid_range_possession': self.calculate_possession_value('mid_range_attempt'),
                'three_point_possession': self.calculate_possession_value('three_point_attempt'),
                'second_chance': self.calculate_possession_value('offensive_rebound')
            }
        else:
            components = {
                'overall': self.calculate_possession_value('start')
            }

        total_value = self.calculate_possession_value('start')

        return {
            'expected_ppp': total_value,
            'component_values': components,
            'efficiency_rating': total_value / 1.08 * 100  # Normalize to 100 scale
        }

    def compare_possession_strategies(
        self,
        strategy_a: Dict[str, float],
        strategy_b: Dict[str, float]
    ) -> Dict:
        """
        Compare expected value of two strategies.

        Args:
            strategy_a: First strategy's team data
            strategy_b: Second strategy's team data

        Returns:
            Comparison results
        """
        value_a = self.expected_points_per_possession(strategy_a)
        value_b = self.expected_points_per_possession(strategy_b)

        return {
            'strategy_a_ppp': value_a,
            'strategy_b_ppp': value_b,
            'difference': value_a - value_b,
            'better_strategy': 'A' if value_a > value_b else 'B',
            'advantage_pct': abs((value_a - value_b) / value_b * 100) if value_b > 0 else 0
        }
