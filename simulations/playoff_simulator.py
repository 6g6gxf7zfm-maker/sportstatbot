"""Playoff bracket simulator with daily auto-updates."""
from typing import Dict, List, Optional
from datetime import datetime
import json
import os


class PlayoffSimulator:
    """
    Simulates playoff brackets and championship probabilities.

    Auto-updates daily as teams' records and ratings change.
    """

    def __init__(
        self,
        monte_carlo_engine=None,
        power_rating_system=None,
        storage_path: str = './data/playoffs'
    ):
        """
        Initialize playoff simulator.

        Args:
            monte_carlo_engine: MonteCarloEngine instance
            power_rating_system: PowerRatingSystem instance
            storage_path: Path to store playoff data
        """
        self.monte_carlo = monte_carlo_engine
        self.power_rating = power_rating_system
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def simulate_playoff_bracket(
        self,
        bracket: Dict,
        sport: str,
        num_simulations: int = 10000
    ) -> Dict:
        """
        Simulate playoff bracket outcomes.

        Args:
            bracket: Playoff bracket structure
            sport: Sport type
            num_simulations: Number of Monte Carlo simulations

        Returns:
            Dictionary with championship probabilities
        """
        championship_wins = {}
        round_appearances = {team: {} for team in bracket.get('teams', [])}

        # Run simulations
        for _ in range(num_simulations):
            winner, rounds = self._simulate_single_bracket(bracket, sport)

            # Track championship wins
            championship_wins[winner] = championship_wins.get(winner, 0) + 1

            # Track round appearances
            for team, final_round in rounds.items():
                round_appearances[team][final_round] = round_appearances[team].get(final_round, 0) + 1

        # Calculate probabilities
        results = {}
        for team in bracket.get('teams', []):
            results[team] = {
                'championship_probability': championship_wins.get(team, 0) / num_simulations,
                'finals_probability': round_appearances[team].get('finals', 0) / num_simulations,
                'conference_finals_probability': round_appearances[team].get('conference_finals', 0) / num_simulations,
                'round_appearances': round_appearances[team],
                'seed': bracket['seeds'].get(team, 'N/A')
            }

        return {
            'results': results,
            'most_likely_champion': max(championship_wins, key=championship_wins.get),
            'simulations_run': num_simulations,
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }

    def _simulate_single_bracket(self, bracket: Dict, sport: str) -> tuple:
        """Simulate a single playoff bracket."""
        current_round = bracket['first_round'].copy()
        rounds_reached = {team: 'first_round' for team in bracket['teams']}

        round_names = ['first_round', 'conference_semis', 'conference_finals', 'finals', 'champion']
        current_round_name = 0

        while len(current_round) > 1:
            next_round = []

            # Simulate each matchup
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    team1 = current_round[i]
                    team2 = current_round[i + 1]

                    winner = self._simulate_series(team1, team2, sport)
                    next_round.append(winner)

                    # Update rounds reached
                    if current_round_name < len(round_names) - 1:
                        rounds_reached[winner] = round_names[current_round_name + 1]

            current_round = next_round
            current_round_name += 1

        champion = current_round[0] if current_round else None
        rounds_reached[champion] = 'champion'

        return champion, rounds_reached

    def _simulate_series(self, team1: str, team2: str, sport: str, best_of: int = 7) -> str:
        """Simulate a playoff series."""
        if not self.monte_carlo or not self.power_rating:
            # Random 50-50
            import random
            return random.choice([team1, team2])

        team1_rating = self.power_rating.get_rating(team1, sport)
        team2_rating = self.power_rating.get_rating(team2, sport)

        team1_wins = 0
        team2_wins = 0
        games_needed = (best_of // 2) + 1

        # Simulate games until one team wins
        while team1_wins < games_needed and team2_wins < games_needed:
            # Alternate home court
            if (team1_wins + team2_wins) % 2 == 0:
                # Team1 home
                result = self.monte_carlo.simulate_game(
                    team1_rating, team2_rating, sport,
                    home_advantage=2.5
                )
                if result.home_win_probability > 0.5:
                    # Determine winner by random draw weighted by probability
                    import random
                    if random.random() < result.home_win_probability:
                        team1_wins += 1
                    else:
                        team2_wins += 1
                else:
                    if random.random() < result.away_win_probability:
                        team2_wins += 1
                    else:
                        team1_wins += 1
            else:
                # Team2 home
                result = self.monte_carlo.simulate_game(
                    team2_rating, team1_rating, sport,
                    home_advantage=2.5
                )
                import random
                if random.random() < result.home_win_probability:
                    team2_wins += 1
                else:
                    team1_wins += 1

        return team1 if team1_wins >= games_needed else team2

    def get_daily_update(self, sport: str, current_standings: Dict) -> Dict:
        """
        Generate daily playoff probability update.

        Args:
            sport: Sport type
            current_standings: Current team standings

        Returns:
            Updated playoff probabilities
        """
        # This would regenerate the bracket based on current standings
        # and re-run simulations

        update = {
            'date': datetime.now().isoformat(),
            'sport': sport,
            'playoff_picture': self._generate_playoff_picture(current_standings, sport),
            'bubble_teams': self._identify_bubble_teams(current_standings),
            'eliminated_teams': self._identify_eliminated_teams(current_standings),
            'clinched_teams': self._identify_clinched_teams(current_standings)
        }

        self._save_daily_update(sport, update)

        return update

    def _generate_playoff_picture(self, standings: Dict, sport: str) -> List[Dict]:
        """Generate current playoff seeding."""
        # Simplified - would need sport-specific playoff formats
        sorted_teams = sorted(
            standings.items(),
            key=lambda x: x[1].get('win_pct', 0),
            reverse=True
        )

        playoff_spots = {
            'nfl': 14,
            'nba': 16,
            'nhl': 16,
            'mlb': 12,
            'mls': 14
        }

        spots = playoff_spots.get(sport, 16)

        playoff_teams = []
        for i, (team, record) in enumerate(sorted_teams[:spots]):
            playoff_teams.append({
                'seed': i + 1,
                'team': team,
                'record': record,
                'clinched': i < spots // 2  # Top half clinched (simplified)
            })

        return playoff_teams

    def _identify_bubble_teams(self, standings: Dict) -> List[str]:
        """Identify teams on playoff bubble."""
        # Teams within 2 games of playoff spot
        return []  # Simplified

    def _identify_eliminated_teams(self, standings: Dict) -> List[str]:
        """Identify mathematically eliminated teams."""
        return []  # Simplified

    def _identify_clinched_teams(self, standings: Dict) -> List[str]:
        """Identify teams that clinched playoffs."""
        return []  # Simplified

    def _save_daily_update(self, sport: str, update: Dict):
        """Save daily update to disk."""
        filepath = os.path.join(
            self.storage_path,
            f'{sport}_daily_{datetime.now().strftime("%Y%m%d")}.json'
        )
        try:
            with open(filepath, 'w') as f:
                json.dump(update, f, indent=2)
        except Exception as e:
            print(f"Error saving playoff update: {e}")
