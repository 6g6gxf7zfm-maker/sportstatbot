"""Rolling backup manager for Google Drive, iCloud, and local storage."""
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json


class BackupManager:
    """
    Manages rolling backups to multiple destinations:
    - Local backups
    - Google Drive (requires google-api-python-client)
    - iCloud (via iCloud Drive folder sync)
    - Cloud storage (S3, GCS via CloudStorageSync)
    """

    def __init__(self, backup_dir: str = "backups",
                 retention_days: int = 7,
                 max_backups: int = 14):
        """
        Initialize backup manager.

        Args:
            backup_dir: Directory for local backups
            retention_days: Days to retain backups
            max_backups: Maximum number of backups to keep
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

        self.retention_days = retention_days
        self.max_backups = max_backups

        # Backup configuration
        self.config_file = self.backup_dir / "backup_config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load backup configuration."""
        default_config = {
            'enabled': True,
            'local_enabled': True,
            'google_drive_enabled': False,
            'google_drive_folder_id': '',
            'icloud_enabled': False,
            'icloud_path': os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/SportStatBot'),
            'include_patterns': [
                'cache/**/*',
                'reports/**/*',
                'monitoring/**/*',
                'config/**/*',
                '*.json'
            ],
            'exclude_patterns': [
                '__pycache__',
                '*.pyc',
                '.git',
                'backups'
            ]
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)
                return {**default_config, **custom_config}
            except Exception as e:
                print(f"Error loading backup config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save backup configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving backup config: {e}")

    def create_backup(self, name: Optional[str] = None,
                     include_data: bool = True,
                     include_reports: bool = True,
                     include_config: bool = True) -> Optional[str]:
        """
        Create a backup archive.

        Args:
            name: Optional backup name (auto-generated if None)
            include_data: Include cached data
            include_reports: Include generated reports
            include_config: Include configuration files

        Returns:
            Path to backup file or None if failed
        """
        if not self.config['enabled']:
            print("Backups are disabled in configuration")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = name or f"sportstatbot_backup_{timestamp}"
        backup_file = self.backup_dir / f"{backup_name}.zip"

        try:
            print(f"📦 Creating backup: {backup_name}")

            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Determine what to include
                directories_to_backup = []

                if include_data:
                    directories_to_backup.append('cache')

                if include_reports:
                    directories_to_backup.extend(['reports', 'monitoring'])

                if include_config:
                    directories_to_backup.append('config')

                # Add files to backup
                for directory in directories_to_backup:
                    dir_path = Path(directory)
                    if dir_path.exists():
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                # Check exclusions
                                if self._should_exclude(file_path):
                                    continue

                                arcname = str(file_path)
                                zipf.write(file_path, arcname)

                # Add metadata
                metadata = {
                    'backup_name': backup_name,
                    'timestamp': timestamp,
                    'included_data': include_data,
                    'included_reports': include_reports,
                    'included_config': include_config,
                    'created_at': datetime.now().isoformat()
                }

                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

            # Get file size
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            print(f"✅ Backup created: {backup_file.name} ({size_mb:.2f} MB)")

            # Sync to cloud if enabled
            self._sync_to_cloud_destinations(backup_file)

            # Cleanup old backups
            self._cleanup_old_backups()

            return str(backup_file)

        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from backup."""
        for pattern in self.config['exclude_patterns']:
            if pattern in str(file_path):
                return True
        return False

    def _sync_to_cloud_destinations(self, backup_file: Path) -> None:
        """Sync backup to configured cloud destinations."""
        # Google Drive
        if self.config['google_drive_enabled']:
            try:
                self._upload_to_google_drive(backup_file)
            except Exception as e:
                print(f"⚠️ Google Drive sync failed: {e}")

        # iCloud
        if self.config['icloud_enabled']:
            try:
                self._copy_to_icloud(backup_file)
            except Exception as e:
                print(f"⚠️ iCloud sync failed: {e}")

    def _upload_to_google_drive(self, backup_file: Path) -> None:
        """
        Upload backup to Google Drive.
        Requires google-api-python-client library.
        """
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials

            # This is a placeholder - actual implementation requires:
            # 1. OAuth2 credentials setup
            # 2. Google Drive API enabled
            # 3. credentials.json file

            print("ℹ️ Google Drive upload requires OAuth setup (see documentation)")
            print("   For now, backups are stored locally only")

            # Actual upload code (when credentials are configured):
            # creds = Credentials.from_authorized_user_file('credentials.json')
            # service = build('drive', 'v3', credentials=creds)
            # file_metadata = {'name': backup_file.name}
            # if self.config['google_drive_folder_id']:
            #     file_metadata['parents'] = [self.config['google_drive_folder_id']]
            # media = MediaFileUpload(str(backup_file), resumable=True)
            # service.files().create(body=file_metadata, media_body=media).execute()

        except ImportError:
            print("ℹ️ google-api-python-client not installed. Install with:")
            print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        except Exception as e:
            raise Exception(f"Google Drive upload error: {e}")

    def _copy_to_icloud(self, backup_file: Path) -> None:
        """Copy backup to iCloud Drive folder."""
        icloud_path = Path(self.config['icloud_path'])

        if not icloud_path.exists():
            print(f"ℹ️ Creating iCloud backup directory: {icloud_path}")
            icloud_path.mkdir(parents=True, exist_ok=True)

        destination = icloud_path / backup_file.name

        try:
            shutil.copy2(backup_file, destination)
            print(f"✅ Copied to iCloud: {destination}")
        except Exception as e:
            raise Exception(f"iCloud copy error: {e}")

    def restore_backup(self, backup_file: str, target_dir: str = ".") -> bool:
        """
        Restore from a backup archive.

        Args:
            backup_file: Path to backup zip file
            target_dir: Directory to restore to

        Returns:
            True if successful
        """
        backup_path = Path(backup_file)

        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_file}")
            return False

        try:
            print(f"📦 Restoring from backup: {backup_path.name}")

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Read metadata
                if 'backup_metadata.json' in zipf.namelist():
                    metadata = json.loads(zipf.read('backup_metadata.json'))
                    print(f"   Backup created: {metadata.get('created_at', 'unknown')}")

                # Extract all files
                zipf.extractall(target_dir)

            print(f"✅ Backup restored to: {target_dir}")
            return True

        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False

    def list_backups(self, location: str = "local") -> List[Dict]:
        """
        List available backups.

        Args:
            location: Backup location ('local', 'icloud', 'gdrive')

        Returns:
            List of backup info dictionaries
        """
        backups = []

        if location == "local":
            for backup_file in self.backup_dir.glob("*.zip"):
                backups.append(self._get_backup_info(backup_file))

        elif location == "icloud":
            icloud_path = Path(self.config['icloud_path'])
            if icloud_path.exists():
                for backup_file in icloud_path.glob("*.zip"):
                    backups.append(self._get_backup_info(backup_file))

        # Sort by date, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)

        return backups

    def _get_backup_info(self, backup_file: Path) -> Dict:
        """Get information about a backup file."""
        stat = backup_file.stat()

        info = {
            'name': backup_file.name,
            'path': str(backup_file),
            'size_mb': stat.st_size / (1024 * 1024),
            'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }

        # Try to read metadata
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                if 'backup_metadata.json' in zipf.namelist():
                    metadata = json.loads(zipf.read('backup_metadata.json'))
                    info['metadata'] = metadata
        except:
            pass

        return info

    def _cleanup_old_backups(self) -> int:
        """
        Remove old backups based on retention policy.

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()

        # Remove backups older than retention period
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0

        for backup in backups:
            backup_date = datetime.fromisoformat(backup['created'])

            # Delete if older than retention OR if we have too many backups
            should_delete = (
                backup_date < cutoff_date or
                len(backups) - deleted_count > self.max_backups
            )

            if should_delete:
                try:
                    Path(backup['path']).unlink()
                    deleted_count += 1
                    print(f"🗑️ Deleted old backup: {backup['name']}")
                except Exception as e:
                    print(f"Error deleting backup: {e}")

        return deleted_count

    def generate_backup_report(self) -> str:
        """Generate backup status report."""
        report = []

        report.append("=" * 60)
        report.append("💾 BACKUP STATUS REPORT")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        # Configuration
        report.append("📋 Configuration:")
        report.append(f"  Enabled: {'✅' if self.config['enabled'] else '❌'}")
        report.append(f"  Retention: {self.retention_days} days")
        report.append(f"  Max Backups: {self.max_backups}")
        report.append(f"  Google Drive: {'✅' if self.config['google_drive_enabled'] else '❌'}")
        report.append(f"  iCloud: {'✅' if self.config['icloud_enabled'] else '❌'}")
        report.append("")

        # Local backups
        local_backups = self.list_backups("local")
        report.append(f"💾 Local Backups: {len(local_backups)}")

        if local_backups:
            total_size = sum(b['size_mb'] for b in local_backups)
            report.append(f"  Total Size: {total_size:.2f} MB")
            report.append(f"  Newest: {local_backups[0]['name']}")
            report.append(f"  Created: {datetime.fromisoformat(local_backups[0]['created']).strftime('%Y-%m-%d %H:%M')}")

        report.append("")

        # iCloud backups
        if self.config['icloud_enabled']:
            icloud_backups = self.list_backups("icloud")
            report.append(f"☁️ iCloud Backups: {len(icloud_backups)}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
