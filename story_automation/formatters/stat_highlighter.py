"""
Stat Highlighter - Inline stat highlighting with colors
"""

import re
from typing import Dict, List, Any, Tuple, Optional


class StatHighlighter:
    """Highlight statistics inline with colors and formatting"""

    # Color schemes for different contexts
    COLOR_SCHEMES = {
        'performance': {
            'high': '#4CAF50',  # Green
            'medium': '#FFC107',  # Amber
            'low': '#F44336'  # Red
        },
        'trend': {
            'positive': '#4CAF50',  # Green
            'neutral': '#9E9E9E',  # Grey
            'negative': '#F44336'  # Red
        },
        'betting': {
            'value': '#4CAF50',  # Green
            'even': '#2196F3',  # Blue
            'risk': '#F44336'  # Red
        }
    }

    # Emoji indicators
    EMOJI_INDICATORS = {
        'up': '📈',
        'down': '📉',
        'hot': '🔥',
        'cold': '❄️',
        'star': '⭐',
        'warning': '⚠️'
    }

    def __init__(self):
        # Regex patterns for detecting stats
        self.number_pattern = re.compile(r'\b(\d+\.?\d*)\b')
        self.percentage_pattern = re.compile(r'(\d+\.?\d*%)')
        self.stat_pattern = re.compile(r'(\d+\.?\d*)\s+([a-zA-Z]+)')

    def highlight_stats(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        format_type: str = 'markdown'
    ) -> str:
        """
        Highlight statistics in text

        Args:
            text: Text containing statistics
            context: Optional context for intelligent highlighting
            format_type: Output format (markdown, html, ansi)

        Returns:
            Text with highlighted statistics
        """
        if format_type == 'markdown':
            return self._highlight_markdown(text, context)
        elif format_type == 'html':
            return self._highlight_html(text, context)
        elif format_type == 'ansi':
            return self._highlight_ansi(text, context)
        else:
            return text

    def colorize_highs_lows(
        self,
        text: str,
        thresholds: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Auto-colorize high and low values

        Args:
            text: Text containing numbers
            thresholds: Optional thresholds for high/medium/low

        Returns:
            Text with colorized numbers
        """
        if thresholds is None:
            thresholds = {'high': 30, 'medium': 15}

        def colorize_number(match):
            number = float(match.group(1))

            if number >= thresholds['high']:
                return f"**🔥 {match.group(1)}**"
            elif number >= thresholds['medium']:
                return f"**{match.group(1)}**"
            else:
                return f"_{match.group(1)}_"

        return self.number_pattern.sub(colorize_number, text)

    def add_stat_indicators(
        self,
        text: str,
        stat_type: str = 'performance'
    ) -> str:
        """
        Add emoji indicators to stats

        Args:
            text: Text containing stats
            stat_type: Type of stats (performance, trend, betting)

        Returns:
            Text with emoji indicators
        """
        # Look for specific keywords
        patterns = {
            'increase|up|gain|rise': self.EMOJI_INDICATORS['up'],
            'decrease|down|drop|fall': self.EMOJI_INDICATORS['down'],
            'hot|streak|win': self.EMOJI_INDICATORS['hot'],
            'cold|slump|lose': self.EMOJI_INDICATORS['cold'],
            'star|standout|lead': self.EMOJI_INDICATORS['star']
        }

        for pattern, emoji in patterns.items():
            text = re.sub(
                f'({pattern})',
                f'{emoji} \\1',
                text,
                flags=re.IGNORECASE
            )

        return text

    def highlight_player_stats(
        self,
        players: List[Dict[str, Any]],
        format_type: str = 'markdown'
    ) -> str:
        """
        Format player statistics with highlighting

        Args:
            players: List of player stat dictionaries
            format_type: Output format

        Returns:
            Formatted player stats
        """
        output = ""

        for player in players:
            name = player.get('player', '')
            team = player.get('team', '')
            stat = player.get('stat_category', '')
            value = player.get('value', '')

            if format_type == 'markdown':
                output += f"• **{name}** ({team}): **{value}** {stat} 📊\n"
            elif format_type == 'html':
                output += f'<li><strong>{name}</strong> ({team}): '
                output += f'<span class="highlight">{value}</span> {stat} 📊</li>\n'
            else:
                output += f"• {name} ({team}): {value} {stat}\n"

        return output

    def highlight_comparison(
        self,
        current: float,
        previous: float,
        label: str = "stat"
    ) -> str:
        """
        Highlight stat comparison

        Args:
            current: Current value
            previous: Previous value
            label: Stat label

        Returns:
            Formatted comparison string
        """
        diff = current - previous
        percent_change = (diff / previous * 100) if previous != 0 else 0

        if diff > 0:
            indicator = self.EMOJI_INDICATORS['up']
            color = "green"
        elif diff < 0:
            indicator = self.EMOJI_INDICATORS['down']
            color = "red"
        else:
            indicator = "→"
            color = "grey"

        return (
            f"{label}: **{current:.1f}** "
            f"{indicator} ({diff:+.1f}, {percent_change:+.1f}%) "
            f"from {previous:.1f}"
        )

    def _highlight_markdown(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Highlight for markdown format"""
        # Bold important numbers
        text = re.sub(
            r'\b(\d{2,}\.?\d*)\b',
            r'**\1**',
            text
        )

        # Add emoji to percentages
        text = re.sub(
            r'(\d+\.?\d*%)',
            r'📊 **\1**',
            text
        )

        return text

    def _highlight_html(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Highlight for HTML format"""
        # Wrap numbers in span with class
        text = re.sub(
            r'\b(\d{2,}\.?\d*)\b',
            r'<span class="stat-highlight">\1</span>',
            text
        )

        return text

    def _highlight_ansi(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Highlight for ANSI terminal"""
        # ANSI color codes
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        RESET = '\033[0m'

        # Highlight numbers in bold
        text = re.sub(
            r'\b(\d{2,}\.?\d*)\b',
            f'{BOLD}\\1{RESET}',
            text
        )

        return text

    def extract_key_numbers(
        self,
        text: str,
        top_n: int = 3
    ) -> List[Tuple[str, str]]:
        """
        Extract key numbers from text

        Args:
            text: Text to analyze
            top_n: Number of key stats to extract

        Returns:
            List of (number, context) tuples
        """
        # Find all numbers with surrounding context
        pattern = re.compile(r'(.{0,30})(\d+\.?\d*)(.{0,30})')
        matches = pattern.findall(text)

        # Score based on size and context
        scored = []
        for before, number, after in matches:
            context = (before + number + after).strip()
            score = float(number)

            # Bonus for certain keywords
            if any(keyword in context.lower() for keyword in ['record', 'career', 'season']):
                score *= 1.5

            scored.append((score, number, context))

        # Sort by score and take top N
        scored.sort(reverse=True)
        return [(num, ctx) for _, num, ctx in scored[:top_n]]
