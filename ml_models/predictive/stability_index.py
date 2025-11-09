"""
Performance Stability Index

Analyzes player performance consistency and volatility.
Identifies reliable players vs. boom-bust performers.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from ..base.feature_engineering import FeatureEngineer


class PerformanceStabilityAnalyzer:
    """
    Calculates performance stability metrics for players

    The Stability Index measures how consistent a player's performance is
    across games. Higher scores indicate more predictable performance.

    Scale: 0-100
    - 80-100: Very Consistent (reliable performers)
    - 60-79:  Consistent (generally reliable)
    - 40-59:  Moderate (some variability)
    - 0-39:   Volatile (boom-bust performers)
    """

    def __init__(self):
        self.feature_engineer = FeatureEngineer()

    def calculate_stability_index(
        self,
        game_logs: List[Dict[str, Any]],
        metric: str = 'points',
        min_games: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate stability index for a player's performance

        Args:
            game_logs: List of game performance dicts
            metric: Stat to analyze (e.g., 'points', 'rebounds', 'assists')
            min_games: Minimum games required for analysis

        Returns:
            Dict with stability metrics and insights

        Example:
            >>> analyzer = PerformanceStabilityAnalyzer()
            >>> games = [
            ...     {'points': 25, 'date': '2024-01-01'},
            ...     {'points': 28, 'date': '2024-01-03'},
            ...     {'points': 22, 'date': '2024-01-05'},
            ... ]
            >>> result = analyzer.calculate_stability_index(games, metric='points')
            >>> print(f"Stability: {result['stability_index']:.1f}/100")
        """
        if len(game_logs) < min_games:
            return {
                'error': f'Insufficient data: {len(game_logs)} games (minimum {min_games})',
                'stability_index': None
            }

        # Extract metric values
        values = [game.get(metric, 0) for game in game_logs]

        # Calculate variance metrics
        variance_metrics = self.feature_engineer.calculate_variance_metrics(values)

        # Calculate coefficient of variation (CV)
        cv = variance_metrics['cv']

        # Stability Index: inverse of CV, scaled to 0-100
        # Lower CV = higher stability
        # We use a scaled sigmoid-like function to map CV to 0-100
        if cv == 0:
            stability_index = 100.0
        else:
            # CV of 0.5 = moderate stability (50)
            # CV of 0.2 = high stability (80+)
            # CV of 1.0 = low stability (20-30)
            stability_index = max(0, min(100, 100 * (1 - cv / 1.5)))

        # Calculate additional insights
        recent_trend = self.feature_engineer.calculate_momentum(values, window=5)
        outliers = self.feature_engineer.detect_outliers(values)
        num_outliers = sum(outliers)

        # Determine consistency rating
        rating = self._get_consistency_rating(stability_index)

        # Calculate floor and ceiling (10th and 90th percentiles)
        floor = np.percentile(values, 10)
        ceiling = np.percentile(values, 90)

        return {
            'stability_index': round(stability_index, 1),
            'consistency_rating': rating,
            'mean_performance': round(variance_metrics['mean'], 1),
            'median_performance': round(variance_metrics['median'], 1),
            'std_dev': round(variance_metrics['std'], 2),
            'coefficient_variation': round(cv, 3),
            'range': {
                'min': variance_metrics['min'],
                'max': variance_metrics['max'],
                'spread': round(variance_metrics['range'], 1)
            },
            'percentiles': {
                'floor_10th': round(floor, 1),
                'ceiling_90th': round(ceiling, 1)
            },
            'recent_trend': self._interpret_trend(recent_trend),
            'trend_value': round(recent_trend, 2),
            'outlier_games': num_outliers,
            'total_games': len(game_logs),
            'reliability_score': self._calculate_reliability(stability_index, recent_trend)
        }

    def compare_players(
        self,
        players_data: Dict[str, List[Dict]],
        metric: str = 'points'
    ) -> List[Dict[str, Any]]:
        """
        Compare stability across multiple players

        Args:
            players_data: Dict mapping player names to their game logs
            metric: Stat to compare

        Returns:
            List of player comparisons sorted by stability

        Example:
            >>> data = {
            ...     'Player A': [{'points': 20}, {'points': 22}, ...],
            ...     'Player B': [{'points': 15}, {'points': 30}, ...]
            ... }
            >>> comparison = analyzer.compare_players(data)
        """
        results = []

        for player_name, game_logs in players_data.items():
            stability = self.calculate_stability_index(game_logs, metric)
            if stability.get('stability_index') is not None:
                results.append({
                    'player': player_name,
                    **stability
                })

        # Sort by stability index (descending)
        results.sort(key=lambda x: x['stability_index'], reverse=True)

        return results

    def analyze_by_context(
        self,
        game_logs: List[Dict[str, Any]],
        metric: str = 'points',
        context_key: str = 'home_away'
    ) -> Dict[str, Dict]:
        """
        Analyze stability in different contexts (home/away, vs opponent, etc.)

        Args:
            game_logs: List of game logs with context data
            metric: Stat to analyze
            context_key: Key to group by ('home_away', 'opponent', etc.)

        Returns:
            Dict mapping contexts to stability metrics
        """
        contexts = {}

        # Group games by context
        for game in game_logs:
            context = game.get(context_key, 'unknown')
            if context not in contexts:
                contexts[context] = []
            contexts[context].append(game)

        # Calculate stability for each context
        results = {}
        for context, games in contexts.items():
            if len(games) >= 3:  # Minimum 3 games for context analysis
                results[context] = self.calculate_stability_index(games, metric)

        return results

    def _get_consistency_rating(self, stability_index: float) -> str:
        """Map stability index to rating category"""
        if stability_index >= 80:
            return "Very Consistent ⭐⭐⭐"
        elif stability_index >= 60:
            return "Consistent ⭐⭐"
        elif stability_index >= 40:
            return "Moderate ⭐"
        else:
            return "Volatile ⚠️"

    def _interpret_trend(self, trend_value: float) -> str:
        """Interpret momentum trend"""
        if trend_value > 1.0:
            return "Improving 📈"
        elif trend_value < -1.0:
            return "Declining 📉"
        else:
            return "Stable ➡️"

    def _calculate_reliability(self, stability_index: float, trend: float) -> float:
        """
        Calculate overall reliability score

        Combines stability with trend (upward trend = more reliable for future)
        """
        # Base score from stability
        base_score = stability_index

        # Adjust for trend (upward trend adds up to 10 points)
        trend_bonus = min(10, max(-10, trend * 2))

        reliability = base_score + trend_bonus
        return round(max(0, min(100, reliability)), 1)

    def generate_report(
        self,
        player_name: str,
        game_logs: List[Dict[str, Any]],
        metric: str = 'points'
    ) -> str:
        """
        Generate a human-readable stability report

        Args:
            player_name: Player's name
            game_logs: Game performance logs
            metric: Metric to analyze

        Returns:
            Formatted report string
        """
        result = self.calculate_stability_index(game_logs, metric)

        if result.get('error'):
            return f"❌ {result['error']}"

        report = f"""
🎯 **Performance Stability Report: {player_name}**

**Stability Index:** {result['stability_index']}/100 - {result['consistency_rating']}

**Performance Summary ({metric}):**
• Average: {result['mean_performance']} (Median: {result['median_performance']})
• Standard Deviation: {result['std_dev']}
• Range: {result['range']['min']} - {result['range']['max']} (spread: {result['range']['spread']})

**Reliability:**
• Floor (10th percentile): {result['percentiles']['floor_10th']}
• Ceiling (90th percentile): {result['percentiles']['ceiling_90th']}
• Reliability Score: {result['reliability_score']}/100

**Recent Form:**
• Trend: {result['recent_trend']} ({result['trend_value']:+.2f} per game)
• Outlier Performances: {result['outlier_games']} out of {result['total_games']} games

**Analysis:**
"""
        # Add context-specific insights
        if result['stability_index'] >= 80:
            report += "This player is extremely reliable and consistent. Excellent for fantasy and daily lineups.\n"
        elif result['stability_index'] >= 60:
            report += "Solid, dependable performer with predictable output. Good floor, minimal risk.\n"
        elif result['stability_index'] >= 40:
            report += "Moderate volatility. Performance varies but not wildly unpredictable.\n"
        else:
            report += "High variance performer - boom or bust. Risky for consistent production.\n"

        if result['trend_value'] > 1:
            report += "⚠️ Note: Recent upward trend suggests improving form.\n"
        elif result['trend_value'] < -1:
            report += "⚠️ Note: Recent downward trend - monitor for potential slump.\n"

        return report.strip()


# Example usage
if __name__ == "__main__":
    # Demo with sample data
    analyzer = PerformanceStabilityAnalyzer()

    # Sample player game logs
    consistent_player = [
        {'points': 24, 'rebounds': 8, 'assists': 5, 'date': '2024-01-01'},
        {'points': 26, 'rebounds': 7, 'assists': 6, 'date': '2024-01-03'},
        {'points': 23, 'rebounds': 9, 'assists': 5, 'date': '2024-01-05'},
        {'points': 25, 'rebounds': 8, 'assists': 7, 'date': '2024-01-07'},
        {'points': 27, 'rebounds': 7, 'assists': 6, 'date': '2024-01-09'},
        {'points': 24, 'rebounds': 8, 'assists': 5, 'date': '2024-01-11'},
        {'points': 26, 'rebounds': 9, 'assists': 6, 'date': '2024-01-13'},
    ]

    volatile_player = [
        {'points': 15, 'rebounds': 4, 'assists': 3, 'date': '2024-01-01'},
        {'points': 35, 'rebounds': 10, 'assists': 8, 'date': '2024-01-03'},
        {'points': 8, 'rebounds': 2, 'assists': 1, 'date': '2024-01-05'},
        {'points': 42, 'rebounds': 12, 'assists': 9, 'date': '2024-01-07'},
        {'points': 12, 'rebounds': 5, 'assists': 2, 'date': '2024-01-09'},
        {'points': 38, 'rebounds': 11, 'assists': 7, 'date': '2024-01-11'},
        {'points': 10, 'rebounds': 3, 'assists': 2, 'date': '2024-01-13'},
    ]

    print("=" * 60)
    print(analyzer.generate_report("Consistent Player", consistent_player))
    print("\n" + "=" * 60)
    print(analyzer.generate_report("Volatile Player", volatile_player))
    print("\n" + "=" * 60)

    # Compare players
    comparison = analyzer.compare_players({
        'Consistent Player': consistent_player,
        'Volatile Player': volatile_player
    })

    print("\n📊 Player Comparison:")
    for i, player in enumerate(comparison, 1):
        print(f"{i}. {player['player']}: {player['stability_index']}/100 - {player['consistency_rating']}")
