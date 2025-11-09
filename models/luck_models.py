"""
Luck and Variance Models

12. Dynamic luck index: expected vs actual scoring differential
"""

import numpy as np
from typing import Dict, List, Optional


class DynamicLuckIndex:
    """
    Dynamic luck index - expected vs actual scoring differential.

    Measures how much a team's results deviate from expected performance,
    identifying teams that are "lucky" or "unlucky".
    """

    def __init__(self):
        """Initialize dynamic luck index model."""
        self.team_luck_profiles = {}

    def calculate_luck_index(
        self,
        team_id: str,
        games: List[Dict]
    ) -> Dict:
        """
        Calculate luck index for a team.

        Args:
            team_id: Team identifier
            games: List of games with 'actual_score', 'opponent_score',
                   'expected_score', 'expected_opponent_score'

        Returns:
            Luck index analysis
        """
        if not games:
            return {
                'luck_index': 0.0,
                'luck_rating': 'Neutral',
                'games_analyzed': 0
            }

        luck_components = []
        actual_wins = 0
        expected_wins = 0

        for game in games:
            actual_score = game.get('actual_score', 0)
            opponent_score = game.get('opponent_score', 0)
            expected_score = game.get('expected_score', actual_score)
            expected_opp_score = game.get('expected_opponent_score', opponent_score)

            # Actual result
            actual_diff = actual_score - opponent_score
            if actual_diff > 0:
                actual_wins += 1

            # Expected result
            expected_diff = expected_score - expected_opp_score
            if expected_diff > 0:
                expected_wins += 0.5  # Could go either way
            elif expected_diff > 3:
                expected_wins += 0.7
            elif expected_diff > 7:
                expected_wins += 0.9

            # Luck component: actual - expected differential
            game_luck = actual_diff - expected_diff
            luck_components.append(game_luck)

        # Overall luck metrics
        total_luck = sum(luck_components)
        avg_luck_per_game = total_luck / len(games)

        # Wins above/below expectation
        win_luck = actual_wins - expected_wins

        # Luck consistency (variance in luck)
        luck_variance = np.var(luck_components)

        # Luck index (standardized)
        # Positive = lucky, negative = unlucky
        luck_index = avg_luck_per_game

        self.team_luck_profiles[team_id] = {
            'luck_index': luck_index,
            'total_luck': total_luck,
            'win_luck': win_luck,
            'luck_variance': luck_variance,
            'games_analyzed': len(games)
        }

        return {
            'luck_index': luck_index,
            'luck_rating': self._luck_to_rating(luck_index),
            'total_luck_points': total_luck,
            'wins_above_expected': win_luck,
            'luck_consistency': self._variance_to_consistency(luck_variance),
            'games_analyzed': len(games),
            'regression_expected': self._predict_regression(luck_index, len(games))
        }

    def _luck_to_rating(self, luck_index: float) -> str:
        """Convert luck index to rating."""
        if luck_index > 5:
            return "Very Lucky"
        elif luck_index > 2:
            return "Lucky"
        elif luck_index > -2:
            return "Neutral"
        elif luck_index > -5:
            return "Unlucky"
        else:
            return "Very Unlucky"

    def _variance_to_consistency(self, variance: float) -> str:
        """Convert variance to consistency description."""
        if variance < 50:
            return "Consistent luck"
        elif variance < 150:
            return "Moderate variance"
        else:
            return "High variance (streaky)"

    def _predict_regression(self, luck_index: float, games_played: int) -> str:
        """Predict regression to mean."""
        if abs(luck_index) < 2:
            return "Performing near expectation - little regression expected"

        # More games = more confidence in regression
        if games_played < 10:
            return "Small sample - results may vary widely"

        if luck_index > 4:
            return "Strong positive luck - expect performance decline"
        elif luck_index > 2:
            return "Moderate positive luck - some decline likely"
        elif luck_index < -4:
            return "Strong negative luck - expect performance improvement"
        else:
            return "Moderate negative luck - some improvement likely"

    def identify_luck_components(
        self,
        team_id: str,
        games: List[Dict]
    ) -> Dict:
        """
        Break down luck into components.

        Args:
            team_id: Team identifier
            games: Games with detailed stats

        Returns:
            Luck component breakdown
        """
        shooting_luck = []
        turnover_luck = []
        bounce_luck = []

        for game in games:
            # Shooting luck (actual FG% vs expected)
            if 'fg_pct' in game and 'expected_fg_pct' in game:
                shooting_luck.append(
                    (game['fg_pct'] - game['expected_fg_pct']) * game.get('fg_attempts', 80)
                )

            # Turnover luck
            if 'turnovers' in game and 'expected_turnovers' in game:
                turnover_luck.append(game['expected_turnovers'] - game['turnovers'])

            # Close game/clutch luck
            if 'score_diff' in game and abs(game.get('score_diff', 10)) <= 5:
                # Close games have luck component
                bounce_luck.append(game.get('actual_score', 0) - game.get('expected_score', 0))

        return {
            'shooting_luck_points': sum(shooting_luck) if shooting_luck else 0,
            'turnover_luck_points': sum(turnover_luck) if turnover_luck else 0,
            'close_game_luck_points': sum(bounce_luck) if bounce_luck else 0,
            'primary_luck_source': self._identify_primary_source(shooting_luck, turnover_luck, bounce_luck)
        }

    def _identify_primary_source(
        self,
        shooting: List[float],
        turnovers: List[float],
        bounces: List[float]
    ) -> str:
        """Identify primary source of luck."""
        totals = {
            'shooting': abs(sum(shooting)) if shooting else 0,
            'turnovers': abs(sum(turnovers)) if turnovers else 0,
            'close_games': abs(sum(bounces)) if bounces else 0
        }

        if max(totals.values()) == 0:
            return "Insufficient data"

        return max(totals.items(), key=lambda x: x[1])[0]

    def predict_future_performance(
        self,
        team_id: str,
        current_record: Dict
    ) -> Dict:
        """
        Predict future performance after luck regression.

        Args:
            team_id: Team identifier
            current_record: Current wins/losses

        Returns:
            Performance prediction
        """
        if team_id not in self.team_luck_profiles:
            return {
                'predicted_wins': current_record.get('wins', 0),
                'confidence': 'Low'
            }

        profile = self.team_luck_profiles[team_id]
        current_wins = current_record.get('wins', 0)
        current_losses = current_record.get('losses', 0)
        total_games = current_wins + current_losses

        if total_games == 0:
            return {'predicted_wins': 0, 'confidence': 'Low'}

        # Current win percentage
        current_win_pct = current_wins / total_games

        # Expected win percentage (adjusted for luck)
        luck_impact_on_wins = profile['win_luck'] / total_games
        expected_win_pct = current_win_pct - luck_impact_on_wins

        # Predict rest of season (assume same number of games remaining)
        remaining_games = total_games  # Simplified assumption

        predicted_future_wins = remaining_games * expected_win_pct
        predicted_total_wins = current_wins + predicted_future_wins

        return {
            'current_wins': current_wins,
            'current_win_pct': current_win_pct,
            'expected_win_pct': expected_win_pct,
            'predicted_final_wins': round(predicted_total_wins),
            'predicted_final_record': f"{round(predicted_total_wins)}-{round(remaining_games - predicted_future_wins)}",
            'confidence': 'High' if total_games > 20 else 'Moderate'
        }
