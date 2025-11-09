"""Game Narrative Detector Plugin - Classifies game narratives automatically."""
from typing import Dict, Any, List
from ..base_plugin import BasePlugin, PluginCategory, PluginPriority


class GameNarrativeDetector(BasePlugin):
    """
    Detects and classifies game narratives such as:
    - Comeback
    - Collapse
    - Blowout
    - Thriller
    - Defensive Battle
    - Shootout
    """

    @property
    def name(self) -> str:
        return "game_narrative_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Automatically detects and classifies game narratives (Comeback, Collapse, Blowout, Thriller, etc.)"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.GENERATOR

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.HIGH

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze games and detect narratives.

        Args:
            data: Contains 'recent_games' with game data

        Returns:
            Dictionary with narrative classifications for each game
        """
        recent_games = data.get('sport_data', {}).get('recent_games', [])

        if not recent_games:
            return {'narratives': []}

        narratives = []

        for game in recent_games:
            narrative = self._classify_game_narrative(game)
            if narrative:
                narratives.append({
                    'game': game.get('matchup', 'Unknown'),
                    'narrative': narrative['type'],
                    'description': narrative['description'],
                    'intensity': narrative['intensity']
                })

        return {'narratives': narratives}

    def _classify_game_narrative(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single game's narrative.

        Args:
            game: Game data dictionary

        Returns:
            Narrative classification with type, description, and intensity
        """
        home_score = game.get('home_score', 0)
        away_score = game.get('away_score', 0)

        if home_score == 0 or away_score == 0:
            return None

        total_points = home_score + away_score
        point_diff = abs(home_score - away_score)

        # Blowout: Large margin of victory
        if point_diff >= 20:
            winner = "home" if home_score > away_score else "away"
            return {
                'type': 'Blowout',
                'description': f"Dominant {winner} team performance",
                'intensity': self._calculate_intensity(point_diff, 'blowout')
            }

        # Thriller: Very close game
        elif point_diff <= 3:
            return {
                'type': 'Thriller',
                'description': 'Down-to-the-wire finish',
                'intensity': self._calculate_intensity(point_diff, 'thriller')
            }

        # Defensive Battle: Low scoring game
        elif total_points < 40 and point_diff <= 10:
            return {
                'type': 'Defensive Battle',
                'description': 'Low-scoring defensive showcase',
                'intensity': 'medium'
            }

        # Shootout: High scoring game
        elif total_points > 100:
            return {
                'type': 'Shootout',
                'description': 'High-octane offensive explosion',
                'intensity': 'high'
            }

        # Comeback detection would require quarter-by-quarter data
        # For now, detect potential comebacks from close games with high total
        elif point_diff <= 7 and total_points > 80:
            return {
                'type': 'Potential Comeback',
                'description': 'Competitive back-and-forth game',
                'intensity': 'medium'
            }

        # Default competitive game
        return {
            'type': 'Competitive',
            'description': 'Standard competitive matchup',
            'intensity': 'medium'
        }

    def _calculate_intensity(self, point_diff: int, narrative_type: str) -> str:
        """
        Calculate narrative intensity based on game factors.

        Args:
            point_diff: Point differential
            narrative_type: Type of narrative

        Returns:
            Intensity level (low, medium, high, extreme)
        """
        if narrative_type == 'blowout':
            if point_diff >= 40:
                return 'extreme'
            elif point_diff >= 30:
                return 'high'
            elif point_diff >= 20:
                return 'medium'
            else:
                return 'low'

        elif narrative_type == 'thriller':
            if point_diff == 1:
                return 'extreme'
            elif point_diff == 2:
                return 'high'
            else:
                return 'medium'

        return 'medium'
