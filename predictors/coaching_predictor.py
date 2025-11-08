"""Coaching change predictor based on team performance vs expectations."""
from typing import Dict, List
from datetime import datetime


class CoachingChangePredictor:
    """
    Predicts likelihood of coaching changes based on performance metrics.

    Analyzes record vs expectations, trends, and organizational factors
    to estimate firing probability.
    """

    def __init__(self):
        """Initialize coaching change predictor."""
        self.risk_factors = {}

    def predict_coaching_changes(
        self,
        teams: List[Dict],
        sport: str
    ) -> List[Dict]:
        """
        Predict which coaches are at risk.

        Args:
            teams: List of team data with records and expectations
            sport: Sport type

        Returns:
            List of at-risk coaching situations
        """
        at_risk = []

        for team in teams:
            analysis = self.analyze_coaching_situation(team, sport)

            if analysis['risk_level'] in ['HIGH', 'CRITICAL']:
                at_risk.append(analysis)

        # Sort by firing probability
        at_risk.sort(key=lambda x: x['firing_probability'], reverse=True)

        return at_risk

    def analyze_coaching_situation(
        self,
        team: Dict,
        sport: str
    ) -> Dict:
        """
        Analyze coaching job security for a team.

        Args:
            team: Team data
            sport: Sport type

        Returns:
            Dictionary with coaching analysis
        """
        coach_name = team.get('head_coach', 'Unknown')
        current_record = team.get('current_record', {})
        expected_record = team.get('expected_record', {})

        wins = current_record.get('wins', 0)
        losses = current_record.get('losses', 0)
        expected_wins = expected_record.get('wins', wins)

        # Calculate record delta
        wins_delta = wins - expected_wins
        games_played = wins + losses
        win_pct = wins / games_played if games_played > 0 else 0

        # Initialize risk score
        risk_score = 0
        risk_factors = []

        # Factor 1: Performance vs expectations
        if wins_delta <= -5:
            risk_score += 40
            risk_factors.append(f"Significantly underperforming expectations ({wins_delta:+d} wins)")
        elif wins_delta <= -3:
            risk_score += 25
            risk_factors.append(f"Underperforming expectations ({wins_delta:+d} wins)")

        # Factor 2: Losing streak
        current_streak = team.get('current_streak', {})
        if current_streak.get('type') == 'L':
            streak_length = current_streak.get('length', 0)
            if streak_length >= 6:
                risk_score += 20
                risk_factors.append(f"On {streak_length}-game losing streak")
            elif streak_length >= 4:
                risk_score += 10
                risk_factors.append(f"On {streak_length}-game losing streak")

        # Factor 3: Win percentage threshold
        if sport == 'nfl' and win_pct < 0.300:
            risk_score += 15
            risk_factors.append(f"Poor win percentage ({win_pct:.3f})")
        elif sport in ['nba', 'mlb', 'nhl'] and win_pct < 0.350:
            risk_score += 15
            risk_factors.append(f"Poor win percentage ({win_pct:.3f})")

        # Factor 4: Tenure
        years_with_team = team.get('coach_tenure_years', 1)
        if years_with_team >= 5 and wins_delta < 0:
            risk_score += 10
            risk_factors.append(f"Long tenure ({years_with_team} years) without success")
        elif years_with_team == 1:
            risk_score -= 10  # First year coaches get some grace

        # Factor 5: Playoff expectations
        if team.get('preseason_playoff_expectation', False) and win_pct < 0.400:
            risk_score += 15
            risk_factors.append("Team expected to make playoffs but struggling")

        # Factor 6: Recent trends
        last_10_record = team.get('last_10_games', {})
        if last_10_record:
            last_10_wins = last_10_record.get('wins', 5)
            if last_10_wins <= 2:
                risk_score += 15
                risk_factors.append(f"Only {last_10_wins} wins in last 10 games")

        # Factor 7: Front office patience
        new_gm = team.get('new_gm_this_year', False)
        if new_gm:
            risk_score += 10
            risk_factors.append("New GM may want their own coach")

        # Factor 8: Star player conflicts
        if team.get('player_coach_conflicts', False):
            risk_score += 10
            risk_factors.append("Reported conflicts with star players")

        # Calculate final probability
        firing_probability = min(0.95, risk_score / 100)

        # Determine risk level
        risk_level = self._get_risk_level(firing_probability)

        return {
            'team': team.get('team_name'),
            'coach': coach_name,
            'current_record': f"{wins}-{losses}",
            'win_percentage': round(win_pct, 3),
            'expected_wins': expected_wins,
            'wins_delta': wins_delta,
            'firing_probability': round(firing_probability, 3),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'tenure_years': years_with_team,
            'recommendation': self._generate_recommendation(firing_probability),
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }

    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level from probability."""
        if probability >= 0.70:
            return "CRITICAL"
        elif probability >= 0.50:
            return "HIGH"
        elif probability >= 0.30:
            return "MODERATE"
        elif probability >= 0.15:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendation(self, probability: float) -> str:
        """Generate recommendation text."""
        if probability >= 0.70:
            return "Coach likely to be fired if team doesn't turn things around immediately"
        elif probability >= 0.50:
            return "Coach on hot seat - next few games critical"
        elif probability >= 0.30:
            return "Coach facing some pressure but job likely safe for now"
        elif probability >= 0.15:
            return "Minor concerns but coach appears secure"
        else:
            return "Coach's job appears secure"

    def track_predictions(
        self,
        predictions: List[Dict],
        actual_firings: List[str]
    ) -> Dict:
        """
        Track accuracy of coaching change predictions.

        Args:
            predictions: List of predictions made
            actual_firings: List of coaches actually fired

        Returns:
            Accuracy metrics
        """
        high_risk_predictions = [
            p['coach'] for p in predictions
            if p['firing_probability'] >= 0.50
        ]

        true_positives = len(set(high_risk_predictions) & set(actual_firings))
        false_positives = len(set(high_risk_predictions) - set(actual_firings))
        false_negatives = len(set(actual_firings) - set(high_risk_predictions))

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        return {
            'total_predictions': len(predictions),
            'high_risk_predictions': len(high_risk_predictions),
            'actual_firings': len(actual_firings),
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'timestamp': datetime.now().isoformat()
        }
