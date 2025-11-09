"""
Image Fetcher for SportStatBot
Automatically fetches team logos, player headshots, and other images
"""

import os
import requests
from typing import Optional, Dict
from urllib.parse import quote


class ImageFetcher:
    """Fetch and cache sports images"""

    def __init__(self, cache_dir: str = "reports/images"):
        """Initialize image fetcher with cache directory"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # ESPN CDN URLs for team logos
        self.espn_logo_base = "https://a.espncdn.com/i/teamlogos"

        # Sport-specific logo paths
        self.logo_paths = {
            'nfl': f"{self.espn_logo_base}/nfl/500",
            'nba': f"{self.espn_logo_base}/nba/500",
            'mlb': f"{self.espn_logo_base}/mlb/500",
            'nhl': f"{self.espn_logo_base}/nhl/500",
            'ncaaf': f"{self.espn_logo_base}/ncaa/500",
            'ncaab': f"{self.espn_logo_base}/ncaa/500",
            'soccer': f"{self.espn_logo_base}/soccer/500",
        }

        # Team ID mappings (abbreviated - would need full mappings)
        self.team_ids = {
            # NFL
            'Kansas City Chiefs': 'kc',
            'Buffalo Bills': 'buf',
            'Dallas Cowboys': 'dal',
            'San Francisco 49ers': 'sf',
            # NBA
            'Los Angeles Lakers': 'lal',
            'Boston Celtics': 'bos',
            'Golden State Warriors': 'gs',
            'Miami Heat': 'mia',
            # MLB
            'New York Yankees': 'nyy',
            'Los Angeles Dodgers': 'lad',
            'Boston Red Sox': 'bos',
            # NHL
            'Toronto Maple Leafs': 'tor',
            'Montreal Canadiens': 'mtl',
        }

    def get_team_logo(self, team_name: str, sport: str) -> Optional[str]:
        """Fetch team logo and return local path"""
        # Sanitize team name for filename
        safe_name = team_name.replace(' ', '_').replace('/', '_')
        filename = f"{sport}_{safe_name}_logo.png"
        filepath = os.path.join(self.cache_dir, filename)

        # Check cache
        if os.path.exists(filepath):
            return filepath

        # Get team ID
        team_id = self.team_ids.get(team_name)
        if not team_id:
            # Try to derive from team name (simplified)
            team_id = team_name.lower().replace(' ', '-')

        # Construct URL
        logo_base = self.logo_paths.get(sport.lower())
        if not logo_base:
            return None

        logo_url = f"{logo_base}/{team_id}.png"

        # Fetch image
        try:
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"Error fetching logo for {team_name}: {e}")

        return None

    def get_player_headshot(self, player_name: str, sport: str) -> Optional[str]:
        """Fetch player headshot (ESPN player images)"""
        # Sanitize player name
        safe_name = player_name.replace(' ', '_').replace('/', '_')
        filename = f"{sport}_{safe_name}_headshot.png"
        filepath = os.path.join(self.cache_dir, filename)

        # Check cache
        if os.path.exists(filepath):
            return filepath

        # ESPN player headshots are typically at:
        # https://a.espncdn.com/i/headshots/{sport}/players/full/{player_id}.png
        # For demo purposes, we'll use a placeholder approach

        # This would require player ID lookup via ESPN API
        # For now, return None (would be implemented with full API integration)
        return None

    def get_generic_sport_image(self, sport: str) -> Optional[str]:
        """Get a generic sport image/icon"""
        filename = f"{sport}_icon.png"
        filepath = os.path.join(self.cache_dir, filename)

        if os.path.exists(filepath):
            return filepath

        # Could fetch from a generic sports icon service
        # For now, return None
        return None

    def fetch_multiple_logos(self, teams: list, sport: str) -> Dict[str, Optional[str]]:
        """Fetch logos for multiple teams"""
        logos = {}
        for team in teams:
            logo_path = self.get_team_logo(team, sport)
            logos[team] = logo_path
        return logos

    def embed_image_in_markdown(self, image_path: str, alt_text: str = "", width: int = None) -> str:
        """Generate markdown to embed an image"""
        if not image_path or not os.path.exists(image_path):
            return ""

        md = f"![{alt_text}]({image_path})"
        if width:
            # HTML img tag for size control
            md = f'<img src="{image_path}" alt="{alt_text}" width="{width}px" />'

        return md

    def create_team_header_with_logos(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        game_info: str = ""
    ) -> str:
        """Create a game header with team logos"""
        home_logo = self.get_team_logo(home_team, sport)
        away_logo = self.get_team_logo(away_team, sport)

        header = "\n<div align='center'>\n"

        if away_logo:
            header += f'<img src="{away_logo}" width="100px" /> '
        else:
            header += f'**{away_team}** '

        header += " **@** "

        if home_logo:
            header += f' <img src="{home_logo}" width="100px" />'
        else:
            header += f' **{home_team}**'

        if game_info:
            header += f"\n\n*{game_info}*"

        header += "\n</div>\n"

        return header

    def clear_cache(self):
        """Clear the image cache"""
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

    def get_cache_size(self) -> int:
        """Get total size of cached images in bytes"""
        total_size = 0
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        return total_size
