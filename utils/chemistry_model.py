"""Team chemistry model for analyzing optimal lineup combinations."""
from typing import Dict, List, Tuple
import itertools


class TeamChemistryModel:
    """
    Analyzes team chemistry and optimal lineup combinations.

    Measures how well different player combinations perform together.
    """

    def __init__(self):
        """Initialize team chemistry model."""
        self.lineup_stats = {}

    def analyze_lineup_performance(
        self,
        lineup: List[str],
        performance_data: List[Dict]
    ) -> Dict:
        """
        Analyze performance of specific lineup combination.

        Args:
            lineup: List of player names in lineup
            performance_data: Historical performance data for this lineup

        Returns:
            Dictionary with lineup performance metrics
        """
        if not performance_data:
            return self._default_analysis(lineup)

        # Calculate aggregate stats
        total_possessions = sum(d.get('possessions', 0) for d in performance_data)
        total_points = sum(d.get('points_scored', 0) for d in performance_data)
        total_allowed = sum(d.get('points_allowed', 0) for d in performance_data)

        offensive_rating = (total_points / total_possessions * 100) if total_possessions > 0 else 100
        defensive_rating = (total_allowed / total_possessions * 100) if total_possessions > 0 else 100
        net_rating = offensive_rating - defensive_rating

        # Calculate win percentage
        wins = sum(1 for d in performance_data if d.get('won', False))
        win_pct = wins / len(performance_data) if performance_data else 0

        return {
            'lineup': lineup,
            'games_played': len(performance_data),
            'win_percentage': round(win_pct, 3),
            'offensive_rating': round(offensive_rating, 1),
            'defensive_rating': round(defensive_rating, 1),
            'net_rating': round(net_rating, 1),
            'plus_minus': round(net_rating * len(performance_data) / 10, 1),
            'chemistry_score': self._calculate_chemistry_score(
                net_rating, win_pct, len(performance_data)
            ),
            'recommendation': self._generate_lineup_recommendation(net_rating, win_pct)
        }

    def find_optimal_lineups(
        self,
        player_pool: List[str],
        lineup_size: int,
        historical_data: Dict[Tuple, List[Dict]],
        min_sample_size: int = 5
    ) -> List[Dict]:
        """
        Find optimal lineup combinations from player pool.

        Args:
            player_pool: Available players
            lineup_size: Number of players in lineup (e.g., 5 for basketball)
            historical_data: Performance data keyed by lineup tuple
            min_sample_size: Minimum games to consider lineup

        Returns:
            List of top lineups sorted by performance
        """
        lineup_analyses = []

        for lineup_tuple in historical_data:
            data = historical_data[lineup_tuple]

            if len(data) < min_sample_size:
                continue

            lineup_list = list(lineup_tuple)
            analysis = self.analyze_lineup_performance(lineup_list, data)
            lineup_analyses.append(analysis)

        # Sort by net rating
        lineup_analyses.sort(key=lambda x: x['net_rating'], reverse=True)

        return lineup_analyses[:10]  # Top 10 lineups

    def analyze_player_combinations(
        self,
        player1: str,
        player2: str,
        combination_data: List[Dict]
    ) -> Dict:
        """
        Analyze how two specific players perform together.

        Args:
            player1: First player name
            player2: Second player name
            combination_data: Performance when both players are on court

        Returns:
            Dictionary with combination analysis
        """
        if not combination_data:
            return {
                'player1': player1,
                'player2': player2,
                'synergy': 'UNKNOWN',
                'note': 'Insufficient data'
            }

        total_minutes = sum(d.get('minutes_together', 0) for d in combination_data)
        total_plus_minus = sum(d.get('plus_minus', 0) for d in combination_data)

        avg_plus_minus = total_plus_minus / len(combination_data)
        per_48_plus_minus = (total_plus_minus / total_minutes * 48) if total_minutes > 0 else 0

        # Determine synergy level
        synergy = self._determine_synergy(per_48_plus_minus)

        return {
            'player1': player1,
            'player2': player2,
            'minutes_together': round(total_minutes, 1),
            'games_together': len(combination_data),
            'avg_plus_minus': round(avg_plus_minus, 1),
            'per_48_plus_minus': round(per_48_plus_minus, 1),
            'synergy': synergy,
            'recommendation': self._generate_duo_recommendation(synergy, per_48_plus_minus)
        }

    def _calculate_chemistry_score(
        self,
        net_rating: float,
        win_pct: float,
        sample_size: int
    ) -> float:
        """
        Calculate overall chemistry score (0-100).

        Combines multiple factors into single score.
        """
        # Base score from net rating
        rating_score = min(50, max(0, 50 + (net_rating / 2)))

        # Win percentage component
        win_score = win_pct * 30

        # Sample size bonus (up to 20 points)
        sample_bonus = min(20, sample_size * 2)

        total_score = rating_score + win_score + sample_bonus

        return round(min(100, total_score), 1)

    def _generate_lineup_recommendation(self, net_rating: float, win_pct: float) -> str:
        """Generate recommendation for lineup usage."""
        if net_rating >= 10 and win_pct >= 0.60:
            return "ELITE - Use this lineup in crucial situations"
        elif net_rating >= 5 and win_pct >= 0.55:
            return "STRONG - Reliable lineup for regular use"
        elif net_rating >= 0:
            return "AVERAGE - Serviceable but not optimal"
        elif net_rating >= -5:
            return "BELOW AVERAGE - Consider alternatives"
        else:
            return "POOR - Avoid this lineup combination"

    def _determine_synergy(self, per_48_plus_minus: float) -> str:
        """Determine synergy level between players."""
        if per_48_plus_minus >= 10:
            return "EXCELLENT"
        elif per_48_plus_minus >= 5:
            return "GOOD"
        elif per_48_plus_minus >= 0:
            return "NEUTRAL"
        elif per_48_plus_minus >= -5:
            return "POOR"
        else:
            return "TERRIBLE"

    def _generate_duo_recommendation(self, synergy: str, plus_minus: float) -> str:
        """Generate recommendation for player pairing."""
        if synergy in ["EXCELLENT", "GOOD"]:
            return f"Play together often - strong synergy (+{plus_minus:.1f} per 48 min)"
        elif synergy == "NEUTRAL":
            return "Pairing is acceptable but not optimal"
        else:
            return f"Avoid pairing - negative synergy ({plus_minus:.1f} per 48 min)"

    def _default_analysis(self, lineup: List[str]) -> Dict:
        """Return default analysis when no data available."""
        return {
            'lineup': lineup,
            'games_played': 0,
            'chemistry_score': 50,
            'note': 'No performance data available'
        }
