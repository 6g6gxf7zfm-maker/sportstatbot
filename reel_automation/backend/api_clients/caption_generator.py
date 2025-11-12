"""
Caption Generator using Claude API
Generates viral Instagram captions for sports reels
"""

import anthropic
import logging
from typing import Dict, List, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Generates viral captions for sports reels using Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize caption generator

        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_caption(
        self,
        sport: str,
        teams: List[str],
        players: List[str],
        play_description: str,
        play_type: str,
        style: str = "hype"
    ) -> Dict[str, any]:
        """
        Generate viral caption for a sports highlight

        Args:
            sport: Sport name (NBA, NFL, etc.)
            teams: List of team names
            players: List of player names involved
            play_description: Description of the play
            play_type: Type of play (dunk, touchdown, etc.)
            style: Caption style (hype, analytical, funny, casual)

        Returns:
            Dictionary with caption, hashtags, and metadata
        """
        if not self.client:
            logger.warning("No API client - using fallback caption")
            return self._generate_fallback_caption(sport, teams, players, play_type)

        try:
            # Build the prompt for Claude
            prompt = self._build_caption_prompt(
                sport, teams, players, play_description, play_type, style
            )

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text
            caption_data = self._parse_caption_response(response_text, sport)

            logger.info(f"Generated caption for {sport} highlight")
            return caption_data

        except Exception as e:
            logger.error(f"Error generating caption with Claude: {e}")
            return self._generate_fallback_caption(sport, teams, players, play_type)

    def _build_caption_prompt(
        self,
        sport: str,
        teams: List[str],
        players: List[str],
        play_description: str,
        play_type: str,
        style: str
    ) -> str:
        """Build the prompt for Claude to generate caption"""

        teams_str = " vs ".join(teams) if teams else "teams"
        players_str = ", ".join(players) if players else "players"

        style_instructions = {
            "hype": "extremely energetic and exciting, use CAPS and fire emojis",
            "analytical": "insightful and strategic, focus on the skill involved",
            "funny": "humorous and entertaining, use clever wordplay",
            "casual": "conversational and relatable, like talking to a friend"
        }

        style_guide = style_instructions.get(style, style_instructions["hype"])

        prompt = f"""You are an expert social media content creator for sports Instagram pages. Create a viral Instagram Reel caption for the following sports highlight.

SPORT: {sport}
TEAMS: {teams_str}
PLAYERS: {players_str}
PLAY TYPE: {play_type}
DESCRIPTION: {play_description}

CAPTION REQUIREMENTS:
1. Start with a 3-word hook in ALL CAPS with an emoji (must be attention-grabbing)
2. Follow with one line of context about the play
3. End with an engagement question to boost comments
4. Style: {style_guide}

HASHTAG REQUIREMENTS:
- Provide exactly 15 hashtags
- 5 broad sports hashtags (e.g., #Sports, #Highlights)
- 5 community hashtags (e.g., #{sport}Community, #{sport}Fans)
- 5 specific hashtags (e.g., #TeamName, #PlayerName, #PlayType)

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
HOOK: [3-word hook in CAPS with emoji]
CONTEXT: [One line context]
QUESTION: [Engagement question]

HASHTAGS: [all 15 hashtags on one line, separated by spaces]

Generate the caption now:"""

        return prompt

    def _parse_caption_response(self, response: str, sport: str) -> Dict[str, any]:
        """Parse Claude's response into structured caption data"""

        lines = response.strip().split('\n')

        hook = ""
        context = ""
        question = ""
        hashtags = []

        for line in lines:
            line = line.strip()
            if line.startswith("HOOK:"):
                hook = line.replace("HOOK:", "").strip()
            elif line.startswith("CONTEXT:"):
                context = line.replace("CONTEXT:", "").strip()
            elif line.startswith("QUESTION:"):
                question = line.replace("QUESTION:", "").strip()
            elif line.startswith("HASHTAGS:"):
                hashtag_line = line.replace("HASHTAGS:", "").strip()
                hashtags = [tag.strip() for tag in hashtag_line.split() if tag.strip().startswith('#')]

        # Construct full caption
        caption_parts = []
        if hook:
            caption_parts.append(hook)
        if context:
            caption_parts.append(context)
        if question:
            caption_parts.append(question)

        full_caption = "\n\n".join(caption_parts)

        # Add hashtags
        if hashtags:
            full_caption += "\n\n" + " ".join(hashtags)

        return {
            "caption": full_caption,
            "hook": hook,
            "context": context,
            "question": question,
            "hashtags": hashtags,
            "hashtag_count": len(hashtags)
        }

    def _generate_fallback_caption(
        self,
        sport: str,
        teams: List[str],
        players: List[str],
        play_type: str
    ) -> Dict[str, any]:
        """Generate a simple fallback caption when API is unavailable"""

        hooks = {
            'NBA': "INSANE PLAY 🔥",
            'NFL': "UNBELIEVABLE TOUCHDOWN 🏈",
            'MLB': "INCREDIBLE CATCH ⚾",
            'MLS': "AMAZING GOAL ⚽",
            'EPL': "ABSOLUTE BANGER ⚽",
            'LaLiga': "WHAT A GOAL ⚽"
        }

        hook = hooks.get(sport, "MUST SEE 🔥")

        teams_str = " vs ".join(teams) if teams else "the game"
        players_str = players[0] if players else "the player"

        context = f"{players_str} came through in {teams_str}!"
        question = "What did you think of this play? 👇"

        # Generate hashtags
        hashtags = self._generate_default_hashtags(sport, teams, players, play_type)

        caption = f"{hook}\n\n{context}\n\n{question}\n\n" + " ".join(hashtags)

        return {
            "caption": caption,
            "hook": hook,
            "context": context,
            "question": question,
            "hashtags": hashtags,
            "hashtag_count": len(hashtags)
        }

    def _generate_default_hashtags(
        self,
        sport: str,
        teams: List[str],
        players: List[str],
        play_type: str
    ) -> List[str]:
        """Generate default hashtags"""

        hashtags = []

        # Broad hashtags
        broad = ["#Sports", "#Highlights", "#SportsHighlights", "#Viral", "#ForYou"]
        hashtags.extend(broad[:5])

        # Sport-specific community hashtags
        sport_tag = f"#{sport}"
        community = [
            sport_tag,
            f"#{sport}Highlights",
            f"#{sport}Fans",
            f"#{sport}Community",
            f"#{sport}Nation"
        ]
        hashtags.extend(community[:5])

        # Specific hashtags
        specific = []
        for team in teams[:2]:
            team_tag = "#" + team.replace(" ", "")
            specific.append(team_tag)

        for player in players[:1]:
            player_tag = "#" + player.replace(" ", "")
            specific.append(player_tag)

        if play_type:
            play_tag = "#" + play_type.replace("_", "").title()
            specific.append(play_tag)

        specific.extend(["#Amazing", "#Incredible", "#MustWatch"])
        hashtags.extend(specific[:5])

        return hashtags[:15]

    def generate_batch_captions(
        self,
        highlights: List[Dict],
        style: str = "hype"
    ) -> List[Dict]:
        """
        Generate captions for multiple highlights

        Args:
            highlights: List of highlight dictionaries
            style: Caption style to use

        Returns:
            List of highlights with added caption data
        """
        results = []

        for highlight in highlights:
            logger.info(f"Generating caption for: {highlight.get('headline', 'Unknown')}")

            caption_data = self.generate_caption(
                sport=highlight.get('sport', 'Sports'),
                teams=highlight.get('teams', []),
                players=highlight.get('players', []),
                play_description=highlight.get('description', ''),
                play_type=highlight.get('play_type', 'highlight'),
                style=style
            )

            # Add caption data to highlight
            highlight['caption'] = caption_data['caption']
            highlight['hook'] = caption_data['hook']
            highlight['hashtags'] = caption_data['hashtags']

            results.append(highlight)

        return results


def test_caption_generator():
    """Test the caption generator"""
    generator = CaptionGenerator()

    # Test with sample highlight
    test_highlight = {
        'sport': 'NBA',
        'teams': ['Lakers', 'Celtics'],
        'players': ['LeBron James'],
        'description': 'LeBron hits game-winning three-pointer at the buzzer',
        'play_type': 'buzzer_beater'
    }

    caption_data = generator.generate_caption(
        sport=test_highlight['sport'],
        teams=test_highlight['teams'],
        players=test_highlight['players'],
        play_description=test_highlight['description'],
        play_type=test_highlight['play_type'],
        style='hype'
    )

    print("\n=== Generated Caption ===")
    print(caption_data['caption'])
    print(f"\nHashtag count: {caption_data['hashtag_count']}")


if __name__ == "__main__":
    test_caption_generator()
