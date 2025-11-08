"""Rate limiting and API throttling system."""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import deque
import json
from pathlib import Path


class RateLimiter:
    """
    Rate limiting system for API-friendly operation.
    Supports per-API limits, burst protection, and smart throttling.
    """

    def __init__(self, config_file: str = "config/rate_limits.json"):
        """
        Initialize rate limiter.

        Args:
            config_file: Path to rate limit configuration
        """
        self.config_file = Path(config_file)
        self.request_history: Dict[str, deque] = {}

        # Default rate limits (requests per minute)
        self.default_limits = {
            'espn': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'burst_size': 5  # Max requests in burst
            },
            'odds_api': {
                'requests_per_minute': 10,
                'requests_per_hour': 100,
                'burst_size': 3
            },
            'nhl_api': {
                'requests_per_minute': 20,
                'requests_per_hour': 300,
                'burst_size': 5
            },
            'mlb_api': {
                'requests_per_minute': 20,
                'requests_per_hour': 300,
                'burst_size': 5
            }
        }

        # Load custom limits if available
        self.limits = self._load_limits()

    def _load_limits(self) -> Dict:
        """Load rate limit configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_limits = json.load(f)
                # Merge with defaults
                return {**self.default_limits, **custom_limits}
            except Exception as e:
                print(f"Error loading rate limits, using defaults: {e}")

        return self.default_limits

    def check_rate_limit(self, api_name: str) -> bool:
        """
        Check if request is allowed under rate limits.

        Args:
            api_name: Name of API (espn, odds_api, etc.)

        Returns:
            True if request is allowed, False if rate limited
        """
        if api_name not in self.limits:
            # No limit configured, allow request
            return True

        limits = self.limits[api_name]

        # Initialize history if needed
        if api_name not in self.request_history:
            self.request_history[api_name] = deque()

        history = self.request_history[api_name]
        now = datetime.now()

        # Remove requests older than 1 hour
        cutoff_hour = now - timedelta(hours=1)
        while history and history[0] < cutoff_hour:
            history.popleft()

        # Check hourly limit
        if len(history) >= limits['requests_per_hour']:
            return False

        # Check per-minute limit
        cutoff_minute = now - timedelta(minutes=1)
        recent_requests = sum(1 for ts in history if ts > cutoff_minute)

        if recent_requests >= limits['requests_per_minute']:
            return False

        # Check burst limit (last 5 seconds)
        cutoff_burst = now - timedelta(seconds=5)
        burst_requests = sum(1 for ts in history if ts > cutoff_burst)

        if burst_requests >= limits['burst_size']:
            return False

        return True

    def record_request(self, api_name: str) -> None:
        """
        Record a request for rate limiting.

        Args:
            api_name: Name of API
        """
        if api_name not in self.request_history:
            self.request_history[api_name] = deque()

        self.request_history[api_name].append(datetime.now())

    def wait_if_needed(self, api_name: str, max_wait_seconds: float = 60.0) -> bool:
        """
        Wait if rate limited, up to max wait time.

        Args:
            api_name: Name of API
            max_wait_seconds: Maximum time to wait

        Returns:
            True if request can proceed, False if max wait exceeded
        """
        if self.check_rate_limit(api_name):
            return True

        if api_name not in self.limits:
            return True

        limits = self.limits[api_name]
        history = self.request_history.get(api_name, deque())

        if not history:
            return True

        # Calculate wait time based on oldest request in minute window
        cutoff_minute = datetime.now() - timedelta(minutes=1)
        minute_requests = [ts for ts in history if ts > cutoff_minute]

        if len(minute_requests) >= limits['requests_per_minute']:
            # Wait until oldest request in minute window expires
            oldest_in_minute = min(minute_requests)
            wait_until = oldest_in_minute + timedelta(minutes=1)
            wait_seconds = (wait_until - datetime.now()).total_seconds()

            if wait_seconds > max_wait_seconds:
                return False

            if wait_seconds > 0:
                print(f"⏳ Rate limit reached for {api_name}, waiting {wait_seconds:.1f}s...")
                time.sleep(wait_seconds)

        return True

    def get_rate_limit_status(self, api_name: str) -> Dict:
        """
        Get current rate limit status for an API.

        Args:
            api_name: Name of API

        Returns:
            Status dictionary
        """
        if api_name not in self.limits:
            return {
                'api': api_name,
                'status': 'unlimited',
                'requests_remaining': None
            }

        limits = self.limits[api_name]
        history = self.request_history.get(api_name, deque())

        if not history:
            return {
                'api': api_name,
                'status': 'ready',
                'requests_per_minute': limits['requests_per_minute'],
                'requests_per_hour': limits['requests_per_hour'],
                'requests_last_minute': 0,
                'requests_last_hour': 0,
                'remaining_minute': limits['requests_per_minute'],
                'remaining_hour': limits['requests_per_hour']
            }

        now = datetime.now()

        # Count requests in windows
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_hour = now - timedelta(hours=1)

        requests_last_minute = sum(1 for ts in history if ts > cutoff_minute)
        requests_last_hour = sum(1 for ts in history if ts > cutoff_hour)

        remaining_minute = max(0, limits['requests_per_minute'] - requests_last_minute)
        remaining_hour = max(0, limits['requests_per_hour'] - requests_last_hour)

        # Determine status
        if requests_last_minute >= limits['requests_per_minute']:
            status = 'rate_limited_minute'
        elif requests_last_hour >= limits['requests_per_hour']:
            status = 'rate_limited_hour'
        elif requests_last_minute > limits['requests_per_minute'] * 0.8:
            status = 'warning'
        else:
            status = 'ready'

        return {
            'api': api_name,
            'status': status,
            'requests_per_minute': limits['requests_per_minute'],
            'requests_per_hour': limits['requests_per_hour'],
            'requests_last_minute': requests_last_minute,
            'requests_last_hour': requests_last_hour,
            'remaining_minute': remaining_minute,
            'remaining_hour': remaining_hour
        }

    def get_all_status(self) -> Dict[str, Dict]:
        """
        Get rate limit status for all configured APIs.

        Returns:
            Dictionary mapping API names to status
        """
        return {
            api_name: self.get_rate_limit_status(api_name)
            for api_name in self.limits.keys()
        }

    def reset_limits(self, api_name: Optional[str] = None) -> None:
        """
        Reset rate limit history.

        Args:
            api_name: Specific API to reset (None for all)
        """
        if api_name:
            if api_name in self.request_history:
                self.request_history[api_name].clear()
        else:
            self.request_history.clear()

    def set_custom_limit(self, api_name: str, requests_per_minute: int,
                        requests_per_hour: int, burst_size: int = 5) -> None:
        """
        Set custom rate limit for an API.

        Args:
            api_name: Name of API
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
            burst_size: Max requests in 5-second burst
        """
        self.limits[api_name] = {
            'requests_per_minute': requests_per_minute,
            'requests_per_hour': requests_per_hour,
            'burst_size': burst_size
        }

        # Save to config file
        self._save_limits()

    def _save_limits(self) -> None:
        """Save current limits to config file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.limits, f, indent=2)

        except Exception as e:
            print(f"Error saving rate limits: {e}")

    def generate_status_report(self) -> str:
        """
        Generate rate limit status report.

        Returns:
            Formatted text report
        """
        all_status = self.get_all_status()

        report = []
        report.append("=" * 60)
        report.append("⏱️ RATE LIMIT STATUS")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")

        for api_name, status in sorted(all_status.items()):
            status_emoji = {
                'ready': '✅',
                'warning': '⚠️',
                'rate_limited_minute': '🚫',
                'rate_limited_hour': '🚫',
                'unlimited': '♾️'
            }
            emoji = status_emoji.get(status['status'], '❓')

            report.append(f"{emoji} {api_name.upper()}:")
            report.append(f"  Status: {status['status']}")

            if status['status'] != 'unlimited':
                report.append(
                    f"  Per Minute: {status['requests_last_minute']}/{status['requests_per_minute']} "
                    f"({status['remaining_minute']} remaining)"
                )
                report.append(
                    f"  Per Hour: {status['requests_last_hour']}/{status['requests_per_hour']} "
                    f"({status['remaining_hour']} remaining)"
                )

            report.append("")

        report.append("=" * 60)

        return "\n".join(report)
