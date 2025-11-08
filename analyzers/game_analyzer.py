"""Game and team performance analyzer."""
from typing import Dict, List, Optional
from datetime import datetime


class GameAnalyzer:
    """Analyzes game results and team performance trends."""

    def __init__(self):
        self.hot_streak_threshold = 3  # wins in a row
        self.cold_streak_threshold = 3  # losses in a row

    def analyze_scoreboard(self, scoreboard_data: Dict) -> Dict:
        """
        Analyze scoreboard data to extract insights.

        Args:
            scoreboard_data: ESPN scoreboard response

        Returns:
            Dictionary with analyzed data
        """
        if not scoreboard_data or 'events' not in scoreboard_data:
            return {'games': [], 'highlights': []}

        events = scoreboard_data.get('events', [])
        analyzed_games = []
        highlights = []

        for event in events:
            try:
                game_info = self._analyze_game(event)
                if game_info:
                    analyzed_games.append(game_info)

                    # Identify highlight-worthy games
                    if game_info.get('is_upset'):
                        highlights.append({
                            'type': 'upset',
                            'description': f"{game_info['winner']} upset {game_info['loser']}",
                            'game': game_info
                        })

                    if game_info.get('is_close'):
                        highlights.append({
                            'type': 'close_game',
                            'description': f"Close game: {game_info['away_team']} vs {game_info['home_team']}",
                            'game': game_info
                        })

                    if game_info.get('is_blowout'):
                        highlights.append({
                            'type': 'blowout',
                            'description': f"Blowout: {game_info['winner']} dominated {game_info['loser']}",
                            'game': game_info
                        })

            except Exception as e:
                print(f"Error analyzing game: {e}")
                continue

        return {
            'games': analyzed_games,
            'highlights': highlights,
            'total_games': len(analyzed_games)
        }

    def _analyze_game(self, event: Dict) -> Optional[Dict]:
        """Analyze a single game event."""
        try:
            competitions = event.get('competitions', [])
            if not competitions:
                return None

            competition = competitions[0]
            competitors = competition.get('competitors', [])

            if len(competitors) != 2:
                return None

            # Extract team info
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)

            if not home_team or not away_team:
                return None

            home_score = int(home_team.get('score', 0))
            away_score = int(away_team.get('score', 0))

            game_info = {
                'id': event.get('id'),
                'name': event.get('name'),
                'date': event.get('date'),
                'status': competition.get('status', {}).get('type', {}).get('description', 'Unknown'),
                'home_team': home_team.get('team', {}).get('displayName', 'Unknown'),
                'away_team': away_team.get('team', {}).get('displayName', 'Unknown'),
                'home_score': home_score,
                'away_score': away_score,
                'home_record': home_team.get('records', [{}])[0].get('summary', 'N/A') if home_team.get('records') else 'N/A',
                'away_record': away_team.get('records', [{}])[0].get('summary', 'N/A') if away_team.get('records') else 'N/A',
            }

            # Determine winner/loser
            if home_score > away_score:
                game_info['winner'] = game_info['home_team']
                game_info['loser'] = game_info['away_team']
                game_info['winner_score'] = home_score
                game_info['loser_score'] = away_score
            elif away_score > home_score:
                game_info['winner'] = game_info['away_team']
                game_info['loser'] = game_info['home_team']
                game_info['winner_score'] = away_score
                game_info['loser_score'] = home_score
            else:
                game_info['winner'] = None
                game_info['loser'] = None

            # Game characteristics
            score_diff = abs(home_score - away_score)
            game_info['score_differential'] = score_diff
            game_info['is_close'] = score_diff <= 7 and score_diff > 0  # Within one score
            game_info['is_blowout'] = score_diff >= 21  # 3+ score margin
            game_info['is_upset'] = self._detect_upset(home_team, away_team, home_score, away_score)

            # Extract additional stats if available
            if 'leaders' in competition:
                game_info['leaders'] = self._extract_leaders(competition['leaders'])

            return game_info

        except Exception as e:
            print(f"Error in _analyze_game: {e}")
            return None

    def _detect_upset(self, home_team: Dict, away_team: Dict, home_score: int, away_score: int) -> bool:
        """Detect if game was an upset based on rankings or odds."""
        try:
            # Check if there's a significant ranking difference
            home_rank = home_team.get('curatedRank', {}).get('current', 999)
            away_rank = away_team.get('curatedRank', {}).get('current', 999)

            # If ranked team loses to unranked team
            if home_rank <= 25 and away_rank > 25 and away_score > home_score:
                return True
            if away_rank <= 25 and home_rank > 25 and home_score > away_score:
                return True

            # If significantly lower ranked team wins
            if abs(home_rank - away_rank) >= 10:
                if home_rank > away_rank and home_score > away_score:
                    return True
                if away_rank > home_rank and away_score > home_score:
                    return True

            return False

        except Exception:
            return False

    def _extract_leaders(self, leaders_data: List[Dict]) -> Dict:
        """Extract stat leaders from game data."""
        leaders = {}
        try:
            for category in leaders_data:
                cat_name = category.get('name', '')
                if category.get('leaders'):
                    leader = category['leaders'][0]
                    athlete = leader.get('athlete', {})
                    leaders[cat_name] = {
                        'name': athlete.get('displayName', 'Unknown'),
                        'value': leader.get('displayValue', 'N/A')
                    }
        except Exception as e:
            print(f"Error extracting leaders: {e}")

        return leaders

    def analyze_standings(self, standings_data: Dict) -> Dict:
        """
        Analyze standings to identify trends.

        Args:
            standings_data: ESPN standings response

        Returns:
            Dictionary with analyzed standings
        """
        if not standings_data:
            return {'teams': [], 'trends': []}

        teams_analysis = []
        trends = []

        try:
            children = standings_data.get('children', [])

            for child in children:
                standings = child.get('standings', {}).get('entries', [])

                for entry in standings:
                    team = entry.get('team', {})
                    stats = entry.get('stats', [])

                    team_info = {
                        'name': team.get('displayName', 'Unknown'),
                        'abbreviation': team.get('abbreviation', 'UNK'),
                        'logo': team.get('logos', [{}])[0].get('href', '') if team.get('logos') else ''
                    }

                    # Extract key stats
                    for stat in stats:
                        stat_name = stat.get('name', '').lower()
                        stat_value = stat.get('displayValue', stat.get('value', 'N/A'))

                        if 'wins' in stat_name:
                            team_info['wins'] = stat_value
                        elif 'losses' in stat_name:
                            team_info['losses'] = stat_value
                        elif 'streak' in stat_name:
                            team_info['streak'] = stat_value
                        elif 'differential' in stat_name or 'diff' in stat_name:
                            team_info['point_diff'] = stat_value

                    teams_analysis.append(team_info)

                    # Identify hot/cold streaks
                    streak = team_info.get('streak', '')
                    if 'W' in str(streak):
                        try:
                            streak_num = int(''.join(filter(str.isdigit, str(streak))))
                            if streak_num >= self.hot_streak_threshold:
                                trends.append({
                                    'type': 'hot_streak',
                                    'team': team_info['name'],
                                    'description': f"{team_info['name']} on {streak_num}-game win streak 🔥"
                                })
                        except ValueError:
                            pass

                    if 'L' in str(streak):
                        try:
                            streak_num = int(''.join(filter(str.isdigit, str(streak))))
                            if streak_num >= self.cold_streak_threshold:
                                trends.append({
                                    'type': 'cold_streak',
                                    'team': team_info['name'],
                                    'description': f"{team_info['name']} on {streak_num}-game losing streak ❄️"
                                })
                        except ValueError:
                            pass

        except Exception as e:
            print(f"Error analyzing standings: {e}")

        return {
            'teams': teams_analysis,
            'trends': trends
        }

    def find_must_watch_matchups(self, schedule_data: Dict, standings_data: Dict = None) -> List[Dict]:
        """
        Identify must-watch upcoming matchups.

        Args:
            schedule_data: ESPN schedule/scoreboard data
            standings_data: ESPN standings data (optional)

        Returns:
            List of must-watch games with reasons
        """
        must_watch = []

        if not schedule_data or 'events' not in schedule_data:
            return must_watch

        events = schedule_data.get('events', [])

        for event in events:
            try:
                competitions = event.get('competitions', [])
                if not competitions:
                    continue

                competition = competitions[0]
                competitors = competition.get('competitors', [])

                if len(competitors) != 2:
                    continue

                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)

                if not home_team or not away_team:
                    continue

                reasons = []

                # Check for ranked matchups
                home_rank = home_team.get('curatedRank', {}).get('current', 999)
                away_rank = away_team.get('curatedRank', {}).get('current', 999)

                if home_rank <= 25 and away_rank <= 25:
                    reasons.append(f"Top 25 matchup: #{home_rank} vs #{away_rank}")

                # Check for rivalry games (if marked)
                if event.get('season', {}).get('type') == 4 or 'rivalry' in event.get('name', '').lower():
                    reasons.append("Rivalry game")

                # Check for playoff implications
                if 'playoff' in event.get('name', '').lower() or 'championship' in event.get('name', '').lower():
                    reasons.append("Playoff implications")

                # Check for division games
                if competition.get('conferenceCompetition') or competition.get('divisionCompetition'):
                    reasons.append("Division/Conference game")

                if reasons:
                    must_watch.append({
                        'game': event.get('name'),
                        'date': event.get('date'),
                        'home_team': home_team.get('team', {}).get('displayName'),
                        'away_team': away_team.get('team', {}).get('displayName'),
                        'reasons': reasons,
                        'venue': competition.get('venue', {}).get('fullName', 'TBD')
                    })

            except Exception as e:
                print(f"Error analyzing matchup: {e}")
                continue

        return must_watch
