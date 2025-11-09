"""User preferences management for SportStatBot."""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class UserPreferences:
    """Manages user preferences and settings."""

    def __init__(self, preferences_file: str = 'data/user_preferences.json'):
        """
        Initialize user preferences.

        Args:
            preferences_file: Path to preferences JSON file
        """
        self.preferences_file = preferences_file
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict:
        """Load preferences from file or return defaults."""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load preferences: {e}")
                return self._get_default_preferences()
        else:
            return self._get_default_preferences()

    def _get_default_preferences(self) -> Dict:
        """Return default preference settings."""
        return {
            'league_toggles': {
                'nfl': True,
                'nba': True,
                'mlb': True,
                'nhl': True,
                'mls': True,
                'soccer': True,
                'golf': True
            },
            'priority_ranking': ['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer', 'golf'],
            'data_window': {
                'days': 3,
                'options': [1, 3, 5, 10, 14, 30]
            },
            'output_length': {
                'level': 'medium',  # brief, medium, in-depth
                'brief_max_lines': 50,
                'medium_max_lines': 150,
                'indepth_max_lines': 500
            },
            'auto_post_slack': True,
            'timezone': 'America/New_York',
            'last_updated': datetime.now().isoformat()
        }

    def save_preferences(self) -> bool:
        """Save current preferences to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)

            # Update timestamp
            self.preferences['last_updated'] = datetime.now().isoformat()

            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving preferences: {e}")
            return False

    def get_enabled_leagues(self) -> List[str]:
        """Get list of currently enabled leagues."""
        return [
            league for league, enabled
            in self.preferences['league_toggles'].items()
            if enabled
        ]

    def toggle_league(self, league: str, enabled: Optional[bool] = None) -> bool:
        """
        Toggle or set league enabled status.

        Args:
            league: League key (nfl, nba, etc.)
            enabled: True to enable, False to disable, None to toggle

        Returns:
            New enabled status
        """
        if league not in self.preferences['league_toggles']:
            print(f"Warning: Unknown league '{league}'")
            return False

        if enabled is None:
            # Toggle current state
            self.preferences['league_toggles'][league] = \
                not self.preferences['league_toggles'][league]
        else:
            self.preferences['league_toggles'][league] = enabled

        self.save_preferences()
        return self.preferences['league_toggles'][league]

    def set_priority_ranking(self, ranking: List[str]) -> bool:
        """
        Set manual priority ranking for leagues.

        Args:
            ranking: Ordered list of league keys (highest priority first)

        Returns:
            True if successful
        """
        # Validate all leagues are known
        valid_leagues = set(self.preferences['league_toggles'].keys())
        if not all(league in valid_leagues for league in ranking):
            print("Error: Invalid league in ranking")
            return False

        self.preferences['priority_ranking'] = ranking
        self.save_preferences()
        return True

    def get_priority_ranking(self) -> List[str]:
        """Get current priority ranking."""
        return self.preferences['priority_ranking']

    def set_data_window(self, days: int) -> bool:
        """
        Set data window in days.

        Args:
            days: Number of days to look back

        Returns:
            True if successful
        """
        if days < 1:
            print("Error: Data window must be at least 1 day")
            return False

        self.preferences['data_window']['days'] = days
        self.save_preferences()
        return True

    def get_data_window(self) -> int:
        """Get current data window in days."""
        return self.preferences['data_window']['days']

    def set_output_length(self, level: str) -> bool:
        """
        Set output length level.

        Args:
            level: 'brief', 'medium', or 'in-depth'

        Returns:
            True if successful
        """
        valid_levels = ['brief', 'medium', 'in-depth']
        if level not in valid_levels:
            print(f"Error: Level must be one of {valid_levels}")
            return False

        self.preferences['output_length']['level'] = level
        self.save_preferences()
        return True

    def get_output_length(self) -> str:
        """Get current output length level."""
        return self.preferences['output_length']['level']

    def get_max_lines_for_level(self) -> int:
        """Get max lines for current output level."""
        level = self.preferences['output_length']['level']
        key_map = {
            'brief': 'brief_max_lines',
            'medium': 'medium_max_lines',
            'in-depth': 'indepth_max_lines'
        }
        return self.preferences['output_length'].get(key_map[level], 150)

    def export_preferences(self) -> str:
        """Export preferences as JSON string."""
        return json.dumps(self.preferences, indent=2)

    def import_preferences(self, json_string: str) -> bool:
        """
        Import preferences from JSON string.

        Args:
            json_string: JSON string with preferences

        Returns:
            True if successful
        """
        try:
            new_prefs = json.loads(json_string)
            self.preferences = new_prefs
            self.save_preferences()
            return True
        except json.JSONDecodeError as e:
            print(f"Error importing preferences: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reset all preferences to defaults."""
        self.preferences = self._get_default_preferences()
        self.save_preferences()
        return True
