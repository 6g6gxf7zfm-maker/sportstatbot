"""
Footnote Inserter - Add source citations and data footnotes
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class FootnoteInserter:
    """Insert footnotes with data sources and timestamps"""

    def __init__(self):
        self.footnotes = []
        self.footnote_counter = 1

    def add_footnote(
        self,
        text: str,
        source: str,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Add a footnote to text

        Args:
            text: Text to add footnote to
            source: Source name (e.g., "ESPN API")
            url: Optional source URL
            timestamp: Optional data timestamp

        Returns:
            Text with footnote marker
        """
        footnote_marker = f"[^{self.footnote_counter}]"

        # Build footnote content
        footnote_content = f"[^{self.footnote_counter}]: Source: {source}"

        if url:
            footnote_content += f" ({url})"

        if timestamp:
            time_str = timestamp.strftime("%Y-%m-%d %H:%M %Z")
            footnote_content += f" - Data as of {time_str}"

        self.footnotes.append(footnote_content)
        self.footnote_counter += 1

        return f"{text}{footnote_marker}"

    def add_stat_footnote(
        self,
        stat_text: str,
        source: str = "ESPN API",
        additional_info: Optional[str] = None
    ) -> str:
        """
        Add footnote specifically for statistics

        Args:
            stat_text: Statistical text
            source: Data source
            additional_info: Optional additional context

        Returns:
            Text with footnote
        """
        timestamp = datetime.now()
        footnote = self.add_footnote(stat_text, source, timestamp=timestamp)

        if additional_info:
            # Add inline context
            footnote = f"{stat_text} ({additional_info})[^{self.footnote_counter-1}]"

        return footnote

    def auto_footnote_stats(
        self,
        text: str,
        sources: Dict[str, str],
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Automatically add footnotes to statistics in text

        Args:
            text: Text containing stats
            sources: Dictionary mapping stat types to sources
            timestamp: Optional timestamp for all stats

        Returns:
            Text with auto-inserted footnotes
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Look for common stat patterns and add footnotes
        import re

        # Pattern for numbers followed by stat categories
        stat_pattern = re.compile(
            r'(\d+\.?\d*)\s+(points|rebounds|assists|yards|touchdowns|goals|saves|strikeouts|home runs)',
            re.IGNORECASE
        )

        def add_footnote_to_stat(match):
            stat_text = match.group(0)
            category = match.group(2).lower()

            # Determine source
            source = sources.get(category, sources.get('default', 'Sports API'))

            return self.add_footnote(stat_text, source, timestamp=timestamp)

        return stat_pattern.sub(add_footnote_to_stat, text)

    def insert_data_provenance(
        self,
        context: Dict[str, Any],
        sport: str
    ) -> str:
        """
        Create data provenance section

        Args:
            context: Story context with data sources
            sport: Sport name

        Returns:
            Formatted provenance section
        """
        timestamp = datetime.now()

        provenance = "\n\n---\n"
        provenance += "### Data Sources & Timestamps\n\n"

        # List data sources
        sources = self._extract_sources(context)

        for source_name, source_info in sources.items():
            provenance += f"• **{source_name}**: "

            if source_info.get('url'):
                provenance += f"[{source_info['url']}]({source_info['url']}) "

            provenance += f"(accessed {timestamp.strftime('%Y-%m-%d %H:%M %Z')})\n"

        # Add update frequency
        provenance += f"\n_Data updates every 15 minutes during {sport} season_\n"

        provenance += "---\n"

        return provenance

    def get_footnotes_section(self) -> str:
        """
        Get formatted footnotes section

        Returns:
            Formatted footnotes for appending to document
        """
        if not self.footnotes:
            return ""

        section = "\n\n---\n### Notes\n\n"
        section += '\n'.join(self.footnotes)
        section += "\n---\n"

        return section

    def reset_footnotes(self):
        """Reset footnote counter and list"""
        self.footnotes = []
        self.footnote_counter = 1

    def _extract_sources(self, context: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract data sources from context"""
        sources = {}

        # Default sources
        sources['ESPN API'] = {
            'url': 'https://www.espn.com',
            'description': 'Scores, standings, and statistics'
        }

        # Add betting source if present
        if context.get('betting_insights'):
            sources['The Odds API'] = {
                'url': 'https://the-odds-api.com',
                'description': 'Betting odds and lines'
            }

        # Add sport-specific sources
        sport = context.get('sport', '').lower()
        if sport == 'mlb':
            sources['MLB Stats API'] = {
                'url': 'https://statsapi.mlb.com',
                'description': 'Official MLB statistics'
            }
        elif sport == 'nhl':
            sources['NHL API'] = {
                'url': 'https://api-web.nhle.com',
                'description': 'Official NHL statistics'
            }

        return sources

    def add_methodology_note(self, methodology: str) -> str:
        """
        Add methodology footnote

        Args:
            methodology: Description of analysis methodology

        Returns:
            Footnote marker
        """
        return self.add_footnote("Analysis", methodology)

    def create_source_legend(
        self,
        sources: List[str]
    ) -> str:
        """
        Create legend for data sources

        Args:
            sources: List of source names

        Returns:
            Formatted source legend
        """
        legend = "\n### Source Legend\n\n"

        source_abbrev = {
            'ESPN API': 'ESPN',
            'The Odds API': 'ODDS',
            'MLB Stats API': 'MLB',
            'NHL API': 'NHL'
        }

        for source in sources:
            abbrev = source_abbrev.get(source, source[:4].upper())
            legend += f"• **{abbrev}**: {source}\n"

        return legend
