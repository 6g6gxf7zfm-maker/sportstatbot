"""
Playoff Bracket Simulator.

Simulates playoff brackets and updates daily with new seeds.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class PlayoffScenario:
    """Single playoff scenario result."""
    scenario_id: int
    bracket: Dict[str, str]  # round -> matchup
    champion: str
    runner_up: str
    final_four: List[str]


@dataclass
class PlayoffProjection:
    """Complete playoff projection."""
    sport: str
    current_seeds: Dict[int, str]  # seed -> team
    championship_odds: Dict[str, float]  # team -> probability
    most_likely_champion: str
    most_likely_matchup: str
    scenarios: List[PlayoffScenario]


class PlayoffBracketSimulator:
    """Simulates playoff brackets and championship odds."""

    def __init__(self, num_simulations: int = 10000):
        """Initialize playoff simulator."""
        self.num_simulations = num_simulations

    def simulate_playoffs(
        self,
        sport: str,
        seeds: Dict[int, str],
        team_ratings: Dict[str, float],
        bracket_format: str = 'standard'
    ) -> PlayoffProjection:
        """
        Simulate playoff bracket.

        Args:
            sport: Sport type
            seeds: Current playoff seeding
            team_ratings: Team power ratings
            bracket_format: 'standard', 'nhl_style', etc.

        Returns:
            PlayoffProjection with championship odds
        """
        championship_count = {}
        scenarios = []

        for sim in range(self.num_simulations):
            # Simulate entire bracket
            result = self._simulate_single_bracket(
                seeds, team_ratings, bracket_format
            )

            champion = result['champion']
            championship_count[champion] = championship_count.get(champion, 0) + 1

            # Store sample scenarios
            if sim < 100:
                scenarios.append(PlayoffScenario(
                    scenario_id=sim,
                    bracket=result['bracket'],
                    champion=champion,
                    runner_up=result['runner_up'],
                    final_four=result['final_four']
                ))

        # Calculate championship odds
        championship_odds = {
            team: (count / self.num_simulations) * 100
            for team, count in championship_count.items()
        }

        most_likely = max(championship_odds.items(), key=lambda x: x[1])[0]

        return PlayoffProjection(
            sport=sport,
            current_seeds=seeds,
            championship_odds=championship_odds,
            most_likely_champion=most_likely,
            most_likely_matchup=f"{seeds[1]} vs {seeds[2]}",
            scenarios=scenarios[:10]
        )

    def _simulate_single_bracket(
        self,
        seeds: Dict[int, str],
        ratings: Dict[str, float],
        bracket_format: str
    ) -> Dict:
        """Simulate a single bracket."""
        # Simplified bracket simulation
        # Round 1 matchups (1v8, 2v7, 3v6, 4v5)
        remaining = list(seeds.values())

        # Quarterfinals
        qf_winners = []
        for i in range(0, len(remaining), 2):
            if i + 1 < len(remaining):
                team1, team2 = remaining[i], remaining[i+1]
                winner = self._simulate_matchup(team1, team2, ratings)
                qf_winners.append(winner)

        # Semifinals
        sf_winners = []
        for i in range(0, len(qf_winners), 2):
            if i + 1 < len(qf_winners):
                team1, team2 = qf_winners[i], qf_winners[i+1]
                winner = self._simulate_matchup(team1, team2, ratings)
                sf_winners.append(winner)

        # Finals
        if len(sf_winners) >= 2:
            champion = self._simulate_matchup(sf_winners[0], sf_winners[1], ratings)
            runner_up = sf_winners[0] if champion == sf_winners[1] else sf_winners[1]
        else:
            champion = sf_winners[0] if sf_winners else remaining[0]
            runner_up = remaining[1] if len(remaining) > 1 else remaining[0]

        return {
            'champion': champion,
            'runner_up': runner_up,
            'final_four': qf_winners if qf_winners else remaining[:4],
            'bracket': {}
        }

    def _simulate_matchup(
        self,
        team1: str,
        team2: str,
        ratings: Dict[str, float]
    ) -> str:
        """Simulate a playoff matchup."""
        rating1 = ratings.get(team1, 1500)
        rating2 = ratings.get(team2, 1500)

        # Win probability
        prob1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))

        return team1 if random.random() < prob1 else team2


