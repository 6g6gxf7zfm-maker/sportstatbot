"""Player performance and injury analyzer."""
from typing import Dict, List, Optional


class PlayerAnalyzer:
    """Analyzes player performance and identifies standouts."""

    def __init__(self):
        self.performance_thresholds = {
            'nfl': {
                'passing_yards': 300,
                'rushing_yards': 100,
                'receiving_yards': 100,
                'touchdowns': 3
            },
            'nba': {
                'points': 30,
                'rebounds': 12,
                'assists': 10,
                'triple_double': True
            },
            'mlb': {
                'home_runs': 2,
                'rbis': 4,
                'hits': 3,
                'strikeouts': 10  # for pitchers
            },
            'nhl': {
                'goals': 2,
                'assists': 3,
                'points': 3,
                'saves': 40  # for goalies
            }
        }

    def extract_standout_players(self, scoreboard_data: Dict, sport: str) -> List[Dict]:
        """
        Extract standout player performances from game data.

        Args:
            scoreboard_data: ESPN scoreboard response
            sport: Sport key (nfl, nba, etc.)

        Returns:
            List of standout player performances
        """
        if not scoreboard_data or 'events' not in scoreboard_data:
            return []

        standouts = []
        events = scoreboard_data.get('events', [])

        for event in events:
            try:
                competitions = event.get('competitions', [])
                if not competitions:
                    continue

                competition = competitions[0]

                # Check for stat leaders in the game
                if 'leaders' in competition:
                    leaders = competition.get('leaders', [])

                    for category in leaders:
                        cat_name = category.get('name', '')
                        cat_leaders = category.get('leaders', [])

                        for leader in cat_leaders:
                            athlete = leader.get('athlete', {})
                            value = leader.get('displayValue', '')
                            team = leader.get('team', {})

                            # Check if performance exceeds threshold
                            if self._is_standout_performance(cat_name, value, sport):
                                standouts.append({
                                    'player': athlete.get('displayName', 'Unknown'),
                                    'team': team.get('displayName', 'Unknown'),
                                    'stat_category': cat_name,
                                    'value': value,
                                    'game': event.get('name', ''),
                                    'date': event.get('date', ''),
                                    'player_id': athlete.get('id')
                                })

            except Exception as e:
                print(f"Error extracting standout players: {e}")
                continue

        # Sort by significance and return top performances
        return standouts[:15]  # Limit to top 15 performances

    def _is_standout_performance(self, stat_name: str, value: str, sport: str) -> bool:
        """Check if a performance meets standout threshold."""
        try:
            thresholds = self.performance_thresholds.get(sport, {})

            # Extract numeric value from display string
            numeric_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', value.split()[0])))

            stat_lower = stat_name.lower()

            for threshold_key, threshold_val in thresholds.items():
                if threshold_key in stat_lower:
                    return numeric_value >= threshold_val

            # Default: if any stat > 30, consider it notable
            return numeric_value >= 30

        except (ValueError, AttributeError):
            return False

    def analyze_injuries(self, news_data: Dict) -> List[Dict]:
        """
        Extract injury information from news data.

        Args:
            news_data: ESPN news response

        Returns:
            List of injury updates
        """
        if not news_data or 'articles' not in news_data:
            return []

        injuries = []
        articles = news_data.get('articles', [])

        for article in articles:
            try:
                headline = article.get('headline', '').lower()
                description = article.get('description', '').lower()

                # Look for injury-related keywords
                injury_keywords = ['injury', 'injured', 'hurt', 'out', 'doubtful',
                                   'questionable', 'ir', 'placed on', 'returns from',
                                   'sideline', 'dnp', 'limited', 'concussion', 'protocol']

                if any(keyword in headline or keyword in description for keyword in injury_keywords):
                    injuries.append({
                        'headline': article.get('headline', ''),
                        'description': article.get('description', ''),
                        'link': article.get('links', {}).get('web', {}).get('href', ''),
                        'published': article.get('published', ''),
                        'type': 'injury_update'
                    })

            except Exception as e:
                print(f"Error analyzing injury news: {e}")
                continue

        return injuries[:10]  # Return top 10 injury updates

    def analyze_roster_changes(self, news_data: Dict) -> List[Dict]:
        """
        Extract roster change information from news.

        Args:
            news_data: ESPN news response

        Returns:
            List of roster updates
        """
        if not news_data or 'articles' not in news_data:
            return []

        roster_changes = []
        articles = news_data.get('articles', [])

        for article in articles:
            try:
                headline = article.get('headline', '').lower()
                description = article.get('description', '').lower()

                # Look for roster change keywords
                roster_keywords = ['signs', 'traded', 'released', 'waived', 'claimed',
                                   'acquired', 'promoted', 'demoted', 'activated',
                                   'designated', 'free agent', 'contract', 'extension']

                if any(keyword in headline or keyword in description for keyword in roster_keywords):
                    roster_changes.append({
                        'headline': article.get('headline', ''),
                        'description': article.get('description', ''),
                        'link': article.get('links', {}).get('web', {}).get('href', ''),
                        'published': article.get('published', ''),
                        'type': 'roster_change'
                    })

            except Exception as e:
                print(f"Error analyzing roster news: {e}")
                continue

        return roster_changes[:10]  # Return top 10 roster changes

    def get_player_summary(self, player_data: Dict) -> Dict:
        """
        Create a summary of player information.

        Args:
            player_data: ESPN player response

        Returns:
            Summarized player data
        """
        if not player_data or 'athlete' not in player_data:
            return {}

        try:
            athlete = player_data.get('athlete', {})

            summary = {
                'name': athlete.get('displayName', 'Unknown'),
                'position': athlete.get('position', {}).get('displayName', 'N/A'),
                'team': athlete.get('team', {}).get('displayName', 'N/A'),
                'jersey': athlete.get('jersey', 'N/A'),
                'experience': athlete.get('experience', {}).get('years', 'N/A')
            }

            # Add current season stats if available
            if 'statistics' in athlete:
                stats = athlete.get('statistics', {})
                summary['stats'] = self._extract_key_stats(stats)

            return summary

        except Exception as e:
            print(f"Error creating player summary: {e}")
            return {}

    def _extract_key_stats(self, statistics: Dict) -> Dict:
        """Extract key statistics from player stats data."""
        key_stats = {}

        try:
            # This will vary by sport and position
            # Extract the most relevant stats
            if isinstance(statistics, dict):
                splits = statistics.get('splits', {})
                if splits and 'categories' in splits:
                    for category in splits['categories']:
                        stats = category.get('stats', [])
                        for stat in stats[:5]:  # Top 5 stats
                            key_stats[stat.get('name', 'Unknown')] = stat.get('displayValue', 'N/A')

        except Exception as e:
            print(f"Error extracting key stats: {e}")

        return key_stats
