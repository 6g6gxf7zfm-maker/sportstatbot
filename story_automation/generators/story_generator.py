"""
Story Generator - Core AI-powered narrative generation module

Handles multiple writing styles and perspectives:
- Analytical
- Storytelling
- Fan Voice
- Coach Lens (tactical/strategic)
- Casual Fan (simplified)
- Academic Mode (deep analysis)
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class StoryGenerator:
    """Main story generator using AI for narrative creation"""

    WRITING_STYLES = {
        'analytical': 'data-driven, objective analysis with statistical insights',
        'storytelling': 'narrative-focused with dramatic arcs and character development',
        'fan_voice': 'passionate, enthusiastic fan perspective with emotional engagement'
    }

    PERSPECTIVES = {
        'coach_lens': 'tactical and strategic emphasis, X's and O's focus',
        'casual_fan': 'simplified explanations, jargon-free, accessible language',
        'academic': 'scholarly analysis with references, deep tactical breakdowns'
    }

    HEADLINE_TONES = {
        'neutral': 'objective, factual reporting',
        'bold': 'strong, assertive statements',
        'tabloid': 'sensational, attention-grabbing',
        'poetic': 'lyrical, metaphorical language',
        'data_driven': 'numbers-first, statistically focused'
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the story generator

        Args:
            api_key: Optional API key for AI service (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.use_ai = self.api_key is not None

    def generate_story(
        self,
        sport_data: Dict[str, Any],
        sport_name: str,
        style: str = 'analytical',
        perspective: Optional[str] = None,
        headline_tone: str = 'neutral',
        include_sidebar: bool = True,
        include_pullquotes: bool = True,
        include_trivia: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a complete story from sport data

        Args:
            sport_data: Analyzed sport data dictionary
            sport_name: Name of the sport
            style: Writing style (analytical, storytelling, fan_voice)
            perspective: Optional perspective overlay (coach_lens, casual_fan, academic)
            headline_tone: Tone for headlines
            include_sidebar: Whether to include dynamic sidebars
            include_pullquotes: Whether to include pull quotes
            include_trivia: Whether to inject trivia

        Returns:
            Dictionary containing generated story components
        """
        if not sport_data.get('enabled', False):
            return {'enabled': False}

        # Build the story context
        context = self._build_context(sport_data, sport_name)

        # Generate main narrative
        main_story = self._generate_narrative(
            context, style, perspective, headline_tone
        )

        # Generate additional components
        story_components = {
            'sport': sport_name,
            'style': style,
            'perspective': perspective,
            'headline': main_story.get('headline', ''),
            'subhead': main_story.get('subhead', ''),
            'tldr': main_story.get('tldr', ''),
            'body': main_story.get('body', ''),
            'conclusion': main_story.get('conclusion', ''),
            'timestamp': datetime.now().isoformat()
        }

        # Add optional components
        if include_sidebar:
            story_components['sidebars'] = self._generate_sidebars(context)

        if include_pullquotes:
            story_components['pullquotes'] = self._extract_pullquotes(
                main_story.get('body', '')
            )

        if include_trivia:
            story_components['trivia'] = self._generate_trivia(context)

        # Add metadata
        story_components['metadata'] = {
            'word_count': len(main_story.get('body', '').split()),
            'key_stats': self._extract_key_stats(context),
            'data_sources': self._get_data_sources(sport_data)
        }

        return story_components

    def recast_story(
        self,
        story: Dict[str, Any],
        target_styles: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Recast Mode - Rewrite story in multiple styles

        Args:
            story: Original story dictionary
            target_styles: List of styles to recast into

        Returns:
            Dictionary mapping style names to recast versions
        """
        recast_versions = {}

        for style in target_styles:
            if style in self.WRITING_STYLES or style in self.PERSPECTIVES:
                recast_versions[style] = self._recast_to_style(story, style)

        return recast_versions

    def _build_context(
        self,
        sport_data: Dict[str, Any],
        sport_name: str
    ) -> Dict[str, Any]:
        """Build context dictionary from sport data"""
        context = {
            'sport': sport_name,
            'trends': sport_data.get('trends', []),
            'recent_games': sport_data.get('recent_games', []),
            'standout_players': sport_data.get('standout_players', []),
            'injuries': sport_data.get('injuries', []),
            'roster_changes': sport_data.get('roster_changes', []),
            'must_watch': sport_data.get('must_watch', []),
            'betting_insights': sport_data.get('betting_insights', {})
        }

        return context

    def _generate_narrative(
        self,
        context: Dict[str, Any],
        style: str,
        perspective: Optional[str],
        headline_tone: str
    ) -> Dict[str, str]:
        """
        Generate narrative using AI or template-based approach

        Returns:
            Dictionary with headline, subhead, tldr, body, conclusion
        """
        if self.use_ai:
            return self._generate_ai_narrative(context, style, perspective, headline_tone)
        else:
            return self._generate_template_narrative(context, style, perspective, headline_tone)

    def _generate_ai_narrative(
        self,
        context: Dict[str, Any],
        style: str,
        perspective: Optional[str],
        headline_tone: str
    ) -> Dict[str, str]:
        """Generate narrative using AI (Claude API)"""
        # Note: Actual API integration would go here
        # For now, return template-based fallback
        return self._generate_template_narrative(context, style, perspective, headline_tone)

    def _generate_template_narrative(
        self,
        context: Dict[str, Any],
        style: str,
        perspective: Optional[str],
        headline_tone: str
    ) -> Dict[str, str]:
        """Generate narrative using templates (fallback when AI unavailable)"""
        sport = context.get('sport', 'Sports')

        # Generate headline based on tone
        headline = self._create_headline(context, headline_tone)

        # Generate subhead
        subhead = self._create_subhead(context)

        # Generate TL;DR
        tldr = self._create_tldr(context)

        # Generate body
        body_sections = []

        # Trends section
        if context.get('trends'):
            body_sections.append(self._format_trends_narrative(
                context['trends'], style, perspective
            ))

        # Recent games section
        if context.get('recent_games'):
            body_sections.append(self._format_games_narrative(
                context['recent_games'], style, perspective
            ))

        # Players section
        if context.get('standout_players'):
            body_sections.append(self._format_players_narrative(
                context['standout_players'], style, perspective
            ))

        # Injuries and roster changes
        if context.get('injuries') or context.get('roster_changes'):
            body_sections.append(self._format_news_narrative(
                context.get('injuries', []),
                context.get('roster_changes', []),
                style, perspective
            ))

        # Must-watch games
        if context.get('must_watch'):
            body_sections.append(self._format_preview_narrative(
                context['must_watch'], style, perspective
            ))

        body = '\n\n'.join(body_sections)

        # Generate conclusion
        conclusion = self._create_conclusion(context, style)

        return {
            'headline': headline,
            'subhead': subhead,
            'tldr': tldr,
            'body': body,
            'conclusion': conclusion
        }

    def _create_headline(self, context: Dict[str, Any], tone: str) -> str:
        """Create headline based on tone"""
        sport = context.get('sport', 'Sports')

        # Find the most significant story element
        trends = context.get('trends', [])
        games = context.get('recent_games', [])

        if tone == 'data_driven':
            if trends:
                return f"{sport}: {len(trends)} Teams Showing Major Trends"
            return f"{sport} By The Numbers: Latest Stats & Analysis"

        elif tone == 'bold':
            if trends and 'hot_streak' in trends[0].get('type', ''):
                team = trends[0].get('team', 'Top Team')
                return f"{team} Unstoppable: {sport} Power Rankings Shift"
            return f"{sport} Shakeup: Who's Rising and Falling"

        elif tone == 'tabloid':
            if trends:
                return f"SHOCKING: {sport} Teams You Won't Believe!"
            return f"{sport} DRAMA: Everything You Need to Know"

        elif tone == 'poetic':
            return f"The Rise and Fall: A {sport} Story"

        else:  # neutral
            return f"{sport} Daily Update: Trends, Games & Analysis"

    def _create_subhead(self, context: Dict[str, Any]) -> str:
        """Create subhead summarizing key points"""
        elements = []

        if context.get('trends'):
            elements.append(f"{len(context['trends'])} teams in flux")
        if context.get('standout_players'):
            elements.append(f"{len(context['standout_players'])} standout performances")
        if context.get('must_watch'):
            elements.append(f"{len(context['must_watch'])} must-watch matchups")

        if elements:
            return ', '.join(elements)
        return "Latest updates and analysis"

    def _create_tldr(self, context: Dict[str, Any]) -> str:
        """Create TL;DR summary"""
        summary_parts = []

        # Highlight top trend
        if context.get('trends'):
            trend = context['trends'][0]
            summary_parts.append(trend.get('description', ''))

        # Highlight top performer
        if context.get('standout_players'):
            player = context['standout_players'][0]
            summary_parts.append(
                f"{player.get('player', 'Player')} leads with "
                f"{player.get('stat_category', 'performance')}"
            )

        # Highlight must-watch
        if context.get('must_watch'):
            game = context['must_watch'][0]
            summary_parts.append(f"Don't miss: {game.get('game', 'key matchup')}")

        if summary_parts:
            return ' | '.join(summary_parts[:3])  # Limit to 3 key points
        return "Latest sports updates and analysis"

    def _format_trends_narrative(
        self,
        trends: List[Dict],
        style: str,
        perspective: Optional[str]
    ) -> str:
        """Format trends into narrative"""
        if not trends:
            return ""

        if style == 'storytelling':
            narrative = "**The Momentum Shifts**\n\n"
            for trend in trends:
                narrative += f"- {trend.get('description', '')}\n"
        elif style == 'fan_voice':
            narrative = "**Who's Hot and Who's Not! 🔥❄️**\n\n"
            for trend in trends:
                narrative += f"- {trend.get('description', '')} "
                if 'hot' in trend.get('type', ''):
                    narrative += "🔥\n"
                else:
                    narrative += "❄️\n"
        else:  # analytical
            narrative = "**Trend Analysis**\n\n"
            for trend in trends:
                narrative += f"- {trend.get('description', '')}\n"

        return narrative

    def _format_games_narrative(
        self,
        games: List[Dict],
        style: str,
        perspective: Optional[str]
    ) -> str:
        """Format recent games into narrative"""
        if not games:
            return ""

        narrative = "**Recent Results**\n\n"

        for game in games[:5]:  # Limit to top 5
            home = game.get('home_team', 'Home')
            away = game.get('away_team', 'Away')
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)

            winner = home if home_score > away_score else away

            if perspective == 'coach_lens':
                narrative += f"- **{away}** @ **{home}**: {away_score}-{home_score} "
                narrative += f"(Tactical implications: {winner} demonstrates execution)\n"
            elif perspective == 'casual_fan':
                narrative += f"- **{winner}** won! ({away} {away_score} @ {home} {home_score})\n"
            else:
                narrative += f"- **{away}** {away_score} @ **{home}** {home_score}\n"

        return narrative

    def _format_players_narrative(
        self,
        players: List[Dict],
        style: str,
        perspective: Optional[str]
    ) -> str:
        """Format player performances into narrative"""
        if not players:
            return ""

        narrative = "**Standout Performances**\n\n"

        for player in players[:5]:
            name = player.get('player', 'Player')
            team = player.get('team', 'Team')
            stat = player.get('stat_category', 'performance')
            value = player.get('value', '')

            if style == 'fan_voice':
                narrative += f"- 🌟 **{name}** ({team}) absolutely killing it: {value} {stat}!\n"
            elif perspective == 'academic':
                narrative += f"- **{name}** ({team}): {value} {stat} - "
                narrative += "statistically significant performance above season average\n"
            else:
                narrative += f"- **{name}** ({team}): {value} {stat}\n"

        return narrative

    def _format_news_narrative(
        self,
        injuries: List[Dict],
        roster_changes: List[Dict],
        style: str,
        perspective: Optional[str]
    ) -> str:
        """Format injuries and roster changes into narrative"""
        if not injuries and not roster_changes:
            return ""

        narrative = "**Team News**\n\n"

        if injuries:
            narrative += "_Injury Updates:_\n"
            for injury in injuries[:3]:
                narrative += f"- {injury.get('headline', '')}\n"
            narrative += "\n"

        if roster_changes:
            narrative += "_Roster Changes:_\n"
            for change in roster_changes[:3]:
                narrative += f"- {change.get('headline', '')}\n"

        return narrative

    def _format_preview_narrative(
        self,
        must_watch: List[Dict],
        style: str,
        perspective: Optional[str]
    ) -> str:
        """Format must-watch games into narrative"""
        if not must_watch:
            return ""

        narrative = "**Games to Watch**\n\n"

        for game in must_watch[:3]:
            game_info = game.get('game', '')
            date = game.get('date', '')
            reasons = game.get('reasons', [])

            if style == 'fan_voice':
                narrative += f"- 📺 **{game_info}** ({date}) - DON'T MISS THIS ONE!\n"
            else:
                narrative += f"- **{game_info}** ({date})\n"

            if reasons:
                for reason in reasons:
                    narrative += f"  - {reason}\n"

        return narrative

    def _create_conclusion(self, context: Dict[str, Any], style: str) -> str:
        """Create concluding paragraph"""
        sport = context.get('sport', 'the sport')

        if style == 'fan_voice':
            return f"What a time to be a {sport} fan! Stay tuned for more updates!"
        elif style == 'storytelling':
            return f"As the {sport} season continues to unfold, these storylines will shape the narrative going forward."
        else:
            return f"Continue monitoring these {sport} trends and developments."

    def _generate_sidebars(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dynamic sidebars"""
        sidebars = []

        # "3 Numbers That Matter"
        if context.get('standout_players'):
            numbers = []
            for player in context['standout_players'][:3]:
                numbers.append({
                    'number': player.get('value', ''),
                    'label': f"{player.get('player', '')} - {player.get('stat_category', '')}"
                })
            if numbers:
                sidebars.append({
                    'type': '3_numbers',
                    'title': '3 Numbers That Matter',
                    'data': numbers
                })

        # "By the Data"
        if context.get('trends'):
            sidebars.append({
                'type': 'by_the_data',
                'title': 'By the Data',
                'data': [{'trend': t.get('description', '')} for t in context['trends'][:3]]
            })

        return sidebars

    def _extract_pullquotes(self, body: str) -> List[str]:
        """Extract potential pull quotes from body text"""
        # Simple extraction: look for impactful sentences
        sentences = body.split('.')
        pullquotes = []

        for sentence in sentences:
            # Look for sentences with emphatic markers
            if any(marker in sentence for marker in ['!', '**', 'unprecedented', 'historic', 'remarkable']):
                clean = sentence.strip().strip('*').strip('-').strip()
                if len(clean) > 20 and len(clean) < 150:
                    pullquotes.append(clean)

        return pullquotes[:3]  # Return top 3

    def _generate_trivia(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate trivia fact (placeholder - would use AI or database)"""
        # This would ideally query a sports trivia database or use AI
        return None

    def _extract_key_stats(self, context: Dict[str, Any]) -> List[str]:
        """Extract key statistics from context"""
        stats = []

        if context.get('trends'):
            stats.append(f"{len(context['trends'])} active trends")
        if context.get('recent_games'):
            stats.append(f"{len(context['recent_games'])} games analyzed")
        if context.get('standout_players'):
            stats.append(f"{len(context['standout_players'])} standout players")

        return stats

    def _get_data_sources(self, sport_data: Dict[str, Any]) -> List[str]:
        """Get list of data sources"""
        sources = ['ESPN API']

        if sport_data.get('betting_insights'):
            sources.append('The Odds API')

        return sources

    def _recast_to_style(
        self,
        story: Dict[str, Any],
        target_style: str
    ) -> Dict[str, Any]:
        """Recast story to a different style"""
        # Extract context from original story
        # Regenerate with new style
        # This would use AI to rewrite
        return story  # Placeholder
