"""
Season Projection System.

Projects win totals, playoff odds, and championship probabilities for teams.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
from datetime import datetime, timedelta


@dataclass
class TeamProjection:
    """Season projection for a team."""
    team_name: str
    sport: str
    current_wins: int
    current_losses: int
    games_remaining: int
    projected_wins: float
    projected_losses: float
    projected_win_total: float
    win_total_range: Tuple[float, float]  # 80% confidence interval
    playoff_probability: float
    division_title_probability: float
    championship_probability: float
    strength_of_schedule_remaining: float
    key_games_remaining: List[str]


@dataclass
class SeasonOutlook:
    """Complete season outlook."""
    sport: str
    projections: List[TeamProjection]
    playoff_scenarios: Dict[str, List[str]]  # seed -> list of teams
    last_updated: str


class SeasonProjector:
    """
    Projects team performance for the remainder of the season.

    Features:
    - Win total forecasts with confidence intervals
    - Playoff probability calculations
    - Division/conference standings projections
    - Championship odds
    - Strength of schedule analysis
    """

    def __init__(self, num_simulations: int = 10000):
        """
        Initialize season projector.

        Args:
            num_simulations: Number of Monte Carlo simulations to run
        """
        self.num_simulations = num_simulations

        # Sport-specific configs
        self.sport_configs = {
            'nfl': {
                'regular_season_games': 17,
                'playoff_teams': 14,
                'divisions': 8
            },
            'nba': {
                'regular_season_games': 82,
                'playoff_teams': 16,
                'divisions': 6
            },
            'mlb': {
                'regular_season_games': 162,
                'playoff_teams': 12,
                'divisions': 6
            },
            'nhl': {
                'regular_season_games': 82,
                'playoff_teams': 16,
                'divisions': 8
            },
            'mls': {
                'regular_season_games': 34,
                'playoff_teams': 18,
                'divisions': 2
            }
        }

    def project_season(
        self,
        team_name: str,
        sport: str,
        current_record: Tuple[int, int],
        team_rating: float,
        remaining_schedule: List[Dict],
        opponent_ratings: Dict[str, float],
        division_teams: Optional[List[str]] = None
    ) -> TeamProjection:
        """
        Project season outcomes for a team.

        Args:
            team_name: Team name
            sport: Sport type
            current_record: (wins, losses) tuple
            team_rating: Team's power rating
            remaining_schedule: List of remaining games with opponent info
            opponent_ratings: Dictionary of opponent name -> rating
            division_teams: List of teams in same division

        Returns:
            TeamProjection with all predictions
        """
        current_wins, current_losses = current_record
        games_remaining = len(remaining_schedule)

        # Run simulations
        win_totals = []
        playoff_appearances = 0
        division_titles = 0
        championships = 0

        for _ in range(self.num_simulations):
            sim_wins = current_wins
            sim_losses = current_losses

            # Simulate each remaining game
            for game in remaining_schedule:
                opponent = game.get('opponent')
                is_home = game.get('is_home', True)
                opponent_rating = opponent_ratings.get(opponent, team_rating)

                # Calculate win probability
                win_prob = self._calculate_win_probability(
                    team_rating, opponent_rating, is_home, sport
                )

                # Simulate game result
                if random.random() < win_prob:
                    sim_wins += 1
                else:
                    sim_losses += 1

            win_totals.append(sim_wins)

            # Check if team makes playoffs based on win total
            # (Simplified - in reality would need full standings)
            if self._makes_playoffs(sim_wins, sport):
                playoff_appearances += 1

                # If in playoffs, chance at division/championship
                if division_teams and self._wins_division(team_rating, opponent_ratings, division_teams):
                    division_titles += 1

                # Championship odds (rough estimate based on rating and playoff seed)
                if self._wins_championship(team_rating, sport):
                    championships += 1

        # Calculate statistics
        projected_wins = sum(win_totals) / len(win_totals)
        projected_losses = current_losses + (games_remaining - (projected_wins - current_wins))

        # 80% confidence interval (10th to 90th percentile)
        win_totals_sorted = sorted(win_totals)
        low_idx = int(len(win_totals_sorted) * 0.10)
        high_idx = int(len(win_totals_sorted) * 0.90)
        win_range = (win_totals_sorted[low_idx], win_totals_sorted[high_idx])

        # Calculate probabilities
        playoff_prob = playoff_appearances / self.num_simulations
        division_prob = division_titles / max(1, playoff_appearances) if playoff_appearances > 0 else 0
        championship_prob = championships / self.num_simulations

        # Calculate strength of schedule
        sos = self._calculate_strength_of_schedule(remaining_schedule, opponent_ratings, team_rating)

        # Identify key games
        key_games = self._identify_key_games(remaining_schedule, opponent_ratings, team_rating, sport)

        return TeamProjection(
            team_name=team_name,
            sport=sport,
            current_wins=current_wins,
            current_losses=current_losses,
            games_remaining=games_remaining,
            projected_wins=round(projected_wins - current_wins, 1),
            projected_losses=round(projected_losses - current_losses, 1),
            projected_win_total=round(projected_wins, 1),
            win_total_range=win_range,
            playoff_probability=round(playoff_prob * 100, 1),
            division_title_probability=round(division_prob * 100, 1),
            championship_probability=round(championship_prob * 100, 1),
            strength_of_schedule_remaining=round(sos, 2),
            key_games_remaining=key_games
        )

    def project_full_season(
        self,
        sport: str,
        teams_data: Dict[str, Dict]
    ) -> SeasonOutlook:
        """
        Project full season for all teams.

        Args:
            sport: Sport type
            teams_data: Dictionary of team_name -> team data including:
                - current_record: (wins, losses)
                - rating: power rating
                - remaining_schedule: list of games
                - division: division name

        Returns:
            SeasonOutlook with all team projections
        """
        projections = []
        opponent_ratings = {
            name: data['rating']
            for name, data in teams_data.items()
        }

        for team_name, team_data in teams_data.items():
            division_teams = [
                name for name, data in teams_data.items()
                if data.get('division') == team_data.get('division')
            ]

            projection = self.project_season(
                team_name=team_name,
                sport=sport,
                current_record=team_data['current_record'],
                team_rating=team_data['rating'],
                remaining_schedule=team_data.get('remaining_schedule', []),
                opponent_ratings=opponent_ratings,
                division_teams=division_teams
            )
            projections.append(projection)

        # Sort by playoff probability
        projections.sort(key=lambda x: x.playoff_probability, reverse=True)

        # Generate playoff scenarios
        playoff_scenarios = self._generate_playoff_scenarios(projections, sport)

        return SeasonOutlook(
            sport=sport,
            projections=projections,
            playoff_scenarios=playoff_scenarios,
            last_updated=datetime.now().isoformat()
        )

    def _calculate_win_probability(
        self,
        team_rating: float,
        opponent_rating: float,
        is_home: bool,
        sport: str
    ) -> float:
        """Calculate win probability for a single game."""
        home_advantage = 50 if is_home else -50  # Rating points
        adjusted_rating = team_rating + home_advantage
        rating_diff = adjusted_rating - opponent_rating

        # Convert rating difference to win probability
        # Using logistic function
        win_prob = 1 / (1 + 10 ** (-rating_diff / 400))
        return win_prob

    def _makes_playoffs(self, wins: int, sport: str) -> bool:
        """Determine if win total is likely to make playoffs."""
        config = self.sport_configs.get(sport, self.sport_configs['nfl'])
        total_games = config['regular_season_games']

        # Rough playoff thresholds by sport
        thresholds = {
            'nfl': 0.53,  # ~9 wins out of 17
            'nba': 0.50,  # ~41 wins out of 82
            'mlb': 0.53,  # ~86 wins out of 162
            'nhl': 0.55,  # ~45 wins out of 82
            'mls': 0.47   # ~16 wins out of 34
        }

        threshold = thresholds.get(sport, 0.50)
        return (wins / total_games) >= threshold

    def _wins_division(
        self,
        team_rating: float,
        opponent_ratings: Dict[str, float],
        division_teams: List[str]
    ) -> bool:
        """Simulate if team wins division."""
        division_ratings = [
            opponent_ratings.get(team, 1500)
            for team in division_teams
        ]

        if not division_ratings:
            return False

        # Probability based on relative rating
        total_strength = sum(division_ratings) + team_rating
        win_prob = team_rating / total_strength

        return random.random() < win_prob

    def _wins_championship(self, team_rating: float, sport: str) -> bool:
        """Simulate if team wins championship (given they're in playoffs)."""
        # Rough championship probability based on rating
        # Higher rated teams have better odds
        avg_rating = 1500
        rating_diff = team_rating - avg_rating

        # Top teams (~1700+) have ~10-15% championship odds
        # Average teams (~1500) have ~3-5% odds
        # Weak playoff teams (~1400) have ~1% odds
        base_prob = 0.03
        rating_factor = rating_diff / 1000
        championship_prob = base_prob + rating_factor

        championship_prob = max(0.01, min(0.20, championship_prob))

        return random.random() < championship_prob

    def _calculate_strength_of_schedule(
        self,
        remaining_schedule: List[Dict],
        opponent_ratings: Dict[str, float],
        team_rating: float
    ) -> float:
        """
        Calculate strength of remaining schedule.

        Returns:
            Float where 1.0 = average, >1.0 = harder, <1.0 = easier
        """
        if not remaining_schedule:
            return 1.0

        opponent_rating_sum = sum(
            opponent_ratings.get(game.get('opponent'), team_rating)
            for game in remaining_schedule
        )

        avg_opponent_rating = opponent_rating_sum / len(remaining_schedule)
        avg_league_rating = sum(opponent_ratings.values()) / max(len(opponent_ratings), 1)

        # Normalize to 1.0
        if avg_league_rating == 0:
            return 1.0

        return avg_opponent_rating / avg_league_rating

    def _identify_key_games(
        self,
        remaining_schedule: List[Dict],
        opponent_ratings: Dict[str, float],
        team_rating: float,
        sport: str
    ) -> List[str]:
        """Identify most important remaining games."""
        key_games = []

        for game in remaining_schedule:
            opponent = game.get('opponent', 'Unknown')
            opponent_rating = opponent_ratings.get(opponent, team_rating)

            # Key game criteria:
            # 1. Close rating match (competitive game)
            # 2. Division game
            # 3. Playoff implications
            rating_diff = abs(team_rating - opponent_rating)

            is_key = False
            reasons = []

            if rating_diff < 100:  # Close matchup
                is_key = True
                reasons.append("close matchup")

            if game.get('is_division', False):
                is_key = True
                reasons.append("division game")

            if game.get('playoff_implications', False):
                is_key = True
                reasons.append("playoff implications")

            if opponent_rating > team_rating + 100:  # Strong opponent
                is_key = True
                reasons.append("vs strong opponent")

            if is_key:
                key_games.append(f"{opponent} ({', '.join(reasons)})")

        return key_games[:10]  # Return top 10

    def _generate_playoff_scenarios(
        self,
        projections: List[TeamProjection],
        sport: str
    ) -> Dict[str, List[str]]:
        """Generate likely playoff seeding scenarios."""
        config = self.sport_configs.get(sport, self.sport_configs['nfl'])
        num_playoff_teams = config['playoff_teams']

        # Sort by projected wins
        sorted_teams = sorted(
            projections,
            key=lambda x: x.projected_win_total,
            reverse=True
        )

        playoff_scenarios = {}

        for i, team in enumerate(sorted_teams[:num_playoff_teams], 1):
            seed = f"Seed {i}"
            if seed not in playoff_scenarios:
                playoff_scenarios[seed] = []
            playoff_scenarios[seed].append(team.team_name)

        return playoff_scenarios
