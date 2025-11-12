"""
Viral Score Calculator
Calculates the viral potential of sports highlights
"""

import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViralScoreCalculator:
    """Calculates viral potential score for sports highlights"""

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize viral score calculator

        Args:
            weights: Custom weights for score components
        """
        self.weights = weights or {
            'game_importance': 0.3,
            'play_type': 0.25,
            'player_popularity': 0.25,
            'historical_engagement': 0.2
        }

        # Play type scores (1-10)
        self.play_type_scores = {
            'buzzer_beater': 10,
            'game_winner': 10,
            'walk_off': 10,
            'dunk': 8,
            'poster': 9,
            'alley_oop': 8,
            'touchdown': 7,
            'interception': 7,
            'home_run': 8,
            'grand_slam': 9,
            'goal': 7,
            'bicycle_kick': 10,
            'volley': 8,
            'block': 7,
            'ankle_breaker': 9,
            'crossover': 8,
            'assist': 6,
            'highlight': 6,
            'save': 7
        }

        # Popular players (simplified - in production use a database)
        self.popular_players = {
            # NBA
            'LeBron James': 10, 'Stephen Curry': 10, 'Kevin Durant': 9,
            'Giannis Antetokounmpo': 9, 'Luka Doncic': 9, 'Jayson Tatum': 8,
            # NFL
            'Patrick Mahomes': 10, 'Josh Allen': 9, 'Joe Burrow': 9,
            'Travis Kelce': 9, 'Christian McCaffrey': 8,
            # Soccer
            'Lionel Messi': 10, 'Cristiano Ronaldo': 10, 'Kylian Mbappe': 10,
            'Erling Haaland': 9, 'Vinicius Junior': 8,
            # MLB
            'Shohei Ohtani': 10, 'Aaron Judge': 9, 'Mike Trout': 9
        }

    def calculate_score(self, highlight: Dict) -> float:
        """
        Calculate viral score for a highlight

        Args:
            highlight: Highlight dictionary with metadata

        Returns:
            Viral score from 1-10
        """
        try:
            scores = {}

            # Game importance score
            scores['game_importance'] = self._calculate_game_importance(highlight)

            # Play type score
            scores['play_type'] = self._calculate_play_type_score(highlight)

            # Player popularity score
            scores['player_popularity'] = self._calculate_player_score(highlight)

            # Historical engagement score (placeholder for now)
            scores['historical_engagement'] = self._calculate_historical_score(highlight)

            # Weighted average
            total_score = sum(
                scores[component] * self.weights[component]
                for component in self.weights.keys()
            )

            # Normalize to 1-10 scale
            final_score = max(1, min(10, total_score))

            logger.info(f"Viral score calculated: {final_score:.1f} for {highlight.get('headline', 'Unknown')}")
            logger.debug(f"Component scores: {scores}")

            return round(final_score, 1)

        except Exception as e:
            logger.error(f"Error calculating viral score: {e}")
            return 5.0  # Default middle score

    def _calculate_game_importance(self, highlight: Dict) -> float:
        """Calculate score based on game importance"""
        score = 5.0  # Base score

        event_name = highlight.get('event_name', '').lower()
        sport = highlight.get('sport', '')

        # Playoffs and championships
        playoff_keywords = ['playoff', 'championship', 'finals', 'conference', 'super bowl', 'world series']
        if any(keyword in event_name for keyword in playoff_keywords):
            score += 3

        # Rivalry games
        rivalry_keywords = ['rivalry', 'classic', 'derby']
        if any(keyword in event_name for keyword in rivalry_keywords):
            score += 2

        # Prime time / national TV
        # Could check game time here
        # For now, boost weekend games
        # This is simplified - would need actual game datetime

        # Division games
        if 'division' in event_name:
            score += 1

        return min(10, score)

    def _calculate_play_type_score(self, highlight: Dict) -> float:
        """Calculate score based on play type"""
        play_type = highlight.get('play_type', 'highlight')

        # Get base score from play type
        base_score = self.play_type_scores.get(play_type, 6)

        # Check headline for excitement keywords
        headline = highlight.get('headline', '').lower()
        description = highlight.get('description', '').lower()

        text = headline + " " + description

        excitement_keywords = {
            'incredible': 1,
            'insane': 1,
            'unbelievable': 1,
            'amazing': 1,
            'ridiculous': 1,
            'nasty': 1,
            'sick': 1,
            'filthy': 1,
            'clutch': 2,
            'game-winning': 2,
            'last-second': 2
        }

        bonus = 0
        for keyword, points in excitement_keywords.items():
            if keyword in text:
                bonus += points

        score = base_score + min(bonus, 2)  # Cap bonus at 2 points

        return min(10, score)

    def _calculate_player_score(self, highlight: Dict) -> float:
        """Calculate score based on player popularity"""
        players = highlight.get('players', [])

        if not players:
            return 5.0  # Default if no players identified

        # Get highest popularity score from involved players
        max_score = 5.0

        for player in players:
            player_score = self.popular_players.get(player, 5)
            max_score = max(max_score, player_score)

        return max_score

    def _calculate_historical_score(self, highlight: Dict) -> float:
        """
        Calculate score based on historical engagement patterns
        This is a placeholder - in production would query database
        """
        sport = highlight.get('sport', '')
        play_type = highlight.get('play_type', '')

        # Simplified scoring based on sport popularity on social media
        sport_engagement = {
            'NBA': 8,
            'NFL': 9,
            'MLB': 6,
            'MLS': 5,
            'EPL': 8,
            'LaLiga': 7,
            'Champions League': 9
        }

        base_score = sport_engagement.get(sport, 5)

        # In production, this would query actual engagement metrics
        # from your database for similar highlights

        return base_score

    def rank_highlights(self, highlights: List[Dict]) -> List[Dict]:
        """
        Rank highlights by viral score

        Args:
            highlights: List of highlight dictionaries

        Returns:
            Sorted list of highlights (highest score first)
        """
        # Calculate scores for all highlights
        for highlight in highlights:
            if 'viral_score' not in highlight:
                highlight['viral_score'] = self.calculate_score(highlight)

        # Sort by viral score (descending)
        ranked = sorted(
            highlights,
            key=lambda x: x.get('viral_score', 0),
            reverse=True
        )

        logger.info(f"Ranked {len(ranked)} highlights by viral score")

        return ranked

    def filter_by_threshold(
        self,
        highlights: List[Dict],
        threshold: float = 7.0
    ) -> List[Dict]:
        """
        Filter highlights by minimum viral score

        Args:
            highlights: List of highlights
            threshold: Minimum viral score

        Returns:
            Filtered list of highlights
        """
        filtered = [
            h for h in highlights
            if h.get('viral_score', 0) >= threshold
        ]

        logger.info(f"Filtered {len(filtered)}/{len(highlights)} highlights above threshold {threshold}")

        return filtered


def test_viral_score():
    """Test the viral score calculator"""
    calculator = ViralScoreCalculator()

    test_highlights = [
        {
            'sport': 'NBA',
            'event_name': 'Lakers vs Celtics - NBA Finals Game 7',
            'headline': 'LeBron James clutch game-winning three at the buzzer',
            'description': 'Incredible shot to win the championship',
            'play_type': 'buzzer_beater',
            'players': ['LeBron James']
        },
        {
            'sport': 'NFL',
            'event_name': 'Chiefs vs Bills',
            'headline': 'Patrick Mahomes touchdown pass',
            'description': 'Nice throw for a TD',
            'play_type': 'touchdown',
            'players': ['Patrick Mahomes']
        },
        {
            'sport': 'MLS',
            'event_name': 'Regular season match',
            'headline': 'Goal scored',
            'description': 'A goal in the match',
            'play_type': 'goal',
            'players': []
        }
    ]

    print("\n=== Viral Score Analysis ===\n")

    for highlight in test_highlights:
        score = calculator.calculate_score(highlight)
        print(f"Highlight: {highlight['headline']}")
        print(f"Viral Score: {score}/10")
        print(f"Sport: {highlight['sport']} | Play Type: {highlight['play_type']}")
        print()

    # Test ranking
    ranked = calculator.rank_highlights(test_highlights)
    print("\n=== Ranked Highlights ===\n")
    for i, h in enumerate(ranked, 1):
        print(f"{i}. [{h['viral_score']}/10] {h['headline']}")


if __name__ == "__main__":
    test_viral_score()
