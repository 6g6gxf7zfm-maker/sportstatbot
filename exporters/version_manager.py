"""Auto-versioning system with semantic naming for digests."""
import logging
import re
from typing import Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Automatic version management system.

    Features:
    - Semantic versioning (v1.0, v1.1, v2.0)
    - Auto-increment based on changes
    - Version naming: {sport}_Digest_{date}_v{major}.{minor}
    - Version history tracking
    - Rollback support
    """

    def __init__(self, version_file: str = 'versions.json'):
        """
        Initialize version manager.

        Args:
            version_file: Path to version history file
        """
        self.version_file = Path(version_file)
        self.versions: Dict[str, Dict] = self._load_versions()

    def _load_versions(self) -> Dict[str, Dict]:
        """Load version history from file."""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading versions: {e}")
                return {}
        return {}

    def _save_versions(self):
        """Save version history to file."""
        try:
            self.version_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.version_file, 'w') as f:
                json.dump(self.versions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving versions: {e}")

    def get_version_key(self, sport: str, date: str, digest_type: str = 'digest') -> str:
        """
        Generate version key.

        Args:
            sport: Sport identifier
            date: Date string (YYYY-MM-DD)
            digest_type: Type of digest

        Returns:
            Version key string
        """
        return f"{sport}_{digest_type}_{date}"

    def parse_version_name(self, name: str) -> Optional[Dict]:
        """
        Parse version name.

        Args:
            name: Version name (e.g., "NFL_Digest_2025-11-07_v1.2")

        Returns:
            Dictionary with parsed components
        """
        # Pattern: {SPORT}_{TYPE}_{DATE}_v{MAJOR}.{MINOR}
        pattern = r'^([A-Z]+)_(\w+)_(\d{4}-\d{2}-\d{2})_v(\d+)\.(\d+)$'
        match = re.match(pattern, name)

        if match:
            return {
                'sport': match.group(1).lower(),
                'type': match.group(2),
                'date': match.group(3),
                'major': int(match.group(4)),
                'minor': int(match.group(5))
            }

        return None

    def get_current_version(self, sport: str, date: str, digest_type: str = 'digest') -> Tuple[int, int]:
        """
        Get current version for a digest.

        Args:
            sport: Sport identifier
            date: Date string
            digest_type: Type of digest

        Returns:
            Tuple of (major, minor) version numbers
        """
        key = self.get_version_key(sport, date, digest_type)
        version_info = self.versions.get(key, {'major': 1, 'minor': 0})
        return version_info['major'], version_info['minor']

    def increment_version(
        self,
        sport: str,
        date: str,
        digest_type: str = 'digest',
        major: bool = False
    ) -> Tuple[int, int]:
        """
        Increment version number.

        Args:
            sport: Sport identifier
            date: Date string
            digest_type: Type of digest
            major: If True, increment major version, otherwise minor

        Returns:
            New (major, minor) version tuple
        """
        current_major, current_minor = self.get_current_version(sport, date, digest_type)

        if major:
            new_major = current_major + 1
            new_minor = 0
        else:
            new_major = current_major
            new_minor = current_minor + 1

        key = self.get_version_key(sport, date, digest_type)
        self.versions[key] = {
            'major': new_major,
            'minor': new_minor,
            'last_updated': datetime.now().isoformat()
        }
        self._save_versions()

        logger.info(f"Version incremented: {key} v{new_major}.{new_minor}")
        return new_major, new_minor

    def generate_version_name(
        self,
        sport: str,
        date: Optional[str] = None,
        digest_type: str = 'Digest',
        auto_increment: bool = True,
        major: bool = False
    ) -> str:
        """
        Generate versioned name.

        Args:
            sport: Sport identifier
            date: Date string, defaults to today
            digest_type: Type of digest
            auto_increment: If True, auto-increment version
            major: If True, increment major version (only if auto_increment=True)

        Returns:
            Versioned name (e.g., "NFL_Digest_2025-11-07_v1.2")
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        if auto_increment:
            major_ver, minor_ver = self.increment_version(
                sport, date, digest_type.lower(), major
            )
        else:
            major_ver, minor_ver = self.get_current_version(
                sport, date, digest_type.lower()
            )

        name = f"{sport.upper()}_{digest_type}_{date}_v{major_ver}.{minor_ver}"
        logger.info(f"Generated version name: {name}")
        return name

    def get_version_history(
        self,
        sport: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        Get version history.

        Args:
            sport: Filter by sport (None for all)
            limit: Maximum number of records

        Returns:
            List of version records
        """
        history = []

        for key, version_info in self.versions.items():
            parts = key.split('_')
            if len(parts) >= 3:
                record_sport = parts[0]

                if sport is None or record_sport == sport:
                    history.append({
                        'key': key,
                        'sport': record_sport,
                        'version': f"v{version_info['major']}.{version_info['minor']}",
                        'last_updated': version_info.get('last_updated')
                    })

        # Sort by last updated
        history.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        return history[:limit]

    def set_version(
        self,
        sport: str,
        date: str,
        major: int,
        minor: int,
        digest_type: str = 'digest'
    ):
        """
        Manually set version number.

        Args:
            sport: Sport identifier
            date: Date string
            major: Major version number
            minor: Minor version number
            digest_type: Type of digest
        """
        key = self.get_version_key(sport, date, digest_type)
        self.versions[key] = {
            'major': major,
            'minor': minor,
            'last_updated': datetime.now().isoformat()
        }
        self._save_versions()
        logger.info(f"Version set manually: {key} v{major}.{minor}")

    def delete_version(self, sport: str, date: str, digest_type: str = 'digest'):
        """
        Delete version entry.

        Args:
            sport: Sport identifier
            date: Date string
            digest_type: Type of digest
        """
        key = self.get_version_key(sport, date, digest_type)
        if key in self.versions:
            del self.versions[key]
            self._save_versions()
            logger.info(f"Version deleted: {key}")

    def get_latest_versions(self, limit: int = 10) -> list:
        """
        Get latest versions across all digests.

        Args:
            limit: Maximum number of records

        Returns:
            List of latest version records
        """
        records = []

        for key, version_info in self.versions.items():
            parts = key.split('_')
            if len(parts) >= 3:
                records.append({
                    'name': f"{parts[0].upper()}_{parts[1]}_{parts[2]}_v{version_info['major']}.{version_info['minor']}",
                    'sport': parts[0],
                    'type': parts[1],
                    'date': parts[2],
                    'version': f"v{version_info['major']}.{version_info['minor']}",
                    'last_updated': version_info.get('last_updated')
                })

        # Sort by last updated
        records.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        return records[:limit]
