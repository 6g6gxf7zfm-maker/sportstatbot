"""Stats-to-story generator for creating narratives from data."""
from typing import Dict, List, Optional, Any
import random


class StoryGenerator:
    """
    Generates narrative paragraphs from statistical data.
    Converts raw numbers into engaging sports stories.
    """

    def __init__(self):
        # Templates for different story types
        self.templates = {
            'player_performance': [
                "{player} put on a show with {stat1} {stat1_name} and {stat2} {stat2_name}, {context}.",
                "In a dominant performance, {player} tallied {stat1} {stat1_name} while adding {stat2} {stat2_name}. {context}.",
                "{player} was unstoppable, recording {stat1} {stat1_name} and {stat2} {stat2_name} to lead {team}. {context}."
            ],
            'team_performance': [
                "{team} {result} with a final score of {score}, {context}.",
                "The {team} {result} in {style} fashion, {score}. {context}.",
                "{team}'s {aspect} was {quality} in their {result}, finishing {score}. {context}."
            ],
            'streak': [
                "{team} has now {result} {count} straight games, {context}.",
                "That makes it {count} in a row for {team}, who {context}.",
                "{team} extends their {type} streak to {count} games with {context}."
            ],
            'milestone': [
                "{player} reached a career milestone with {achievement}, {context}.",
                "History was made as {player} {achievement}, {context}.",
                "{achievement} for {player}, who {context}."
            ],
            'comparison': [
                "{entity1} outperformed {entity2} in {aspect}, {stat1} to {stat2}.",
                "While {entity1} managed {stat1} {aspect}, {entity2} could only muster {stat2}.",
                "{entity1} dominated with {stat1} {aspect} compared to {entity2}'s {stat2}."
            ]
        }

        # Context phrases
        self.context_phrases = {
            'positive': [
                "showcasing elite-level play",
                "continuing their hot streak",
                "cementing their status as a top performer",
                "proving why they're among the league's best",
                "delivering in clutch moments"
            ],
            'negative': [
                "in a disappointing outing",
                "struggling to find their rhythm",
                "unable to overcome adversity",
                "extending their rough patch",
                "falling short of expectations"
            ],
            'neutral': [
                "in a competitive matchup",
                "as both teams battled",
                "in regulation play",
                "during standard game action",
                "throughout the contest"
            ]
        }

    def generate_player_story(self, player: str, stats: Dict,
                             team: Optional[str] = None,
                             context: str = 'neutral') -> str:
        """
        Generate a story about a player's performance.

        Args:
            player: Player name
            stats: Dictionary of statistics
            team: Team name (optional)
            context: 'positive', 'negative', or 'neutral'

        Returns:
            Generated story paragraph
        """
        if len(stats) < 2:
            return f"{player} played for {team if team else 'their team'}."

        # Get top 2 stats
        stat_items = list(stats.items())[:2]

        template = random.choice(self.templates['player_performance'])
        context_phrase = random.choice(self.context_phrases.get(context, self.context_phrases['neutral']))

        story = template.format(
            player=player,
            team=team or "their team",
            stat1=stat_items[0][1],
            stat1_name=self._format_stat_name(stat_items[0][0]),
            stat2=stat_items[1][1] if len(stat_items) > 1 else 0,
            stat2_name=self._format_stat_name(stat_items[1][0]) if len(stat_items) > 1 else "",
            context=context_phrase
        )

        return story

    def generate_team_story(self, team: str, result: str, score: str,
                           stats: Optional[Dict] = None,
                           opponent: Optional[str] = None) -> str:
        """
        Generate a story about a team's game result.

        Args:
            team: Team name
            result: 'won' or 'lost'
            score: Final score string
            stats: Team statistics (optional)
            opponent: Opponent name (optional)

        Returns:
            Generated story paragraph
        """
        template = random.choice(self.templates['team_performance'])

        # Determine style and quality based on stats
        style = self._determine_game_style(stats) if stats else "competitive"
        aspect = self._get_dominant_aspect(stats) if stats else "overall play"
        quality = "outstanding" if result == "won" else "lacking"

        context_type = 'positive' if result == 'won' else 'negative'
        context = random.choice(self.context_phrases[context_type])

        if opponent:
            score = f"{score} against {opponent}"

        story = template.format(
            team=team,
            result=result,
            score=score,
            style=style,
            aspect=aspect,
            quality=quality,
            context=context
        )

        return story

    def generate_streak_story(self, team: str, streak_type: str,
                             count: int, context: Optional[str] = None) -> str:
        """
        Generate a story about a team's streak.

        Args:
            team: Team name
            streak_type: 'winning' or 'losing'
            count: Streak length
            context: Additional context (optional)

        Returns:
            Generated story paragraph
        """
        template = random.choice(self.templates['streak'])

        result = "won" if streak_type == "winning" else "lost"

        if not context:
            if streak_type == "winning":
                context = f"establishing themselves as a force in the league"
            else:
                context = f"desperately seeking to right the ship"

        story = template.format(
            team=team,
            result=result,
            count=count,
            type=streak_type,
            context=context
        )

        return story

    def generate_milestone_story(self, player: str, achievement: str,
                                context: Optional[str] = None) -> str:
        """
        Generate a story about a player milestone.

        Args:
            player: Player name
            achievement: Achievement description
            context: Additional context (optional)

        Returns:
            Generated story paragraph
        """
        template = random.choice(self.templates['milestone'])

        if not context:
            context = "joins an elite group of players with this accomplishment"

        story = template.format(
            player=player,
            achievement=achievement,
            context=context
        )

        return story

    def generate_comparison_story(self, entity1: str, entity2: str,
                                 aspect: str, stat1: Any, stat2: Any) -> str:
        """
        Generate a comparative story.

        Args:
            entity1: First entity (player or team)
            entity2: Second entity
            aspect: What's being compared
            stat1: First entity's stat
            stat2: Second entity's stat

        Returns:
            Generated comparison paragraph
        """
        template = random.choice(self.templates['comparison'])

        story = template.format(
            entity1=entity1,
            entity2=entity2,
            aspect=aspect,
            stat1=stat1,
            stat2=stat2
        )

        return story

    def generate_data_story(self, data: Dict, story_type: str = 'auto') -> str:
        """
        Generate a story from a data dictionary.

        Args:
            data: Dictionary with story data
            story_type: Type of story to generate ('auto' to detect)

        Returns:
            Generated story
        """
        if story_type == 'auto':
            story_type = self._detect_story_type(data)

        if story_type == 'player_performance':
            return self.generate_player_story(
                player=data.get('player', 'Unknown'),
                stats=data.get('stats', {}),
                team=data.get('team'),
                context=data.get('context', 'neutral')
            )

        elif story_type == 'team_performance':
            return self.generate_team_story(
                team=data.get('team', 'Unknown'),
                result=data.get('result', 'played'),
                score=data.get('score', ''),
                stats=data.get('stats'),
                opponent=data.get('opponent')
            )

        elif story_type == 'streak':
            return self.generate_streak_story(
                team=data.get('team', 'Unknown'),
                streak_type=data.get('streak_type', 'winning'),
                count=data.get('count', 0),
                context=data.get('context')
            )

        elif story_type == 'milestone':
            return self.generate_milestone_story(
                player=data.get('player', 'Unknown'),
                achievement=data.get('achievement', 'an achievement'),
                context=data.get('context')
            )

        elif story_type == 'comparison':
            return self.generate_comparison_story(
                entity1=data.get('entity1', 'Team A'),
                entity2=data.get('entity2', 'Team B'),
                aspect=data.get('aspect', 'performance'),
                stat1=data.get('stat1', 0),
                stat2=data.get('stat2', 0)
            )

        return "Unable to generate story from provided data."

    def generate_multi_stat_paragraph(self, title: str, stats_list: List[Dict]) -> str:
        """
        Generate a paragraph from multiple statistics.

        Args:
            title: Paragraph title/topic
            stats_list: List of stat dictionaries

        Returns:
            Generated paragraph
        """
        if not stats_list:
            return f"{title}: No data available."

        sentences = [f"{title}:"]

        for stat_data in stats_list[:5]:  # Max 5 items
            name = stat_data.get('name', 'Unknown')
            value = stat_data.get('value', '')
            stat_name = stat_data.get('stat', '')

            if value and stat_name:
                sentences.append(f"{name} with {value} {stat_name}")
            elif value:
                sentences.append(f"{name} ({value})")
            else:
                sentences.append(name)

        # Join sentences intelligently
        if len(sentences) <= 2:
            return ' '.join(sentences)
        else:
            # Use commas and 'and' for last item
            paragraph = sentences[0] + ' '
            paragraph += ', '.join(sentences[1:-1])
            paragraph += f', and {sentences[-1]}.'

        return paragraph

    def _detect_story_type(self, data: Dict) -> str:
        """Detect the type of story from data structure."""
        if 'player' in data and 'stats' in data:
            return 'player_performance'
        elif 'streak_type' in data:
            return 'streak'
        elif 'achievement' in data:
            return 'milestone'
        elif 'entity1' in data and 'entity2' in data:
            return 'comparison'
        elif 'team' in data and 'result' in data:
            return 'team_performance'

        return 'player_performance'  # Default

    def _format_stat_name(self, stat_key: str) -> str:
        """Format a stat key into readable name."""
        # Remove underscores and capitalize
        formatted = stat_key.replace('_', ' ').lower()

        # Handle common abbreviations
        replacements = {
            'pts': 'points',
            'reb': 'rebounds',
            'ast': 'assists',
            'yds': 'yards',
            'td': 'touchdowns',
            'int': 'interceptions',
            'fg': 'field goals',
            'pct': 'percent'
        }

        for abbr, full in replacements.items():
            formatted = formatted.replace(abbr, full)

        return formatted

    def _determine_game_style(self, stats: Dict) -> str:
        """Determine the style of game from statistics."""
        if not stats:
            return "competitive"

        # Check for high-scoring
        points = stats.get('points', 0) or stats.get('score', 0)
        if isinstance(points, (int, float)) and points > 100:
            return "high-scoring"

        # Check for defensive battle
        if isinstance(points, (int, float)) and points < 80:
            return "defensive"

        # Check for blowout
        margin = stats.get('margin', 0)
        if isinstance(margin, (int, float)) and abs(margin) > 20:
            return "dominant"

        return "competitive"

    def _get_dominant_aspect(self, stats: Dict) -> str:
        """Get the dominant aspect of performance from stats."""
        if not stats:
            return "overall play"

        # Check which stats are present and highest
        offensive_stats = ['points', 'yards', 'goals', 'scoring']
        defensive_stats = ['blocks', 'steals', 'sacks', 'interceptions']

        has_offense = any(key in stats for key in offensive_stats)
        has_defense = any(key in stats for key in defensive_stats)

        if has_offense and not has_defense:
            return "offense"
        elif has_defense and not has_offense:
            return "defense"
        elif has_offense and has_defense:
            return "two-way play"

        return "overall play"


class SmartPromptCompletion:
    """
    Smart prompt completion for helping users write sports content.
    Suggests completions based on context.
    """

    def __init__(self, story_generator: StoryGenerator):
        self.story_generator = story_generator

        # Common completion patterns
        self.patterns = {
            'player_intro': [
                "{player} has been on fire lately, averaging",
                "{player} struggled in this matchup, only managing",
                "Despite the {result}, {player} had a strong showing with"
            ],
            'team_intro': [
                "The {team} came into this game with momentum, having",
                "{team} needed this win to stay in playoff contention, and",
                "In a must-win situation, {team}"
            ],
            'stat_context': [
                "This performance ranks among the best of {player}'s career,",
                "These numbers are particularly impressive considering",
                "For context, the league average for this stat is"
            ]
        }

    def complete_prompt(self, partial_text: str, context: Optional[Dict] = None) -> List[str]:
        """
        Suggest completions for partial text.

        Args:
            partial_text: Incomplete text
            context: Optional context about players, teams, stats

        Returns:
            List of suggested completions
        """
        suggestions = []

        # Detect what type of completion is needed
        if self._is_player_intro(partial_text):
            suggestions.extend(self._suggest_player_intro(partial_text, context))

        elif self._is_team_intro(partial_text):
            suggestions.extend(self._suggest_team_intro(partial_text, context))

        elif self._is_stat_explanation(partial_text):
            suggestions.extend(self._suggest_stat_context(partial_text, context))

        else:
            # Generic completions
            suggestions.extend(self._suggest_generic(partial_text))

        return suggestions[:5]  # Return top 5

    def _is_player_intro(self, text: str) -> bool:
        """Check if text is starting a player description."""
        player_keywords = ['player', 'scored', 'recorded', 'finished with', 'had']
        return any(keyword in text.lower() for keyword in player_keywords)

    def _is_team_intro(self, text: str) -> bool:
        """Check if text is starting a team description."""
        team_keywords = ['team', 'won', 'lost', 'defeated', 'beat', 'fell to']
        return any(keyword in text.lower() for keyword in team_keywords)

    def _is_stat_explanation(self, text: str) -> bool:
        """Check if text is explaining statistics."""
        stat_keywords = ['average', 'percentage', 'rating', 'stat', 'number']
        return any(keyword in text.lower() for keyword in stat_keywords)

    def _suggest_player_intro(self, text: str, context: Optional[Dict]) -> List[str]:
        """Suggest player introduction completions."""
        suggestions = []

        for pattern in self.patterns['player_intro']:
            if context and 'player' in context:
                completion = pattern.format(
                    player=context['player'],
                    result=context.get('result', 'game')
                )
                suggestions.append(text + " " + completion)

        return suggestions

    def _suggest_team_intro(self, text: str, context: Optional[Dict]) -> List[str]:
        """Suggest team introduction completions."""
        suggestions = []

        for pattern in self.patterns['team_intro']:
            if context and 'team' in context:
                completion = pattern.format(
                    team=context['team'],
                    result=context.get('result', 'played')
                )
                suggestions.append(text + " " + completion)

        return suggestions

    def _suggest_stat_context(self, text: str, context: Optional[Dict]) -> List[str]:
        """Suggest statistical context completions."""
        suggestions = []

        for pattern in self.patterns['stat_context']:
            completion = pattern
            if context and 'player' in context:
                completion = completion.format(player=context['player'])
            suggestions.append(text + " " + completion)

        return suggestions

    def _suggest_generic(self, text: str) -> List[str]:
        """Suggest generic completions."""
        return [
            text + " showcasing elite-level performance",
            text + " in what was a competitive matchup",
            text + " demonstrating why they're among the league's best"
        ]
