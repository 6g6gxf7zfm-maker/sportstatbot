"""Offline mode with cached data fallback."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.cache_manager import CacheManager


class OfflineMode:
    """
    Offline mode manager that uses cached data when APIs are unavailable.
    Provides graceful degradation and cache-first strategies.
    """

    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize offline mode manager.

        Args:
            cache_dir: Directory for cache storage
        """
        self.cache_manager = CacheManager(cache_dir=cache_dir)
        self.offline_config_file = Path("config/offline_mode.json")
        self.config = self._load_config()

        # Track offline status
        self.is_offline = False
        self.last_online_check = None

    def _load_config(self) -> Dict:
        """Load offline mode configuration."""
        default_config = {
            'enabled': True,
            'cache_first': False,  # If True, always use cache first
            'max_cache_age_hours': 48,  # Maximum age of cache to use in offline mode
            'fallback_message': 'Using cached data - API unavailable',
            'offline_features': {
                'standings': True,
                'scores': True,
                'odds': False,  # Disable odds in offline mode (too time-sensitive)
                'news': True
            }
        }

        if self.offline_config_file.exists():
            try:
                with open(self.offline_config_file, 'r') as f:
                    custom_config = json.load(f)
                return {**default_config, **custom_config}
            except Exception as e:
                print(f"Error loading offline config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save offline mode configuration."""
        try:
            self.offline_config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.offline_config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving offline config: {e}")

    def get_data(self, sport: str, data_type: str,
                fetch_func: Optional[callable] = None) -> Optional[Dict]:
        """
        Get data with offline mode support.

        Args:
            sport: Sport identifier
            data_type: Type of data (scoreboard, standings, etc.)
            fetch_func: Function to fetch fresh data (called if online)

        Returns:
            Data dictionary or None
        """
        if not self.config['enabled']:
            # Offline mode disabled, just try to fetch
            if fetch_func:
                return fetch_func()
            return None

        # Check if this feature is enabled in offline mode
        if data_type not in self.config['offline_features']:
            feature_enabled = True
        else:
            feature_enabled = self.config['offline_features'][data_type]

        # Cache-first strategy
        if self.config['cache_first']:
            cached_data = self.cache_manager.get(
                sport, data_type,
                max_age_hours=self.config['max_cache_age_hours']
            )

            if cached_data:
                print(f"ℹ️ Using cached {data_type} for {sport}")
                return cached_data

        # Try to fetch fresh data if we have a fetch function
        if fetch_func:
            try:
                fresh_data = fetch_func()

                if fresh_data:
                    # Cache the fresh data
                    self.cache_manager.set(sport, data_type, fresh_data)
                    self.is_offline = False
                    self.last_online_check = datetime.now()
                    return fresh_data

            except Exception as e:
                print(f"⚠️ Error fetching {data_type} for {sport}: {e}")
                self.is_offline = True

        # Fetch failed or no fetch function - use cached data if available
        if feature_enabled:
            cached_data = self.cache_manager.get(
                sport, data_type,
                max_age_hours=self.config['max_cache_age_hours']
            )

            if cached_data:
                print(f"📂 {self.config['fallback_message']}: {sport} {data_type}")
                return cached_data

        return None

    def get_last_known_standings(self, sport: str) -> Optional[Dict]:
        """
        Get last known standings from cache.

        Args:
            sport: Sport identifier

        Returns:
            Cached standings or None
        """
        return self.cache_manager.get(
            sport, 'standings',
            max_age_hours=self.config['max_cache_age_hours']
        )

    def get_last_known_scores(self, sport: str) -> Optional[Dict]:
        """
        Get last known scores from cache.

        Args:
            sport: Sport identifier

        Returns:
            Cached scores or None
        """
        return self.cache_manager.get(
            sport, 'scoreboard',
            max_age_hours=self.config['max_cache_age_hours']
        )

    def get_last_known_odds(self, sport: str) -> Optional[Dict]:
        """
        Get last known odds from cache.

        Args:
            sport: Sport identifier

        Returns:
            Cached odds or None (if enabled in offline mode)
        """
        if not self.config['offline_features'].get('odds', False):
            return None

        return self.cache_manager.get(
            sport, 'odds',
            max_age_hours=self.config['max_cache_age_hours']
        )

    def get_offline_status(self) -> Dict:
        """
        Get current offline mode status.

        Returns:
            Status dictionary
        """
        cache_stats = self.cache_manager.get_cache_stats()

        status = {
            'enabled': self.config['enabled'],
            'is_offline': self.is_offline,
            'cache_first': self.config['cache_first'],
            'max_cache_age_hours': self.config['max_cache_age_hours'],
            'last_online_check': self.last_online_check.isoformat() if self.last_online_check else None,
            'cache_stats': {
                'total_entries': cache_stats['total_entries'],
                'size_mb': cache_stats['size_mb']
            },
            'enabled_features': {
                feature: enabled
                for feature, enabled in self.config['offline_features'].items()
                if enabled
            }
        }

        return status

    def get_available_cached_sports(self) -> List[str]:
        """
        Get list of sports with cached data available.

        Returns:
            List of sport identifiers
        """
        sports = set()

        for cache_dir in [self.cache_manager.scoreboard_cache,
                         self.cache_manager.standings_cache,
                         self.cache_manager.odds_cache]:
            for cache_file in cache_dir.glob("*.json"):
                # Extract sport from filename (format: sport_datatype_date.json)
                parts = cache_file.stem.split('_')
                if parts:
                    sports.add(parts[0])

        return sorted(list(sports))

    def generate_offline_report(self) -> str:
        """
        Generate offline mode status report.

        Returns:
            Formatted text report
        """
        status = self.get_offline_status()

        report = []

        report.append("=" * 60)
        report.append("📡 OFFLINE MODE STATUS")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        # Status
        mode_emoji = '🔌' if status['is_offline'] else '📡'
        mode_text = 'OFFLINE' if status['is_offline'] else 'ONLINE'

        report.append(f"{mode_emoji} Current Mode: {mode_text}")
        report.append(f"Offline Mode Enabled: {'✅' if status['enabled'] else '❌'}")
        report.append(f"Cache-First Strategy: {'✅' if status['cache_first'] else '❌'}")
        report.append(f"Max Cache Age: {status['max_cache_age_hours']} hours")

        if status['last_online_check']:
            last_check = datetime.fromisoformat(status['last_online_check'])
            report.append(f"Last Online: {last_check.strftime('%Y-%m-%d %H:%M')}")

        report.append("")

        # Cache stats
        report.append("💾 Cache Status:")
        report.append(f"  Total Entries: {status['cache_stats']['total_entries']}")
        report.append(f"  Size: {status['cache_stats']['size_mb']:.2f} MB")

        report.append("")

        # Available sports
        available_sports = self.get_available_cached_sports()
        report.append(f"🏆 Cached Sports ({len(available_sports)}):")

        for sport in available_sports:
            # Check freshness for each sport
            freshness = self.cache_manager.get_freshness_status(sport, 'scoreboard')

            status_emoji_map = {
                'fresh': '🟢',
                'stale': '🟡',
                'very_stale': '🔴',
                'missing': '⚪'
            }
            emoji = status_emoji_map.get(freshness['status'], '⚪')

            age_info = ""
            if freshness['age_hours']:
                age_info = f" ({freshness['age_hours']:.1f}h old)"

            report.append(f"  {emoji} {sport.upper()}{age_info}")

        report.append("")

        # Enabled features
        report.append("🎯 Offline Features:")
        for feature, enabled in status['enabled_features'].items():
            report.append(f"  ✅ {feature.title()}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def force_offline_mode(self, offline: bool = True) -> None:
        """
        Force offline or online mode.

        Args:
            offline: True to force offline, False to allow online
        """
        self.is_offline = offline

        if offline:
            print("🔌 Forced offline mode - will use cached data only")
        else:
            print("📡 Online mode restored - will attempt fresh data fetches")

    def clear_offline_cache(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear offline cache.

        Args:
            older_than_hours: Only clear cache older than this (None for all)

        Returns:
            Number of entries cleared
        """
        if older_than_hours:
            # Clear old cache
            original_retention = self.cache_manager.retention_days
            self.cache_manager.retention_days = older_than_hours / 24
            deleted = self.cache_manager.cleanup_old_cache()
            self.cache_manager.retention_days = original_retention
            return deleted
        else:
            # Clear all cache
            deleted = 0
            for cache_dir in [self.cache_manager.scoreboard_cache,
                             self.cache_manager.standings_cache,
                             self.cache_manager.odds_cache]:
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"Error deleting {cache_file}: {e}")

            print(f"🗑️ Cleared {deleted} cache entries")
            return deleted
