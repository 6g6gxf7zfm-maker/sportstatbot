"""
Timeline Visual Generator for SportStatBot
Creates timeline visualizations for major storylines
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta


class TimelineGenerator:
    """Generate timeline visuals for sports storylines"""

    def __init__(self):
        """Initialize timeline generator"""
        self.timeline_symbols = {
            'start': '⚫',
            'milestone': '🔵',
            'highlight': '🌟',
            'injury': '🏥',
            'trade': '🔄',
            'win': '✅',
            'loss': '❌',
            'playoff': '🏆',
            'end': '⚪'
        }

    def generate_season_timeline(
        self,
        events: List[Dict],
        title: str = "Season Timeline"
    ) -> str:
        """Generate a visual timeline for season events"""
        timeline = f"\n## {title}\n\n"
        timeline += "```\n"

        # Sort events by date
        sorted_events = sorted(events, key=lambda x: x.get('date', datetime.now()))

        for i, event in enumerate(sorted_events):
            date = event.get('date', datetime.now())
            event_type = event.get('type', 'milestone')
            description = event.get('description', 'Event')
            symbol = self.timeline_symbols.get(event_type, '•')

            # Format date
            date_str = date.strftime('%b %d') if isinstance(date, datetime) else str(date)

            # Draw timeline
            if i == 0:
                timeline += f"{date_str:12} {symbol} {description}\n"
                timeline += f"{'':12} |\n"
            elif i == len(sorted_events) - 1:
                timeline += f"{'':12} |\n"
                timeline += f"{date_str:12} {symbol} {description}\n"
            else:
                timeline += f"{'':12} |\n"
                timeline += f"{date_str:12} {symbol} {description}\n"

        timeline += "```\n\n"
        return timeline

    def generate_game_flow_timeline(
        self,
        game_events: List[Dict],
        home_team: str,
        away_team: str
    ) -> str:
        """Generate a timeline for key moments in a game"""
        timeline = f"\n### Game Flow: {away_team} @ {home_team}\n\n"
        timeline += "```\n"

        for event in game_events:
            quarter = event.get('quarter', 'Q1')
            time = event.get('time', '0:00')
            team = event.get('team', '')
            action = event.get('action', '')
            score = event.get('score', '')

            timeline += f"[{quarter:3} {time:5}] {team:20} {action:30} ({score})\n"

        timeline += "```\n\n"
        return timeline

    def generate_streak_timeline(
        self,
        team_name: str,
        games: List[Dict],
        limit: int = 10
    ) -> str:
        """Generate a visual timeline of team's recent results"""
        timeline = f"\n### {team_name} Last {min(limit, len(games))} Games\n\n"
        timeline += "```\n"

        recent_games = games[:limit]

        for i, game in enumerate(recent_games):
            date = game.get('date', datetime.now())
            opponent = game.get('opponent', 'Unknown')
            result = game.get('result', 'L')  # W or L
            score = game.get('score', '0-0')

            # Symbol based on result
            symbol = self.timeline_symbols['win'] if result == 'W' else self.timeline_symbols['loss']

            # Format date
            date_str = date.strftime('%b %d') if isinstance(date, datetime) else str(date)

            timeline += f"{date_str:10} {symbol} vs {opponent:20} ({score})\n"

        timeline += "```\n\n"
        return timeline

    def generate_player_career_timeline(
        self,
        player_name: str,
        milestones: List[Dict]
    ) -> str:
        """Generate a timeline of player career milestones"""
        timeline = f"\n### {player_name} Career Timeline\n\n"
        timeline += "```\n"

        for milestone in milestones:
            year = milestone.get('year', '????')
            event = milestone.get('event', 'Event')
            team = milestone.get('team', '')
            symbol = self.timeline_symbols.get(milestone.get('type', 'milestone'), '•')

            if team:
                timeline += f"{year:6} {symbol} {event:40} [{team}]\n"
            else:
                timeline += f"{year:6} {symbol} {event}\n"

        timeline += "```\n\n"
        return timeline

    def generate_playoff_bracket_timeline(
        self,
        rounds: List[Dict],
        sport: str = "NBA"
    ) -> str:
        """Generate a playoff bracket timeline"""
        timeline = f"\n## {sport} Playoff Timeline\n\n"

        for round_data in rounds:
            round_name = round_data.get('name', 'Round')
            matchups = round_data.get('matchups', [])

            timeline += f"\n### {round_name}\n\n"
            timeline += "```\n"

            for matchup in matchups:
                team1 = matchup.get('team1', 'TBD')
                team2 = matchup.get('team2', 'TBD')
                winner = matchup.get('winner', '')
                series_score = matchup.get('series', '')

                if winner:
                    winner_symbol = '→'
                    if winner == team1:
                        timeline += f"{team1:20} {winner_symbol}\n"
                        timeline += f"                     vs {series_score}\n"
                        timeline += f"{team2:20}\n"
                    else:
                        timeline += f"{team1:20}\n"
                        timeline += f"                     vs {series_score}\n"
                        timeline += f"{team2:20} {winner_symbol}\n"
                else:
                    timeline += f"{team1:20}\n"
                    timeline += f"        vs\n"
                    timeline += f"{team2:20}\n"

                timeline += "\n"

            timeline += "```\n"

        return timeline

    def generate_injury_timeline(
        self,
        player_name: str,
        injury_history: List[Dict]
    ) -> str:
        """Generate timeline of player injuries"""
        timeline = f"\n### {player_name} Injury History\n\n"
        timeline += "```\n"

        for injury in injury_history:
            date = injury.get('date', datetime.now())
            injury_type = injury.get('type', 'Injury')
            status = injury.get('status', 'Unknown')
            duration = injury.get('duration', 'Unknown')

            date_str = date.strftime('%b %d, %Y') if isinstance(date, datetime) else str(date)
            symbol = self.timeline_symbols['injury']

            timeline += f"{date_str:15} {symbol} {injury_type:25} ({status}, {duration})\n"

        timeline += "```\n\n"
        return timeline

    def generate_trade_deadline_timeline(
        self,
        trades: List[Dict],
        deadline_date: datetime
    ) -> str:
        """Generate timeline of trades leading up to deadline"""
        timeline = f"\n## Trade Deadline Timeline\n"
        timeline += f"*Deadline: {deadline_date.strftime('%B %d, %Y')}*\n\n"
        timeline += "```\n"

        for trade in sorted(trades, key=lambda x: x.get('date', datetime.now())):
            date = trade.get('date', datetime.now())
            player = trade.get('player', 'Unknown')
            from_team = trade.get('from', 'Team A')
            to_team = trade.get('to', 'Team B')

            date_str = date.strftime('%b %d') if isinstance(date, datetime) else str(date)
            symbol = self.timeline_symbols['trade']

            days_before = (deadline_date - date).days if isinstance(date, datetime) else 0

            timeline += f"{date_str:10} {symbol} {player:20} {from_team:15} → {to_team:15} "
            timeline += f"(D-{days_before})\n"

        timeline += "```\n\n"
        return timeline

    def generate_compact_visual_timeline(
        self,
        events: List[str],
        labels: List[str] = None
    ) -> str:
        """Generate a compact visual-only timeline"""
        if labels and len(labels) != len(events):
            labels = None

        timeline = "\n"

        # Visual line
        visual = "●"
        for i, event in enumerate(events[:-1]):
            visual += "─────●"

        timeline += visual + "\n"

        # Labels
        if labels:
            label_line = ""
            for label in labels:
                label_line += f"{label[:5]:^6}"
            timeline += label_line + "\n"

        timeline += "\n"
        return timeline

    def generate_markdown_timeline(
        self,
        storylines: List[Dict],
        title: str = "Major Storylines"
    ) -> str:
        """Generate a rich markdown timeline with multiple storylines"""
        timeline = f"\n## 📊 {title}\n\n"

        for storyline in storylines:
            story_title = storyline.get('title', 'Storyline')
            events = storyline.get('events', [])
            timeline += f"\n### {story_title}\n\n"

            for event in events:
                date = event.get('date', '')
                description = event.get('description', '')
                impact = event.get('impact', '')
                event_type = event.get('type', 'milestone')

                symbol = self.timeline_symbols.get(event_type, '•')

                timeline += f"- **{date}** {symbol} {description}\n"
                if impact:
                    timeline += f"  *Impact: {impact}*\n"

        return timeline
