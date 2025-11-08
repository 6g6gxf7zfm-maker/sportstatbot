"""
Sidebar Generator - Dynamic sidebars for stories
"""

from typing import Dict, List, Any, Optional


class SidebarGenerator:
    """Generate dynamic sidebars for stories"""

    SIDEBAR_TYPES = [
        '3_numbers',      # "3 Numbers That Matter"
        'by_the_data',    # "By the Data"
        'key_stats',      # Key statistics
        'quick_facts',    # Quick facts
        'player_watch',   # Players to watch
        'betting_corner', # Betting insights
    ]

    def __init__(self):
        pass

    def generate_sidebars(
        self,
        context: Dict[str, Any],
        sport: str,
        types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate sidebars for a story

        Args:
            context: Story context data
            sport: Sport name
            types: Specific sidebar types to generate (None = all applicable)

        Returns:
            List of sidebar dictionaries
        """
        sidebars = []

        # Determine which sidebars to generate
        if types is None:
            types = self._determine_applicable_sidebars(context)

        for sidebar_type in types:
            sidebar = self._generate_sidebar(sidebar_type, context, sport)
            if sidebar:
                sidebars.append(sidebar)

        return sidebars

    def _determine_applicable_sidebars(self, context: Dict[str, Any]) -> List[str]:
        """Determine which sidebars are applicable based on available data"""
        applicable = []

        # "3 Numbers That Matter" - needs player stats
        if context.get('standout_players') and len(context['standout_players']) >= 3:
            applicable.append('3_numbers')

        # "By the Data" - needs trends
        if context.get('trends'):
            applicable.append('by_the_data')

        # "Key Stats" - always applicable
        applicable.append('key_stats')

        # "Player Watch" - needs standout players
        if context.get('standout_players'):
            applicable.append('player_watch')

        # "Betting Corner" - needs betting data
        if context.get('betting_insights'):
            applicable.append('betting_corner')

        return applicable

    def _generate_sidebar(
        self,
        sidebar_type: str,
        context: Dict[str, Any],
        sport: str
    ) -> Optional[Dict[str, Any]]:
        """Generate a specific sidebar type"""
        if sidebar_type == '3_numbers':
            return self._generate_3_numbers(context)
        elif sidebar_type == 'by_the_data':
            return self._generate_by_the_data(context)
        elif sidebar_type == 'key_stats':
            return self._generate_key_stats(context, sport)
        elif sidebar_type == 'quick_facts':
            return self._generate_quick_facts(context, sport)
        elif sidebar_type == 'player_watch':
            return self._generate_player_watch(context)
        elif sidebar_type == 'betting_corner':
            return self._generate_betting_corner(context)

        return None

    def _generate_3_numbers(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate '3 Numbers That Matter' sidebar"""
        players = context.get('standout_players', [])
        if len(players) < 3:
            return None

        numbers = []
        for player in players[:3]:
            numbers.append({
                'number': player.get('value', ''),
                'stat': player.get('stat_category', ''),
                'player': player.get('player', ''),
                'team': player.get('team', '')
            })

        return {
            'type': '3_numbers',
            'title': '📊 3 Numbers That Matter',
            'items': numbers
        }

    def _generate_by_the_data(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate 'By the Data' sidebar"""
        trends = context.get('trends', [])
        if not trends:
            return None

        data_points = []
        for trend in trends[:5]:
            data_points.append({
                'team': trend.get('team', ''),
                'stat': trend.get('description', ''),
                'type': trend.get('type', '')
            })

        return {
            'type': 'by_the_data',
            'title': '📈 By the Data',
            'items': data_points
        }

    def _generate_key_stats(
        self,
        context: Dict[str, Any],
        sport: str
    ) -> Dict[str, Any]:
        """Generate 'Key Stats' sidebar"""
        stats = []

        # Count various elements
        if context.get('trends'):
            stats.append({
                'label': 'Teams in Flux',
                'value': len(context['trends'])
            })

        if context.get('recent_games'):
            stats.append({
                'label': 'Games Analyzed',
                'value': len(context['recent_games'])
            })

        if context.get('standout_players'):
            stats.append({
                'label': 'Standout Performers',
                'value': len(context['standout_players'])
            })

        if context.get('injuries'):
            stats.append({
                'label': 'Injury Updates',
                'value': len(context['injuries'])
            })

        return {
            'type': 'key_stats',
            'title': '🔢 Key Stats',
            'items': stats
        }

    def _generate_quick_facts(
        self,
        context: Dict[str, Any],
        sport: str
    ) -> Dict[str, Any]:
        """Generate 'Quick Facts' sidebar"""
        facts = []

        # Extract interesting facts
        trends = context.get('trends', [])
        for trend in trends[:3]:
            if 'streak' in trend.get('description', '').lower():
                facts.append(trend.get('description', ''))

        return {
            'type': 'quick_facts',
            'title': '⚡ Quick Facts',
            'items': [{'fact': f} for f in facts]
        }

    def _generate_player_watch(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate 'Player Watch' sidebar"""
        players = context.get('standout_players', [])
        if not players:
            return None

        player_list = []
        for player in players[:5]:
            player_list.append({
                'player': player.get('player', ''),
                'team': player.get('team', ''),
                'reason': f"{player.get('value', '')} {player.get('stat_category', '')}"
            })

        return {
            'type': 'player_watch',
            'title': '👀 Players to Watch',
            'items': player_list
        }

    def _generate_betting_corner(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate 'Betting Corner' sidebar"""
        betting = context.get('betting_insights', {})
        if not betting:
            return None

        value_bets = betting.get('value_bets', [])
        if not value_bets:
            return None

        bets = []
        for bet in value_bets[:3]:
            bets.append({
                'game': bet.get('game', ''),
                'pick': bet.get('recommendation', ''),
                'odds': bet.get('odds', ''),
                'reasoning': bet.get('reasoning', '')
            })

        return {
            'type': 'betting_corner',
            'title': '💰 Betting Corner',
            'items': bets
        }

    def format_sidebar(self, sidebar: Dict[str, Any], format_type: str = 'markdown') -> str:
        """
        Format sidebar for output

        Args:
            sidebar: Sidebar data
            format_type: Output format (markdown, html, plain)

        Returns:
            Formatted sidebar string
        """
        if format_type == 'markdown':
            return self._format_markdown(sidebar)
        elif format_type == 'html':
            return self._format_html(sidebar)
        else:
            return self._format_plain(sidebar)

    def _format_markdown(self, sidebar: Dict[str, Any]) -> str:
        """Format sidebar as markdown"""
        output = f"\n---\n### {sidebar['title']}\n\n"

        sidebar_type = sidebar['type']
        items = sidebar.get('items', [])

        if sidebar_type == '3_numbers':
            for item in items:
                output += f"**{item['number']}** - {item['player']} ({item['team']}) - {item['stat']}\n"

        elif sidebar_type == 'by_the_data':
            for item in items:
                output += f"• **{item['team']}**: {item['stat']}\n"

        elif sidebar_type == 'key_stats':
            for item in items:
                output += f"• {item['label']}: **{item['value']}**\n"

        elif sidebar_type == 'player_watch':
            for item in items:
                output += f"• **{item['player']}** ({item['team']}): {item['reason']}\n"

        elif sidebar_type == 'betting_corner':
            for item in items:
                output += f"• **{item['game']}**: {item['pick']} ({item['odds']})\n"
                if item.get('reasoning'):
                    output += f"  _{item['reasoning']}_\n"

        output += "---\n"
        return output

    def _format_html(self, sidebar: Dict[str, Any]) -> str:
        """Format sidebar as HTML"""
        # Placeholder for HTML formatting
        return self._format_markdown(sidebar)

    def _format_plain(self, sidebar: Dict[str, Any]) -> str:
        """Format sidebar as plain text"""
        # Placeholder for plain text formatting
        return self._format_markdown(sidebar)
