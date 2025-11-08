"""
Summary Generator - TL;DR paragraph generation
"""

from typing import Dict, List, Any


class SummaryGenerator:
    """Generate concise TL;DR summaries for stories"""

    def __init__(self, max_sentences: int = 3):
        """
        Initialize summary generator

        Args:
            max_sentences: Maximum sentences in summary
        """
        self.max_sentences = max_sentences

    def generate_summary(
        self,
        context: Dict[str, Any],
        sport: str,
        style: str = 'bullets'
    ) -> str:
        """
        Generate TL;DR summary

        Args:
            context: Story context data
            sport: Sport name
            style: Summary style (bullets, paragraph, numbers)

        Returns:
            Generated summary string
        """
        # Extract key points
        key_points = self._extract_key_points(context)

        # Format based on style
        if style == 'bullets':
            return self._format_bullets(key_points)
        elif style == 'paragraph':
            return self._format_paragraph(key_points, sport)
        elif style == 'numbers':
            return self._format_numbers(key_points)
        else:
            return self._format_bullets(key_points)

    def _extract_key_points(self, context: Dict[str, Any]) -> List[str]:
        """Extract key points from context"""
        points = []

        # Top trend
        trends = context.get('trends', [])
        if trends:
            top_trend = trends[0]
            points.append(top_trend.get('description', ''))

        # Top performer
        players = context.get('standout_players', [])
        if players:
            player = players[0]
            point = f"{player.get('player', 'Player')} leads with {player.get('value', '')} {player.get('stat_category', '')}"
            points.append(point)

        # Must-watch game
        must_watch = context.get('must_watch', [])
        if must_watch and len(points) < self.max_sentences:
            game = must_watch[0]
            points.append(f"Key matchup: {game.get('game', '')}")

        # Notable injury
        injuries = context.get('injuries', [])
        if injuries and len(points) < self.max_sentences:
            injury = injuries[0]
            headline = injury.get('headline', '')
            if headline:
                points.append(headline)

        return points[:self.max_sentences]

    def _format_bullets(self, points: List[str]) -> str:
        """Format as bullet points"""
        if not points:
            return "No significant updates at this time."

        summary = "**TL;DR:**\n"
        for point in points:
            summary += f"• {point}\n"

        return summary.strip()

    def _format_paragraph(self, points: List[str], sport: str) -> str:
        """Format as paragraph"""
        if not points:
            return "No significant updates at this time."

        if len(points) == 1:
            return f"**TL;DR:** {points[0]}"

        summary = "**TL;DR:** "
        summary += '. '.join(points)
        if not summary.endswith('.'):
            summary += '.'

        return summary

    def _format_numbers(self, points: List[str]) -> str:
        """Format as numbered list"""
        if not points:
            return "No significant updates at this time."

        summary = "**TL;DR:**\n"
        for i, point in enumerate(points, 1):
            summary += f"{i}. {point}\n"

        return summary.strip()
