"""Auto-cleanup manager for archiving old documents."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import json

logger = logging.getLogger(__name__)


class CleanupManager:
    """
    Automatic cleanup and archiving system.

    Features:
    - Archive old documents based on age
    - Configurable retention policies per sport/type
    - Automatic folder organization
    - Cleanup history tracking
    - Safe deletion with archive backup
    """

    def __init__(
        self,
        archive_dir: str = 'reports/archive',
        cleanup_log: str = 'cleanup_log.json'
    ):
        """
        Initialize cleanup manager.

        Args:
            archive_dir: Directory for archived files
            cleanup_log: Path to cleanup history log
        """
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_log = Path(cleanup_log)
        self.cleanup_history: List[Dict] = self._load_cleanup_log()

        # Default retention policies (in days)
        self.retention_policies = {
            'nfl': 30,
            'nba': 30,
            'mlb': 30,
            'nhl': 30,
            'mls': 14,
            'soccer': 14,
            'golf': 14,
            'default': 21
        }

    def _load_cleanup_log(self) -> List[Dict]:
        """Load cleanup history from log file."""
        if self.cleanup_log.exists():
            try:
                with open(self.cleanup_log, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cleanup log: {e}")
                return []
        return []

    def _save_cleanup_log(self):
        """Save cleanup history to log file."""
        try:
            self.cleanup_log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cleanup_log, 'w') as f:
                json.dump(self.cleanup_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cleanup log: {e}")

    def set_retention_policy(self, sport: str, days: int):
        """
        Set retention policy for a sport.

        Args:
            sport: Sport identifier
            days: Number of days to retain files
        """
        self.retention_policies[sport] = days
        logger.info(f"Retention policy set for {sport}: {days} days")

    def get_retention_days(self, sport: str) -> int:
        """
        Get retention days for a sport.

        Args:
            sport: Sport identifier

        Returns:
            Number of days to retain files
        """
        return self.retention_policies.get(sport, self.retention_policies['default'])

    def should_archive(self, file_path: Path, sport: str) -> bool:
        """
        Check if a file should be archived.

        Args:
            file_path: Path to file
            sport: Sport identifier

        Returns:
            True if file should be archived
        """
        if not file_path.exists():
            return False

        # Get file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_days = (datetime.now() - mtime).days

        retention_days = self.get_retention_days(sport)
        return age_days > retention_days

    def archive_file(self, file_path: Path, sport: str, preserve_original: bool = False) -> bool:
        """
        Archive a file.

        Args:
            file_path: Path to file to archive
            sport: Sport identifier
            preserve_original: If True, copy instead of move

        Returns:
            True if successful
        """
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            # Create sport-specific archive directory
            sport_archive = self.archive_dir / sport.upper()
            sport_archive.mkdir(parents=True, exist_ok=True)

            # Generate archive filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archive_path = sport_archive / archive_name

            # Copy or move file
            if preserve_original:
                shutil.copy2(file_path, archive_path)
                operation = 'copied'
            else:
                shutil.move(str(file_path), archive_path)
                operation = 'moved'

            logger.info(f"File {operation} to archive: {file_path} -> {archive_path}")

            # Log cleanup action
            self.cleanup_history.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'original_path': str(file_path),
                'archive_path': str(archive_path),
                'sport': sport
            })
            self._save_cleanup_log()

            return True

        except Exception as e:
            logger.error(f"Error archiving file: {e}")
            return False

    def cleanup_directory(
        self,
        directory: Path,
        sport: str,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Clean up old files in a directory.

        Args:
            directory: Directory to clean
            sport: Sport identifier
            dry_run: If True, only report what would be done

        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            'scanned': 0,
            'archived': 0,
            'failed': 0,
            'skipped': 0
        }

        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return stats

        # Find files to archive
        for file_path in directory.glob('**/*'):
            if file_path.is_file():
                stats['scanned'] += 1

                if self.should_archive(file_path, sport):
                    if dry_run:
                        logger.info(f"[DRY RUN] Would archive: {file_path}")
                        stats['archived'] += 1
                    else:
                        if self.archive_file(file_path, sport):
                            stats['archived'] += 1
                        else:
                            stats['failed'] += 1
                else:
                    stats['skipped'] += 1

        logger.info(f"Cleanup completed for {directory}: {stats}")
        return stats

    def cleanup_all_sports(
        self,
        base_directory: Path,
        dry_run: bool = False
    ) -> Dict[str, Dict]:
        """
        Clean up files for all sports.

        Args:
            base_directory: Base directory containing sport subdirectories
            dry_run: If True, only report what would be done

        Returns:
            Dictionary with cleanup statistics per sport
        """
        all_stats = {}

        for sport in self.retention_policies.keys():
            if sport == 'default':
                continue

            sport_dir = base_directory / sport.upper()
            if sport_dir.exists():
                logger.info(f"Cleaning up {sport.upper()} directory...")
                stats = self.cleanup_directory(sport_dir, sport, dry_run)
                all_stats[sport] = stats

        return all_stats

    def restore_from_archive(self, archive_path: Path, restore_path: Path) -> bool:
        """
        Restore a file from archive.

        Args:
            archive_path: Path to archived file
            restore_path: Path to restore file to

        Returns:
            True if successful
        """
        if not archive_path.exists():
            logger.error(f"Archive file not found: {archive_path}")
            return False

        try:
            restore_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archive_path, restore_path)

            logger.info(f"File restored from archive: {archive_path} -> {restore_path}")

            # Log restore action
            self.cleanup_history.append({
                'timestamp': datetime.now().isoformat(),
                'operation': 'restored',
                'archive_path': str(archive_path),
                'restore_path': str(restore_path)
            })
            self._save_cleanup_log()

            return True

        except Exception as e:
            logger.error(f"Error restoring file: {e}")
            return False

    def list_archived_files(self, sport: Optional[str] = None) -> List[Dict]:
        """
        List archived files.

        Args:
            sport: Filter by sport (None for all)

        Returns:
            List of archived file info
        """
        archived_files = []

        search_dirs = []
        if sport:
            search_dirs.append(self.archive_dir / sport.upper())
        else:
            search_dirs.append(self.archive_dir)

        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.glob('**/*'):
                    if file_path.is_file():
                        archived_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'sport': file_path.parent.name.lower(),
                            'size': file_path.stat().st_size,
                            'archived_at': datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat()
                        })

        return archived_files

    def get_cleanup_statistics(self) -> Dict:
        """
        Get cleanup statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_actions': len(self.cleanup_history),
            'by_operation': {},
            'by_sport': {}
        }

        for action in self.cleanup_history:
            operation = action.get('operation', 'unknown')
            sport = action.get('sport', 'unknown')

            stats['by_operation'][operation] = stats['by_operation'].get(operation, 0) + 1
            stats['by_sport'][sport] = stats['by_sport'].get(sport, 0) + 1

        return stats

    def delete_old_archives(self, days: int = 90) -> int:
        """
        Permanently delete very old archived files.

        Args:
            days: Delete archives older than this many days

        Returns:
            Number of files deleted
        """
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=days)

        for file_path in self.archive_dir.glob('**/*'):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old archive: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting archive: {e}")

        return deleted_count
