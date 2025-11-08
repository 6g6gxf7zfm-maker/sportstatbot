"""Player regression model for identifying bounce-back candidates."""
from typing import Dict, List
import statistics


class PlayerRegressionModel:
    """
    Identifies players likely to regress to mean or bounce back.

    Uses statistical analysis to find players who are over/under-performing
    and likely to return to their typical performance level.
    """

    def __init__(self, lookback_seasons: int = 3):
        """
        Initialize regression model.

        Args:
            lookback_seasons: Number of past seasons to consider
        """
        self.lookback_seasons = lookback_seasons

    def identify_bounce_back_candidates(
        self,
        players: List[Dict],
        sport: str,
        min_sample_size: int = 10
    ) -> List[Dict]:
        """
        Identify players likely to bounce back from poor performance.

        Args:
            players: List of player data with current and historical stats
            sport: Sport type
            min_sample_size: Minimum games to consider

        Returns:
            List of bounce-back candidates with analysis
        """
        candidates = []

        for player in players:
            analysis = self.analyze_regression_potential(player, sport, min_sample_size)

            if analysis.get('bounce_back_candidate'):
                candidates.append(analysis)

        # Sort by bounce-back potential
        candidates.sort(key=lambda x: x.get('expected_improvement', 0), reverse=True)

        return candidates

    def analyze_regression_potential(
        self,
        player: Dict,
        sport: str,
        min_sample_size: int = 10
    ) -> Dict:
        """
        Analyze individual player for regression potential.

        Args:
            player: Player stats data
            sport: Sport type
            min_sample_size: Minimum sample size

        Returns:
            Dictionary with regression analysis
        """
        # Get key stat based on sport
        key_stat = self._get_key_stat(sport)

        current_stats = player.get('current_season', {})
        historical_stats = player.get('historical_seasons', [])

        if not historical_stats or len(historical_stats) < 1:
            return {
                'player': player.get('name'),
                'bounce_back_candidate': False,
                'reason': 'Insufficient historical data'
            }

        # Calculate historical average (career norm)
        historical_values = [season.get(key_stat, 0) for season in historical_stats]
        career_average = statistics.mean(historical_values)
        career_std = statistics.stdev(historical_values) if len(historical_values) > 1 else 5

        # Current season performance
        current_value = current_stats.get(key_stat, 0)
        games_played = current_stats.get('games_played', 0)

        if games_played < min_sample_size:
            return {
                'player': player.get('name'),
                'bounce_back_candidate': False,
                'reason': f'Sample size too small ({games_played} games)'
            }

        # Calculate z-score (how many standard deviations from mean)
        z_score = (current_value - career_average) / career_std if career_std > 0 else 0

        # Check for negative regression (underperformance)
        is_underperforming = z_score < -1.0  # More than 1 SD below career average

        # Look for contextual factors
        factors = self._analyze_contextual_factors(player, current_stats)

        # Calculate expected regression
        if is_underperforming and not factors.get('age_decline'):
            # Expect regression toward mean
            expected_value = career_average + (current_value - career_average) * 0.3
            expected_improvement = expected_value - current_value
            bounce_back_candidate = True
            confidence = self._calculate_confidence(z_score, factors, games_played)
        elif z_score > 1.5:  # Overperforming
            # Expect negative regression
            expected_value = career_average + (current_value - career_average) * 0.4
            expected_improvement = expected_value - current_value  # Will be negative
            bounce_back_candidate = False
            confidence = self._calculate_confidence(z_score, factors, games_played)
        else:
            # Performing near average
            expected_value = current_value
            expected_improvement = 0
            bounce_back_candidate = False
            confidence = 0.5

        return {
            'player': player.get('name'),
            'position': player.get('position'),
            'team': player.get('team'),
            'bounce_back_candidate': bounce_back_candidate,
            'current_value': round(current_value, 2),
            'career_average': round(career_average, 2),
            'expected_value': round(expected_value, 2),
            'expected_improvement': round(expected_improvement, 2),
            'z_score': round(z_score, 2),
            'confidence': round(confidence, 2),
            'key_stat': key_stat,
            'factors': factors,
            'recommendation': self._generate_recommendation(
                bounce_back_candidate, expected_improvement, confidence, sport
            ),
            'sport': sport
        }

    def _get_key_stat(self, sport: str) -> str:
        """Get primary stat to analyze by sport."""
        key_stats = {
            'nba': 'points_per_game',
            'nfl': 'yards_per_game',
            'mlb': 'batting_average',
            'nhl': 'points_per_game',
            'mls': 'goals_per_game',
            'soccer': 'goals_per_game'
        }
        return key_stats.get(sport, 'points_per_game')

    def _analyze_contextual_factors(self, player: Dict, current_stats: Dict) -> Dict:
        """Analyze contextual factors affecting performance."""
        factors = {}

        # Age factor
        age = player.get('age', 25)
        if age >= 33:
            factors['age_decline'] = True
            factors['age_note'] = "Player may be in natural decline phase"
        elif age <= 23:
            factors['still_developing'] = True

        # Injury factor
        games_missed = current_stats.get('games_missed', 0)
        if games_missed >= 5:
            factors['injury_concerns'] = True
            factors['injury_note'] = f"Missed {games_missed} games - may explain underperformance"

        # Role change
        minutes_diff = current_stats.get('minutes_per_game', 0) - player.get('career_mpg', 0)
        if abs(minutes_diff) >= 5:
            factors['role_change'] = True
            factors['role_note'] = f"Playing {abs(minutes_diff):.1f} {'more' if minutes_diff > 0 else 'fewer'} minutes"

        # Team change
        if player.get('changed_teams', False):
            factors['new_team'] = True
            factors['team_note'] = "Adjusting to new team/system"

        # Shooting luck (for applicable sports)
        shooting_pct = current_stats.get('shooting_percentage')
        career_shooting = player.get('career_shooting_percentage')
        if shooting_pct and career_shooting:
            diff = shooting_pct - career_shooting
            if abs(diff) >= 5:
                factors['shooting_variance'] = True
                factors['shooting_note'] = f"Shooting {diff:+.1f}% {'above' if diff > 0 else 'below'} career average"

        return factors

    def _calculate_confidence(
        self,
        z_score: float,
        factors: Dict,
        games_played: int
    ) -> float:
        """Calculate confidence in regression prediction."""
        base_confidence = 0.6

        # Larger z-score = higher confidence in regression
        z_score_factor = min(abs(z_score) * 0.1, 0.3)

        # More games = higher confidence
        sample_factor = min(games_played / 50, 0.15)

        # Negative factors reduce confidence
        factor_penalty = 0
        if factors.get('age_decline'):
            factor_penalty += 0.2
        if factors.get('injury_concerns'):
            factor_penalty += 0.1

        # Positive factors increase confidence
        factor_bonus = 0
        if factors.get('shooting_variance'):
            factor_bonus += 0.1
        if factors.get('new_team'):
            factor_bonus += 0.05

        confidence = base_confidence + z_score_factor + sample_factor + factor_bonus - factor_penalty

        return max(0.2, min(0.95, confidence))

    def _generate_recommendation(
        self,
        is_bounce_back: bool,
        expected_improvement: float,
        confidence: float,
        sport: str
    ) -> str:
        """Generate betting/fantasy recommendation."""
        if not is_bounce_back:
            if expected_improvement < 0:
                return f"SELL - Likely to regress negatively (confidence: {confidence:.0%})"
            return "HOLD - Performing near expected level"

        if confidence >= 0.75:
            return f"STRONG BUY - High confidence bounce-back candidate (confidence: {confidence:.0%})"
        elif confidence >= 0.60:
            return f"BUY - Good bounce-back potential (confidence: {confidence:.0%})"
        else:
            return f"SPECULATIVE BUY - Moderate bounce-back chance (confidence: {confidence:.0%})"
