"""Health monitoring system for data pipeline."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class HealthMonitor:
    """
    Monitors health and staleness of each data beat.
    Tracks API status, data freshness, and error rates.
    """

    def __init__(self, health_dir: str = "monitoring/health"):
        """
        Initialize health monitor.

        Args:
            health_dir: Directory to store health data
        """
        self.health_dir = Path(health_dir)
        self.health_dir.mkdir(parents=True, exist_ok=True)

        self.beats_file = self.health_dir / "beats_status.json"
        self.errors_file = self.health_dir / "error_log.json"
        self.metrics_file = self.health_dir / "metrics.json"

    def record_beat(self, sport: str, data_type: str, success: bool,
                   response_time_ms: Optional[float] = None,
                   error: Optional[str] = None) -> None:
        """
        Record a data fetch attempt (beat).

        Args:
            sport: Sport identifier
            data_type: Type of data fetched
            success: Whether fetch was successful
            response_time_ms: Response time in milliseconds
            error: Error message if failed
        """
        beats = self._load_beats()

        beat_key = f"{sport}_{data_type}"
        if beat_key not in beats:
            beats[beat_key] = {
                'sport': sport,
                'data_type': data_type,
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0,
                'last_success': None,
                'last_failure': None,
                'last_attempt': None,
                'avg_response_time_ms': 0,
                'error_count_24h': 0
            }

        beat = beats[beat_key]
        beat['total_attempts'] += 1
        beat['last_attempt'] = datetime.now().isoformat()

        if success:
            beat['successful_attempts'] += 1
            beat['last_success'] = datetime.now().isoformat()

            if response_time_ms:
                # Update rolling average
                current_avg = beat['avg_response_time_ms']
                total_success = beat['successful_attempts']
                beat['avg_response_time_ms'] = (
                    (current_avg * (total_success - 1) + response_time_ms) / total_success
                )
        else:
            beat['failed_attempts'] += 1
            beat['last_failure'] = datetime.now().isoformat()
            beat['error_count_24h'] += 1

            if error:
                self._log_error(sport, data_type, error)

        self._save_beats(beats)

    def get_beat_status(self, sport: str, data_type: str) -> Dict:
        """
        Get current status of a specific beat.

        Args:
            sport: Sport identifier
            data_type: Type of data

        Returns:
            Status dictionary
        """
        beats = self._load_beats()
        beat_key = f"{sport}_{data_type}"

        if beat_key not in beats:
            return {
                'status': 'unknown',
                'message': 'No data available'
            }

        beat = beats[beat_key]

        # Calculate staleness
        if beat['last_success']:
            last_success = datetime.fromisoformat(beat['last_success'])
            age = datetime.now() - last_success
            hours_stale = age.total_seconds() / 3600

            if hours_stale < 1:
                status = 'healthy'
                color = 'green'
            elif hours_stale < 24:
                status = 'stale'
                color = 'yellow'
            else:
                status = 'critical'
                color = 'red'
        else:
            status = 'no_data'
            color = 'gray'
            hours_stale = None

        # Calculate success rate
        total = beat['total_attempts']
        success_rate = (beat['successful_attempts'] / total * 100) if total > 0 else 0

        return {
            'status': status,
            'color': color,
            'hours_stale': round(hours_stale, 2) if hours_stale else None,
            'success_rate': round(success_rate, 2),
            'total_attempts': total,
            'successful_attempts': beat['successful_attempts'],
            'failed_attempts': beat['failed_attempts'],
            'last_success': beat['last_success'],
            'last_failure': beat['last_failure'],
            'avg_response_time_ms': round(beat['avg_response_time_ms'], 2),
            'error_count_24h': beat['error_count_24h']
        }

    def get_all_beats_status(self) -> Dict[str, Dict]:
        """
        Get status of all monitored beats.

        Returns:
            Dictionary mapping beat keys to status
        """
        beats = self._load_beats()
        statuses = {}

        for beat_key, beat_data in beats.items():
            sport = beat_data['sport']
            data_type = beat_data['data_type']
            statuses[beat_key] = self.get_beat_status(sport, data_type)

        return statuses

    def generate_health_report(self) -> Dict:
        """
        Generate comprehensive health report.

        Returns:
            Health report with statistics and recommendations
        """
        all_statuses = self.get_all_beats_status()

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_beats': len(all_statuses),
            'healthy': 0,
            'stale': 0,
            'critical': 0,
            'no_data': 0,
            'overall_status': 'healthy',
            'beats': all_statuses,
            'recommendations': []
        }

        # Count by status
        for status in all_statuses.values():
            report[status['status']] += 1

        # Determine overall status
        if report['critical'] > 0:
            report['overall_status'] = 'critical'
        elif report['stale'] > report['healthy']:
            report['overall_status'] = 'degraded'

        # Generate recommendations
        if report['critical'] > 0:
            report['recommendations'].append(
                f"⚠️ {report['critical']} beat(s) are critical - investigate immediately"
            )

        if report['stale'] > 0:
            report['recommendations'].append(
                f"⏰ {report['stale']} beat(s) are stale - consider refreshing data"
            )

        return report

    def generate_freshness_heatmap(self) -> Dict:
        """
        Generate data freshness heatmap.

        Returns:
            Heatmap data structure (red=stale, yellow=warning, green=fresh)
        """
        all_statuses = self.get_all_beats_status()

        heatmap = {
            'timestamp': datetime.now().isoformat(),
            'sports': defaultdict(dict)
        }

        for beat_key, status in all_statuses.items():
            sport = beat_key.split('_')[0]
            data_type = '_'.join(beat_key.split('_')[1:])

            heatmap['sports'][sport][data_type] = {
                'color': status['color'],
                'status': status['status'],
                'hours_stale': status['hours_stale'],
                'success_rate': status['success_rate']
            }

        # Convert defaultdict to regular dict for JSON serialization
        heatmap['sports'] = dict(heatmap['sports'])

        return heatmap

    def generate_daily_digest(self) -> str:
        """
        Generate daily digest health report.

        Returns:
            Formatted text report
        """
        report = self.generate_health_report()

        digest = []
        digest.append("=" * 60)
        digest.append("📊 DAILY HEALTH DIGEST")
        digest.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        digest.append("=" * 60)
        digest.append("")

        # Overall status
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'critical': '🚨'
        }
        emoji = status_emoji.get(report['overall_status'], '❓')
        digest.append(f"{emoji} Overall Status: {report['overall_status'].upper()}")
        digest.append("")

        # Statistics
        digest.append("📈 Statistics:")
        digest.append(f"  Total Beats: {report['total_beats']}")
        digest.append(f"  ✅ Healthy: {report['healthy']}")
        digest.append(f"  ⏰ Stale: {report['stale']}")
        digest.append(f"  🚨 Critical: {report['critical']}")
        digest.append(f"  ❓ No Data: {report['no_data']}")
        digest.append("")

        # Recommendations
        if report['recommendations']:
            digest.append("💡 Recommendations:")
            for rec in report['recommendations']:
                digest.append(f"  {rec}")
            digest.append("")

        # Beat details
        digest.append("🎯 Beat Details:")
        for beat_key, status in sorted(report['beats'].items()):
            color_emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴', 'gray': '⚪'}
            emoji = color_emoji.get(status['color'], '⚪')

            sport = beat_key.split('_')[0].upper()
            data_type = '_'.join(beat_key.split('_')[1:])

            stale_info = f" ({status['hours_stale']}h old)" if status['hours_stale'] else ""
            digest.append(
                f"  {emoji} {sport} - {data_type}: "
                f"{status['success_rate']}% success{stale_info}"
            )

        digest.append("")
        digest.append("=" * 60)

        return "\n".join(digest)

    def _log_error(self, sport: str, data_type: str, error: str) -> None:
        """Log error to error file."""
        try:
            errors = []
            if self.errors_file.exists():
                with open(self.errors_file, 'r') as f:
                    errors = json.load(f)

            errors.append({
                'timestamp': datetime.now().isoformat(),
                'sport': sport,
                'data_type': data_type,
                'error': str(error)
            })

            # Keep only last 1000 errors
            errors = errors[-1000:]

            with open(self.errors_file, 'w') as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            print(f"Error logging error: {e}")

    def _load_beats(self) -> Dict:
        """Load beats data from file."""
        if not self.beats_file.exists():
            return {}

        try:
            with open(self.beats_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading beats: {e}")
            return {}

    def _save_beats(self, beats: Dict) -> None:
        """Save beats data to file."""
        try:
            with open(self.beats_file, 'w') as f:
                json.dump(beats, f, indent=2)
        except Exception as e:
            print(f"Error saving beats: {e}")

    def reset_24h_counters(self) -> None:
        """Reset 24-hour error counters (call daily)."""
        beats = self._load_beats()

        for beat in beats.values():
            beat['error_count_24h'] = 0

        self._save_beats(beats)
