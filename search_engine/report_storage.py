"""Report storage and indexing system."""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from tinydb import TinyDB, Query


class ReportStorage:
    """
    Storage system for sports reports and digests.
    Enables persistence and retrieval of historical reports.
    """

    def __init__(self, storage_dir: str = './reports_db'):
        """
        Initialize report storage.

        Args:
            storage_dir: Directory for storing reports database
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        # Initialize TinyDB
        db_path = os.path.join(storage_dir, 'reports.json')
        self.db = TinyDB(db_path)

        # Collections
        self.reports = self.db.table('reports')
        self.sections = self.db.table('sections')
        self.metadata = self.db.table('metadata')

    def store_report(self, report_data: Dict) -> str:
        """
        Store a complete report.

        Args:
            report_data: Report data dictionary

        Returns:
            Report ID
        """
        # Generate ID if not present
        if 'id' not in report_data:
            report_data['id'] = self._generate_id()

        # Add timestamp
        if 'timestamp' not in report_data:
            report_data['timestamp'] = datetime.now().isoformat()

        # Store in database
        self.reports.insert(report_data)

        # Store sections separately for better search
        if 'sections' in report_data:
            for section in report_data['sections']:
                section_data = {
                    'report_id': report_data['id'],
                    'sport': section.get('sport'),
                    'content': section.get('content'),
                    'metadata': section.get('metadata', {}),
                    'timestamp': report_data['timestamp']
                }
                self.sections.insert(section_data)

        return report_data['id']

    def get_report(self, report_id: str) -> Optional[Dict]:
        """
        Retrieve a report by ID.

        Args:
            report_id: Report ID

        Returns:
            Report data or None
        """
        Report = Query()
        results = self.reports.search(Report.id == report_id)

        if results:
            return results[0]

        return None

    def search_reports(self, filters: Optional[Dict] = None,
                      limit: int = 10) -> List[Dict]:
        """
        Search reports with filters.

        Args:
            filters: Filter criteria (sport, date_range, etc.)
            limit: Maximum number of results

        Returns:
            List of matching reports
        """
        Report = Query()

        if not filters:
            results = self.reports.all()
        else:
            # Build query
            query = self._build_query(Report, filters)
            results = self.reports.search(query)

        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return results[:limit]

    def get_recent_reports(self, days: int = 7, sport: Optional[str] = None) -> List[Dict]:
        """
        Get reports from the last N days.

        Args:
            days: Number of days to look back
            sport: Optional sport filter

        Returns:
            List of recent reports
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        Report = Query()
        query = Report.timestamp >= cutoff_iso

        if sport:
            query = query & (Report.sport == sport)

        results = self.reports.search(query)
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return results

    def get_reports_by_team(self, team: str, limit: int = 10) -> List[Dict]:
        """
        Get reports mentioning a specific team.

        Args:
            team: Team name
            limit: Maximum number of results

        Returns:
            List of reports
        """
        Report = Query()

        # Search in teams array or content
        results = self.reports.search(
            (Report.teams.any([team])) |
            (Report.content.search(team, flags=0))
        )

        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results[:limit]

    def get_reports_by_player(self, player: str, limit: int = 10) -> List[Dict]:
        """
        Get reports mentioning a specific player.

        Args:
            player: Player name
            limit: Maximum number of results

        Returns:
            List of reports
        """
        Report = Query()

        results = self.reports.search(
            (Report.players.any([player])) |
            (Report.content.search(player, flags=0))
        )

        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results[:limit]

    def store_game_data(self, game_data: Dict) -> str:
        """
        Store individual game data.

        Args:
            game_data: Game data dictionary

        Returns:
            Game ID
        """
        if 'id' not in game_data:
            game_data['id'] = self._generate_id('game')

        if 'timestamp' not in game_data:
            game_data['timestamp'] = datetime.now().isoformat()

        games_table = self.db.table('games')
        games_table.insert(game_data)

        return game_data['id']

    def get_game_history(self, team1: str, team2: Optional[str] = None,
                        limit: int = 10) -> List[Dict]:
        """
        Get game history for a team or matchup.

        Args:
            team1: First team
            team2: Second team (optional, for head-to-head)
            limit: Maximum results

        Returns:
            List of games
        """
        games_table = self.db.table('games')
        Game = Query()

        if team2:
            # Head-to-head
            results = games_table.search(
                ((Game.home_team == team1) & (Game.away_team == team2)) |
                ((Game.home_team == team2) & (Game.away_team == team1))
            )
        else:
            # All games for team
            results = games_table.search(
                (Game.home_team == team1) | (Game.away_team == team1)
            )

        results.sort(key=lambda x: x.get('date', ''), reverse=True)
        return results[:limit]

    def update_metadata(self, key: str, value: any):
        """
        Update metadata value.

        Args:
            key: Metadata key
            value: Value to store
        """
        Meta = Query()
        existing = self.metadata.search(Meta.key == key)

        if existing:
            self.metadata.update({'value': value}, Meta.key == key)
        else:
            self.metadata.insert({
                'key': key,
                'value': value,
                'updated_at': datetime.now().isoformat()
            })

    def get_metadata(self, key: str, default=None) -> any:
        """
        Get metadata value.

        Args:
            key: Metadata key
            default: Default value if not found

        Returns:
            Metadata value
        """
        Meta = Query()
        results = self.metadata.search(Meta.key == key)

        if results:
            return results[0].get('value', default)

        return default

    def get_stats(self) -> Dict:
        """
        Get storage statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'total_reports': len(self.reports),
            'total_sections': len(self.sections),
            'total_games': len(self.db.table('games')),
            'oldest_report': self._get_oldest_report_date(),
            'newest_report': self._get_newest_report_date(),
            'storage_dir': self.storage_dir
        }

    def clear_old_reports(self, days: int = 90):
        """
        Clear reports older than specified days.

        Args:
            days: Age threshold in days
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        Report = Query()
        self.reports.remove(Report.timestamp < cutoff_iso)
        self.sections.remove(Report.timestamp < cutoff_iso)

    def _generate_id(self, prefix: str = 'report') -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{prefix}_{timestamp}"

    def _build_query(self, QueryObj, filters: Dict):
        """Build TinyDB query from filters."""
        query = None

        if 'sport' in filters:
            q = QueryObj.sport == filters['sport']
            query = q if query is None else query & q

        if 'date_after' in filters:
            date_str = filters['date_after']
            if isinstance(date_str, datetime):
                date_str = date_str.isoformat()

            q = QueryObj.timestamp >= date_str
            query = q if query is None else query & q

        if 'date_before' in filters:
            date_str = filters['date_before']
            if isinstance(date_str, datetime):
                date_str = date_str.isoformat()

            q = QueryObj.timestamp <= date_str
            query = q if query is None else query & q

        if 'team' in filters:
            q = QueryObj.teams.any([filters['team']])
            query = q if query is None else query & q

        return query if query is not None else QueryObj.id.exists()

    def _get_oldest_report_date(self) -> Optional[str]:
        """Get date of oldest report."""
        all_reports = self.reports.all()

        if not all_reports:
            return None

        dates = [r.get('timestamp') for r in all_reports if r.get('timestamp')]

        if dates:
            return min(dates)

        return None

    def _get_newest_report_date(self) -> Optional[str]:
        """Get date of newest report."""
        all_reports = self.reports.all()

        if not all_reports:
            return None

        dates = [r.get('timestamp') for r in all_reports if r.get('timestamp')]

        if dates:
            return max(dates)

        return None

    def export_to_file(self, filepath: str):
        """
        Export all data to JSON file.

        Args:
            filepath: Output file path
        """
        export_data = {
            'reports': self.reports.all(),
            'sections': self.sections.all(),
            'games': self.db.table('games').all(),
            'metadata': self.metadata.all(),
            'exported_at': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

    def import_from_file(self, filepath: str):
        """
        Import data from JSON file.

        Args:
            filepath: Input file path
        """
        with open(filepath, 'r') as f:
            import_data = json.load(f)

        # Import each table
        if 'reports' in import_data:
            for report in import_data['reports']:
                self.reports.insert(report)

        if 'sections' in import_data:
            for section in import_data['sections']:
                self.sections.insert(section)

        if 'games' in import_data:
            games_table = self.db.table('games')
            for game in import_data['games']:
                games_table.insert(game)

        if 'metadata' in import_data:
            for meta in import_data['metadata']:
                self.metadata.insert(meta)
