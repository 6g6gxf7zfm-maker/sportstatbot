"""Incremental caching system for sports data."""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class CacheManager:
    """
    Manages incremental caching of sports data.
    Stores last 7 days of diffs to minimize API calls and storage.
    """

    def __init__(self, cache_dir: str = "cache", retention_days: int = 7):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            retention_days: Number of days to retain cache data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.retention_days = retention_days

        # Create subdirectories for different data types
        self.scoreboard_cache = self.cache_dir / "scoreboards"
        self.standings_cache = self.cache_dir / "standings"
        self.odds_cache = self.cache_dir / "odds"
        self.metadata_cache = self.cache_dir / "metadata"

        for cache_path in [self.scoreboard_cache, self.standings_cache,
                          self.odds_cache, self.metadata_cache]:
            cache_path.mkdir(exist_ok=True)

    def _get_cache_key(self, sport: str, data_type: str, date: datetime) -> str:
        """Generate cache key for data."""
        date_str = date.strftime('%Y%m%d')
        return f"{sport}_{data_type}_{date_str}"

    def _get_cache_path(self, data_type: str, cache_key: str) -> Path:
        """Get file path for cache entry."""
        cache_dirs = {
            'scoreboard': self.scoreboard_cache,
            'standings': self.standings_cache,
            'odds': self.odds_cache,
            'metadata': self.metadata_cache
        }
        cache_dir = cache_dirs.get(data_type, self.cache_dir)
        return cache_dir / f"{cache_key}.json"

    def get(self, sport: str, data_type: str, max_age_hours: int = 1) -> Optional[Dict]:
        """
        Retrieve cached data if fresh enough.

        Args:
            sport: Sport identifier (nfl, nba, etc.)
            data_type: Type of data (scoreboard, standings, odds)
            max_age_hours: Maximum age of cache in hours

        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(sport, data_type, datetime.now())
        cache_path = self._get_cache_path(data_type, cache_key)

        if not cache_path.exists():
            return None

        # Check if cache is fresh
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if cache_age > timedelta(hours=max_age_hours):
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return data.get('data')
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None

    def set(self, sport: str, data_type: str, data: Dict) -> bool:
        """
        Store data in cache with metadata.

        Args:
            sport: Sport identifier
            data_type: Type of data
            data: Data to cache

        Returns:
            True if successful
        """
        cache_key = self._get_cache_key(sport, data_type, datetime.now())
        cache_path = self._get_cache_path(data_type, cache_key)

        try:
            cache_entry = {
                'sport': sport,
                'data_type': data_type,
                'timestamp': datetime.now().isoformat(),
                'data_hash': self._hash_data(data),
                'data': data
            }

            with open(cache_path, 'w') as f:
                json.dump(cache_entry, f, indent=2)

            # Store metadata
            self._update_metadata(sport, data_type, cache_key, cache_entry)

            return True
        except Exception as e:
            print(f"Error writing cache: {e}")
            return False

    def get_diff(self, sport: str, data_type: str, days_back: int = 1) -> Optional[Dict]:
        """
        Get difference between current and previous cached data.

        Args:
            sport: Sport identifier
            data_type: Type of data
            days_back: Number of days to look back

        Returns:
            Dictionary with added, removed, and changed items
        """
        current_date = datetime.now()
        previous_date = current_date - timedelta(days=days_back)

        current_key = self._get_cache_key(sport, data_type, current_date)
        previous_key = self._get_cache_key(sport, data_type, previous_date)

        current_path = self._get_cache_path(data_type, current_key)
        previous_path = self._get_cache_path(data_type, previous_key)

        if not current_path.exists() or not previous_path.exists():
            return None

        try:
            with open(current_path, 'r') as f:
                current_data = json.load(f)['data']
            with open(previous_path, 'r') as f:
                previous_data = json.load(f)['data']

            return self._compute_diff(previous_data, current_data)
        except Exception as e:
            print(f"Error computing diff: {e}")
            return None

    def _compute_diff(self, old_data: Dict, new_data: Dict) -> Dict:
        """Compute differences between two data snapshots."""
        diff = {
            'added': [],
            'removed': [],
            'changed': [],
            'unchanged': []
        }

        # Simple diff for now - can be enhanced based on data structure
        old_hash = self._hash_data(old_data)
        new_hash = self._hash_data(new_data)

        if old_hash != new_hash:
            diff['changed'].append({
                'old_hash': old_hash,
                'new_hash': new_hash,
                'timestamp': datetime.now().isoformat()
            })

        return diff

    def _hash_data(self, data: Any) -> str:
        """Generate hash of data for change detection."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _update_metadata(self, sport: str, data_type: str, cache_key: str,
                        cache_entry: Dict) -> None:
        """Update metadata index for cache entries."""
        metadata_file = self.metadata_cache / f"{sport}_{data_type}_index.json"

        try:
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {'entries': []}

            metadata['entries'].append({
                'key': cache_key,
                'timestamp': cache_entry['timestamp'],
                'hash': cache_entry['data_hash']
            })

            # Keep only recent entries
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            metadata['entries'] = [
                e for e in metadata['entries']
                if datetime.fromisoformat(e['timestamp']) > cutoff_date
            ]

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error updating metadata: {e}")

    def cleanup_old_cache(self) -> int:
        """
        Remove cache entries older than retention period.

        Returns:
            Number of files deleted
        """
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for cache_dir in [self.scoreboard_cache, self.standings_cache,
                         self.odds_cache]:
            for cache_file in cache_dir.glob("*.json"):
                file_date = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_date < cutoff_date:
                    try:
                        cache_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {cache_file}: {e}")

        return deleted_count

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cache usage.

        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'total_entries': 0,
            'size_mb': 0,
            'oldest_entry': None,
            'newest_entry': None,
            'by_type': {}
        }

        all_files = []
        for cache_dir in [self.scoreboard_cache, self.standings_cache,
                         self.odds_cache]:
            files = list(cache_dir.glob("*.json"))
            all_files.extend(files)

            cache_type = cache_dir.name
            stats['by_type'][cache_type] = {
                'count': len(files),
                'size_mb': sum(f.stat().st_size for f in files) / (1024 * 1024)
            }

        stats['total_entries'] = len(all_files)
        stats['size_mb'] = sum(
            sum(f.stat().st_size for f in cache_dir.glob("*.json"))
            for cache_dir in [self.scoreboard_cache, self.standings_cache,
                            self.odds_cache]
        ) / (1024 * 1024)

        if all_files:
            dates = [datetime.fromtimestamp(f.stat().st_mtime) for f in all_files]
            stats['oldest_entry'] = min(dates).isoformat()
            stats['newest_entry'] = max(dates).isoformat()

        return stats

    def get_freshness_status(self, sport: str, data_type: str) -> Dict:
        """
        Check freshness of cached data.

        Returns:
            Status dict with freshness information
        """
        cache_key = self._get_cache_key(sport, data_type, datetime.now())
        cache_path = self._get_cache_path(data_type, cache_key)

        status = {
            'sport': sport,
            'data_type': data_type,
            'exists': cache_path.exists(),
            'fresh': False,
            'age_hours': None,
            'status': 'missing'
        }

        if cache_path.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            age_hours = cache_age.total_seconds() / 3600

            status['age_hours'] = round(age_hours, 2)

            if age_hours < 1:
                status['fresh'] = True
                status['status'] = 'fresh'
            elif age_hours < 24:
                status['status'] = 'stale'
            else:
                status['status'] = 'very_stale'

        return status
