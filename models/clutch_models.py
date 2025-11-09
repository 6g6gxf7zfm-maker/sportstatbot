"""
Clutch Performance Models

22. Clutch index adjusted for usage rate
"""

import numpy as np
from typing import Dict, List, Optional


class ClutchIndex:
    """
    Clutch index adjusted for usage rate.

    Measures player/team performance in high-leverage situations,
    adjusted for usage and opportunity.
    """

    def __init__(self):
        """Initialize clutch index model."""
        self.player_clutch_stats = {}

    def calculate_clutch_index(
        self,
        player_id: str,
        clutch_situations: List[Dict],
        regular_situations: List[Dict]
    ) -> Dict:
        """
        Calculate player's clutch performance index.

        Args:
            player_id: Player identifier
            clutch_situations: Stats in clutch situations
            regular_situations: Stats in regular situations

        Returns:
            Clutch index analysis
        """
        # Aggregate clutch stats
        clutch_stats = self._aggregate_performance(clutch_situations)
        regular_stats = self._aggregate_performance(regular_situations)

        # Calculate clutch vs regular differentials
        clutch_shooting = clutch_stats.get('fg_pct', 0)
        regular_shooting = regular_stats.get('fg_pct', 0)

        clutch_scoring = clutch_stats.get('points_per_poss', 0)
        regular_scoring = regular_stats.get('points_per_poss', 0)

        # Clutch index components
        shooting_clutch = clutch_shooting - regular_shooting
        scoring_clutch = clutch_scoring - regular_scoring

        # Adjust for usage rate
        usage_rate = clutch_stats.get('usage_rate', 0.20)
        usage_adjustment = self._usage_adjustment(usage_rate)

        # Final clutch index
        raw_clutch_index = (
            0.6 * scoring_clutch +
            0.4 * shooting_clutch
        )

        adjusted_clutch_index = raw_clutch_index * usage_adjustment

        # Normalize to -10 to +10 scale
        normalized_index = adjusted_clutch_index * 100

        self.player_clutch_stats[player_id] = {
            'clutch_index': normalized_index,
            'clutch_rating': self._index_to_rating(normalized_index),
            'clutch_situations_count': len(clutch_situations),
            'usage_rate': usage_rate,
            'clutch_fg_pct': clutch_shooting,
            'regular_fg_pct': regular_shooting,
            'clutch_ppg': clutch_scoring,
            'regular_ppg': regular_scoring
        }

        return self.player_clutch_stats[player_id]

    def _aggregate_performance(self, situations: List[Dict]) -> Dict:
        """Aggregate performance across situations."""
        if not situations:
            return {
                'fg_pct': 0,
                'points_per_poss': 0,
                'usage_rate': 0
            }

        total_fgm = sum(s.get('fg_made', 0) for s in situations)
        total_fga = sum(s.get('fg_attempts', 0) for s in situations)
        total_points = sum(s.get('points', 0) for s in situations)
        total_possessions = sum(s.get('possessions', 0) for s in situations)

        fg_pct = total_fgm / total_fga if total_fga > 0 else 0
        points_per_poss = total_points / total_possessions if total_possessions > 0 else 0

        # Usage rate approximation
        team_possessions = sum(s.get('team_possessions', 0) for s in situations)
        usage = total_fga / team_possessions if team_possessions > 0 else 0.20

        return {
            'fg_pct': fg_pct,
            'points_per_poss': points_per_poss,
            'usage_rate': usage
        }

    def _usage_adjustment(self, usage_rate: float) -> float:
        """
        Adjust clutch index for usage rate.

        Higher usage in clutch = harder to maintain efficiency.
        """
        # Normalize around 25% usage
        if usage_rate < 0.15:
            # Low usage = easier to be efficient, reduce credit
            return 0.8
        elif usage_rate < 0.20:
            return 0.9
        elif usage_rate < 0.30:
            return 1.0  # Normal usage
        elif usage_rate < 0.35:
            return 1.1  # High usage bonus
        else:
            return 1.2  # Very high usage bonus

    def _index_to_rating(self, index: float) -> str:
        """Convert clutch index to rating."""
        if index > 5:
            return "Elite Clutch"
        elif index > 2:
            return "Above Average Clutch"
        elif index > -2:
            return "Average"
        elif index > -5:
            return "Below Average Clutch"
        else:
            return "Poor in Clutch"

    def identify_clutch_situations(
        self,
        game_events: List[Dict],
        score_threshold: int = 5,
        time_threshold: float = 5.0
    ) -> List[Dict]:
        """
        Identify clutch situations from game events.

        Args:
            game_events: List of game events
            score_threshold: Score differential threshold for clutch
            time_threshold: Time remaining threshold (minutes)

        Returns:
            List of clutch situation events
        """
        clutch_events = []

        for event in game_events:
            score_diff = abs(event.get('score_diff', 100))
            time_remaining = event.get('time_remaining', 100)

            # Clutch = close game + late
            if score_diff <= score_threshold and time_remaining <= time_threshold:
                event['clutch_leverage'] = self._calculate_leverage(
                    score_diff,
                    time_remaining
                )
                clutch_events.append(event)

        return clutch_events

    def _calculate_leverage(
        self,
        score_diff: int,
        time_remaining: float
    ) -> float:
        """
        Calculate leverage/importance of situation.

        Args:
            score_diff: Current score differential
            time_remaining: Minutes remaining

        Returns:
            Leverage score (0-1)
        """
        # Closer score = higher leverage
        score_factor = 1.0 - (score_diff / 10.0)
        score_factor = max(score_factor, 0)

        # Less time = higher leverage
        time_factor = 1.0 - (time_remaining / 10.0)
        time_factor = max(time_factor, 0)

        # Combined leverage
        leverage = (score_factor + time_factor) / 2

        return np.clip(leverage, 0, 1)

    def clutch_win_probability_added(
        self,
        player_id: str,
        clutch_events: List[Dict]
    ) -> Dict:
        """
        Calculate win probability added in clutch situations.

        Args:
            player_id: Player identifier
            clutch_events: Player's clutch events with 'wp_before', 'wp_after'

        Returns:
            WPA analysis
        """
        total_wpa = 0.0
        positive_plays = 0
        negative_plays = 0

        for event in clutch_events:
            if event.get('player_id') == player_id:
                wp_before = event.get('wp_before', 0.5)
                wp_after = event.get('wp_after', 0.5)

                wpa = wp_after - wp_before
                total_wpa += wpa

                if wpa > 0:
                    positive_plays += 1
                else:
                    negative_plays += 1

        return {
            'total_clutch_wpa': total_wpa,
            'avg_wpa_per_play': total_wpa / len(clutch_events) if clutch_events else 0,
            'positive_plays': positive_plays,
            'negative_plays': negative_plays,
            'clutch_impact': 'Positive' if total_wpa > 0 else 'Negative'
        }

    def team_clutch_performance(
        self,
        team_id: str,
        clutch_games: List[Dict]
    ) -> Dict:
        """
        Analyze team's clutch performance.

        Args:
            team_id: Team identifier
            clutch_games: Games decided in clutch situations

        Returns:
            Team clutch analysis
        """
        wins = sum(1 for g in clutch_games if g.get('won', False))
        losses = len(clutch_games) - wins

        clutch_win_pct = wins / len(clutch_games) if clutch_games else 0

        # Calculate expected win% in clutch games based on talent
        expected_wins = sum(g.get('pre_game_win_prob', 0.5) for g in clutch_games)
        expected_win_pct = expected_wins / len(clutch_games) if clutch_games else 0.5

        # Clutch performance vs expectation
        clutch_advantage = clutch_win_pct - expected_win_pct

        return {
            'clutch_record': f"{wins}-{losses}",
            'clutch_win_pct': clutch_win_pct,
            'expected_win_pct': expected_win_pct,
            'clutch_advantage': clutch_advantage,
            'wins_above_expected': wins - expected_wins,
            'clutch_rating': self._team_clutch_rating(clutch_advantage)
        }

    def _team_clutch_rating(self, advantage: float) -> str:
        """Convert team clutch advantage to rating."""
        if advantage > 0.10:
            return "Elite in Clutch"
        elif advantage > 0.05:
            return "Good in Clutch"
        elif advantage > -0.05:
            return "Average in Clutch"
        elif advantage > -0.10:
            return "Poor in Clutch"
        else:
            return "Very Poor in Clutch"
