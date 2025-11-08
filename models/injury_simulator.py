"""
Injury Replacement Simulation.

Simulates expected drop-off when key players are injured.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InjuryImpact:
    """Impact assessment for an injury."""
    player_name: str
    team: str
    position: str
    importance_score: float  # 0-100
    expected_games_missed: int
    replacement_player: Optional[str]
    talent_dropoff: float  # Percentage
    rating_impact: float  # Points impact on team rating
    affected_stats: Dict[str, float]  # Stat -> expected change
    severity: str  # 'minor', 'moderate', 'major', 'season-ending'


class InjuryReplacementSimulator:
    """Simulates the impact of player injuries on team performance."""

    def __init__(self):
        """Initialize injury simulator."""
        self.position_importance = {
            'nfl': {'QB': 100, 'RB': 60, 'WR': 50, 'TE': 40, 'OL': 45, 'DL': 50, 'LB': 45, 'DB': 40},
            'nba': {'PG': 80, 'SG': 70, 'SF': 70, 'PF': 65, 'C': 70},
            'mlb': {'SP': 90, 'RP': 50, 'C': 60, 'IF': 55, 'OF': 50, 'DH': 55},
            'nhl': {'C': 75, 'W': 65, 'D': 70, 'G': 95},
            'soccer': {'GK': 95, 'DF': 60, 'MF': 70, 'FW': 80}
        }

    def simulate_injury_impact(
        self,
        player_name: str,
        team: str,
        position: str,
        sport: str,
        player_value: float,  # Season stats or rating
        team_depth: float,  # Team depth rating 0-100
        games_expected_missed: int,
        replacement_value: Optional[float] = None
    ) -> InjuryImpact:
        """
        Simulate the impact of a player injury.

        Args:
            player_name: Injured player name
            team: Team name
            position: Player position
            sport: Sport type
            player_value: Player's production value
            team_depth: Team's depth chart quality
            games_expected_missed: Expected games out
            replacement_value: Replacement player value (if known)

        Returns:
            InjuryImpact with simulation results
        """
        # Calculate importance score
        position_weight = self.position_importance.get(sport, {}).get(position, 50)
        importance = min(100, (player_value / 100) * position_weight)

        # Calculate replacement value if not provided
        if replacement_value is None:
            # Estimate based on team depth
            replacement_value = player_value * (0.4 + team_depth / 200)

        # Calculate talent dropoff
        dropoff = ((player_value - replacement_value) / player_value) * 100

        # Rating impact (based on importance and dropoff)
        rating_impact = (importance / 100) * (dropoff / 100) * 100

        # Determine severity
        if games_expected_missed >= 8 or 'season' in player_name.lower():
            severity = 'season-ending'
        elif games_expected_missed >= 4:
            severity = 'major'
        elif games_expected_missed >= 2:
            severity = 'moderate'
        else:
            severity = 'minor'

        # Affected stats estimation
        affected_stats = self._estimate_stat_changes(
            sport, position, dropoff
        )

        return InjuryImpact(
            player_name=player_name,
            team=team,
            position=position,
            importance_score=round(importance, 1),
            expected_games_missed=games_expected_missed,
            replacement_player=None,
            talent_dropoff=round(dropoff, 1),
            rating_impact=round(rating_impact, 1),
            affected_stats=affected_stats,
            severity=severity
        )

    def _estimate_stat_changes(
        self,
        sport: str,
        position: str,
        dropoff: float
    ) -> Dict[str, float]:
        """Estimate how team stats will change."""
        changes = {}

        if sport == 'nfl':
            if position == 'QB':
                changes = {
                    'passing_yards': -dropoff * 2.5,
                    'passing_td': -dropoff * 0.02,
                    'turnovers': dropoff * 0.015
                }
            elif position in ['RB', 'WR']:
                changes = {
                    'rushing_yards': -dropoff * 0.8,
                    'receiving_yards': -dropoff * 0.8
                }

        elif sport == 'nba':
            changes = {
                'points_per_game': -dropoff * 0.15,
                'assists_per_game': -dropoff * 0.08,
                'rebounds_per_game': -dropoff * 0.07
            }

        return changes


