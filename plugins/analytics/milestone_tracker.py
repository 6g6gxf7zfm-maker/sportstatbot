"""Player Milestone Tracker Plugin - Tracks players approaching career milestones."""
from typing import Dict, Any, List
from ..base_plugin import BasePlugin, PluginCategory, PluginPriority


class MilestoneTracker(BasePlugin):
    """
    Tracks players approaching significant career milestones:
    - 10,000 career yards (rushing/passing/receiving)
    - 500 career goals/home runs
    - 1,000 career games played
    - 300 career wins (pitchers)
    - 10,000 career points (NBA)
    - And many more sport-specific milestones
    """

    # Define milestone thresholds by sport
    MILESTONES = {
        'nfl': {
            'passing_yards': [5000, 10000, 20000, 30000, 40000, 50000, 60000, 70000],
            'rushing_yards': [1000, 5000, 10000, 15000, 20000],
            'receiving_yards': [1000, 5000, 10000, 15000, 20000],
            'touchdowns': [100, 200, 300, 400, 500],
            'sacks': [50, 100, 150, 200],
            'interceptions': [25, 50, 75, 100]
        },
        'nba': {
            'points': [10000, 15000, 20000, 25000, 30000, 35000, 40000],
            'rebounds': [5000, 10000, 15000, 20000],
            'assists': [5000, 10000, 15000],
            'steals': [1000, 2000, 3000],
            'blocks': [1000, 2000, 3000],
            'three_pointers': [1000, 2000, 3000]
        },
        'mlb': {
            'home_runs': [100, 200, 300, 400, 500, 600, 700],
            'hits': [1000, 1500, 2000, 2500, 3000],
            'rbi': [500, 1000, 1500, 2000],
            'strikeouts_pitcher': [1000, 2000, 3000, 4000, 5000],
            'wins_pitcher': [100, 150, 200, 250, 300],
            'saves': [100, 200, 300, 400, 500]
        },
        'nhl': {
            'goals': [100, 200, 300, 400, 500, 600, 700, 800],
            'assists': [200, 400, 600, 800, 1000, 1200],
            'points': [500, 1000, 1500, 2000],
            'wins_goalie': [100, 200, 300, 400, 500],
            'shutouts': [25, 50, 75, 100]
        }
    }

    @property
    def name(self) -> str:
        return "milestone_tracker"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Tracks players approaching career milestones (10k yards, 500 goals, etc.)"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.ANALYTICS

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.MEDIUM

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify players approaching milestones.

        Args:
            data: Contains sport and player statistics

        Returns:
            List of players approaching milestones
        """
        sport = data.get('sport', 'nfl')
        standout_players = data.get('sport_data', {}).get('standout_players', [])

        if not standout_players or sport not in self.MILESTONES:
            return {'milestones': []}

        approaching_milestones = []

        for player in standout_players:
            milestones = self._check_player_milestones(player, sport)
            if milestones:
                approaching_milestones.append({
                    'player': player.get('name', 'Unknown'),
                    'team': player.get('team', 'Unknown'),
                    'milestones': milestones
                })

        return {'approaching_milestones': approaching_milestones}

    def _check_player_milestones(self, player: Dict[str, Any], sport: str) -> List[Dict[str, Any]]:
        """
        Check if a player is approaching any milestones.

        Args:
            player: Player data dictionary
            sport: Sport identifier

        Returns:
            List of approaching milestones for this player
        """
        milestones = []
        sport_milestones = self.MILESTONES.get(sport, {})

        # This is a placeholder - in real implementation, would check career stats
        # For now, check if recent performance suggests milestone approach

        stats = player.get('stats', {})

        # Example: Check passing yards for NFL
        if sport == 'nfl' and 'passing_yards' in stats:
            # In real implementation, would have career_passing_yards
            # For demo, just show structure
            career_yards = self._get_career_stat(player, 'passing_yards', sport)
            next_milestone = self._find_next_milestone(career_yards, sport_milestones.get('passing_yards', []))

            if next_milestone and self._is_approaching(career_yards, next_milestone):
                milestones.append({
                    'stat': 'Passing Yards',
                    'current': career_yards,
                    'milestone': next_milestone,
                    'remaining': next_milestone - career_yards,
                    'significance': self._get_milestone_significance(next_milestone, 'passing_yards')
                })

        return milestones

    def _get_career_stat(self, player: Dict[str, Any], stat: str, sport: str) -> int:
        """
        Get career stat total for a player.

        Args:
            player: Player data
            stat: Stat name
            sport: Sport identifier

        Returns:
            Career total (placeholder implementation)
        """
        # This would query a career stats database
        # For now, return placeholder
        return 0

    def _find_next_milestone(self, current_value: int, milestone_list: List[int]) -> int:
        """
        Find the next milestone threshold.

        Args:
            current_value: Current stat value
            milestone_list: List of milestone thresholds

        Returns:
            Next milestone value or 0 if none
        """
        for milestone in sorted(milestone_list):
            if milestone > current_value:
                return milestone
        return 0

    def _is_approaching(self, current: int, milestone: int, threshold_pct: float = 0.95) -> bool:
        """
        Check if player is approaching a milestone.

        Args:
            current: Current value
            milestone: Milestone threshold
            threshold_pct: What percentage counts as "approaching"

        Returns:
            True if approaching milestone
        """
        return current >= (milestone * threshold_pct)

    def _get_milestone_significance(self, milestone: int, stat_type: str) -> str:
        """
        Get significance description for a milestone.

        Args:
            milestone: Milestone value
            stat_type: Type of stat

        Returns:
            Significance description
        """
        significance_map = {
            10000: "rare career achievement",
            20000: "elite career milestone",
            30000: "legendary career total",
            50000: "all-time great territory",
            500: "Hall of Fame benchmark",
            1000: "historic achievement"
        }

        return significance_map.get(milestone, "notable milestone")
