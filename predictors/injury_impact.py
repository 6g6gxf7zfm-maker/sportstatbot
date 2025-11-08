"""Injury replacement simulation for expected performance drop-off."""
from typing import Dict, List, Optional


class InjuryReplacementSimulator:
    """
    Simulates the impact of player injuries on team performance.

    Calculates expected drop-off when key players are injured and
    replaced by backups.
    """

    def __init__(self):
        """Initialize injury impact simulator."""
        self.position_value_weights = self._get_position_weights()

    def simulate_injury_impact(
        self,
        injured_player: Dict,
        replacement_player: Optional[Dict],
        team: str,
        sport: str
    ) -> Dict:
        """
        Calculate expected impact of player injury.

        Args:
            injured_player: Stats/info about injured player
            replacement_player: Stats/info about replacement (if known)
            team: Team name
            sport: Sport type

        Returns:
            Dictionary with impact analysis
        """
        # Get player values
        injured_value = self._calculate_player_value(injured_player, sport)
        replacement_value = (
            self._calculate_player_value(replacement_player, sport)
            if replacement_player
            else injured_value * 0.4  # Assume replacement is 40% as effective
        )

        # Calculate drop-off
        value_dropoff = injured_value - replacement_value
        percentage_dropoff = (value_dropoff / injured_value) * 100 if injured_value > 0 else 0

        # Convert to team impact (points/goals per game)
        team_impact = self._convert_to_team_impact(value_dropoff, sport)

        # Estimate win probability impact
        win_prob_impact = team_impact * 0.02  # ~2% per point impact

        return {
            'injured_player': injured_player.get('name', 'Unknown'),
            'replacement_player': replacement_player.get('name', 'Unknown') if replacement_player else 'TBD',
            'injured_value': round(injured_value, 2),
            'replacement_value': round(replacement_value, 2),
            'value_dropoff': round(value_dropoff, 2),
            'percentage_dropoff': round(percentage_dropoff, 1),
            'team_impact_per_game': round(team_impact, 2),
            'win_probability_impact': round(win_prob_impact, 3),
            'severity': self._get_severity_rating(percentage_dropoff),
            'team': team,
            'sport': sport
        }

    def simulate_multiple_injuries(
        self,
        injuries: List[Dict],
        team: str,
        sport: str
    ) -> Dict:
        """
        Simulate impact of multiple injuries.

        Args:
            injuries: List of injury scenarios
            team: Team name
            sport: Sport type

        Returns:
            Cumulative impact analysis
        """
        total_impact = 0
        total_dropoff = 0
        injury_details = []

        for injury in injuries:
            impact = self.simulate_injury_impact(
                injury['injured'],
                injury.get('replacement'),
                team,
                sport
            )
            total_impact += impact['team_impact_per_game']
            total_dropoff += impact['percentage_dropoff']
            injury_details.append(impact)

        # Calculate cumulative win probability impact
        cumulative_win_impact = total_impact * 0.02

        return {
            'team': team,
            'total_injuries': len(injuries),
            'total_team_impact': round(total_impact, 2),
            'average_dropoff_pct': round(total_dropoff / len(injuries), 1) if injuries else 0,
            'cumulative_win_probability_impact': round(cumulative_win_impact, 3),
            'severity': self._get_cumulative_severity(total_impact, sport),
            'injury_details': injury_details,
            'sport': sport
        }

    def _calculate_player_value(self, player: Dict, sport: str) -> float:
        """
        Calculate player value metric.

        Sport-specific formulas to quantify player contribution.
        """
        if sport == 'nba':
            # Simplified NBA value: PTS + REB*0.5 + AST*0.7 + ...
            ppg = player.get('points_per_game', 0)
            rpg = player.get('rebounds_per_game', 0)
            apg = player.get('assists_per_game', 0)
            return ppg + (rpg * 0.5) + (apg * 0.7)

        elif sport == 'nfl':
            position = player.get('position', 'UNKNOWN')
            if position == 'QB':
                yards = player.get('passing_yards_per_game', 0)
                tds = player.get('passing_tds_per_game', 0)
                return (yards / 25) + (tds * 4)
            elif position in ['RB', 'WR', 'TE']:
                yards = player.get('total_yards_per_game', 0)
                tds = player.get('total_tds_per_game', 0)
                return (yards / 10) + (tds * 6)
            else:
                return 5.0  # Default defensive value

        elif sport in ['nhl', 'mls', 'soccer']:
            goals = player.get('goals_per_game', 0)
            assists = player.get('assists_per_game', 0)
            return (goals * 2) + (assists * 1.5)

        elif sport == 'mlb':
            # Simplified baseball value
            if player.get('position') == 'P':
                era = player.get('era', 4.5)
                return max(0, 10 - era)
            else:
                avg = player.get('batting_average', 0.250)
                hr = player.get('home_runs', 0)
                return (avg * 100) + (hr * 0.5)

        return 10.0  # Default value

    def _convert_to_team_impact(self, value_dropoff: float, sport: str) -> float:
        """
        Convert individual value drop-off to team points/goals impact.

        Args:
            value_dropoff: Individual player value lost
            sport: Sport type

        Returns:
            Expected team scoring impact (points/goals per game)
        """
        # Sport-specific conversion factors
        conversion_factors = {
            'nba': 0.8,   # NBA value translates more directly
            'nfl': 0.3,   # NFL is more team-dependent
            'nhl': 0.2,   # Hockey is very team-dependent
            'mls': 0.2,
            'soccer': 0.2,
            'mlb': 0.15
        }

        factor = conversion_factors.get(sport, 0.3)
        return value_dropoff * factor

    def _get_position_weights(self) -> Dict:
        """Get position importance weights by sport."""
        return {
            'nfl': {
                'QB': 1.5,
                'RB': 0.8,
                'WR': 0.9,
                'TE': 0.6,
                'OL': 0.7,
                'DL': 0.7,
                'LB': 0.6,
                'DB': 0.6
            },
            'nba': {
                'PG': 1.0,
                'SG': 1.0,
                'SF': 1.0,
                'PF': 1.0,
                'C': 1.0
            }
        }

    def _get_severity_rating(self, percentage_dropoff: float) -> str:
        """Rate injury severity based on drop-off percentage."""
        if percentage_dropoff >= 70:
            return "CRITICAL"
        elif percentage_dropoff >= 50:
            return "SEVERE"
        elif percentage_dropoff >= 30:
            return "SIGNIFICANT"
        elif percentage_dropoff >= 15:
            return "MODERATE"
        else:
            return "MINOR"

    def _get_cumulative_severity(self, total_impact: float, sport: str) -> str:
        """Rate cumulative severity of multiple injuries."""
        if sport == 'nfl':
            if total_impact >= 10:
                return "DEVASTATING"
            elif total_impact >= 6:
                return "SEVERE"
            elif total_impact >= 3:
                return "SIGNIFICANT"
            else:
                return "MANAGEABLE"
        else:  # NBA, NHL, etc.
            if total_impact >= 15:
                return "DEVASTATING"
            elif total_impact >= 10:
                return "SEVERE"
            elif total_impact >= 5:
                return "SIGNIFICANT"
            else:
                return "MANAGEABLE"
