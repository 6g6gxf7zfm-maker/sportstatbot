"""Odds API fetcher for betting data."""
import requests
from typing import Dict, List, Optional
import config


class OddsFetcher:
    """Fetches betting odds data from The Odds API."""

    def __init__(self):
        self.base_url = config.ODDS_API_BASE
        self.api_key = config.ODDS_API_KEY
        self.session = requests.Session()

        # Sport mappings for The Odds API
        self.sport_keys = {
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'mlb': 'baseball_mlb',
            'nhl': 'icehockey_nhl',
            'mls': 'soccer_usa_mls',
            'soccer': 'soccer_epl',  # Premier League
            'golf': 'golf_pga_championship'
        }

    def get_odds(self, sport: str, markets: str = 'h2h,spreads,totals') -> Optional[List[Dict]]:
        """
        Get betting odds for a sport.

        Args:
            sport: Sport key from SPORTS_CONFIG
            markets: Comma-separated markets to fetch (h2h, spreads, totals)

        Returns:
            List of games with odds data or None if error
        """
        if not self.api_key:
            print("Warning: No Odds API key configured. Skipping betting data.")
            return None

        try:
            sport_key = self.sport_keys.get(sport)
            if not sport_key:
                return None

            url = f"{self.base_url}/sports/{sport_key}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': markets,
                'oddsFormat': 'american'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"Error fetching odds for {sport}: {e}")
            return None

    def get_upcoming_odds(self, sport: str) -> Optional[List[Dict]]:
        """
        Get odds for upcoming games.

        Args:
            sport: Sport key from SPORTS_CONFIG

        Returns:
            List of upcoming games with odds or None if error
        """
        return self.get_odds(sport)

    def find_value_bets(self, odds_data: List[Dict]) -> List[Dict]:
        """
        Analyze odds to find potential value bets.

        Args:
            odds_data: List of games with odds

        Returns:
            List of potential value bets with analysis
        """
        if not odds_data:
            return []

        value_bets = []

        for game in odds_data:
            try:
                bookmakers = game.get('bookmakers', [])
                if not bookmakers:
                    continue

                # Analyze spread discrepancies across bookmakers
                spreads = []
                totals = []

                for bookmaker in bookmakers:
                    for market in bookmaker.get('markets', []):
                        if market['key'] == 'spreads':
                            for outcome in market['outcomes']:
                                spreads.append({
                                    'bookmaker': bookmaker['title'],
                                    'team': outcome['name'],
                                    'point': outcome.get('point', 0),
                                    'price': outcome['price']
                                })
                        elif market['key'] == 'totals':
                            for outcome in market['outcomes']:
                                totals.append({
                                    'bookmaker': bookmaker['title'],
                                    'type': outcome['name'],
                                    'point': outcome.get('point', 0),
                                    'price': outcome['price']
                                })

                # Simple value detection: look for price discrepancies
                if spreads and len(spreads) >= 4:
                    avg_price = sum(s['price'] for s in spreads) / len(spreads)
                    for spread in spreads:
                        if spread['price'] > avg_price + 15:  # 15+ points better than average
                            value_bets.append({
                                'game': f"{game['home_team']} vs {game['away_team']}",
                                'type': 'spread',
                                'recommendation': f"{spread['team']} {spread['point']}",
                                'bookmaker': spread['bookmaker'],
                                'odds': spread['price'],
                                'reason': 'Better odds than market average'
                            })

            except Exception as e:
                print(f"Error analyzing game for value bets: {e}")
                continue

        return value_bets
