"""Data retention and cleanup policies."""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil


class RetentionPolicy:
    """
    Manages data retention and cleanup policies.
    Configurable retention windows with automatic cleanup.
    """

    def __init__(self, config_file: str = "config/retention_policy.json"):
        """
        Initialize retention policy manager.

        Args:
            config_file: Path to retention configuration
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load retention configuration."""
        default_config = {
            'enabled': True,
            'auto_cleanup': True,
            'cleanup_interval_hours': 24,
            'retention_windows': {
                'cache': {
                    'scoreboard': 7,  # days
                    'standings': 14,
                    'odds': 3,
                    'news': 7
                },
                'reports': {
                    'daily': 30,
                    'monitoring': 30,
                    'backup': 90
                },
                'logs': {
                    'error': 30,
                    'recovery': 30,
                    'validation': 30,
                    'health': 60
                },
                'backups': {
                    'local': 14,
                    'cloud': 90
                }
            },
            'archive_before_delete': True,
            'archive_path': 'archives',
            'min_free_space_mb': 1000  # Minimum free space to maintain
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)

                # Merge configurations
                for key in default_config:
                    if key in custom_config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(custom_config[key])
                        else:
                            default_config[key] = custom_config[key]

                return default_config
            except Exception as e:
                print(f"Error loading retention config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save retention configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving retention config: {e}")

    def cleanup_cache(self, cache_type: Optional[str] = None) -> Dict:
        """
        Cleanup old cache data.

        Args:
            cache_type: Specific cache type to clean (None for all)

        Returns:
            Cleanup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'deleted_files': 0,
            'freed_space_mb': 0,
            'archived_files': 0,
            'details': {}
        }

        if not self.config['enabled']:
            results['message'] = 'Retention policy disabled'
            return results

        cache_base = Path('cache')

        if not cache_base.exists():
            results['message'] = 'Cache directory not found'
            return results

        # Get retention windows for cache
        cache_retention = self.config['retention_windows']['cache']

        # Determine which cache types to clean
        if cache_type:
            cache_types = {cache_type: cache_retention.get(cache_type, 7)}
        else:
            cache_types = cache_retention

        for c_type, retention_days in cache_types.items():
            cache_dir = cache_base / f"{c_type}s"  # e.g., cache/scoreboards

            if not cache_dir.exists():
                continue

            deleted, freed, archived = self._cleanup_directory(
                cache_dir,
                retention_days,
                f"cache/{c_type}"
            )

            results['deleted_files'] += deleted
            results['freed_space_mb'] += freed
            results['archived_files'] += archived
            results['details'][c_type] = {
                'deleted': deleted,
                'freed_mb': freed,
                'archived': archived
            }

        return results

    def cleanup_reports(self, report_type: Optional[str] = None) -> Dict:
        """
        Cleanup old reports.

        Args:
            report_type: Specific report type to clean (None for all)

        Returns:
            Cleanup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'deleted_files': 0,
            'freed_space_mb': 0,
            'archived_files': 0,
            'details': {}
        }

        if not self.config['enabled']:
            results['message'] = 'Retention policy disabled'
            return results

        reports_base = Path('reports')

        if not reports_base.exists():
            results['message'] = 'Reports directory not found'
            return results

        # Get retention windows for reports
        report_retention = self.config['retention_windows']['reports']

        # Determine which report types to clean
        if report_type:
            report_types = {report_type: report_retention.get(report_type, 30)}
        else:
            report_types = report_retention

        for r_type, retention_days in report_types.items():
            report_dir = reports_base / r_type

            if not report_dir.exists():
                continue

            deleted, freed, archived = self._cleanup_directory(
                report_dir,
                retention_days,
                f"reports/{r_type}"
            )

            results['deleted_files'] += deleted
            results['freed_space_mb'] += freed
            results['archived_files'] += archived
            results['details'][r_type] = {
                'deleted': deleted,
                'freed_mb': freed,
                'archived': archived
            }

        return results

    def cleanup_logs(self, log_type: Optional[str] = None) -> Dict:
        """
        Cleanup old log files.

        Args:
            log_type: Specific log type to clean (None for all)

        Returns:
            Cleanup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'deleted_files': 0,
            'freed_space_mb': 0,
            'archived_files': 0,
            'details': {}
        }

        if not self.config['enabled']:
            results['message'] = 'Retention policy disabled'
            return results

        logs_base = Path('logs')

        if not logs_base.exists():
            results['message'] = 'Logs directory not found'
            return results

        # Get retention windows for logs
        log_retention = self.config['retention_windows']['logs']

        # Determine which log types to clean
        if log_type:
            log_types = {log_type: log_retention.get(log_type, 30)}
        else:
            log_types = log_retention

        for l_type, retention_days in log_types.items():
            log_file = logs_base / f"{l_type}.json"

            if log_file.exists():
                # For JSON logs, clean entries within the file
                deleted = self._cleanup_json_log(log_file, retention_days)
                results['details'][l_type] = {'entries_removed': deleted}

        return results

    def cleanup_backups(self, location: str = 'local') -> Dict:
        """
        Cleanup old backups.

        Args:
            location: Backup location ('local' or 'cloud')

        Returns:
            Cleanup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'deleted_files': 0,
            'freed_space_mb': 0,
            'details': {}
        }

        if not self.config['enabled']:
            results['message'] = 'Retention policy disabled'
            return results

        if location != 'local':
            results['message'] = f'Cloud backup cleanup not implemented for {location}'
            return results

        backups_dir = Path('backups')

        if not backups_dir.exists():
            results['message'] = 'Backups directory not found'
            return results

        retention_days = self.config['retention_windows']['backups']['local']

        deleted, freed, archived = self._cleanup_directory(
            backups_dir,
            retention_days,
            'backups',
            archive=False  # Don't archive backups
        )

        results['deleted_files'] = deleted
        results['freed_space_mb'] = freed
        results['details']['local'] = {
            'deleted': deleted,
            'freed_mb': freed
        }

        return results

    def _cleanup_directory(self, directory: Path, retention_days: int,
                          category: str, archive: bool = None) -> tuple:
        """
        Cleanup files in a directory based on retention policy.

        Args:
            directory: Directory to clean
            retention_days: Days to retain files
            category: Category name for logging
            archive: Whether to archive before delete (None = use config)

        Returns:
            Tuple of (deleted_count, freed_mb, archived_count)
        """
        if archive is None:
            archive = self.config['archive_before_delete']

        cutoff_date = datetime.now() - timedelta(days=retention_days)

        deleted_count = 0
        freed_mb = 0.0
        archived_count = 0

        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue

            # Check file age
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            if file_mtime < cutoff_date:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)

                # Archive if enabled
                if archive:
                    if self._archive_file(file_path, category):
                        archived_count += 1

                # Delete file
                try:
                    file_path.unlink()
                    deleted_count += 1
                    freed_mb += file_size_mb
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

        return deleted_count, freed_mb, archived_count

    def _archive_file(self, file_path: Path, category: str) -> bool:
        """
        Archive a file before deletion.

        Args:
            file_path: File to archive
            category: Archive category

        Returns:
            True if successful
        """
        try:
            archive_base = Path(self.config['archive_path'])
            archive_dir = archive_base / category
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Create archive filename with date
            archive_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d')}{file_path.suffix}"
            archive_path = archive_dir / archive_name

            # Copy file to archive
            shutil.copy2(file_path, archive_path)

            return True

        except Exception as e:
            print(f"Error archiving {file_path}: {e}")
            return False

    def _cleanup_json_log(self, log_file: Path, retention_days: int) -> int:
        """
        Clean entries from a JSON log file.

        Args:
            log_file: Path to JSON log file
            retention_days: Days to retain entries

        Returns:
            Number of entries removed
        """
        try:
            with open(log_file, 'r') as f:
                entries = json.load(f)

            if not isinstance(entries, list):
                return 0

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            original_count = len(entries)

            # Filter entries
            filtered_entries = [
                entry for entry in entries
                if datetime.fromisoformat(entry.get('timestamp', '2000-01-01')) > cutoff_date
            ]

            # Write back filtered entries
            with open(log_file, 'w') as f:
                json.dump(filtered_entries, f, indent=2)

            return original_count - len(filtered_entries)

        except Exception as e:
            print(f"Error cleaning log {log_file}: {e}")
            return 0

    def cleanup_all(self) -> Dict:
        """
        Run cleanup for all categories.

        Returns:
            Combined cleanup results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'cache': self.cleanup_cache(),
            'reports': self.cleanup_reports(),
            'logs': self.cleanup_logs(),
            'backups': self.cleanup_backups()
        }

        # Calculate totals
        results['total_deleted_files'] = sum(
            r.get('deleted_files', 0) for r in results.values()
            if isinstance(r, dict)
        )

        results['total_freed_mb'] = sum(
            r.get('freed_space_mb', 0) for r in results.values()
            if isinstance(r, dict)
        )

        return results

    def generate_retention_report(self) -> str:
        """Generate retention policy status report."""
        report = []

        report.append("=" * 60)
        report.append("🗂️ DATA RETENTION POLICY")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        report.append("⚙️ Configuration:")
        report.append(f"  Enabled: {'✅' if self.config['enabled'] else '❌'}")
        report.append(f"  Auto Cleanup: {'✅' if self.config['auto_cleanup'] else '❌'}")
        report.append(f"  Cleanup Interval: {self.config['cleanup_interval_hours']} hours")
        report.append(f"  Archive Before Delete: {'✅' if self.config['archive_before_delete'] else '❌'}")
        report.append("")

        report.append("📋 Retention Windows:")

        for category, items in self.config['retention_windows'].items():
            report.append(f"\n  {category.title()}:")
            for item_name, days in items.items():
                report.append(f"    {item_name}: {days} days")

        # Disk space check
        report.append("\n💾 Disk Space:")
        total, used, free = shutil.disk_usage("/")
        free_mb = free // (1024 * 1024)
        min_free = self.config['min_free_space_mb']

        status = '✅' if free_mb > min_free else '⚠️'
        report.append(f"  {status} Free Space: {free_mb:,} MB")
        report.append(f"  Minimum Required: {min_free:,} MB")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
