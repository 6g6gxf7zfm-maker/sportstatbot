"""
Trivia Generator - Random trivia injection for stories
"""

import random
from typing import Dict, List, Any, Optional


class TriviaGenerator:
    """Generate and inject sports trivia into stories"""

    # Sports trivia database
    TRIVIA_DB = {
        'nfl': [
            "The NFL's regular season is 18 weeks long, with each team playing 17 games.",
            "The Super Bowl is the most-watched television event in the United States annually.",
            "The Green Bay Packers are the only community-owned franchise in major American sports.",
            "The NFL salary cap for 2024 season is approximately $255 million per team.",
            "Tom Brady holds the record for most Super Bowl victories with seven wins.",
        ],
        'nba': [
            "The NBA three-point line is 23 feet 9 inches from the basket in the corners.",
            "Wilt Chamberlain scored 100 points in a single game on March 2, 1962.",
            "The Boston Celtics have won the most NBA championships with 17 titles.",
            "An NBA regulation game consists of four 12-minute quarters.",
            "Michael Jordan was drafted third overall in the 1984 NBA Draft.",
        ],
        'mlb': [
            "Baseball games have no time limit - they continue until all innings are complete.",
            "The fastest recorded pitch in MLB history was 105.8 mph by Aroldis Chapman.",
            "The New York Yankees have won 27 World Series championships.",
            "A perfect game requires retiring all 27 batters without allowing anyone to reach base.",
            "MLB players use approximately 1,000 baseballs per game.",
        ],
        'nhl': [
            "The Stanley Cup is the oldest professional sports trophy in North America.",
            "A regulation hockey puck weighs between 5.5 and 6 ounces.",
            "NHL ice rinks are 200 feet long and 85 feet wide.",
            "The fastest recorded shot in NHL history was 108.8 mph by Zdeno Chara.",
            "Wayne Gretzky holds 61 NHL records including most career goals and assists.",
        ],
        'soccer': [
            "A regulation soccer ball must be between 27-28 inches in circumference.",
            "The World Cup is held every four years and is watched by billions globally.",
            "A soccer field can range from 100-130 yards long and 50-100 yards wide.",
            "Goalkeepers are the only players allowed to use their hands (in the penalty area).",
            "Pelé scored 1,283 goals in his professional career.",
        ],
        'ncaaf': [
            "College football overtime rules differ from the NFL with alternating possessions.",
            "The Heisman Trophy has been awarded since 1935 to the best player in college football.",
            "The Rose Bowl is known as 'The Granddaddy of Them All' - first played in 1902.",
            "College football teams can have up to 85 scholarship players.",
            "The longest college football game went seven overtimes.",
        ],
        'ncaab': [
            "The NCAA Tournament, 'March Madness,' features 68 teams competing for the championship.",
            "The college three-point line is 22 feet 1.75 inches from the basket.",
            "UCLA has won the most NCAA basketball championships with 11 titles.",
            "College basketball games consist of two 20-minute halves.",
            "The shot clock in college basketball is 30 seconds.",
        ]
    }

    # Rivalry facts
    RIVALRY_FACTS = {
        ('Yankees', 'Red Sox'): "The Yankees-Red Sox rivalry is one of the oldest in professional sports.",
        ('Lakers', 'Celtics'): "Lakers-Celtics have met in the NBA Finals 12 times.",
        ('Packers', 'Bears'): "Packers-Bears is the NFL's oldest rivalry, dating back to 1921.",
    }

    def __init__(self):
        pass

    def get_trivia(
        self,
        sport: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get random trivia fact

        Args:
            sport: Sport name
            context: Optional context to find relevant trivia

        Returns:
            Trivia string or None
        """
        sport_key = sport.lower()

        # Try to find context-relevant trivia first
        if context:
            relevant_trivia = self._get_relevant_trivia(sport_key, context)
            if relevant_trivia:
                return relevant_trivia

        # Otherwise return random trivia for sport
        trivia_list = self.TRIVIA_DB.get(sport_key, [])
        if trivia_list:
            return random.choice(trivia_list)

        return None

    def get_multiple_trivia(
        self,
        sport: str,
        count: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Get multiple trivia facts

        Args:
            sport: Sport name
            count: Number of trivia facts to return
            context: Optional context for relevance

        Returns:
            List of trivia strings
        """
        sport_key = sport.lower()
        trivia_list = self.TRIVIA_DB.get(sport_key, [])

        if not trivia_list:
            return []

        # Get random sample
        count = min(count, len(trivia_list))
        return random.sample(trivia_list, count)

    def _get_relevant_trivia(
        self,
        sport: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Get context-relevant trivia"""
        # Check for rivalries in recent games
        games = context.get('recent_games', [])
        for game in games:
            home = game.get('home_team', '')
            away = game.get('away_team', '')

            # Check rivalry facts
            for (team1, team2), fact in self.RIVALRY_FACTS.items():
                if (team1 in home and team2 in away) or (team1 in away and team2 in home):
                    return f"💡 **Did You Know?** {fact}"

        # Check for team-specific trivia based on trends
        trends = context.get('trends', [])
        for trend in trends:
            team = trend.get('team', '')
            # Could expand with team-specific facts
            pass

        return None

    def format_trivia_injection(
        self,
        trivia: str,
        style: str = 'callout'
    ) -> str:
        """
        Format trivia for injection into story

        Args:
            trivia: Trivia text
            style: Display style (callout, inline, sidebar)

        Returns:
            Formatted trivia string
        """
        if style == 'callout':
            return f"\n\n---\n💡 **Did You Know?**\n\n_{trivia}_\n---\n\n"
        elif style == 'inline':
            return f" (Fun fact: {trivia})"
        elif style == 'sidebar':
            return f"\n### 💡 Trivia\n\n{trivia}\n"
        else:
            return trivia

    def inject_trivia_into_story(
        self,
        story_text: str,
        sport: str,
        context: Optional[Dict[str, Any]] = None,
        position: str = 'middle'
    ) -> str:
        """
        Inject trivia into story text

        Args:
            story_text: Original story text
            sport: Sport name
            context: Optional context
            position: Where to inject (top, middle, bottom)

        Returns:
            Story text with trivia injected
        """
        trivia = self.get_trivia(sport, context)
        if not trivia:
            return story_text

        formatted_trivia = self.format_trivia_injection(trivia)

        # Split story into paragraphs
        paragraphs = story_text.split('\n\n')

        if position == 'top':
            insert_index = 1  # After headline
        elif position == 'bottom':
            insert_index = len(paragraphs) - 1
        else:  # middle
            insert_index = len(paragraphs) // 2

        # Insert trivia
        paragraphs.insert(insert_index, formatted_trivia)

        return '\n\n'.join(paragraphs)
