"""Agent activity tracking and performance metrics for SportStatBot."""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AgentTracker:
    """Tracks agent runs and performance metrics."""

    def __init__(self, log_file: str = 'data/agent_logs.json'):
        """
        Initialize agent tracker.

        Args:
            log_file: Path to agent log file
        """
        self.log_file = log_file
        self.logs = self._load_logs()

    def _load_logs(self) -> List[Dict]:
        """Load agent logs from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_logs(self) -> bool:
        """Save logs to file."""
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving logs: {e}")
            return False

    def log_run(
        self,
        agent_type: str,
        leagues: Optional[List[str]] = None,
        success: bool = True,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Log an agent run.

        Args:
            agent_type: Type of agent (e.g., 'report_generator', 'analyzer')
            leagues: List of leagues processed
            success: Whether the run was successful
            execution_time: Execution time in seconds
            metadata: Additional metadata

        Returns:
            Run ID
        """
        run_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        log_entry = {
            'run_id': run_id,
            'agent_type': agent_type,
            'timestamp': datetime.now().isoformat(),
            'leagues': leagues or [],
            'success': success,
            'execution_time': execution_time,
            'metadata': metadata or {}
        }

        self.logs.append(log_entry)
        self._save_logs()

        return run_id

    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent agent runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of recent runs
        """
        return sorted(
            self.logs,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]

    def get_runs_since(self, cutoff: datetime) -> List[Dict]:
        """
        Get all runs since a cutoff time.

        Args:
            cutoff: Cutoff datetime

        Returns:
            List of runs since cutoff
        """
        cutoff_str = cutoff.isoformat()
        return [
            log for log in self.logs
            if log['timestamp'] >= cutoff_str
        ]

    def get_runs_by_agent(self, agent_type: str) -> List[Dict]:
        """
        Get all runs for a specific agent type.

        Args:
            agent_type: Agent type to filter by

        Returns:
            List of runs for that agent
        """
        return [
            log for log in self.logs
            if log['agent_type'] == agent_type
        ]

    def get_performance_metrics(self, hours: int = 24) -> Dict:
        """
        Calculate performance metrics for recent period.

        Args:
            hours: Hours to look back

        Returns:
            Dictionary of performance metrics
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_runs = self.get_runs_since(cutoff)

        if not recent_runs:
            return {
                'total_runs': 0,
                'successful_runs': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'runs_by_agent': {},
                'errors': []
            }

        # Calculate metrics
        total_runs = len(recent_runs)
        successful_runs = sum(1 for r in recent_runs if r['success'])
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

        # Average execution time (only for runs that recorded it)
        times = [r['execution_time'] for r in recent_runs if r.get('execution_time')]
        avg_time = sum(times) / len(times) if times else 0

        # Runs by agent type
        runs_by_agent = defaultdict(int)
        for run in recent_runs:
            runs_by_agent[run['agent_type']] += 1

        # Failed runs
        errors = [
            {
                'agent_type': r['agent_type'],
                'timestamp': r['timestamp'],
                'metadata': r.get('metadata', {})
            }
            for r in recent_runs
            if not r['success']
        ]

        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'success_rate': round(success_rate, 2),
            'avg_execution_time': round(avg_time, 2),
            'runs_by_agent': dict(runs_by_agent),
            'errors': errors
        }

    def get_league_coverage(self, hours: int = 24) -> Dict[str, int]:
        """
        Get coverage statistics by league.

        Args:
            hours: Hours to look back

        Returns:
            Dictionary mapping league to run count
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_runs = self.get_runs_since(cutoff)

        coverage = defaultdict(int)
        for run in recent_runs:
            for league in run.get('leagues', []):
                coverage[league] += 1

        return dict(coverage)

    def get_timeliness_score(self, hours: int = 24) -> float:
        """
        Calculate timeliness score based on run frequency.

        Args:
            hours: Hours to look back

        Returns:
            Timeliness score (0-100)
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_runs = self.get_runs_since(cutoff)

        if not recent_runs:
            return 0.0

        # Calculate expected runs (e.g., 2 per day = 48 for 24h)
        expected_runs = (hours / 24) * 2
        actual_runs = len(recent_runs)

        # Score based on meeting/exceeding expectations
        score = min(100, (actual_runs / expected_runs) * 100)
        return round(score, 2)

    def clear_old_logs(self, days: int = 30) -> int:
        """
        Clear logs older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of logs removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        original_count = len(self.logs)
        self.logs = [
            log for log in self.logs
            if log['timestamp'] >= cutoff_str
        ]

        removed = original_count - len(self.logs)
        if removed > 0:
            self._save_logs()

        return removed

    def export_metrics(self, filepath: str, hours: int = 24) -> bool:
        """
        Export performance metrics to JSON file.

        Args:
            filepath: Path to export file
            hours: Hours to include in metrics

        Returns:
            True if successful
        """
        try:
            metrics = {
                'export_timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'performance_metrics': self.get_performance_metrics(hours),
                'league_coverage': self.get_league_coverage(hours),
                'timeliness_score': self.get_timeliness_score(hours)
            }

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)

            return True
        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return False
