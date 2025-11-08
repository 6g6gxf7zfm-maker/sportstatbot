"""Slack markdown report formatter."""
from typing import Dict, List, Optional
from datetime import datetime
import config


class SlackFormatter:
    """Formats sports analysis reports for Slack markdown."""

    def __init__(self):
        self.emoji = {
            'fire': '🔥',
            'cold': '❄️',
            'warning': '⚠️',
            'trophy': '🏆',
            'chart_up': '📈',
            'chart_down': '📉',
            'star': '⭐',
            'moneybag': '💰',
            'eyes': '👀',
            'calendar': '📅',
            'injury': '🏥',
            'new': '🆕'
        }

    def format_full_report(self, all_sports_data: Dict) -> str:
        """
        Format a complete sports report for all leagues.

        Args:
            all_sports_data: Dictionary with data for all sports

        Returns:
            Formatted Slack markdown string
        """
        report_sections = []

        # Header
        now = datetime.now()
        report_sections.append(f"# {self.emoji['trophy']} SPORTS UPDATE - {now.strftime('%B %d, %Y')}\n")
        report_sections.append(f"_Your daily sports briefing covering all the action_\n")
        report_sections.append("---\n")

        # Generate report for each sport
        for sport, data in all_sports_data.items():
            if data and data.get('enabled', True):
                sport_config = config.SPORTS_CONFIG.get(sport, {})
                sport_section = self._format_sport_section(sport, data, sport_config)
                if sport_section:
                    report_sections.append(sport_section)
                    report_sections.append("\n---\n")

        # Footer
        report_sections.append(f"\n_Report generated at {now.strftime('%I:%M %p ET')}_")

        return "\n".join(report_sections)

    def _format_sport_section(self, sport: str, data: Dict, sport_config: Dict) -> str:
        """Format a single sport's section."""
        sections = []

        # Sport header
        emoji = sport_config.get('emoji', '🏀')
        display_name = sport_config.get('display_name', sport.upper())
        sections.append(f"\n## {emoji} {display_name} UPDATE\n")

        # Key trends
        if data.get('trends'):
            sections.append(self._format_trends(data['trends']))

        # Recent results
        if data.get('recent_games'):
            sections.append(self._format_recent_games(data['recent_games']))

        # Standout players
        if data.get('standout_players'):
            sections.append(self._format_standout_players(data['standout_players']))

        # Injuries and roster changes
        if data.get('injuries') or data.get('roster_changes'):
            sections.append(self._format_injury_roster_updates(data.get('injuries', []),
                                                                 data.get('roster_changes', [])))

        # Betting insights
        if data.get('betting_insights'):
            sections.append(self._format_betting_insights(data['betting_insights']))

        # Must-watch matchups
        if data.get('must_watch'):
            sections.append(self._format_must_watch(data['must_watch']))

        return "\n".join(sections)

    def _format_trends(self, trends: List[Dict]) -> str:
        """Format team trends section."""
        if not trends:
            return ""

        lines = [f"\n### {self.emoji['chart_up']} KEY TRENDS\n"]

        hot_streaks = [t for t in trends if t.get('type') == 'hot_streak']
        cold_streaks = [t for t in trends if t.get('type') == 'cold_streak']

        if hot_streaks:
            lines.append(f"**{self.emoji['fire']} Hot Teams:**")
            for trend in hot_streaks[:5]:
                lines.append(f"• **{trend['team']}** - {trend['description']}")

        if cold_streaks:
            lines.append(f"\n**{self.emoji['cold']} Cold Teams:**")
            for trend in cold_streaks[:5]:
                lines.append(f"• **{trend['team']}** - {trend['description']}")

        return "\n".join(lines)

    def _format_recent_games(self, games: List[Dict]) -> str:
        """Format recent game results."""
        if not games:
            return ""

        lines = [f"\n### {self.emoji['calendar']} RECENT RESULTS\n"]

        # Show highlights first
        highlights = [g for g in games if g.get('is_upset') or g.get('is_blowout') or g.get('is_close')]

        if highlights:
            lines.append("**Notable Games:**")
            for game in highlights[:5]:
                status_emoji = ""
                if game.get('is_upset'):
                    status_emoji = f" {self.emoji['warning']}"
                elif game.get('is_blowout'):
                    status_emoji = f" {self.emoji['fire']}"
                elif game.get('is_close'):
                    status_emoji = f" {self.emoji['eyes']}"

                winner = game.get('winner', 'TBD')
                loser = game.get('loser', 'TBD')
                winner_score = game.get('winner_score', 0)
                loser_score = game.get('loser_score', 0)

                lines.append(f"• **{winner}** {winner_score}, {loser} {loser_score}{status_emoji}")

                # Add game leaders if available
                if game.get('leaders'):
                    leaders_text = self._format_game_leaders(game['leaders'])
                    if leaders_text:
                        lines.append(f"  _{leaders_text}_")

        return "\n".join(lines)

    def _format_game_leaders(self, leaders: Dict) -> str:
        """Format game statistical leaders."""
        leader_strings = []

        for category, leader_info in list(leaders.items())[:2]:  # Top 2 categories
            name = leader_info.get('name', 'Unknown')
            value = leader_info.get('value', 'N/A')
            leader_strings.append(f"{name}: {value}")

        return " | ".join(leader_strings)

    def _format_standout_players(self, players: List[Dict]) -> str:
        """Format standout player performances."""
        if not players:
            return ""

        lines = [f"\n### {self.emoji['star']} STANDOUT PERFORMANCES\n"]

        for player in players[:8]:  # Top 8 players
            name = player.get('player', 'Unknown')
            team = player.get('team', 'Unknown')
            stat = player.get('stat_category', '')
            value = player.get('value', '')

            lines.append(f"• **{name}** ({team}) - {value} {stat}")

        return "\n".join(lines)

    def _format_injury_roster_updates(self, injuries: List[Dict], roster_changes: List[Dict]) -> str:
        """Format injury and roster change updates."""
        if not injuries and not roster_changes:
            return ""

        lines = [f"\n### {self.emoji['warning']} INJURY & ROSTER UPDATES\n"]

        if injuries:
            lines.append(f"**{self.emoji['injury']} Injuries:**")
            for injury in injuries[:5]:
                headline = injury.get('headline', 'Unknown')
                lines.append(f"• {headline}")

        if roster_changes:
            lines.append(f"\n**{self.emoji['new']} Roster Moves:**")
            for change in roster_changes[:5]:
                headline = change.get('headline', 'Unknown')
                lines.append(f"• {headline}")

        return "\n".join(lines)

    def _format_betting_insights(self, betting_data: Dict) -> str:
        """Format betting insights and odds."""
        if not betting_data:
            return ""

        lines = [f"\n### {self.emoji['moneybag']} BETTING INSIGHTS\n"]

        # Value bets
        if betting_data.get('value_bets'):
            lines.append("**Value Picks:**")
            for bet in betting_data['value_bets'][:3]:
                game = bet.get('game', 'Unknown')
                rec = bet.get('recommendation', '')
                odds = bet.get('odds', '')
                reason = bet.get('reason', '')

                lines.append(f"• **{game}**")
                lines.append(f"  {rec} ({odds}) - _{reason}_")

        # Featured odds
        if betting_data.get('featured_games'):
            lines.append("\n**Featured Lines:**")
            for game in betting_data['featured_games'][:5]:
                matchup = game.get('matchup', 'Unknown')
                spread = game.get('spread', 'N/A')
                total = game.get('total', 'N/A')

                lines.append(f"• **{matchup}** - Spread: {spread} | O/U: {total}")

        if not betting_data.get('value_bets') and not betting_data.get('featured_games'):
            lines.append("_Betting data unavailable - configure ODDS_API_KEY in .env_")

        return "\n".join(lines)

    def _format_must_watch(self, matchups: List[Dict]) -> str:
        """Format must-watch upcoming matchups."""
        if not matchups:
            return ""

        lines = [f"\n### {self.emoji['eyes']} MUST-WATCH MATCHUPS\n"]

        for matchup in matchups[:5]:
            game = matchup.get('game', 'Unknown')
            date_str = self._format_game_date(matchup.get('date'))
            reasons = matchup.get('reasons', [])

            lines.append(f"• **{game}** - {date_str}")
            if reasons:
                lines.append(f"  _{', '.join(reasons)}_")

        return "\n".join(lines)

    def _format_game_date(self, date_str: Optional[str]) -> str:
        """Format game date/time for display."""
        if not date_str:
            return "TBD"

        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%a %I:%M %p")
        except Exception:
            return "TBD"

    def format_sport_quick_update(self, sport: str, data: Dict) -> str:
        """
        Format a quick update for a single sport.

        Args:
            sport: Sport key
            data: Sport data dictionary

        Returns:
            Formatted quick update
        """
        sport_config = config.SPORTS_CONFIG.get(sport, {})
        emoji = sport_config.get('emoji', '🏀')
        display_name = sport_config.get('display_name', sport.upper())

        lines = [f"## {emoji} {display_name} Quick Update\n"]

        # Most important info only
        if data.get('recent_games'):
            top_games = [g for g in data['recent_games'] if g.get('is_upset') or g.get('is_close')][:3]
            if top_games:
                lines.append("**Top Results:**")
                for game in top_games:
                    winner = game.get('winner', 'TBD')
                    loser = game.get('loser', 'TBD')
                    winner_score = game.get('winner_score', 0)
                    loser_score = game.get('loser_score', 0)
                    lines.append(f"• {winner} {winner_score}, {loser} {loser_score}")

        if data.get('standout_players'):
            lines.append(f"\n**{self.emoji['star']} Top Performer:**")
            player = data['standout_players'][0]
            lines.append(f"• **{player['player']}** - {player['value']} {player['stat_category']}")

        return "\n".join(lines)
