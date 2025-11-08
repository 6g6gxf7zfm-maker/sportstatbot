"""Generate comprehensive monitoring and health reports."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.health_monitor import HealthMonitor
from pipeline.cache_manager import CacheManager
from pipeline.error_recovery import ErrorRecoveryBot
from pipeline.rate_limiter import RateLimiter


class MonitoringReportGenerator:
    """
    Generates comprehensive monitoring reports including:
    - Daily digest health reports
    - Cache statistics
    - Error recovery status
    - Rate limit status
    - System health overview
    """

    def __init__(self):
        """Initialize monitoring report generator."""
        self.health_monitor = HealthMonitor()
        self.cache_manager = CacheManager()
        self.error_recovery = ErrorRecoveryBot()
        self.rate_limiter = RateLimiter()

        self.reports_dir = Path("reports/monitoring")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_digest(self, sports: Optional[List[str]] = None) -> str:
        """
        Generate comprehensive daily digest report.

        Args:
            sports: List of sports to include (None for all)

        Returns:
            Formatted report text
        """
        report = []

        # Header
        report.append("=" * 70)
        report.append("📊 SPORTSTATBOT - DAILY OPERATIONS DIGEST")
        report.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        report.append("=" * 70)
        report.append("")

        # System Health Overview
        health_report = self.health_monitor.generate_health_report()
        report.append("🏥 SYSTEM HEALTH OVERVIEW")
        report.append("-" * 70)

        status_emoji = {
            'healthy': '✅ HEALTHY',
            'degraded': '⚠️ DEGRADED',
            'critical': '🚨 CRITICAL'
        }
        overall = status_emoji.get(health_report['overall_status'], '❓ UNKNOWN')
        report.append(f"Overall Status: {overall}")
        report.append(f"Total Data Beats: {health_report['total_beats']}")
        report.append(f"  ✅ Healthy: {health_report['healthy']}")
        report.append(f"  ⏰ Stale: {health_report['stale']}")
        report.append(f"  🚨 Critical: {health_report['critical']}")
        report.append("")

        # Cache Statistics
        cache_stats = self.cache_manager.get_cache_stats()
        report.append("💾 CACHE STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Entries: {cache_stats['total_entries']}")
        report.append(f"Storage Used: {cache_stats['size_mb']:.2f} MB")

        if cache_stats['oldest_entry'] and cache_stats['newest_entry']:
            oldest = datetime.fromisoformat(cache_stats['oldest_entry']).strftime('%m/%d %H:%M')
            newest = datetime.fromisoformat(cache_stats['newest_entry']).strftime('%m/%d %H:%M')
            report.append(f"Data Range: {oldest} - {newest}")

        report.append("\nBy Type:")
        for cache_type, type_stats in cache_stats.get('by_type', {}).items():
            report.append(
                f"  {cache_type}: {type_stats['count']} entries "
                f"({type_stats['size_mb']:.2f} MB)"
            )
        report.append("")

        # Error Recovery Statistics
        recovery_stats = self.error_recovery.get_recovery_stats()
        if recovery_stats:
            total_recoveries = sum(s['total_recoveries'] for s in recovery_stats.values())
            total_successful = sum(s['successful_recoveries'] for s in recovery_stats.values())

            report.append("🔧 ERROR RECOVERY")
            report.append("-" * 70)
            report.append(f"Total Recovery Attempts: {total_recoveries}")
            report.append(f"Successful Recoveries: {total_successful}")

            if total_recoveries > 0:
                success_rate = (total_successful / total_recoveries * 100)
                report.append(f"Success Rate: {success_rate:.1f}%")

            recent_failures = self.error_recovery.get_recent_failures(hours=24)
            if recent_failures:
                report.append(f"\n⚠️ Recent Failures (24h): {len(recent_failures)}")
                for failure in recent_failures[-3:]:  # Show last 3
                    time = datetime.fromisoformat(failure['timestamp']).strftime('%H:%M')
                    report.append(f"  {time} - {failure['operation']}")

            report.append("")

        # Rate Limit Status
        rate_status = self.rate_limiter.get_all_status()
        report.append("⏱️ API RATE LIMITS")
        report.append("-" * 70)

        for api_name, status in sorted(rate_status.items()):
            status_emoji_map = {
                'ready': '✅',
                'warning': '⚠️',
                'rate_limited_minute': '🚫',
                'rate_limited_hour': '🚫'
            }
            emoji = status_emoji_map.get(status['status'], '❓')

            report.append(f"{emoji} {api_name.upper()}:")

            if status['status'] != 'unlimited':
                report.append(
                    f"  Minute: {status['requests_last_minute']}/{status['requests_per_minute']}"
                )
                report.append(
                    f"  Hour: {status['requests_last_hour']}/{status['requests_per_hour']}"
                )

        report.append("")

        # Recommendations
        if health_report.get('recommendations'):
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 70)
            for rec in health_report['recommendations']:
                report.append(f"  {rec}")
            report.append("")

        # Footer
        report.append("=" * 70)
        report.append("Report generated by SportStatBot Operations System")
        report.append("=" * 70)

        return "\n".join(report)

    def generate_leagues_update_report(self, sports: Optional[List[str]] = None) -> str:
        """
        Generate report on how many leagues updated successfully.

        Args:
            sports: List of sports to check (None for all)

        Returns:
            Formatted report text
        """
        all_beats = self.health_monitor.get_all_beats_status()

        # Group by sport
        sports_summary = {}
        for beat_key, status in all_beats.items():
            sport = beat_key.split('_')[0]

            if sports and sport not in sports:
                continue

            if sport not in sports_summary:
                sports_summary[sport] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'stale': 0
                }

            sports_summary[sport]['total'] += 1

            if status['status'] == 'healthy':
                sports_summary[sport]['successful'] += 1
            elif status['status'] in ['stale', 'critical']:
                sports_summary[sport]['stale'] += 1
            else:
                sports_summary[sport]['failed'] += 1

        # Generate report
        report = []
        report.append("=" * 60)
        report.append("📈 LEAGUE UPDATE STATUS")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        total_leagues = sum(s['total'] for s in sports_summary.values())
        total_successful = sum(s['successful'] for s in sports_summary.values())

        report.append("📊 Overall:")
        report.append(f"  Total Leagues: {total_leagues}")
        report.append(f"  ✅ Successfully Updated: {total_successful}")
        report.append(f"  ❌ Failed/Stale: {total_leagues - total_successful}")

        if total_leagues > 0:
            success_rate = (total_successful / total_leagues * 100)
            report.append(f"  Success Rate: {success_rate:.1f}%")

        report.append("")
        report.append("🏆 By Sport:")

        for sport, summary in sorted(sports_summary.items()):
            sport_success_rate = (
                (summary['successful'] / summary['total'] * 100)
                if summary['total'] > 0 else 0
            )

            status_icon = '✅' if sport_success_rate >= 80 else '⚠️' if sport_success_rate >= 50 else '❌'

            report.append(f"\n  {status_icon} {sport.upper()}:")
            report.append(f"    Total: {summary['total']}")
            report.append(f"    Successful: {summary['successful']}")
            report.append(f"    Failed/Stale: {summary['failed'] + summary['stale']}")
            report.append(f"    Success Rate: {sport_success_rate:.1f}%")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def save_report(self, report_content: str, report_type: str = "digest") -> str:
        """
        Save report to file.

        Args:
            report_content: Report text
            report_type: Type of report (digest, league_update, etc.)

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_{timestamp}.txt"
        filepath = self.reports_dir / filename

        try:
            with open(filepath, 'w') as f:
                f.write(report_content)

            return str(filepath)

        except Exception as e:
            print(f"Error saving report: {e}")
            return ""

    def get_system_metrics(self) -> Dict:
        """
        Get comprehensive system metrics as JSON.

        Returns:
            Dictionary with all system metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'health': self.health_monitor.generate_health_report(),
            'cache': self.cache_manager.get_cache_stats(),
            'recovery': self.error_recovery.get_recovery_stats(),
            'rate_limits': self.rate_limiter.get_all_status()
        }

    def export_metrics_json(self, filepath: Optional[str] = None) -> str:
        """
        Export system metrics as JSON file.

        Args:
            filepath: Optional path to save to

        Returns:
            Path to exported file
        """
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = self.reports_dir / f"metrics_{timestamp}.json"

        try:
            metrics = self.get_system_metrics()

            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)

            return str(filepath)

        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return ""
