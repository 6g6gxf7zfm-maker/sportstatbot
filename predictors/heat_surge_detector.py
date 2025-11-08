"""Heat Surge alert system for teams outperforming expected metrics."""
from typing import Dict, List
from datetime import datetime


class HeatSurgeDetector:
    """
    Detects teams that are significantly outperforming their expected metrics.

    Identifies "heat surges" where teams are playing above their rating.
    """

    def __init__(self, threshold: float = 1.5):
        """
        Initialize heat surge detector.

        Args:
            threshold: Standard deviations above expected to trigger alert
        """
        self.threshold = threshold

    def detect_heat_surges(
        self,
        teams_data: List[Dict],
        sport: str
    ) -> List[Dict]:
        """
        Detect teams experiencing heat surges.

        Args:
            teams_data: List of team performance data
            sport: Sport type

        Returns:
            List of teams with heat surge alerts
        """
        heat_surges = []

        for team_data in teams_data:
            analysis = self.analyze_team_performance(team_data, sport)

            if analysis['is_heat_surge']:
                heat_surges.append(analysis)

        # Sort by surge magnitude
        heat_surges.sort(key=lambda x: x['surge_score'], reverse=True)

        return heat_surges

    def analyze_team_performance(
        self,
        team_data: Dict,
        sport: str
    ) -> Dict:
        """
        Analyze if team is in a heat surge.

        Args:
            team_data: Team performance data
            sport: Sport type

        Returns:
            Analysis dictionary
        """
        team_name = team_data.get('team_name')

        # Get actual vs expected metrics
        actual_record = team_data.get('actual_wins', 0)
        expected_record = team_data.get('expected_wins', 0)
        wins_over_expected = actual_record - expected_record

        actual_scoring = team_data.get('actual_points_per_game', 0)
        expected_scoring = team_data.get('expected_points_per_game', 0)
        scoring_differential = actual_scoring - expected_scoring

        actual_defense = team_data.get('actual_points_allowed', 0)
        expected_defense = team_data.get('expected_points_allowed', 0)
        defensive_differential = expected_defense - actual_defense  # Positive is better

        # Calculate surge score
        surge_components = []

        if wins_over_expected >= 3:
            surge_components.append(('record', wins_over_expected * 0.3))

        if scoring_differential >= 5:
            surge_components.append(('scoring', scoring_differential * 0.15))

        if defensive_differential >= 3:
            surge_components.append(('defense', defensive_differential * 0.15))

        # Recent form
        last_10_wins = team_data.get('last_10_wins', 5)
        if last_10_wins >= 8:
            surge_components.append(('recent_form', (last_10_wins - 5) * 0.2))

        surge_score = sum(score for _, score in surge_components)

        is_heat_surge = surge_score >= self.threshold

        return {
            'team': team_name,
            'is_heat_surge': is_heat_surge,
            'surge_score': round(surge_score, 2),
            'wins_over_expected': wins_over_expected,
            'scoring_differential': round(scoring_differential, 1),
            'defensive_differential': round(defensive_differential, 1),
            'last_10_record': f"{last_10_wins}-{10 - last_10_wins}",
            'surge_factors': [factor for factor, _ in surge_components],
            'alert_level': self._get_alert_level(surge_score),
            'recommendation': self._generate_recommendation(surge_score, wins_over_expected),
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }

    def _get_alert_level(self, surge_score: float) -> str:
        """Get alert level based on surge score."""
        if surge_score >= 3.0:
            return "🔥 EXTREME HEAT"
        elif surge_score >= 2.0:
            return "🔥 HIGH HEAT"
        elif surge_score >= 1.5:
            return "🟡 MODERATE HEAT"
        else:
            return "🟢 NORMAL"

    def _generate_recommendation(self, surge_score: float, wins_over: float) -> str:
        """Generate recommendation for heat surge."""
        if surge_score >= 3.0:
            return "Team is significantly outperforming - consider regression coming"
        elif surge_score >= 2.0:
            return "Team playing well above expectations - monitor for sustainability"
        elif surge_score >= 1.5:
            return "Team showing positive surge - may continue or regress to mean"
        else:
            return "Team performing near expectations"
