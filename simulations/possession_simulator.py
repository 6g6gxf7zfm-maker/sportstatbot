"""Ball possession simulator for soccer and hockey expected sequences."""
from typing import Dict, List
import random


class PossessionSimulator:
    """
    Simulates ball/puck possession sequences for soccer and hockey.

    Models possession chains, expected goals, and scoring opportunities.
    """

    def __init__(self):
        """Initialize possession simulator."""
        self.possession_weights = self._get_possession_weights()

    def simulate_match_possession(
        self,
        home_team_strength: float,
        away_team_strength: float,
        sport: str = 'soccer'
    ) -> Dict:
        """
        Simulate possession-based match.

        Args:
            home_team_strength: Home team attacking strength
            away_team_strength: Away team attacking strength
            sport: 'soccer' or 'hockey'

        Returns:
            Dictionary with possession-based predictions
        """
        # Calculate expected possession split
        total_strength = home_team_strength + away_team_strength
        home_possession_pct = home_team_strength / total_strength if total_strength > 0 else 0.5

        # Simulate possession sequences
        num_sequences = 200 if sport == 'soccer' else 120  # Total possessions in match

        home_chances = 0
        away_chances = 0
        home_goals = 0
        away_goals = 0

        for _ in range(num_sequences):
            if random.random() < home_possession_pct:
                # Home team possession
                outcome = self._simulate_possession_sequence(
                    home_team_strength, away_team_strength, 'attack'
                )
                if outcome == 'chance':
                    home_chances += 1
                    if self._converts_chance(home_team_strength, sport):
                        home_goals += 1
            else:
                # Away team possession
                outcome = self._simulate_possession_sequence(
                    away_team_strength, home_team_strength, 'attack'
                )
                if outcome == 'chance':
                    away_chances += 1
                    if self._converts_chance(away_team_strength, sport):
                        away_goals += 1

        # Calculate expected goals (xG)
        home_xg = home_chances * self._chance_quality_factor(home_team_strength, sport)
        away_xg = away_chances * self._chance_quality_factor(away_team_strength, sport)

        return {
            'home_possession_pct': round(home_possession_pct * 100, 1),
            'away_possession_pct': round((1 - home_possession_pct) * 100, 1),
            'home_scoring_chances': home_chances,
            'away_scoring_chances': away_chances,
            'home_expected_goals': round(home_xg, 2),
            'away_expected_goals': round(away_xg, 2),
            'home_simulated_goals': home_goals,
            'away_simulated_goals': away_goals,
            'home_chance_conversion': round(home_goals / home_chances * 100, 1) if home_chances > 0 else 0,
            'away_chance_conversion': round(away_goals / away_chances * 100, 1) if away_chances > 0 else 0,
            'sport': sport
        }

    def _simulate_possession_sequence(
        self,
        attacking_strength: float,
        defending_strength: float,
        sequence_type: str
    ) -> str:
        """
        Simulate a single possession sequence.

        Returns: 'chance', 'turnover', or 'neutral'
        """
        # Calculate probability of creating chance
        strength_diff = attacking_strength - defending_strength
        chance_prob = 0.15 + (strength_diff / 1000)  # Base 15% + strength diff

        rand = random.random()

        if rand < chance_prob:
            return 'chance'
        elif rand < chance_prob + 0.3:
            return 'turnover'
        else:
            return 'neutral'

    def _converts_chance(self, team_strength: float, sport: str) -> bool:
        """Determine if scoring chance results in goal."""
        if sport == 'soccer':
            base_conversion = 0.12  # ~12% conversion rate
        else:  # hockey
            base_conversion = 0.10  # ~10% conversion rate

        # Adjust based on team strength
        conversion_rate = base_conversion + ((team_strength - 1500) / 10000)

        return random.random() < conversion_rate

    def _chance_quality_factor(self, team_strength: float, sport: str) -> float:
        """Calculate expected goals per chance."""
        if sport == 'soccer':
            base_quality = 0.10
        else:
            base_quality = 0.08

        # Adjust for team strength
        quality = base_quality + ((team_strength - 1500) / 15000)

        return max(0.05, min(0.25, quality))

    def _get_possession_weights(self) -> Dict:
        """Get possession importance weights by sport."""
        return {
            'soccer': {
                'possession_importance': 0.6,
                'counterattack_effectiveness': 0.8
            },
            'hockey': {
                'possession_importance': 0.5,
                'counterattack_effectiveness': 0.9
            }
        }
