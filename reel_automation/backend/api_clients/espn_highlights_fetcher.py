"""
ESPN Highlights Fetcher
Fetches video highlights from ESPN and other sports sources
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESPNHighlightsFetcher:
    """Fetches sports highlights from ESPN and related sources"""

    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_highlights(
        self,
        sports: List[str],
        hours_back: int = 24
    ) -> List[Dict]:
        """
        Fetch highlights for specified sports

        Args:
            sports: List of sports to fetch (e.g., ['NBA', 'NFL'])
            hours_back: How many hours back to look for highlights

        Returns:
            List of highlight dictionaries
        """
        all_highlights = []

        for sport in sports:
            logger.info(f"Fetching highlights for {sport}")
            sport_highlights = self._fetch_sport_highlights(sport, hours_back)
            all_highlights.extend(sport_highlights)

        logger.info(f"Total highlights found: {len(all_highlights)}")
        return all_highlights

    def _fetch_sport_highlights(self, sport: str, hours_back: int) -> List[Dict]:
        """Fetch highlights for a specific sport"""
        sport_mapping = {
            'NBA': 'basketball/nba',
            'NFL': 'football/nfl',
            'MLB': 'baseball/mlb',
            'MLS': 'soccer/usa.1',
            'EPL': 'soccer/eng.1',
            'LaLiga': 'soccer/esp.1',
            'Champions League': 'soccer/uefa.champions'
        }

        league_path = sport_mapping.get(sport)
        if not league_path:
            logger.warning(f"Unknown sport: {sport}")
            return []

        highlights = []

        try:
            # Get recent games/events
            events = self._fetch_recent_events(league_path, hours_back)

            for event in events:
                # Extract highlight information
                event_highlights = self._extract_highlights_from_event(event, sport)
                highlights.extend(event_highlights)

        except Exception as e:
            logger.error(f"Error fetching {sport} highlights: {e}")

        return highlights

    def _fetch_recent_events(self, league_path: str, hours_back: int) -> List[Dict]:
        """Fetch recent events/games for a league"""
        try:
            url = f"{self.base_url}/{league_path}/scoreboard"

            # Get current date and date range
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours_back)

            params = {
                'limit': 20
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = data.get('events', [])

            logger.info(f"Found {len(events)} events for {league_path}")
            return events

        except requests.RequestException as e:
            logger.error(f"Error fetching events: {e}")
            return []

    def _extract_highlights_from_event(self, event: Dict, sport: str) -> List[Dict]:
        """Extract highlight information from an event"""
        highlights = []

        try:
            # Get event details
            event_id = event.get('id')
            event_name = event.get('name', 'Unknown')
            competition = event.get('competitions', [{}])[0]

            # Get teams
            competitors = competition.get('competitors', [])
            teams = [comp.get('team', {}).get('displayName', '') for comp in competitors]

            # Get video/highlights
            videos = event.get('videos', [])

            # Also check in competitions
            if not videos:
                videos = competition.get('videos', [])

            for video in videos:
                headline = video.get('headline', '')
                description = video.get('description', '')

                # Look for actual video links
                links = video.get('links', {})
                video_url = None

                # Try to find source URL
                if 'source' in links:
                    video_url = links['source'].get('href')
                elif 'self' in links:
                    video_url = links['self'].get('href')

                # Extract duration if available
                duration = video.get('duration', 0)

                highlight = {
                    'sport': sport,
                    'event_id': event_id,
                    'event_name': event_name,
                    'teams': teams,
                    'headline': headline,
                    'description': description,
                    'video_url': video_url,
                    'duration': duration,
                    'thumbnail': video.get('thumbnail', ''),
                    'timestamp': datetime.now().isoformat(),
                    'play_type': self._classify_play_type(headline, description),
                    'players': self._extract_players(headline, description)
                }

                highlights.append(highlight)

        except Exception as e:
            logger.error(f"Error extracting highlights from event: {e}")

        return highlights

    def _classify_play_type(self, headline: str, description: str) -> str:
        """Classify the type of play from headline/description"""
        text = (headline + " " + description).lower()

        play_types = {
            'dunk': ['dunk', 'slam', 'jam'],
            'buzzer_beater': ['buzzer', 'game-winner', 'walk-off'],
            'touchdown': ['touchdown', 'td', 'score'],
            'home_run': ['home run', 'homer', 'grand slam'],
            'goal': ['goal', 'gol'],
            'assist': ['assist', 'pass'],
            'block': ['block', 'rejection'],
            'interception': ['interception', 'pick'],
            'highlight': ['highlight', 'best', 'top']
        }

        for play_type, keywords in play_types.items():
            if any(keyword in text for keyword in keywords):
                return play_type

        return 'highlight'

    def _extract_players(self, headline: str, description: str) -> List[str]:
        """Extract player names from headline/description"""
        # This is a simple implementation - could be enhanced with NLP
        text = headline + " " + description

        # Common name patterns (simplified)
        # In production, you'd want a proper player database
        players = []

        # Look for capitalized words that might be names
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                # Check if next word is also capitalized (likely full name)
                if i + 1 < len(words) and words[i + 1] and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    if len(full_name) > 5 and full_name not in players:
                        players.append(full_name)

        return players[:3]  # Return up to 3 player names

    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download video from URL

        Args:
            url: Video URL
            output_path: Where to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading video from: {url}")

            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Video downloaded successfully: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False


class AlternativeHighlightsFetcher:
    """
    Fetcher for alternative highlight sources
    Uses yt-dlp to download from YouTube, Twitter, etc.
    """

    def __init__(self):
        self.search_queries = {
            'NBA': ['NBA highlights today', 'NBA best plays'],
            'NFL': ['NFL highlights today', 'NFL touchdown'],
            'MLB': ['MLB highlights today', 'MLB home run'],
            'MLS': ['MLS highlights', 'MLS goals today'],
            'EPL': ['Premier League highlights', 'EPL goals'],
            'LaLiga': ['La Liga highlights', 'La Liga goals'],
        }

    def fetch_youtube_highlights(self, sport: str, max_results: int = 5) -> List[Dict]:
        """
        Fetch highlights from YouTube
        Note: Requires yt-dlp to be installed
        """
        try:
            import yt_dlp

            search_query = self.search_queries.get(sport, [f"{sport} highlights"])[0]

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': max_results,
            }

            highlights = []

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch{max_results}:{search_query}",
                    download=False
                )

                if 'entries' in search_results:
                    for entry in search_results['entries']:
                        highlight = {
                            'sport': sport,
                            'title': entry.get('title'),
                            'url': entry.get('url'),
                            'video_url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'duration': entry.get('duration', 0),
                            'thumbnail': entry.get('thumbnail'),
                            'source': 'youtube'
                        }
                        highlights.append(highlight)

            return highlights

        except ImportError:
            logger.warning("yt-dlp not installed. YouTube fetching disabled.")
            return []
        except Exception as e:
            logger.error(f"Error fetching YouTube highlights: {e}")
            return []


def test_fetcher():
    """Test the highlights fetcher"""
    fetcher = ESPNHighlightsFetcher()
    highlights = fetcher.fetch_highlights(['NBA'], hours_back=48)

    print(f"\nFound {len(highlights)} highlights:")
    for i, h in enumerate(highlights[:5], 1):
        print(f"\n{i}. {h['headline']}")
        print(f"   Teams: {', '.join(h['teams'])}")
        print(f"   Play Type: {h['play_type']}")
        if h['players']:
            print(f"   Players: {', '.join(h['players'])}")


if __name__ == "__main__":
    test_fetcher()
