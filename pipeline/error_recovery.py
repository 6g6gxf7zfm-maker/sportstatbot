"""Error recovery bot for handling failed API requests."""
import time
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any
import json
from pathlib import Path


class ErrorRecoveryBot:
    """
    Handles automatic retry of failed API calls with exponential backoff.
    Tracks failure patterns and provides recovery statistics.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 2.0,
                 recovery_dir: str = "monitoring/recovery"):
        """
        Initialize error recovery bot.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            recovery_dir: Directory to store recovery logs
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.recovery_dir = Path(recovery_dir)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)

        self.recovery_log_file = self.recovery_dir / "recovery_log.json"
        self.stats_file = self.recovery_dir / "recovery_stats.json"

    def execute_with_retry(self, func: Callable, *args,
                          operation_name: str = "API call",
                          **kwargs) -> Optional[Any]:
        """
        Execute function with automatic retry on failure.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            operation_name: Name of operation for logging
            **kwargs: Keyword arguments for function

        Returns:
            Function result or None if all retries failed
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000

                if attempt > 0:
                    # Log successful recovery
                    self._log_recovery(
                        operation_name=operation_name,
                        attempts=attempt + 1,
                        success=True,
                        error=None,
                        response_time_ms=elapsed_ms
                    )

                return result

            except Exception as e:
                last_error = e

                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    delay = self.base_delay * (2 ** attempt)

                    print(f"⚠️ {operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    print(f"   Retrying in {delay:.1f} seconds...")

                    time.sleep(delay)
                else:
                    # All retries exhausted
                    self._log_recovery(
                        operation_name=operation_name,
                        attempts=attempt + 1,
                        success=False,
                        error=str(e),
                        response_time_ms=None
                    )

                    print(f"❌ {operation_name} failed after {attempt + 1} attempts: {e}")

        return None

    def _log_recovery(self, operation_name: str, attempts: int,
                     success: bool, error: Optional[str],
                     response_time_ms: Optional[float]) -> None:
        """Log recovery attempt."""
        try:
            # Load existing log
            recovery_log = []
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r') as f:
                    recovery_log = json.load(f)

            # Add new entry
            recovery_log.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'attempts': attempts,
                'success': success,
                'error': error,
                'response_time_ms': response_time_ms
            })

            # Keep only last 500 entries
            recovery_log = recovery_log[-500:]

            # Save log
            with open(self.recovery_log_file, 'w') as f:
                json.dump(recovery_log, f, indent=2)

            # Update stats
            self._update_stats(operation_name, attempts, success)

        except Exception as e:
            print(f"Error logging recovery: {e}")

    def _update_stats(self, operation_name: str, attempts: int, success: bool) -> None:
        """Update recovery statistics."""
        try:
            stats = {}
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)

            if operation_name not in stats:
                stats[operation_name] = {
                    'total_recoveries': 0,
                    'successful_recoveries': 0,
                    'failed_recoveries': 0,
                    'total_retry_attempts': 0,
                    'avg_attempts_to_success': 0
                }

            op_stats = stats[operation_name]
            op_stats['total_recoveries'] += 1
            op_stats['total_retry_attempts'] += attempts

            if success:
                op_stats['successful_recoveries'] += 1

                # Update average attempts to success
                total_success = op_stats['successful_recoveries']
                current_avg = op_stats['avg_attempts_to_success']
                op_stats['avg_attempts_to_success'] = (
                    (current_avg * (total_success - 1) + attempts) / total_success
                )
            else:
                op_stats['failed_recoveries'] += 1

            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)

        except Exception as e:
            print(f"Error updating recovery stats: {e}")

    def get_recovery_stats(self, operation_name: Optional[str] = None) -> Dict:
        """
        Get recovery statistics.

        Args:
            operation_name: Specific operation to get stats for (None for all)

        Returns:
            Statistics dictionary
        """
        if not self.stats_file.exists():
            return {}

        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)

            if operation_name:
                return stats.get(operation_name, {})
            return stats

        except Exception as e:
            print(f"Error getting recovery stats: {e}")
            return {}

    def get_recent_failures(self, hours: int = 24) -> list:
        """
        Get recent recovery failures.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent failures
        """
        if not self.recovery_log_file.exists():
            return []

        try:
            with open(self.recovery_log_file, 'r') as f:
                recovery_log = json.load(f)

            cutoff_time = datetime.now() - timedelta(hours=hours)

            recent_failures = [
                entry for entry in recovery_log
                if not entry['success']
                and datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]

            return recent_failures

        except Exception as e:
            print(f"Error getting recent failures: {e}")
            return []

    def generate_recovery_report(self) -> str:
        """
        Generate recovery report.

        Returns:
            Formatted text report
        """
        stats = self.get_recovery_stats()

        if not stats:
            return "No recovery data available"

        report = []
        report.append("=" * 60)
        report.append("🔧 ERROR RECOVERY REPORT")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        total_recoveries = sum(s['total_recoveries'] for s in stats.values())
        total_successful = sum(s['successful_recoveries'] for s in stats.values())
        total_failed = sum(s['failed_recoveries'] for s in stats.values())

        overall_success_rate = (total_successful / total_recoveries * 100) if total_recoveries > 0 else 0

        report.append("📊 Overall Statistics:")
        report.append(f"  Total Recovery Attempts: {total_recoveries}")
        report.append(f"  ✅ Successful: {total_successful}")
        report.append(f"  ❌ Failed: {total_failed}")
        report.append(f"  Success Rate: {overall_success_rate:.1f}%")
        report.append("")

        report.append("📋 By Operation:")
        for operation, op_stats in sorted(stats.items()):
            success_rate = (
                op_stats['successful_recoveries'] / op_stats['total_recoveries'] * 100
                if op_stats['total_recoveries'] > 0 else 0
            )

            report.append(f"\n  {operation}:")
            report.append(f"    Total Recoveries: {op_stats['total_recoveries']}")
            report.append(f"    Success Rate: {success_rate:.1f}%")
            report.append(f"    Avg Attempts to Success: {op_stats['avg_attempts_to_success']:.1f}")

        # Recent failures
        recent_failures = self.get_recent_failures(hours=24)
        if recent_failures:
            report.append("\n⚠️ Recent Failures (Last 24h):")
            for failure in recent_failures[-5:]:  # Show last 5
                timestamp = datetime.fromisoformat(failure['timestamp']).strftime('%H:%M')
                report.append(f"  {timestamp} - {failure['operation']}: {failure['error']}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def clear_old_logs(self, days: int = 7) -> int:
        """
        Clear recovery logs older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of entries removed
        """
        if not self.recovery_log_file.exists():
            return 0

        try:
            with open(self.recovery_log_file, 'r') as f:
                recovery_log = json.load(f)

            original_count = len(recovery_log)
            cutoff_time = datetime.now() - timedelta(days=days)

            recovery_log = [
                entry for entry in recovery_log
                if datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]

            with open(self.recovery_log_file, 'w') as f:
                json.dump(recovery_log, f, indent=2)

            return original_count - len(recovery_log)

        except Exception as e:
            print(f"Error clearing old logs: {e}")
            return 0
