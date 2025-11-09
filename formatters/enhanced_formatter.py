"""
Enhanced Formatter for SportStatBot
Provides advanced presentation features including themes, colors, and rich formatting
"""

from datetime import datetime
from typing import Dict, List, Optional
from presentation_config import (
    PresentationConfig, ToneLevel, StyleTheme, Colors,
    get_random_opener, HEADER_TEMPLATES, SECTION_DIVIDERS
)
from config import SPORTS_CONFIG


class EnhancedFormatter:
    """Enhanced formatter with presentation features"""

    def __init__(self, config: Optional[PresentationConfig] = None):
        """Initialize with presentation configuration"""
        self.config = config or PresentationConfig()

    def format_full_report(self, data: Dict, date: str = None) -> str:
        """Format a complete multi-sport report with enhanced presentation"""
        if date is None:
            date = datetime.now().strftime('%B %d, %Y')

        # Track credits
        self.config.add_credit('formatter', 'Full Report Generation')

        # Build report
        report = self._format_main_header(date)

        for sport, sport_data in data.items():
            if sport_data and sport_data.get('trends') or sport_data.get('recent_games'):
                report += self._format_sport_section(sport, sport_data)

        # Add credits if enabled
        report += self.config.get_credits_section()

        # Add footer
        report += self._format_footer(date)

        return report

    def _format_main_header(self, date: str) -> str:
        """Generate main report header with theme styling"""
        trophy = self.config.get_emoji('trophy')

        if self.config.theme == StyleTheme.ESPN:
            header = f"\n{trophy * 3} SPORTS REPORT - {date.upper()} {trophy * 3}\n"
            header += "═" * 70 + "\n"
        elif self.config.theme == StyleTheme.THE_ATHLETIC:
            header = f"\n# The Daily Briefing\n"
            header += f"*{date}*\n"
            header += "─" * 70 + "\n"
        elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
            header = f"\n# Statistical Sports Digest\n"
            header += f"## {date}\n"
            header += "─" * 70 + "\n"
        elif self.config.theme == StyleTheme.BLEACHER_REPORT:
            header = f"\n{trophy} THE BUZZ - {date.upper()} {trophy}\n"
            header += "▬" * 70 + "\n"
        else:
            header = f"\n# Sports Report - {date}\n"
            header += "═" * 70 + "\n"

        return header

    def _format_sport_section(self, sport: str, data: Dict) -> str:
        """Format a single sport section with theme-specific styling"""
        sport_config = SPORTS_CONFIG.get(sport, {})
        sport_name = sport_config.get('display_name', sport.upper())
        sport_emoji = sport_config.get('emoji', '')

        # Track credit
        self.config.add_credit('game_analyzer', f'{sport_name} Analysis')

        # Generate header
        header_template = self.config.get_header_template()
        section = header_template.format(
            sport_emoji=sport_emoji,
            sport_name=sport_name,
            date=datetime.now().strftime('%B %d, %Y')
        )

        # Add random opener if enabled
        opener = self.config.get_opener(sport)
        if opener:
            section += f"\n{opener}\n\n"

        # Add sections based on available data
        if data.get('trends'):
            section += self._format_trends(data['trends'])

        if data.get('recent_games'):
            section += self._format_recent_games(data['recent_games'], sport)

        if data.get('standout_players'):
            section += self._format_standout_players(data['standout_players'], sport)

        if data.get('injuries') or data.get('roster_changes'):
            section += self._format_injury_roster_updates(
                data.get('injuries', []),
                data.get('roster_changes', [])
            )

        if data.get('betting_insights'):
            section += self._format_betting_insights(data['betting_insights'])

        if data.get('must_watch'):
            section += self._format_must_watch(data['must_watch'], sport)

        # Add section divider
        section += "\n" + self.config.style['section_divider'] + "\n"

        return section

    def _format_trends(self, trends: List[str]) -> str:
        """Format trends section with color coding"""
        if not trends:
            return ""

        fire = self.config.get_emoji('fire')
        cold = self.config.get_emoji('cold')
        chart_up = self.config.get_emoji('chart_up')

        section = f"\n### {chart_up} Key Trends\n\n"

        for trend in trends:
            # Apply color coding for hot/cold streaks
            if 'won' in trend.lower() or 'winning' in trend.lower():
                # Extract wins if possible (simplified)
                formatted_trend = self.config.colorize_streak(trend, wins=3, losses=0)
                section += f"• {fire} {formatted_trend}\n"
            elif 'lost' in trend.lower() or 'losing' in trend.lower():
                formatted_trend = self.config.colorize_streak(trend, wins=0, losses=3)
                section += f"• {cold} {formatted_trend}\n"
            else:
                section += f"• {trend}\n"

        return section + "\n"

    def _format_recent_games(self, games: List[Dict], sport: str) -> str:
        """Format recent games with theme-specific styling"""
        if not games:
            return ""

        calendar = self.config.get_emoji('calendar')
        warning = self.config.get_emoji('warning')
        boom = self.config.get_emoji('boom')

        section = f"\n### {calendar} Recent Results\n\n"

        for game in games[:10]:  # Limit to top 10
            home_team = game.get('home_team', 'Home')
            away_team = game.get('away_team', 'Away')
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)
            notes = game.get('notes', [])

            # Determine winner and style accordingly
            if home_score > away_score:
                winner = home_team
                loser = away_team
                winner_score = home_score
                loser_score = away_score
            else:
                winner = away_team
                loser = home_team
                winner_score = away_score
                loser_score = home_score

            # Format based on theme
            if self.config.theme == StyleTheme.ESPN:
                game_line = f"**{winner}** {winner_score}, {loser} {loser_score}"
            elif self.config.theme == StyleTheme.THE_ATHLETIC:
                margin = abs(home_score - away_score)
                game_line = f"{winner} defeats {loser} ({winner_score}-{loser_score})"
            elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
                margin = abs(home_score - away_score)
                game_line = f"{winner} {winner_score}-{loser_score} {loser} (Margin: {margin})"
            elif self.config.theme == StyleTheme.BLEACHER_REPORT:
                game_line = f"{boom} **{winner}** BEATS {loser} {winner_score}-{loser_score}"
            else:
                game_line = f"**{winner}** {winner_score}-{loser_score} {loser}"

            # Add upset indicator
            if any('upset' in note.lower() for note in notes):
                game_line = f"{warning} {game_line} **(UPSET)**"

            section += f"• {game_line}\n"

            # Add game leaders if available
            if game.get('leaders'):
                leaders = game['leaders']
                if self.config.style['emphasize_highlights']:
                    for leader in leaders[:2]:  # Top 2 leaders
                        section += f"  ↳ {leader}\n"

        return section + "\n"

    def _format_standout_players(self, players: List[Dict], sport: str) -> str:
        """Format standout players section"""
        if not players:
            return ""

        star = self.config.get_emoji('star')
        rocket = self.config.get_emoji('rocket')

        section = f"\n### {star} Standout Performers\n\n"

        # Track credit
        self.config.add_credit('player_analyzer', 'Standout Players')

        for player in players[:8]:  # Top 8 players
            name = player.get('name', 'Unknown')
            team = player.get('team', '')
            stats = player.get('stats', '')

            if self.config.theme == StyleTheme.ESPN:
                line = f"{rocket} **{name}** ({team}): {stats}"
            elif self.config.theme == StyleTheme.THE_ATHLETIC:
                line = f"**{name}** ({team}) — {stats}"
            elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
                line = f"{name} ({team}): {stats}"
            elif self.config.theme == StyleTheme.BLEACHER_REPORT:
                line = f"{rocket} {rocket} **{name.upper()}** ({team}): {stats}"
            else:
                line = f"• **{name}** ({team}): {stats}"

            section += f"{line}\n"

        return section + "\n"

    def _format_injury_roster_updates(self, injuries: List[Dict], roster_changes: List[Dict]) -> str:
        """Format injuries and roster changes"""
        if not injuries and not roster_changes:
            return ""

        injury_emoji = self.config.get_emoji('injury')
        new_emoji = self.config.get_emoji('new')

        section = ""

        # Track credit
        self.config.add_credit('player_analyzer', 'Injury & Roster Updates')

        if injuries:
            section += f"\n### {injury_emoji} Injury Report\n\n"
            for injury in injuries[:5]:  # Top 5
                player = injury.get('player', 'Unknown')
                team = injury.get('team', '')
                status = injury.get('status', 'Unknown')
                section += f"• **{player}** ({team}): {status}\n"
            section += "\n"

        if roster_changes:
            section += f"\n### {new_emoji} Roster Moves\n\n"
            for change in roster_changes[:5]:  # Top 5
                player = change.get('player', 'Unknown')
                team = change.get('team', '')
                move_type = change.get('type', 'Update')
                section += f"• **{player}** ({team}): {move_type}\n"
            section += "\n"

        return section

    def _format_betting_insights(self, insights: Dict) -> str:
        """Format betting insights"""
        if not insights:
            return ""

        money = self.config.get_emoji('moneybag')
        section = f"\n### {money} Betting Insights\n\n"

        # Track credit
        self.config.add_credit('odds_analyzer', 'Betting Analysis')

        if insights.get('value_bets'):
            section += "**Value Opportunities:**\n"
            for bet in insights['value_bets'][:3]:
                section += f"• {bet}\n"
            section += "\n"

        if insights.get('line_moves'):
            section += "**Notable Line Movements:**\n"
            for move in insights['line_moves'][:3]:
                section += f"• {move}\n"
            section += "\n"

        return section

    def _format_must_watch(self, games: List[Dict], sport: str) -> str:
        """Format must-watch games"""
        if not games:
            return ""

        eyes = self.config.get_emoji('eyes')
        section = f"\n### {eyes} Must-Watch Matchups\n\n"

        for game in games[:5]:  # Top 5
            home = game.get('home_team', 'Home')
            away = game.get('away_team', 'Away')
            time = game.get('time', 'TBD')
            reason = game.get('reason', '')

            if self.config.theme == StyleTheme.BLEACHER_REPORT:
                line = f"{eyes} **{away} @ {home}** — {time}"
            else:
                line = f"• **{away} @ {home}** — {time}"

            if reason:
                line += f"\n  ↳ {reason}"

            section += f"{line}\n"

        return section + "\n"

    def _format_footer(self, date: str) -> str:
        """Format report footer"""
        checkmark = self.config.get_emoji('checkmark')

        footer = f"\n{self.config.style['section_divider']}\n"
        footer += f"{checkmark} Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return footer

    def format_sport_quick_update(self, sport: str, data: Dict) -> str:
        """Format a quick sport update"""
        sport_config = SPORTS_CONFIG.get(sport, {})
        sport_name = sport_config.get('display_name', sport.upper())
        sport_emoji = sport_config.get('emoji', '')

        rocket = self.config.get_emoji('rocket')

        update = f"\n{rocket} **{sport_emoji} {sport_name} Quick Update**\n\n"

        # Top result
        if data.get('recent_games'):
            game = data['recent_games'][0]
            update += f"Latest: **{game.get('away_team')}** {game.get('away_score')} @ "
            update += f"**{game.get('home_team')}** {game.get('home_score')}\n\n"

        # Top player
        if data.get('standout_players'):
            player = data['standout_players'][0]
            update += f"Standout: **{player.get('name')}** ({player.get('team')}) — {player.get('stats')}\n"

        return update
