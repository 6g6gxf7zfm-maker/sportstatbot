"""
Configuration loader for Sports Reel Automation Bot
Loads settings from config.json and environment variables
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for reel automation system"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config directory
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.json"

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "sports": ["NBA", "NFL", "MLB", "MLS"],
            "exclude_sports": ["NHL", "Hockey"],
            "posts_per_day": 5,
            "viral_score_threshold": 7,
            "max_reel_length": 15,
            "output_directory": "~/Desktop/reels_ready"
        }

    # Sports Settings
    @property
    def sports(self) -> List[str]:
        """Get enabled sports list"""
        return self._config.get("sports", [])

    @property
    def exclude_sports(self) -> List[str]:
        """Get excluded sports list"""
        return self._config.get("exclude_sports", [])

    # Processing Settings
    @property
    def posts_per_day(self) -> int:
        """Target number of posts per day"""
        return self._config.get("posts_per_day", 5)

    @property
    def viral_score_threshold(self) -> float:
        """Minimum viral score to process"""
        return self._config.get("viral_score_threshold", 7)

    @property
    def max_reel_length(self) -> int:
        """Maximum reel length in seconds"""
        return self._config.get("max_reel_length", 15)

    @property
    def output_directory(self) -> Path:
        """Output directory for processed reels"""
        path = os.path.expanduser(self._config.get("output_directory", "~/Desktop/reels_ready"))
        return Path(path)

    # Video Settings
    @property
    def video_resolution(self) -> tuple:
        """Video resolution (width, height)"""
        res = self._config.get("video_settings", {}).get("resolution", [1080, 1920])
        return tuple(res)

    @property
    def video_fps(self) -> int:
        """Video frames per second"""
        return self._config.get("video_settings", {}).get("fps", 30)

    # API Keys (from environment variables)
    @property
    def anthropic_api_key(self) -> str:
        """Anthropic API key for Claude"""
        return os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def supabase_url(self) -> str:
        """Supabase project URL"""
        return os.getenv("SUPABASE_URL", "")

    @property
    def supabase_key(self) -> str:
        """Supabase anon/service key"""
        return os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))

    # Caption Settings
    @property
    def caption_style(self) -> str:
        """Caption generation style"""
        return self._config.get("caption_style", "hype")

    @property
    def hashtag_count(self) -> int:
        """Number of hashtags to generate"""
        return self._config.get("caption_format", {}).get("hashtag_count", 15)

    # Viral Score Weights
    @property
    def viral_score_weights(self) -> Dict[str, float]:
        """Weights for viral score calculation"""
        return self._config.get("viral_score_weights", {
            "game_importance": 0.3,
            "play_type": 0.25,
            "player_popularity": 0.25,
            "historical_engagement": 0.2
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        self._config.update(updates)
        self.save_config()

    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


# Global config instance
config = Config()
