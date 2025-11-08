"""Main sports report generator."""
from typing import Dict, List, Optional
from datetime import datetime
import time

from data_fetchers.espn_fetcher import ESPNFetcher
from data_fetchers.odds_fetcher import OddsFetcher
from analyzers.game_analyzer import GameAnalyzer
from analyzers.player_analyzer import PlayerAnalyzer
from formatters.slack_formatter import SlackFormatter
import config


class SportsReportGenerator:
    """Generates comprehensive sports analysis reports."""

    def __init__(self):
        self.espn_fetcher = ESPNFetcher()
        self.odds_fetcher = OddsFetcher()
        self.game_analyzer = GameAnalyzer()
        self.player_analyzer = PlayerAnalyzer()
        self.slack_formatter = SlackFormatter()

    def generate_full_report(self, sports: Optional[List[str]] = None) -> str:
        """
        Generate a full sports report for specified sports.

        Args:
            sports: List of sport keys to include (None = all sports)

        Returns:
            Formatted report string
        """
        if sports is None:
            sports = list(config.SPORTS_CONFIG.keys())

        all_sports_data = {}

        print(f"Generating report for {len(sports)} sports...")

        for sport in sports:
            print(f"  Fetching {sport.upper()} data...")
            sport_data = self._generate_sport_data(sport)

            if sport_data:
                all_sports_data[sport] = sport_data
            else:
                print(f"  Warning: No data available for {sport}")

            # Be respectful to APIs
            time.sleep(0.5)

        # Format the complete report
        print("Formatting report...")
        report = self.slack_formatter.format_full_report(all_sports_data)

        print("Report generated successfully!")
        return report

    def generate_sport_report(self, sport: str, quick: bool = False) -> str:
        """
        Generate a report for a single sport.

        Args:
            sport: Sport key
            quick: If True, generate quick update instead of full report

        Returns:
            Formatted report string
        """
        print(f"Generating {sport.upper()} report...")

        sport_data = self._generate_sport_data(sport)

        if not sport_data:
            return f"No data available for {sport.upper()}"

        if quick:
            return self.slack_formatter.format_sport_quick_update(sport, sport_data)
        else:
            sport_config = config.SPORTS_CONFIG.get(sport, {})
            return self.slack_formatter._format_sport_section(sport, sport_data, sport_config)

    def _generate_sport_data(self, sport: str) -> Optional[Dict]:
        """
        Fetch and analyze data for a single sport.

        Args:
            sport: Sport key

        Returns:
            Dictionary with analyzed sport data
        """
        try:
            sport_data = {
                'enabled': True,
                'trends': [],
                'recent_games': [],
                'standout_players': [],
                'injuries': [],
                'roster_changes': [],
                'betting_insights': {},
                'must_watch': []
            }

            # Fetch scoreboard (recent games)
            scoreboard = self.espn_fetcher.get_scoreboard(sport, limit=15)
            if scoreboard:
                game_analysis = self.game_analyzer.analyze_scoreboard(scoreboard)
                sport_data['recent_games'] = game_analysis.get('games', [])

                # Extract standout players from recent games
                standout_players = self.player_analyzer.extract_standout_players(scoreboard, sport)
                sport_data['standout_players'] = standout_players

            # Fetch standings for trends
            standings = self.espn_fetcher.get_standings(sport)
            if standings:
                standings_analysis = self.game_analyzer.analyze_standings(standings)
                sport_data['trends'] = standings_analysis.get('trends', [])

            # Fetch news for injuries and roster changes
            news = self.espn_fetcher.get_news(sport, limit=20)
            if news:
                injuries = self.player_analyzer.analyze_injuries(news)
                roster_changes = self.player_analyzer.analyze_roster_changes(news)
                sport_data['injuries'] = injuries
                sport_data['roster_changes'] = roster_changes

            # Fetch betting odds
            odds = self.odds_fetcher.get_odds(sport)
            if odds:
                betting_insights = self._analyze_betting_data(odds)
                sport_data['betting_insights'] = betting_insights

            # Find must-watch upcoming matchups
            schedule = self.espn_fetcher.get_schedule(sport, days_ahead=7)
            if schedule:
                must_watch = self.game_analyzer.find_must_watch_matchups(schedule, standings)
                sport_data['must_watch'] = must_watch

            return sport_data

        except Exception as e:
            print(f"Error generating sport data for {sport}: {e}")
            return None

    def _analyze_betting_data(self, odds_data: List[Dict]) -> Dict:
        """
        Analyze betting odds data.

        Args:
            odds_data: Raw odds data from API

        Returns:
            Analyzed betting insights
        """
        betting_insights = {
            'value_bets': [],
            'featured_games': []
        }

        try:
            # Find value bets
            value_bets = self.odds_fetcher.find_value_bets(odds_data)
            betting_insights['value_bets'] = value_bets

            # Format featured games with odds
            featured = []
            for game in odds_data[:5]:  # Top 5 games
                home_team = game.get('home_team', 'Unknown')
                away_team = game.get('away_team', 'Unknown')

                # Extract odds from first bookmaker
                bookmakers = game.get('bookmakers', [])
                if bookmakers:
                    markets = bookmakers[0].get('markets', [])

                    spread = 'N/A'
                    total = 'N/A'

                    for market in markets:
                        if market['key'] == 'spreads' and market.get('outcomes'):
                            outcome = market['outcomes'][0]
                            spread = f"{outcome.get('point', 0)} ({outcome.get('price', 'N/A')})"

                        if market['key'] == 'totals' and market.get('outcomes'):
                            outcome = market['outcomes'][0]
                            total = f"{outcome.get('point', 0)} ({outcome.get('price', 'N/A')})"

                    featured.append({
                        'matchup': f"{away_team} @ {home_team}",
                        'spread': spread,
                        'total': total
                    })

            betting_insights['featured_games'] = featured

        except Exception as e:
            print(f"Error analyzing betting data: {e}")

        return betting_insights

    def generate_custom_analysis(self, sport: str, team: str) -> str:
        """
        Generate custom analysis for a specific team.

        Args:
            sport: Sport key
            team: Team name or abbreviation

        Returns:
            Custom analysis report
        """
        print(f"Generating custom analysis for {team} in {sport.upper()}...")

        # This is a placeholder for custom team analysis
        # Would need team ID resolution and more detailed queries
        return f"Custom analysis for {team} - Feature coming soon!"

    def save_report(self, report: str, filename: Optional[str] = None) -> str:
        """
        Save report to file.

        Args:
            report: Report content
            filename: Output filename (None = auto-generate)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"sports_report_{timestamp}.md"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"Report saved to: {filename}")
            return filename

        except Exception as e:
            print(f"Error saving report: {e}")
            return ""
