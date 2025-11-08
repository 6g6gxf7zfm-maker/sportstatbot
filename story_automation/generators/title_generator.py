"""
Title Generator - Auto-title generation with SEO optimization
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class TitleGenerator:
    """Generate SEO-optimized titles for sports stories"""

    # SEO keywords by sport
    SEO_KEYWORDS = {
        'nfl': ['NFL', 'football', 'playoffs', 'Super Bowl', 'standings', 'week'],
        'nba': ['NBA', 'basketball', 'playoffs', 'championship', 'standings', 'scores'],
        'mlb': ['MLB', 'baseball', 'World Series', 'standings', 'scores', 'season'],
        'nhl': ['NHL', 'hockey', 'Stanley Cup', 'playoffs', 'standings', 'scores'],
        'soccer': ['MLS', 'soccer', 'football', 'standings', 'scores', 'match'],
        'ncaaf': ['college football', 'NCAA', 'bowl', 'rankings', 'scores'],
        'ncaab': ['college basketball', 'NCAA', 'March Madness', 'rankings', 'scores']
    }

    POWER_WORDS = [
        'dominate', 'surge', 'battle', 'clash', 'showdown', 'thriller',
        'upset', 'stunning', 'historic', 'record-breaking', 'phenomenal',
        'explosive', 'crucial', 'pivotal', 'decisive', 'unstoppable'
    ]

    def __init__(self):
        self.max_title_length = 60  # SEO best practice

    def generate_title(
        self,
        sport: str,
        context: Dict[str, Any],
        tone: str = 'neutral',
        include_date: bool = True,
        seo_optimize: bool = True
    ) -> str:
        """
        Generate an SEO-optimized title

        Args:
            sport: Sport name
            context: Story context data
            tone: Title tone (neutral, bold, tabloid, poetic, data_driven)
            include_date: Whether to include date reference
            seo_optimize: Whether to optimize for SEO

        Returns:
            Generated title string
        """
        # Extract key elements
        main_story = self._identify_main_story(context)

        # Generate base title
        title = self._create_base_title(sport, main_story, tone)

        # Add date reference if requested
        if include_date:
            title = self._add_date_context(title, sport)

        # SEO optimization
        if seo_optimize:
            title = self._optimize_for_seo(title, sport)

        # Ensure proper length
        title = self._ensure_length(title)

        return title

    def generate_variations(
        self,
        sport: str,
        context: Dict[str, Any],
        count: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate multiple title variations for A/B testing

        Args:
            sport: Sport name
            context: Story context
            count: Number of variations to generate

        Returns:
            List of title variations with metadata
        """
        tones = ['neutral', 'bold', 'data_driven'][:count]
        variations = []

        for tone in tones:
            title = self.generate_title(sport, context, tone=tone)
            variations.append({
                'title': title,
                'tone': tone,
                'seo_score': self._calculate_seo_score(title, sport),
                'length': len(title)
            })

        return variations

    def _identify_main_story(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify the main story element from context"""
        # Priority: hot streaks > upsets > standout players > general update
        if context.get('trends'):
            for trend in context['trends']:
                if 'hot_streak' in trend.get('type', ''):
                    return {
                        'type': 'hot_streak',
                        'team': trend.get('team', ''),
                        'description': trend.get('description', '')
                    }

        if context.get('recent_games'):
            # Check for upsets or notable games
            for game in context['recent_games']:
                if game.get('classification') == 'upset':
                    return {
                        'type': 'upset',
                        'game': game
                    }

        if context.get('standout_players'):
            return {
                'type': 'player_performance',
                'player': context['standout_players'][0]
            }

        return {'type': 'general_update'}

    def _create_base_title(
        self,
        sport: str,
        main_story: Dict[str, Any],
        tone: str
    ) -> str:
        """Create base title from main story"""
        story_type = main_story.get('type')

        if story_type == 'hot_streak':
            team = main_story.get('team', 'Team')
            if tone == 'bold':
                return f"{team} On Fire: Winning Streak Analysis"
            elif tone == 'tabloid':
                return f"UNSTOPPABLE: {team} Can't Lose!"
            elif tone == 'data_driven':
                return f"{team} Win Streak: By The Numbers"
            else:
                return f"{team} Extends Winning Streak"

        elif story_type == 'upset':
            if tone == 'bold':
                return f"Major Upset Shakes Up {sport.upper()}"
            elif tone == 'tabloid':
                return f"SHOCKING UPSET: You Won't Believe This!"
            else:
                return f"Upset Alert: {sport.upper()} Results"

        elif story_type == 'player_performance':
            player_data = main_story.get('player', {})
            player_name = player_data.get('player', 'Star Player')
            if tone == 'bold':
                return f"{player_name} Dominates in {sport.upper()}"
            elif tone == 'data_driven':
                stat = player_data.get('stat_category', 'performance')
                return f"{player_name} Leads {sport.upper()} in {stat}"
            else:
                return f"{player_name} Shines in Latest {sport.upper()} Action"

        else:  # general_update
            if tone == 'data_driven':
                return f"{sport.upper()} Stats & Analysis"
            else:
                return f"{sport.upper()} Update: Trends & Highlights"

    def _add_date_context(self, title: str, sport: str) -> str:
        """Add date context to title"""
        now = datetime.now()
        day_name = now.strftime('%A')

        # Check if title already has date context
        if any(day in title for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            return title

        # For certain sports on certain days, add day context
        if sport.lower() == 'nfl' and day_name == 'Sunday':
            return f"{title} - Sunday Edition"
        elif sport.lower() == 'nba':
            return f"{title} - {day_name} Roundup"

        return title

    def _optimize_for_seo(self, title: str, sport: str) -> str:
        """Optimize title for SEO"""
        sport_key = sport.lower()

        # Ensure sport acronym is present
        sport_keywords = self.SEO_KEYWORDS.get(sport_key, [sport.upper()])
        has_keyword = any(keyword.upper() in title.upper() for keyword in sport_keywords)

        if not has_keyword and sport_keywords:
            # Add primary keyword
            title = f"{sport_keywords[0]}: {title}"

        # Add current year if relevant for season context
        current_year = datetime.now().year
        if 'season' in title.lower() and str(current_year) not in title:
            title = f"{title} {current_year}"

        return title

    def _ensure_length(self, title: str) -> str:
        """Ensure title is optimal length for SEO"""
        if len(title) <= self.max_title_length:
            return title

        # Truncate intelligently at word boundary
        truncated = title[:self.max_title_length]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            return truncated[:last_space] + '...'

        return truncated + '...'

    def _calculate_seo_score(self, title: str, sport: str) -> float:
        """Calculate SEO score for a title (0-100)"""
        score = 50.0  # Base score

        # Length score (50-60 chars is ideal)
        length = len(title)
        if 50 <= length <= 60:
            score += 20
        elif 40 <= length <= 70:
            score += 10

        # Keyword presence
        sport_key = sport.lower()
        keywords = self.SEO_KEYWORDS.get(sport_key, [sport])
        keyword_count = sum(1 for kw in keywords if kw.upper() in title.upper())
        score += min(keyword_count * 10, 20)

        # Power word presence
        power_word_count = sum(1 for pw in self.POWER_WORDS if pw.lower() in title.lower())
        score += min(power_word_count * 5, 10)

        return min(score, 100.0)
