"""ESPN API data fetcher for sports data."""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config


class ESPNFetcher:
    """Fetches sports data from ESPN's unofficial API."""

    def __init__(self):
        self.base_url = config.ESPN_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.espn.com/',
            'Origin': 'https://www.espn.com'
        })

    def get_scoreboard(self, sport: str, limit: int = 20) -> Optional[Dict]:
        """
        Get current scoreboard/recent games for a sport.

        Args:
            sport: Sport key from SPORTS_CONFIG (e.g., 'nfl', 'nba')
            limit: Number of games to fetch

        Returns:
            Dictionary with scoreboard data or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            url = f"{self.base_url}/{league}/scoreboard"
            params = {'limit': limit}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching scoreboard for {sport}: {e}")
            return None

    def get_standings(self, sport: str) -> Optional[Dict]:
        """
        Get current standings for a sport.

        Args:
            sport: Sport key from SPORTS_CONFIG

        Returns:
            Dictionary with standings data or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            url = f"{self.base_url}/{league}/standings"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching standings for {sport}: {e}")
            return None

    def get_team_info(self, sport: str, team_id: str) -> Optional[Dict]:
        """
        Get detailed team information.

        Args:
            sport: Sport key from SPORTS_CONFIG
            team_id: ESPN team ID

        Returns:
            Dictionary with team data or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            url = f"{self.base_url}/{league}/teams/{team_id}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching team info for {sport}/{team_id}: {e}")
            return None

    def get_news(self, sport: str, limit: int = 10) -> Optional[Dict]:
        """
        Get latest news for a sport.

        Args:
            sport: Sport key from SPORTS_CONFIG
            limit: Number of news items

        Returns:
            Dictionary with news data or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            url = f"{self.base_url}/{league}/news"
            params = {'limit': limit}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching news for {sport}: {e}")
            return None

    def get_player_stats(self, sport: str, player_id: str) -> Optional[Dict]:
        """
        Get player statistics.

        Args:
            sport: Sport key from SPORTS_CONFIG
            player_id: ESPN player ID

        Returns:
            Dictionary with player stats or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            url = f"{self.base_url}/{league}/athletes/{player_id}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching player stats for {sport}/{player_id}: {e}")
            return None

    def get_schedule(self, sport: str, days_ahead: int = 7) -> Optional[Dict]:
        """
        Get upcoming schedule for a sport.

        Args:
            sport: Sport key from SPORTS_CONFIG
            days_ahead: Number of days to look ahead

        Returns:
            Dictionary with schedule data or None if error
        """
        try:
            league = config.SPORTS_CONFIG.get(sport, {}).get('espn_league')
            if not league:
                return None

            # Get dates for the next week
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)

            url = f"{self.base_url}/{league}/scoreboard"
            params = {
                'dates': today.strftime('%Y%m%d'),
                'limit': 50
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching schedule for {sport}: {e}")
            return None
