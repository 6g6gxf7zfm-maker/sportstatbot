"""Smart rate limiting for API calls."""
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import threading

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Smart rate limiter with API quota management.

    Features:
    - Per-API rate limiting
    - Quota tracking
    - Automatic backoff
    - Burst handling
    - Statistics and monitoring
    """

    def __init__(self):
        """Initialize rate limiter."""
        self.limits: Dict[str, Dict] = {}
        self.call_history: Dict[str, deque] = {}
        self.lock = threading.Lock()

        # Default rate limits for common APIs
        self.default_limits = {
            'espn': {
                'calls_per_minute': 60,
                'calls_per_hour': 1000,
                'calls_per_day': 10000
            },
            'odds': {
                'calls_per_minute': 10,
                'calls_per_hour': 500,
                'calls_per_day': 5000
            },
            'google_docs': {
                'calls_per_minute': 60,
                'calls_per_hour': 3000,
                'calls_per_day': 50000
            },
            'default': {
                'calls_per_minute': 30,
                'calls_per_hour': 1000,
                'calls_per_day': 10000
            }
        }

    def set_limit(
        self,
        api_name: str,
        calls_per_minute: Optional[int] = None,
        calls_per_hour: Optional[int] = None,
        calls_per_day: Optional[int] = None
    ):
        """
        Set rate limit for an API.

        Args:
            api_name: API identifier
            calls_per_minute: Max calls per minute
            calls_per_hour: Max calls per hour
            calls_per_day: Max calls per day
        """
        if api_name not in self.limits:
            # Use default limits as base
            base_limits = self.default_limits.get(api_name, self.default_limits['default'])
            self.limits[api_name] = base_limits.copy()

        if calls_per_minute is not None:
            self.limits[api_name]['calls_per_minute'] = calls_per_minute
        if calls_per_hour is not None:
            self.limits[api_name]['calls_per_hour'] = calls_per_hour
        if calls_per_day is not None:
            self.limits[api_name]['calls_per_day'] = calls_per_day

        logger.info(f"Rate limit set for {api_name}: {self.limits[api_name]}")

    def get_limit(self, api_name: str) -> Dict:
        """
        Get rate limit for an API.

        Args:
            api_name: API identifier

        Returns:
            Dictionary with rate limits
        """
        if api_name not in self.limits:
            self.limits[api_name] = self.default_limits.get(
                api_name, self.default_limits['default']
            ).copy()

        return self.limits[api_name]

    def _cleanup_old_calls(self, api_name: str):
        """Remove calls older than 24 hours."""
        if api_name not in self.call_history:
            return

        cutoff = time.time() - 86400  # 24 hours
        while self.call_history[api_name] and self.call_history[api_name][0] < cutoff:
            self.call_history[api_name].popleft()

    def _count_calls_in_window(self, api_name: str, seconds: int) -> int:
        """Count calls in the last N seconds."""
        if api_name not in self.call_history:
            return 0

        cutoff = time.time() - seconds
        count = 0
        for call_time in reversed(self.call_history[api_name]):
            if call_time >= cutoff:
                count += 1
            else:
                break

        return count

    def can_make_call(self, api_name: str) -> bool:
        """
        Check if a call can be made without exceeding limits.

        Args:
            api_name: API identifier

        Returns:
            True if call is allowed
        """
        with self.lock:
            limits = self.get_limit(api_name)
            self._cleanup_old_calls(api_name)

            # Check per-minute limit
            calls_last_minute = self._count_calls_in_window(api_name, 60)
            if calls_last_minute >= limits['calls_per_minute']:
                return False

            # Check per-hour limit
            calls_last_hour = self._count_calls_in_window(api_name, 3600)
            if calls_last_hour >= limits['calls_per_hour']:
                return False

            # Check per-day limit
            calls_last_day = self._count_calls_in_window(api_name, 86400)
            if calls_last_day >= limits['calls_per_day']:
                return False

            return True

    def wait_for_slot(self, api_name: str, max_wait: int = 60) -> bool:
        """
        Wait for an available slot to make a call.

        Args:
            api_name: API identifier
            max_wait: Maximum seconds to wait

        Returns:
            True if slot became available, False if timed out
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            if self.can_make_call(api_name):
                return True

            # Wait a bit before checking again
            time.sleep(0.5)

        return False

    def record_call(self, api_name: str):
        """
        Record an API call.

        Args:
            api_name: API identifier
        """
        with self.lock:
            if api_name not in self.call_history:
                self.call_history[api_name] = deque()

            self.call_history[api_name].append(time.time())
            self._cleanup_old_calls(api_name)

    def make_call(self, api_name: str, func, *args, max_wait: int = 60, **kwargs):
        """
        Make an API call with rate limiting.

        Args:
            api_name: API identifier
            func: Function to call
            *args: Positional arguments for func
            max_wait: Maximum seconds to wait for slot
            **kwargs: Keyword arguments for func

        Returns:
            Result of func call

        Raises:
            RuntimeError: If rate limit exceeded and max_wait reached
        """
        if not self.wait_for_slot(api_name, max_wait):
            raise RuntimeError(f"Rate limit exceeded for {api_name}, max wait time reached")

        try:
            result = func(*args, **kwargs)
            self.record_call(api_name)
            return result
        except Exception as e:
            logger.error(f"Error in API call to {api_name}: {e}")
            raise

    def get_quota_status(self, api_name: str) -> Dict:
        """
        Get current quota status for an API.

        Args:
            api_name: API identifier

        Returns:
            Dictionary with quota information
        """
        with self.lock:
            limits = self.get_limit(api_name)
            self._cleanup_old_calls(api_name)

            calls_last_minute = self._count_calls_in_window(api_name, 60)
            calls_last_hour = self._count_calls_in_window(api_name, 3600)
            calls_last_day = self._count_calls_in_window(api_name, 86400)

            return {
                'api': api_name,
                'limits': limits,
                'usage': {
                    'per_minute': {
                        'used': calls_last_minute,
                        'limit': limits['calls_per_minute'],
                        'remaining': limits['calls_per_minute'] - calls_last_minute,
                        'percentage': (calls_last_minute / limits['calls_per_minute'] * 100)
                    },
                    'per_hour': {
                        'used': calls_last_hour,
                        'limit': limits['calls_per_hour'],
                        'remaining': limits['calls_per_hour'] - calls_last_hour,
                        'percentage': (calls_last_hour / limits['calls_per_hour'] * 100)
                    },
                    'per_day': {
                        'used': calls_last_day,
                        'limit': limits['calls_per_day'],
                        'remaining': limits['calls_per_day'] - calls_last_day,
                        'percentage': (calls_last_day / limits['calls_per_day'] * 100)
                    }
                }
            }

    def get_all_quota_status(self) -> Dict[str, Dict]:
        """
        Get quota status for all APIs.

        Returns:
            Dictionary mapping API names to quota status
        """
        status = {}
        for api_name in set(list(self.limits.keys()) + list(self.call_history.keys())):
            status[api_name] = self.get_quota_status(api_name)
        return status

    def reset_quota(self, api_name: str):
        """
        Reset quota for an API.

        Args:
            api_name: API identifier
        """
        with self.lock:
            if api_name in self.call_history:
                self.call_history[api_name].clear()
            logger.info(f"Quota reset for {api_name}")

    def get_statistics(self) -> Dict:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            stats = {
                'total_apis': len(set(list(self.limits.keys()) + list(self.call_history.keys()))),
                'apis': {}
            }

            for api_name in set(list(self.limits.keys()) + list(self.call_history.keys())):
                self._cleanup_old_calls(api_name)
                total_calls = len(self.call_history.get(api_name, []))

                stats['apis'][api_name] = {
                    'total_calls_24h': total_calls,
                    'calls_last_minute': self._count_calls_in_window(api_name, 60),
                    'calls_last_hour': self._count_calls_in_window(api_name, 3600)
                }

            return stats
