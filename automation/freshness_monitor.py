"""Data freshness monitoring and auto-re-harvest triggers."""
import logging
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)


class FreshnessMonitor:
    """
    Monitor data freshness and trigger re-harvests.

    Features:
    - Track data age per sport
    - Configurable freshness thresholds
    - Auto-trigger re-harvest when data is stale
    - Event-based triggers (game completion, breaking news)
    - Monitoring dashboard integration
    """

    def __init__(
        self,
        data_file: str = 'data_freshness.json',
        check_interval: int = 300  # 5 minutes
    ):
        """
        Initialize freshness monitor.

        Args:
            data_file: Path to freshness data file
            check_interval: Seconds between freshness checks
        """
        self.data_file = Path(data_file)
        self.check_interval = check_interval
        self.data_ages: Dict[str, Dict] = self._load_data_ages()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Freshness thresholds (in minutes)
        self.thresholds = {
            'nfl': 15,  # NFL games update frequently during game days
            'nba': 10,
            'mlb': 15,
            'nhl': 15,
            'mls': 20,
            'soccer': 20,
            'golf': 30,
            'default': 20
        }

        # Callbacks for re-harvest triggers
        self.harvest_callbacks: Dict[str, Callable] = {}

    def _load_data_ages(self) -> Dict[str, Dict]:
        """Load data ages from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data ages: {e}")
                return {}
        return {}

    def _save_data_ages(self):
        """Save data ages to file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.data_ages, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data ages: {e}")

    def set_threshold(self, sport: str, minutes: int):
        """
        Set freshness threshold for a sport.

        Args:
            sport: Sport identifier
            minutes: Freshness threshold in minutes
        """
        self.thresholds[sport] = minutes
        logger.info(f"Freshness threshold set for {sport}: {minutes} minutes")

    def get_threshold(self, sport: str) -> int:
        """
        Get freshness threshold for a sport.

        Args:
            sport: Sport identifier

        Returns:
            Threshold in minutes
        """
        return self.thresholds.get(sport, self.thresholds['default'])

    def register_harvest_callback(self, sport: str, callback: Callable):
        """
        Register callback to trigger re-harvest.

        Args:
            sport: Sport identifier
            callback: Function to call for re-harvest
        """
        self.harvest_callbacks[sport] = callback
        logger.info(f"Harvest callback registered for {sport}")

    def update_data_timestamp(self, sport: str, data_type: str = 'general'):
        """
        Update timestamp for data.

        Args:
            sport: Sport identifier
            data_type: Type of data (general, scores, standings, etc.)
        """
        key = f"{sport}_{data_type}"
        self.data_ages[key] = {
            'sport': sport,
            'data_type': data_type,
            'last_updated': datetime.now().isoformat(),
            'update_count': self.data_ages.get(key, {}).get('update_count', 0) + 1
        }
        self._save_data_ages()
        logger.info(f"Data timestamp updated: {key}")

    def get_data_age(self, sport: str, data_type: str = 'general') -> Optional[timedelta]:
        """
        Get age of data.

        Args:
            sport: Sport identifier
            data_type: Type of data

        Returns:
            Timedelta representing data age, or None if no data
        """
        key = f"{sport}_{data_type}"
        data_info = self.data_ages.get(key)

        if not data_info:
            return None

        last_updated = datetime.fromisoformat(data_info['last_updated'])
        age = datetime.now() - last_updated
        return age

    def is_data_stale(self, sport: str, data_type: str = 'general') -> bool:
        """
        Check if data is stale.

        Args:
            sport: Sport identifier
            data_type: Type of data

        Returns:
            True if data is stale
        """
        age = self.get_data_age(sport, data_type)

        if age is None:
            return True  # No data = stale

        threshold_minutes = self.get_threshold(sport)
        threshold = timedelta(minutes=threshold_minutes)

        return age > threshold

    def trigger_re_harvest(self, sport: str) -> bool:
        """
        Trigger re-harvest for a sport.

        Args:
            sport: Sport identifier

        Returns:
            True if re-harvest was triggered
        """
        callback = self.harvest_callbacks.get(sport)

        if callback:
            try:
                logger.info(f"Triggering re-harvest for {sport}")
                callback(sport)
                self.update_data_timestamp(sport)
                return True
            except Exception as e:
                logger.error(f"Error triggering re-harvest for {sport}: {e}")
                return False
        else:
            logger.warning(f"No harvest callback registered for {sport}")
            return False

    def check_freshness(self):
        """Check freshness of all monitored data and trigger re-harvests if needed."""
        logger.debug("Checking data freshness...")

        stale_sports = set()

        for key, data_info in self.data_ages.items():
            sport = data_info['sport']
            data_type = data_info['data_type']

            if self.is_data_stale(sport, data_type):
                age = self.get_data_age(sport, data_type)
                logger.info(f"Stale data detected: {sport}/{data_type} (age: {age})")
                stale_sports.add(sport)

        # Trigger re-harvest for stale sports
        for sport in stale_sports:
            self.trigger_re_harvest(sport)

    def start_monitoring(self):
        """Start automatic freshness monitoring."""
        if self.running:
            logger.warning("Freshness monitoring already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="FreshnessMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"Freshness monitoring started (interval: {self.check_interval}s)")

    def stop_monitoring(self):
        """Stop automatic freshness monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Freshness monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self.check_freshness()
            except Exception as e:
                logger.error(f"Error in freshness check: {e}")

            # Sleep in small increments to allow quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)

    def get_freshness_report(self) -> Dict:
        """
        Get freshness report for all monitored data.

        Returns:
            Dictionary with freshness information
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'sports': {}
        }

        for key, data_info in self.data_ages.items():
            sport = data_info['sport']
            data_type = data_info['data_type']
            age = self.get_data_age(sport, data_type)
            is_stale = self.is_data_stale(sport, data_type)

            if sport not in report['sports']:
                report['sports'][sport] = {}

            report['sports'][sport][data_type] = {
                'last_updated': data_info['last_updated'],
                'age_minutes': age.total_seconds() / 60 if age else None,
                'threshold_minutes': self.get_threshold(sport),
                'is_stale': is_stale,
                'update_count': data_info.get('update_count', 0)
            }

        return report

    def force_refresh(self, sport: str) -> bool:
        """
        Force immediate refresh for a sport.

        Args:
            sport: Sport identifier

        Returns:
            True if refresh was triggered
        """
        logger.info(f"Force refresh requested for {sport}")
        return self.trigger_re_harvest(sport)

    def get_statistics(self) -> Dict:
        """
        Get monitoring statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_monitored': len(self.data_ages),
            'by_sport': {},
            'stale_count': 0
        }

        for key, data_info in self.data_ages.items():
            sport = data_info['sport']

            if sport not in stats['by_sport']:
                stats['by_sport'][sport] = {
                    'data_types': 0,
                    'total_updates': 0,
                    'stale': 0
                }

            stats['by_sport'][sport]['data_types'] += 1
            stats['by_sport'][sport]['total_updates'] += data_info.get('update_count', 0)

            if self.is_data_stale(sport, data_info['data_type']):
                stats['by_sport'][sport]['stale'] += 1
                stats['stale_count'] += 1

        return stats
