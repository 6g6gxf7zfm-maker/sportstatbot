"""Upset probability detector for flagging potential shocking results."""
from typing import Dict, List, Optional
from datetime import datetime


class UpsetProbabilityDetector:
    """
    Detects and flags games with high upset potential.

    Uses multiple factors to identify games where underdogs have
    a realistic chance of winning.
    """

    def __init__(
        self,
        monte_carlo_engine=None,
        power_rating_system=None,
        upset_threshold: float = 0.30
    ):
        """
        Initialize upset detector.

        Args:
            monte_carlo_engine: MonteCarloEngine instance
            power_rating_system: PowerRatingSystem instance
            upset_threshold: Minimum probability to flag as potential upset
        """
        self.monte_carlo = monte_carlo_engine
        self.power_rating = power_rating_system
        self.upset_threshold = upset_threshold

    def detect_upsets(
        self,
        games: List[Dict],
        sport: str,
        **context
    ) -> List[Dict]:
        """
        Analyze games for upset potential.

        Args:
            games: List of upcoming games
            sport: Sport type
            **context: Additional context factors

        Returns:
            List of games with high upset potential
        """
        upset_alerts = []

        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')

            if not home_team or not away_team:
                continue

            # Determine favorite
            home_rating = self.power_rating.get_rating(home_team, sport) if self.power_rating else 1500
            away_rating = self.power_rating.get_rating(away_team, sport) if self.power_rating else 1500

            is_home_favorite = (home_rating + 100) > away_rating  # 100 = home advantage
            favorite = home_team if is_home_favorite else away_team
            underdog = away_team if is_home_favorite else home_team
            favorite_rating = home_rating if is_home_favorite else away_rating
            underdog_rating = away_rating if is_home_favorite else home_rating

            # Calculate upset probability using Monte Carlo
            if self.monte_carlo:
                upset_analysis = self.monte_carlo.calculate_upset_probability(
                    favorite_rating,
                    underdog_rating,
                    sport,
                    **game.get('adjustments', {})
                )
                upset_prob = upset_analysis['upset_probability']
            else:
                # Simple calculation
                rating_diff = favorite_rating - underdog_rating
                upset_prob = 1 / (1 + pow(10, rating_diff / 400))

            # Check if meets threshold
            if upset_prob >= self.upset_threshold:
                upset_factors = self._analyze_upset_factors(
                    game, favorite, underdog, sport, upset_prob
                )

                upset_alerts.append({
                    'game': f"{away_team} @ {home_team}",
                    'favorite': favorite,
                    'underdog': underdog,
                    'upset_probability': round(upset_prob, 3),
                    'confidence_level': self._get_confidence_level(upset_prob),
                    'upset_factors': upset_factors,
                    'alert_level': self._get_alert_level(upset_prob),
                    'game_date': game.get('date'),
                    'sport': sport,
                    'timestamp': datetime.now().isoformat()
                })

        # Sort by upset probability
        upset_alerts.sort(key=lambda x: x['upset_probability'], reverse=True)

        return upset_alerts

    def _analyze_upset_factors(
        self,
        game: Dict,
        favorite: str,
        underdog: str,
        sport: str,
        upset_prob: float
    ) -> List[str]:
        """Analyze what factors contribute to upset potential."""
        factors = []

        # Check for injuries to favorite
        if game.get('favorite_injuries', 0) > 3:
            factors.append(f"{favorite} dealing with significant injuries")

        # Check for underdog momentum
        underdog_streak = game.get('underdog_streak', 0)
        if underdog_streak >= 3:
            factors.append(f"{underdog} on {underdog_streak}-game win streak")

        # Check for rest advantage
        rest_diff = game.get('rest_differential', 0)
        if rest_diff >= 2:
            factors.append(f"{underdog} has {rest_diff} more days rest")

        # Check for home underdog
        is_home_underdog = game.get('home_team') == underdog
        if is_home_underdog:
            factors.append(f"{underdog} has home court/field advantage")

        # Check for recent head-to-head
        if game.get('underdog_won_last_h2h', False):
            factors.append(f"{underdog} won last head-to-head matchup")

        # Motivation factors
        if game.get('underdog_playoff_implications', False):
            factors.append(f"{underdog} playing for playoff position")

        if game.get('favorite_looking_ahead', False):
            factors.append(f"{favorite} may be looking ahead to next opponent")

        # Add probability-based factor
        if upset_prob >= 0.40:
            factors.append("Statistical models show this as nearly 50-50 game")
        elif upset_prob >= 0.30:
            factors.append("Underdog has realistic path to victory")

        return factors

    def _get_confidence_level(self, upset_prob: float) -> str:
        """Get confidence level for upset prediction."""
        if upset_prob >= 0.45:
            return "VERY HIGH"
        elif upset_prob >= 0.35:
            return "HIGH"
        elif upset_prob >= 0.25:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_alert_level(self, upset_prob: float) -> str:
        """Get alert level (for UI/notifications)."""
        if upset_prob >= 0.40:
            return "🔴 UPSET ALERT"
        elif upset_prob >= 0.30:
            return "🟡 UPSET WATCH"
        else:
            return "🟢 MILD UPSET CHANCE"

    def get_historical_upset_accuracy(
        self,
        predictions: List[Dict],
        actual_results: List[Dict]
    ) -> Dict:
        """
        Calculate historical accuracy of upset predictions.

        Args:
            predictions: List of past upset predictions
            actual_results: List of actual game results

        Returns:
            Dictionary with accuracy metrics
        """
        if not predictions or not actual_results:
            return {'error': 'Insufficient data'}

        total_upset_alerts = len(predictions)
        actual_upsets = 0
        correct_predictions = 0

        for pred in predictions:
            # Find matching result
            result = next(
                (r for r in actual_results if r.get('game') == pred.get('game')),
                None
            )

            if not result:
                continue

            predicted_underdog = pred.get('underdog')
            actual_winner = result.get('winner')

            if actual_winner == predicted_underdog:
                actual_upsets += 1
                correct_predictions += 1

        accuracy = correct_predictions / total_upset_alerts if total_upset_alerts > 0 else 0

        return {
            'total_upset_alerts': total_upset_alerts,
            'actual_upsets': actual_upsets,
            'correct_predictions': correct_predictions,
            'accuracy': round(accuracy, 3),
            'upset_rate': round(actual_upsets / total_upset_alerts, 3) if total_upset_alerts > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
