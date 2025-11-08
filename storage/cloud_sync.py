"""Cloud storage synchronization for AWS S3 and Google Cloud Storage."""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


class CloudStorageSync:
    """
    Manages synchronization with cloud storage providers:
    - AWS S3
    - Google Cloud Storage (GCS)
    - Configurable retention and archival
    """

    def __init__(self, config_file: str = "config/cloud_storage.json"):
        """
        Initialize cloud storage sync.

        Args:
            config_file: Path to cloud storage configuration
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load cloud storage configuration."""
        default_config = {
            's3': {
                'enabled': False,
                'bucket_name': '',
                'region': 'us-east-1',
                'prefix': 'sportstatbot/',
                'access_key_id': '',  # Or use IAM roles
                'secret_access_key': ''
            },
            'gcs': {
                'enabled': False,
                'bucket_name': '',
                'project_id': '',
                'prefix': 'sportstatbot/',
                'credentials_file': ''  # Path to service account JSON
            },
            'sync_settings': {
                'auto_sync': False,
                'sync_interval_hours': 24,
                'retention_days': 30,
                'include_cache': False,
                'include_reports': True,
                'include_backups': True
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)

                # Merge configs
                for key in default_config:
                    if key in custom_config:
                        default_config[key].update(custom_config[key])

                return default_config
            except Exception as e:
                print(f"Error loading cloud storage config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save cloud storage configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving cloud storage config: {e}")

    def sync_to_s3(self, local_path: str, s3_key: Optional[str] = None) -> bool:
        """
        Sync file or directory to AWS S3.

        Args:
            local_path: Local file or directory path
            s3_key: S3 object key (auto-generated if None)

        Returns:
            True if successful
        """
        if not self.config['s3']['enabled']:
            print("S3 sync is disabled in configuration")
            return False

        try:
            import boto3
            from botocore.exceptions import ClientError

            # Initialize S3 client
            s3_config = self.config['s3']

            if s3_config['access_key_id'] and s3_config['secret_access_key']:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=s3_config['access_key_id'],
                    aws_secret_access_key=s3_config['secret_access_key'],
                    region_name=s3_config['region']
                )
            else:
                # Use IAM roles or AWS credentials file
                s3_client = boto3.client('s3', region_name=s3_config['region'])

            bucket_name = s3_config['bucket_name']
            prefix = s3_config['prefix']

            local_path_obj = Path(local_path)

            if local_path_obj.is_file():
                # Upload single file
                s3_key = s3_key or f"{prefix}{local_path_obj.name}"

                print(f"📤 Uploading to S3: {local_path_obj.name}")

                s3_client.upload_file(
                    str(local_path_obj),
                    bucket_name,
                    s3_key
                )

                print(f"✅ Uploaded to s3://{bucket_name}/{s3_key}")
                return True

            elif local_path_obj.is_dir():
                # Upload directory
                uploaded_count = 0

                for file_path in local_path_obj.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(local_path_obj)
                        s3_key = f"{prefix}{relative_path}"

                        s3_client.upload_file(
                            str(file_path),
                            bucket_name,
                            s3_key
                        )
                        uploaded_count += 1

                print(f"✅ Uploaded {uploaded_count} files to S3")
                return True

            else:
                print(f"❌ Path not found: {local_path}")
                return False

        except ImportError:
            print("❌ boto3 not installed. Install with: pip install boto3")
            return False

        except ClientError as e:
            print(f"❌ S3 error: {e}")
            return False

        except Exception as e:
            print(f"❌ Error syncing to S3: {e}")
            return False

    def sync_to_gcs(self, local_path: str, gcs_key: Optional[str] = None) -> bool:
        """
        Sync file or directory to Google Cloud Storage.

        Args:
            local_path: Local file or directory path
            gcs_key: GCS object key (auto-generated if None)

        Returns:
            True if successful
        """
        if not self.config['gcs']['enabled']:
            print("GCS sync is disabled in configuration")
            return False

        try:
            from google.cloud import storage
            from google.oauth2 import service_account

            # Initialize GCS client
            gcs_config = self.config['gcs']

            if gcs_config['credentials_file']:
                credentials = service_account.Credentials.from_service_account_file(
                    gcs_config['credentials_file']
                )
                client = storage.Client(
                    project=gcs_config['project_id'],
                    credentials=credentials
                )
            else:
                # Use default credentials
                client = storage.Client(project=gcs_config['project_id'])

            bucket = client.bucket(gcs_config['bucket_name'])
            prefix = gcs_config['prefix']

            local_path_obj = Path(local_path)

            if local_path_obj.is_file():
                # Upload single file
                gcs_key = gcs_key or f"{prefix}{local_path_obj.name}"

                print(f"📤 Uploading to GCS: {local_path_obj.name}")

                blob = bucket.blob(gcs_key)
                blob.upload_from_filename(str(local_path_obj))

                print(f"✅ Uploaded to gs://{gcs_config['bucket_name']}/{gcs_key}")
                return True

            elif local_path_obj.is_dir():
                # Upload directory
                uploaded_count = 0

                for file_path in local_path_obj.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(local_path_obj)
                        gcs_key = f"{prefix}{relative_path}"

                        blob = bucket.blob(gcs_key)
                        blob.upload_from_filename(str(file_path))
                        uploaded_count += 1

                print(f"✅ Uploaded {uploaded_count} files to GCS")
                return True

            else:
                print(f"❌ Path not found: {local_path}")
                return False

        except ImportError:
            print("❌ google-cloud-storage not installed. Install with: pip install google-cloud-storage")
            return False

        except Exception as e:
            print(f"❌ Error syncing to GCS: {e}")
            return False

    def sync_all_backups(self) -> Dict:
        """
        Sync all configured items to cloud storage.

        Returns:
            Sync results dictionary
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            's3_synced': False,
            'gcs_synced': False,
            'items_synced': [],
            'errors': []
        }

        settings = self.config['sync_settings']

        # Determine what to sync
        items_to_sync = []

        if settings['include_backups'] and Path('backups').exists():
            items_to_sync.append('backups')

        if settings['include_reports'] and Path('reports').exists():
            items_to_sync.append('reports')

        if settings['include_cache'] and Path('cache').exists():
            items_to_sync.append('cache')

        # Sync to S3
        if self.config['s3']['enabled']:
            try:
                for item in items_to_sync:
                    if self.sync_to_s3(item):
                        results['items_synced'].append(f"s3:{item}")
                results['s3_synced'] = True
            except Exception as e:
                results['errors'].append(f"S3: {str(e)}")

        # Sync to GCS
        if self.config['gcs']['enabled']:
            try:
                for item in items_to_sync:
                    if self.sync_to_gcs(item):
                        results['items_synced'].append(f"gcs:{item}")
                results['gcs_synced'] = True
            except Exception as e:
                results['errors'].append(f"GCS: {str(e)}")

        return results

    def download_from_s3(self, s3_key: str, local_path: str) -> bool:
        """
        Download file from S3.

        Args:
            s3_key: S3 object key
            local_path: Local path to save to

        Returns:
            True if successful
        """
        if not self.config['s3']['enabled']:
            print("S3 is disabled in configuration")
            return False

        try:
            import boto3

            s3_config = self.config['s3']

            if s3_config['access_key_id'] and s3_config['secret_access_key']:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=s3_config['access_key_id'],
                    aws_secret_access_key=s3_config['secret_access_key'],
                    region_name=s3_config['region']
                )
            else:
                s3_client = boto3.client('s3', region_name=s3_config['region'])

            bucket_name = s3_config['bucket_name']

            print(f"📥 Downloading from S3: {s3_key}")

            # Create parent directory if needed
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            s3_client.download_file(bucket_name, s3_key, local_path)

            print(f"✅ Downloaded to: {local_path}")
            return True

        except Exception as e:
            print(f"❌ Error downloading from S3: {e}")
            return False

    def list_s3_backups(self) -> List[str]:
        """
        List available backups in S3.

        Returns:
            List of S3 object keys
        """
        if not self.config['s3']['enabled']:
            return []

        try:
            import boto3

            s3_config = self.config['s3']

            if s3_config['access_key_id'] and s3_config['secret_access_key']:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=s3_config['access_key_id'],
                    aws_secret_access_key=s3_config['secret_access_key'],
                    region_name=s3_config['region']
                )
            else:
                s3_client = boto3.client('s3', region_name=s3_config['region'])

            bucket_name = s3_config['bucket_name']
            prefix = s3_config['prefix']

            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )

            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]

            return []

        except Exception as e:
            print(f"Error listing S3 backups: {e}")
            return []

    def generate_sync_report(self) -> str:
        """Generate cloud sync status report."""
        report = []

        report.append("=" * 60)
        report.append("☁️ CLOUD STORAGE SYNC STATUS")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        # S3 Status
        s3_config = self.config['s3']
        report.append("📦 AWS S3:")
        report.append(f"  Enabled: {'✅' if s3_config['enabled'] else '❌'}")

        if s3_config['enabled']:
            report.append(f"  Bucket: {s3_config['bucket_name']}")
            report.append(f"  Region: {s3_config['region']}")
            report.append(f"  Prefix: {s3_config['prefix']}")

            # List backups
            backups = self.list_s3_backups()
            report.append(f"  Files in S3: {len(backups)}")

        report.append("")

        # GCS Status
        gcs_config = self.config['gcs']
        report.append("📦 Google Cloud Storage:")
        report.append(f"  Enabled: {'✅' if gcs_config['enabled'] else '❌'}")

        if gcs_config['enabled']:
            report.append(f"  Bucket: {gcs_config['bucket_name']}")
            report.append(f"  Project: {gcs_config['project_id']}")
            report.append(f"  Prefix: {gcs_config['prefix']}")

        report.append("")

        # Sync Settings
        sync_settings = self.config['sync_settings']
        report.append("⚙️ Sync Settings:")
        report.append(f"  Auto Sync: {'✅' if sync_settings['auto_sync'] else '❌'}")
        report.append(f"  Interval: {sync_settings['sync_interval_hours']} hours")
        report.append(f"  Retention: {sync_settings['retention_days']} days")
        report.append(f"  Include Cache: {'✅' if sync_settings['include_cache'] else '❌'}")
        report.append(f"  Include Reports: {'✅' if sync_settings['include_reports'] else '❌'}")
        report.append(f"  Include Backups: {'✅' if sync_settings['include_backups'] else '❌'}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
