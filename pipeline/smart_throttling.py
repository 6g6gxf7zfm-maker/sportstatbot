"""Smart throttling system for major events like Super Bowl, Finals, etc."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path


class SmartThrottling:
    """
    Smart throttling that adjusts API request rates based on:
    - Major sporting events (Super Bowl, NBA Finals, World Series, etc.)
    - Time of day (game times vs off-hours)
    - Day of week (game days vs off days)
    - Season status (in-season vs off-season)
    """

    def __init__(self, config_file: str = "config/smart_throttling.json"):
        """
        Initialize smart throttling system.

        Args:
            config_file: Path to throttling configuration
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load throttling configuration."""
        default_config = {
            'enabled': True,
            'base_interval_seconds': 60,  # Base interval between requests
            'major_events': {
                'super_bowl': {
                    'date_pattern': 'first_sunday_february',
                    'multiplier': 0.25,  # 4x more frequent updates
                    'duration_hours': 6
                },
                'nba_finals': {
                    'date_range': ['06-01', '06-20'],
                    'multiplier': 0.5,  # 2x more frequent
                    'duration_hours': 4
                },
                'world_series': {
                    'date_range': ['10-20', '11-05'],
                    'multiplier': 0.5,
                    'duration_hours': 5
                },
                'stanley_cup_finals': {
                    'date_range': ['05-25', '06-25'],
                    'multiplier': 0.5,
                    'duration_hours': 4
                },
                'march_madness': {
                    'date_range': ['03-15', '04-10'],
                    'multiplier': 0.6,
                    'duration_hours': 12
                }
            },
            'game_day_adjustments': {
                'nfl': {
                    'days': ['thursday', 'sunday', 'monday'],
                    'peak_hours': [[13, 23]],  # 1 PM - 11 PM
                    'multiplier': 0.5
                },
                'nba': {
                    'days': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                    'peak_hours': [[18, 23]],  # 6 PM - 11 PM
                    'multiplier': 0.7
                },
                'mlb': {
                    'days': ['everyday'],
                    'peak_hours': [[18, 22]],  # 6 PM - 10 PM
                    'multiplier': 0.8
                },
                'nhl': {
                    'days': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                    'peak_hours': [[18, 23]],
                    'multiplier': 0.7
                }
            },
            'off_hours_multiplier': 2.0,  # Slower updates during off-hours
            'off_season_multiplier': 3.0  # Much slower during off-season
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)

                # Merge configurations
                for key in default_config:
                    if key in custom_config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(custom_config[key])
                        else:
                            default_config[key] = custom_config[key]

                return default_config
            except Exception as e:
                print(f"Error loading throttling config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save throttling configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving throttling config: {e}")

    def get_interval(self, sport: str, data_type: str = 'scoreboard') -> int:
        """
        Get current throttling interval for a sport.

        Args:
            sport: Sport identifier (nfl, nba, etc.)
            data_type: Type of data being fetched

        Returns:
            Interval in seconds between requests
        """
        if not self.config['enabled']:
            return self.config['base_interval_seconds']

        base_interval = self.config['base_interval_seconds']
        multiplier = 1.0

        now = datetime.now()

        # Check for major events
        event_multiplier = self._check_major_events()
        if event_multiplier:
            multiplier = min(multiplier, event_multiplier)

        # Check for game day adjustments
        game_day_multiplier = self._check_game_day(sport, now)
        if game_day_multiplier:
            multiplier = min(multiplier, game_day_multiplier)
        else:
            # Apply off-hours multiplier if not game time
            if self._is_off_hours(sport, now):
                multiplier = max(multiplier, self.config['off_hours_multiplier'])

        # Apply off-season multiplier if applicable
        # (This would need season data - simplified for now)

        return int(base_interval * multiplier)

    def _check_major_events(self) -> Optional[float]:
        """
        Check if any major events are happening now.

        Returns:
            Event multiplier or None
        """
        now = datetime.now()

        for event_name, event_config in self.config['major_events'].items():
            if self._is_major_event_active(event_name, event_config, now):
                return event_config['multiplier']

        return None

    def _is_major_event_active(self, event_name: str, event_config: Dict,
                               check_time: datetime) -> bool:
        """
        Check if a major event is currently active.

        Args:
            event_name: Name of the event
            event_config: Event configuration
            check_time: Time to check

        Returns:
            True if event is active
        """
        # Check date range
        if 'date_range' in event_config:
            start_date_str, end_date_str = event_config['date_range']

            # Parse as month-day
            start_month, start_day = map(int, start_date_str.split('-'))
            end_month, end_day = map(int, end_date_str.split('-'))

            current_month = check_time.month
            current_day = check_time.day

            # Simple date range check (doesn't handle year boundaries perfectly)
            in_date_range = (
                (current_month == start_month and current_day >= start_day) or
                (current_month == end_month and current_day <= end_day) or
                (start_month < current_month < end_month)
            )

            if not in_date_range:
                return False

        # Check if within event hours
        # For simplicity, assume events happen in evening
        # More sophisticated logic could be added

        return True

    def _check_game_day(self, sport: str, check_time: datetime) -> Optional[float]:
        """
        Check if it's a game day for the sport.

        Args:
            sport: Sport identifier
            check_time: Time to check

        Returns:
            Game day multiplier or None
        """
        if sport not in self.config['game_day_adjustments']:
            return None

        game_config = self.config['game_day_adjustments'][sport]

        # Check day of week
        current_day = check_time.strftime('%A').lower()

        if 'everyday' not in game_config['days'] and current_day not in game_config['days']:
            return None

        # Check if within peak hours
        current_hour = check_time.hour

        for hour_range in game_config['peak_hours']:
            start_hour, end_hour = hour_range
            if start_hour <= current_hour <= end_hour:
                return game_config['multiplier']

        return None

    def _is_off_hours(self, sport: str, check_time: datetime) -> bool:
        """
        Check if it's off-hours (no games typically played).

        Args:
            sport: Sport identifier
            check_time: Time to check

        Returns:
            True if off-hours
        """
        # Early morning hours (midnight - 6 AM)
        if 0 <= check_time.hour < 6:
            return True

        # Mid-day on non-game days
        if sport in self.config['game_day_adjustments']:
            game_config = self.config['game_day_adjustments'][sport]
            current_day = check_time.strftime('%A').lower()

            if 'everyday' not in game_config['days'] and current_day not in game_config['days']:
                return True

        return False

    def get_throttling_status(self, sport: str) -> Dict:
        """
        Get current throttling status for a sport.

        Args:
            sport: Sport identifier

        Returns:
            Status dictionary
        """
        now = datetime.now()
        interval = self.get_interval(sport)
        base_interval = self.config['base_interval_seconds']

        status = {
            'sport': sport,
            'current_interval_seconds': interval,
            'base_interval_seconds': base_interval,
            'multiplier': interval / base_interval if base_interval > 0 else 1.0,
            'is_game_time': bool(self._check_game_day(sport, now)),
            'is_major_event': bool(self._check_major_events()),
            'is_off_hours': self._is_off_hours(sport, now),
            'timestamp': now.isoformat()
        }

        # Determine mode
        if status['is_major_event']:
            status['mode'] = 'major_event'
        elif status['is_game_time']:
            status['mode'] = 'game_time'
        elif status['is_off_hours']:
            status['mode'] = 'off_hours'
        else:
            status['mode'] = 'normal'

        return status

    def generate_throttling_report(self) -> str:
        """Generate smart throttling status report."""
        report = []

        report.append("=" * 60)
        report.append("⚡ SMART THROTTLING STATUS")
        report.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        report.append("=" * 60)
        report.append("")

        report.append("⚙️ Configuration:")
        report.append(f"  Enabled: {'✅' if self.config['enabled'] else '❌'}")
        report.append(f"  Base Interval: {self.config['base_interval_seconds']}s")
        report.append(f"  Off-Hours Multiplier: {self.config['off_hours_multiplier']}x")
        report.append("")

        # Check for active major events
        major_event = self._check_major_events()
        if major_event:
            report.append("🏆 MAJOR EVENT ACTIVE:")
            report.append(f"  Throttle Multiplier: {major_event}x")
            report.append(f"  Update Frequency: Increased")
            report.append("")

        # Status for each sport
        report.append("🏅 Sport-Specific Status:")

        for sport in ['nfl', 'nba', 'mlb', 'nhl', 'mls']:
            status = self.get_throttling_status(sport)

            mode_emoji = {
                'major_event': '🏆',
                'game_time': '🎮',
                'off_hours': '😴',
                'normal': '⚪'
            }
            emoji = mode_emoji.get(status['mode'], '⚪')

            report.append(f"\n  {emoji} {sport.upper()}:")
            report.append(f"    Mode: {status['mode'].replace('_', ' ').title()}")
            report.append(f"    Interval: {status['current_interval_seconds']}s")
            report.append(f"    Multiplier: {status['multiplier']:.2f}x")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def add_major_event(self, event_name: str, date_range: List[str],
                       multiplier: float = 0.5, duration_hours: int = 4) -> None:
        """
        Add a new major event configuration.

        Args:
            event_name: Name of the event
            date_range: Date range as ['MM-DD', 'MM-DD']
            multiplier: Throttle multiplier during event
            duration_hours: Event duration
        """
        self.config['major_events'][event_name] = {
            'date_range': date_range,
            'multiplier': multiplier,
            'duration_hours': duration_hours
        }

        self._save_config()
        print(f"✅ Added major event: {event_name}")
