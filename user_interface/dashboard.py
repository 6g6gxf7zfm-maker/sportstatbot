"""Dashboard for displaying agent activity and performance metrics."""
from typing import Dict, List
from datetime import datetime, timedelta

from .agent_tracker import AgentTracker
from .user_preferences import UserPreferences
import config


class Dashboard:
    """Visual dashboard for SportStatBot metrics and activity."""

    def __init__(self):
        """Initialize the dashboard."""
        self.tracker = AgentTracker()
        self.preferences = UserPreferences()

    def render_full_dashboard(self, hours: int = 24) -> str:
        """
        Render complete dashboard.

        Args:
            hours: Hours to look back for metrics

        Returns:
            Formatted dashboard string
        """
        sections = [
            self._render_header(),
            self._render_performance_metrics(hours),
            self._render_league_coverage(hours),
            self._render_recent_activity(limit=10),
            self._render_errors(hours),
            self._render_footer()
        ]

        return "\n".join(sections)

    def _render_header(self) -> str:
        """Render dashboard header."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
{'='*80}
📊 SPORTSTATBOT DASHBOARD
{'='*80}
Generated: {now}
"""

    def _render_performance_metrics(self, hours: int = 24) -> str:
        """Render performance metrics section."""
        metrics = self.tracker.get_performance_metrics(hours)

        success_bar = self._create_bar(metrics['success_rate'], 100, width=40)
        timeliness = self.tracker.get_timeliness_score(hours)
        timeliness_bar = self._create_bar(timeliness, 100, width=40)

        output = [f"\n🎯 PERFORMANCE METRICS (Last {hours}h)"]
        output.append("─" * 80)
        output.append(f"  Total Runs:        {metrics['total_runs']}")
        output.append(f"  Successful:        {metrics['successful_runs']}")
        output.append(f"  Success Rate:      {metrics['success_rate']}% {success_bar}")
        output.append(f"  Avg Exec Time:     {metrics['avg_execution_time']}s")
        output.append(f"  Timeliness Score:  {timeliness}% {timeliness_bar}")

        # Runs by agent type
        if metrics['runs_by_agent']:
            output.append("\n  Runs by Agent Type:")
            for agent_type, count in sorted(
                metrics['runs_by_agent'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                output.append(f"    • {agent_type}: {count}")

        return "\n".join(output)

    def _render_league_coverage(self, hours: int = 24) -> str:
        """Render league coverage section."""
        coverage = self.tracker.get_league_coverage(hours)

        output = [f"\n🏆 LEAGUE COVERAGE (Last {hours}h)"]
        output.append("─" * 80)

        if not coverage:
            output.append("  No league coverage data available")
            return "\n".join(output)

        # Sort by coverage count
        max_count = max(coverage.values()) if coverage else 1

        for league, count in sorted(
            coverage.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            emoji = config.SPORTS_CONFIG.get(league, {}).get('emoji', '📊')
            name = config.SPORTS_CONFIG.get(league, {}).get('display_name', league.upper())
            bar = self._create_bar(count, max_count, width=30)
            output.append(f"  {emoji} {name:20} {count:3} runs {bar}")

        return "\n".join(output)

    def _render_recent_activity(self, limit: int = 10) -> str:
        """Render recent activity section."""
        recent = self.tracker.get_recent_runs(limit=limit)

        output = [f"\n🤖 RECENT ACTIVITY (Last {limit} runs)"]
        output.append("─" * 80)

        if not recent:
            output.append("  No recent activity")
            return "\n".join(output)

        for run in recent:
            status = "✅" if run['success'] else "❌"
            timestamp = run['timestamp'][:16].replace('T', ' ')
            agent_type = run['agent_type']
            leagues = ', '.join(run.get('leagues', []))

            exec_time = ""
            if run.get('execution_time'):
                exec_time = f" ({run['execution_time']:.2f}s)"

            league_info = f" [{leagues}]" if leagues else ""

            output.append(
                f"  {status} {timestamp} | {agent_type}{exec_time}{league_info}"
            )

        return "\n".join(output)

    def _render_errors(self, hours: int = 24) -> str:
        """Render errors section."""
        metrics = self.tracker.get_performance_metrics(hours)
        errors = metrics.get('errors', [])

        output = [f"\n⚠️  ERRORS & FAILURES (Last {hours}h)"]
        output.append("─" * 80)

        if not errors:
            output.append("  No errors - all systems running smoothly! ✨")
            return "\n".join(output)

        for error in errors[:5]:  # Show max 5 recent errors
            timestamp = error['timestamp'][:16].replace('T', ' ')
            agent_type = error['agent_type']
            metadata = error.get('metadata', {})
            error_msg = metadata.get('error', 'Unknown error')

            output.append(f"  ❌ {timestamp} | {agent_type}")
            output.append(f"     Error: {error_msg}")

        if len(errors) > 5:
            output.append(f"\n  ... and {len(errors) - 5} more errors")

        return "\n".join(output)

    def _render_footer(self) -> str:
        """Render dashboard footer."""
        return f"\n{'='*80}\n"

    def _create_bar(self, value: float, max_value: float, width: int = 40) -> str:
        """
        Create a text-based progress bar.

        Args:
            value: Current value
            max_value: Maximum value
            width: Bar width in characters

        Returns:
            Progress bar string
        """
        if max_value == 0:
            percentage = 0
        else:
            percentage = min(100, (value / max_value) * 100)

        filled = int((percentage / 100) * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty
        return f"[{bar}]"

    def render_compact_dashboard(self, hours: int = 24) -> str:
        """
        Render compact dashboard for quick overview.

        Args:
            hours: Hours to look back

        Returns:
            Compact dashboard string
        """
        metrics = self.tracker.get_performance_metrics(hours)
        coverage = self.tracker.get_league_coverage(hours)
        timeliness = self.tracker.get_timeliness_score(hours)

        output = []
        output.append("\n" + "="*60)
        output.append(f"📊 QUICK STATUS (Last {hours}h)")
        output.append("="*60)
        output.append(f"Runs: {metrics['total_runs']} | "
                     f"Success: {metrics['success_rate']}% | "
                     f"Timeliness: {timeliness}%")

        if coverage:
            leagues = ', '.join([
                f"{config.SPORTS_CONFIG.get(l, {}).get('emoji', '')} {l.upper()}"
                for l in sorted(coverage.keys())
            ])
            output.append(f"Coverage: {leagues}")

        output.append("="*60 + "\n")

        return "\n".join(output)

    def export_dashboard(self, filepath: str, hours: int = 24) -> bool:
        """
        Export dashboard to file.

        Args:
            filepath: Path to export file
            hours: Hours to include

        Returns:
            True if successful
        """
        try:
            dashboard = self.render_full_dashboard(hours)

            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                f.write(dashboard)

            return True
        except Exception as e:
            print(f"Error exporting dashboard: {e}")
            return False

    def get_alerts(self, hours: int = 24) -> List[str]:
        """
        Get alerts for issues requiring attention.

        Args:
            hours: Hours to look back

        Returns:
            List of alert messages
        """
        alerts = []
        metrics = self.tracker.get_performance_metrics(hours)

        # Low success rate
        if metrics['success_rate'] < 80 and metrics['total_runs'] > 0:
            alerts.append(
                f"⚠️  Low success rate: {metrics['success_rate']}% "
                f"({metrics['total_runs'] - metrics['successful_runs']} failures)"
            )

        # No recent runs
        if metrics['total_runs'] == 0:
            alerts.append("⚠️  No agent runs in the last 24 hours")

        # Low timeliness
        timeliness = self.tracker.get_timeliness_score(hours)
        if timeliness < 50:
            alerts.append(f"⚠️  Low timeliness score: {timeliness}%")

        # Missing league coverage
        enabled_leagues = self.preferences.get_enabled_leagues()
        coverage = self.tracker.get_league_coverage(hours)
        missing = set(enabled_leagues) - set(coverage.keys())
        if missing:
            alerts.append(
                f"⚠️  No coverage for enabled leagues: {', '.join(missing)}"
            )

        return alerts
