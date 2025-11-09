"""
Utility functions for visualizations
"""

import os
import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import pickle


class VisualizationCache:
    """Simple file-based cache for visualizations"""

    def __init__(self, cache_dir: str = 'visualizations/cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, viz_type: str, params: Dict) -> str:
        """Generate cache key from visualization type and parameters"""
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        key_str = f"{viz_type}_{sorted_params}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, viz_type: str, params: Dict, max_age_hours: int = 24) -> Optional[Any]:
        """
        Get cached visualization

        Args:
            viz_type: Type of visualization
            params: Parameters used to create viz
            max_age_hours: Maximum age of cache in hours

        Returns:
            Cached data or None
        """
        cache_key = self._get_cache_key(viz_type, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if not os.path.exists(cache_file):
            return None

        # Check age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time > timedelta(hours=max_age_hours):
            return None

        # Load cached data
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None

    def set(self, viz_type: str, params: Dict, data: Any):
        """
        Cache visualization data

        Args:
            viz_type: Type of visualization
            params: Parameters used to create viz
            data: Data to cache
        """
        cache_key = self._get_cache_key(viz_type, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Failed to cache visualization: {e}")

    def clear(self, max_age_hours: Optional[int] = None):
        """
        Clear cache

        Args:
            max_age_hours: Only clear files older than this (None = clear all)
        """
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)

            if max_age_hours is None:
                os.remove(filepath)
            else:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if datetime.now() - file_time > timedelta(hours=max_age_hours):
                    os.remove(filepath)


# Global cache instance
_cache = VisualizationCache()


def cache_visualization(func):
    """
    Decorator to cache visualization results

    Usage:
        @cache_visualization
        def create_heatmap(data, team_id):
            ...
    """
    def wrapper(self, *args, **kwargs):
        # Build cache params
        params = {
            'args': str(args),
            'kwargs': kwargs,
            'class': self.__class__.__name__
        }

        # Try to get from cache
        cached = _cache.get(func.__name__, params)
        if cached is not None:
            return cached

        # Generate new
        result = func(self, *args, **kwargs)

        # Cache result
        _cache.set(func.__name__, params, result)

        return result

    return wrapper


def export_chart(
    fig,
    filename: str,
    format: str = 'html',
    output_dir: str = 'visualizations/output'
) -> str:
    """
    Export Plotly chart to file

    Args:
        fig: Plotly Figure object
        filename: Output filename (without extension)
        format: Output format ('html', 'png', 'jpg', 'svg', 'pdf', 'json')
        output_dir: Output directory

    Returns:
        Full path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{filename}.{format}")

    if format == 'html':
        fig.write_html(
            filepath,
            include_plotlyjs='cdn',
            config={'displayModeBar': True, 'responsive': True}
        )
    elif format in ['png', 'jpg', 'jpeg', 'svg', 'pdf']:
        fig.write_image(filepath)
    elif format == 'json':
        with open(filepath, 'w') as f:
            f.write(fig.to_json())
    else:
        raise ValueError(f"Unsupported format: {format}")

    return filepath


def create_output_directory(subdir: str = None) -> str:
    """
    Create and return path to output directory

    Args:
        subdir: Optional subdirectory name

    Returns:
        Path to output directory
    """
    base_dir = 'visualizations/output'
    if subdir:
        output_dir = os.path.join(base_dir, subdir)
    else:
        output_dir = base_dir

    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def format_number(num: float, precision: int = 1) -> str:
    """Format number for display"""
    if abs(num) >= 1e6:
        return f"{num/1e6:.{precision}f}M"
    elif abs(num) >= 1e3:
        return f"{num/1e3:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"


def format_percentage(value: float, precision: int = 1) -> str:
    """Format value as percentage"""
    return f"{value * 100:.{precision}f}%"


def format_time_remaining(seconds: int) -> str:
    """Format game time remaining"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def get_sport_emoji(sport: str) -> str:
    """Get emoji for sport"""
    emoji_map = {
        'nfl': '🏈',
        'nba': '🏀',
        'mlb': '⚾',
        'nhl': '🏒',
        'mls': '⚽',
        'soccer': '⚽',
        'golf': '⛳',
    }
    return emoji_map.get(sport.lower(), '🏆')
