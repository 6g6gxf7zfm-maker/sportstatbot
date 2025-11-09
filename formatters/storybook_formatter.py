"""
Storybook View Formatter for SportStatBot
Renders all stories in sequence as one long feature article
"""

from typing import Dict, List, Optional
from datetime import datetime
from presentation_config import PresentationConfig, StyleTheme
from config import SPORTS_CONFIG


class StorybookFormatter:
    """Format reports in storybook/feature article style"""

    def __init__(self, config: Optional[PresentationConfig] = None):
        """Initialize storybook formatter"""
        self.config = config or PresentationConfig()

    def format_storybook_view(
        self,
        reports_data: List[Dict],
        title: str = "This Week in Sports",
        date_range: str = None
    ) -> str:
        """Render all stories in sequence as one long feature"""
        storybook = self._generate_storybook_cover(title, date_range)

        # Table of contents
        storybook += self._generate_table_of_contents(reports_data)

        # Chapter separator
        storybook += "\n\n" + "═" * 80 + "\n\n"

        # Generate chapters for each sport
        for i, report in enumerate(reports_data, 1):
            sport = report.get('sport', 'Unknown')
            data = report.get('data', {})

            storybook += self._format_sport_chapter(sport, data, chapter_num=i)
            storybook += "\n\n" + "═" * 80 + "\n\n"

        # Epilogue
        storybook += self._generate_epilogue(reports_data)

        # Credits
        storybook += self.config.get_credits_section()

        return storybook

    def _generate_storybook_cover(self, title: str, date_range: str = None) -> str:
        """Generate storybook cover page"""
        trophy = self.config.get_emoji('trophy')
        star = self.config.get_emoji('star')

        cover = "\n"
        cover += "╔" + "═" * 78 + "╗\n"
        cover += "║" + " " * 78 + "║\n"
        cover += "║" + f"{title:^78}" + "║\n"
        cover += "║" + " " * 78 + "║\n"

        if date_range:
            cover += "║" + f"{date_range:^78}" + "║\n"
            cover += "║" + " " * 78 + "║\n"

        cover += "║" + f"{star * 10:^78}" + "║\n"
        cover += "║" + " " * 78 + "║\n"
        cover += "║" + "A Comprehensive Sports Narrative".center(78) + "║\n"
        cover += "║" + " " * 78 + "║\n"
        cover += "╚" + "═" * 78 + "╝\n\n"

        return cover

    def _generate_table_of_contents(self, reports_data: List[Dict]) -> str:
        """Generate table of contents"""
        toc = "\n## Table of Contents\n\n"

        for i, report in enumerate(reports_data, 1):
            sport = report.get('sport', 'Unknown')
            sport_config = SPORTS_CONFIG.get(sport, {})
            sport_name = sport_config.get('display_name', sport.upper())
            sport_emoji = sport_config.get('emoji', '')

            toc += f"{i}. {sport_emoji} **{sport_name}** — The Week That Was\n"

        toc += "\n"
        return toc

    def _format_sport_chapter(self, sport: str, data: Dict, chapter_num: int) -> str:
        """Format a sport as a narrative chapter"""
        sport_config = SPORTS_CONFIG.get(sport, {})
        sport_name = sport_config.get('display_name', sport.upper())
        sport_emoji = sport_config.get('emoji', '')

        # Chapter header
        chapter = f"\n# Chapter {chapter_num}: {sport_emoji} {sport_name}\n\n"

        # Get story opener
        opener = self.config.get_opener(sport)
        if opener:
            chapter += f"*{opener}*\n\n"

        # Narrative introduction
        chapter += self._generate_narrative_intro(sport, data)

        # Key storylines
        chapter += self._format_storylines_narrative(data)

        # Player spotlights
        chapter += self._format_player_spotlights_narrative(data)

        # Looking ahead
        chapter += self._format_looking_ahead_narrative(sport, data)

        return chapter

    def _generate_narrative_intro(self, sport: str, data: Dict) -> str:
        """Generate narrative introduction for a sport"""
        intro = ""

        trends = data.get('trends', [])
        if trends:
            if self.config.theme == StyleTheme.THE_ATHLETIC:
                intro += "The latest developments paint an intriguing picture. "
            elif self.config.theme == StyleTheme.ESPN:
                intro += "Here's what's dominating the headlines: "
            elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
                intro += "The data reveals several notable patterns: "
            elif self.config.theme == StyleTheme.BLEACHER_REPORT:
                intro += "The action has been absolutely wild: "

            intro += f"{trends[0]} "
            if len(trends) > 1:
                intro += f"Meanwhile, {trends[1].lower()}"

            intro += "\n\n"

        return intro

    def _format_storylines_narrative(self, data: Dict) -> str:
        """Format key games as narrative storylines"""
        if not data.get('recent_games'):
            return ""

        fire = self.config.get_emoji('fire')
        warning = self.config.get_emoji('warning')

        section = "## The Highlights\n\n"

        games = data['recent_games'][:5]  # Top 5 games

        for i, game in enumerate(games, 1):
            home_team = game.get('home_team', 'Home')
            away_team = game.get('away_team', 'Away')
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)
            notes = game.get('notes', [])
            leaders = game.get('leaders', [])

            # Determine narrative style based on game type
            margin = abs(home_score - away_score)
            winner = home_team if home_score > away_score else away_team
            loser = away_team if winner == home_team else home_team
            winner_score = max(home_score, away_score)
            loser_score = min(home_score, away_score)

            if self.config.theme == StyleTheme.ESPN:
                if margin <= 3:
                    narrative = f"### {fire} Thriller Alert\n\n"
                    narrative += f"In a nail-biter, **{winner}** edged **{loser}** {winner_score}-{loser_score}. "
                elif margin >= 20:
                    narrative = f"### Dominant Display\n\n"
                    narrative += f"**{winner}** steamrolled **{loser}** {winner_score}-{loser_score} in emphatic fashion. "
                else:
                    narrative = f"### {winner} Prevails\n\n"
                    narrative += f"**{winner}** defeated **{loser}** {winner_score}-{loser_score}. "

            elif self.config.theme == StyleTheme.THE_ATHLETIC:
                narrative = f"### {away_team} at {home_team}\n\n"
                narrative += f"The {winner} demonstrated why they're among the league's elite, "
                narrative += f"securing a {winner_score}-{loser_score} victory over the {loser}. "

            elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
                narrative = f"### Statistical Snapshot: {away_team} vs {home_team}\n\n"
                narrative += f"**Final Score:** {winner} {winner_score}, {loser} {loser_score} "
                narrative += f"(Margin of Victory: {margin}). "

            elif self.config.theme == StyleTheme.BLEACHER_REPORT:
                if margin <= 3:
                    narrative = f"### {fire} INSTANT CLASSIC\n\n"
                    narrative += f"**{winner.upper()}** SURVIVES AGAINST **{loser.upper()}** {winner_score}-{loser_score}! "
                else:
                    narrative = f"### {winner.upper()} WINS BIG\n\n"
                    narrative += f"**{winner.upper()}** CRUSHES **{loser.upper()}** {winner_score}-{loser_score}! "
            else:
                narrative = f"### {winner} {winner_score}, {loser} {loser_score}\n\n"

            # Add leaders if available
            if leaders:
                narrative += f"The performance was headlined by {leaders[0].lower()}. "

            # Add upset note
            if any('upset' in note.lower() for note in notes):
                narrative += f"{warning} This result marked a significant upset. "

            narrative += "\n\n"
            section += narrative

        return section

    def _format_player_spotlights_narrative(self, data: Dict) -> str:
        """Format standout players as narrative spotlights"""
        if not data.get('standout_players'):
            return ""

        star = self.config.get_emoji('star')
        rocket = self.config.get_emoji('rocket')

        section = f"## {star} Player Spotlights\n\n"

        players = data['standout_players'][:3]  # Top 3 players

        for player in players:
            name = player.get('name', 'Unknown')
            team = player.get('team', '')
            stats = player.get('stats', '')

            if self.config.theme == StyleTheme.ESPN:
                spotlight = f"### {rocket} {name}\n\n"
                spotlight += f"The {team} star put on a show with {stats.lower()}, "
                spotlight += "cementing their status as one of the league's premier talents.\n\n"

            elif self.config.theme == StyleTheme.THE_ATHLETIC:
                spotlight = f"### {name}'s Excellence Continues\n\n"
                spotlight += f"Playing for the {team}, {name} recorded {stats.lower()}, "
                spotlight += "adding another chapter to what's becoming a remarkable season.\n\n"

            elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
                spotlight = f"### Performance Analysis: {name}\n\n"
                spotlight += f"**Team:** {team}\n"
                spotlight += f"**Statistics:** {stats}\n"
                spotlight += f"*This performance ranks among the top outputs for the position this week.*\n\n"

            elif self.config.theme == StyleTheme.BLEACHER_REPORT:
                spotlight = f"### {rocket} {name.upper()} GOES OFF\n\n"
                spotlight += f"The {team} superstar was UNSTOPPABLE: {stats}! "
                spotlight += "Absolutely incredible.\n\n"
            else:
                spotlight = f"### {name}\n\n**{team}** — {stats}\n\n"

            section += spotlight

        return section

    def _format_looking_ahead_narrative(self, sport: str, data: Dict) -> str:
        """Format upcoming games as narrative preview"""
        if not data.get('must_watch'):
            return ""

        eyes = self.config.get_emoji('eyes')

        section = f"## {eyes} Looking Ahead\n\n"

        if self.config.theme == StyleTheme.ESPN:
            section += "The slate of upcoming games promises more fireworks:\n\n"
        elif self.config.theme == StyleTheme.THE_ATHLETIC:
            section += "Several intriguing matchups await on the horizon:\n\n"
        elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
            section += "The schedule features these statistically significant matchups:\n\n"
        elif self.config.theme == StyleTheme.BLEACHER_REPORT:
            section += "Get ready for these MUST-SEE showdowns:\n\n"

        games = data['must_watch'][:3]  # Top 3 upcoming

        for game in games:
            home = game.get('home_team', 'Home')
            away = game.get('away_team', 'Away')
            time = game.get('time', 'TBD')
            reason = game.get('reason', '')

            preview = f"**{away} @ {home}** — *{time}*\n"
            if reason:
                preview += f"> {reason}\n"
            preview += "\n"

            section += preview

        return section

    def _generate_epilogue(self, reports_data: List[Dict]) -> str:
        """Generate epilogue/conclusion"""
        checkmark = self.config.get_emoji('checkmark')

        epilogue = "\n# Epilogue\n\n"

        if self.config.theme == StyleTheme.ESPN:
            epilogue += "That's a wrap on another action-packed period in the sports world. "
            epilogue += "From buzzer-beaters to blowouts, the competition never disappoints. "
            epilogue += "Stay tuned for more coverage as the storylines continue to unfold.\n\n"

        elif self.config.theme == StyleTheme.THE_ATHLETIC:
            epilogue += "As we've examined, this period offered no shortage of compelling narratives. "
            epilogue += "Each sport presents its own unique storylines, collectively painting a "
            epilogue += "rich tapestry of athletic achievement and competition.\n\n"

        elif self.config.theme == StyleTheme.FIVETHIRTYEIGHT:
            epilogue += "The statistical patterns observed during this period provide valuable insights "
            epilogue += "into team performance trends and player development trajectories. "
            epilogue += "Future analysis will reveal whether these trends hold.\n\n"

        elif self.config.theme == StyleTheme.BLEACHER_REPORT:
            epilogue += "WOW. What a week! The sports world delivered AGAIN with incredible moments, "
            epilogue += "unforgettable performances, and non-stop excitement. "
            epilogue += "Can't wait to see what happens next!\n\n"

        epilogue += f"{checkmark} *Report compiled: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n"

        return epilogue

    def format_sequential_stories(
        self,
        stories: List[Dict],
        overall_title: str = "Today's Sports Stories"
    ) -> str:
        """Format multiple stories in sequence (simpler than full storybook)"""
        output = f"\n# {overall_title}\n\n"
        output += f"*{datetime.now().strftime('%B %d, %Y')}*\n\n"
        output += "─" * 70 + "\n\n"

        for i, story in enumerate(stories, 1):
            title = story.get('title', f'Story {i}')
            content = story.get('content', '')
            author = story.get('author', 'SportStatBot')

            output += f"\n## Story {i}: {title}\n\n"
            output += content + "\n\n"
            output += f"*— {author}*\n\n"
            output += "─" * 70 + "\n\n"

        return output
