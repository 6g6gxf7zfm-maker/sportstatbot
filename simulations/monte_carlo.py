"""Monte Carlo simulation engine for game outcome predictions."""
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimulationResult:
    """Result of a single simulation run."""
    home_score: float
    away_score: float
    home_win: bool
    margin: float


@dataclass
class GameSimulationSummary:
    """Summary statistics from Monte Carlo simulations."""
    home_win_probability: float
    away_win_probability: float
    tie_probability: float
    expected_home_score: float
    expected_away_score: float
    expected_margin: float
    home_score_std: float
    away_score_std: float
    home_score_percentiles: Dict[int, float]
    away_score_percentiles: Dict[int, float]
    simulations_run: int
    timestamp: datetime


class MonteCarloEngine:
    """
    Monte Carlo simulation engine for sports game predictions.

    Runs 10,000+ simulations per game to generate probability distributions
    for scores, win probabilities, and various game outcomes.
    """

    def __init__(self, num_simulations: int = 10000, seed: Optional[int] = None):
        """
        Initialize Monte Carlo engine.

        Args:
            num_simulations: Number of simulations to run per game (default 10,000)
            seed: Random seed for reproducibility (optional)
        """
        self.num_simulations = num_simulations
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def simulate_game(
        self,
        home_team_strength: float,
        away_team_strength: float,
        sport: str = 'nfl',
        home_advantage: float = 2.5,
        variance_factor: float = 1.0,
        **kwargs
    ) -> GameSimulationSummary:
        """
        Run Monte Carlo simulation for a single game.

        Args:
            home_team_strength: Home team power rating (e.g., Elo rating)
            away_team_strength: Away team power rating
            sport: Sport type ('nfl', 'nba', 'nhl', 'mlb', 'mls')
            home_advantage: Points added for home field advantage
            variance_factor: Multiplier for score variance (1.0 = normal)
            **kwargs: Additional factors (fatigue, injuries, momentum, etc.)

        Returns:
            GameSimulationSummary with probability distributions and statistics
        """
        # Extract additional factors
        home_fatigue = kwargs.get('home_fatigue', 0)  # Negative impact
        away_fatigue = kwargs.get('away_fatigue', 0)
        home_injuries = kwargs.get('home_injuries', 0)  # Negative impact (0-10 scale)
        away_injuries = kwargs.get('away_injuries', 0)
        home_momentum = kwargs.get('home_momentum', 0)  # Positive/negative (-5 to +5)
        away_momentum = kwargs.get('away_momentum', 0)
        travel_penalty = kwargs.get('travel_penalty', 0)  # Applied to away team
        weather_impact = kwargs.get('weather_impact', 0)  # Can affect both teams

        # Adjust team strengths based on factors
        adjusted_home = (home_team_strength + home_advantage + home_momentum -
                        home_fatigue - home_injuries * 0.5 + weather_impact)
        adjusted_away = (away_team_strength + away_momentum -
                        away_fatigue - away_injuries * 0.5 - travel_penalty)

        # Get sport-specific parameters
        scoring_params = self._get_sport_parameters(sport)
        base_score = scoring_params['base_score']
        score_std = scoring_params['score_std'] * variance_factor
        min_score = scoring_params['min_score']
        max_score = scoring_params['max_score']

        # Run simulations
        simulations = []
        for _ in range(self.num_simulations):
            sim_result = self._run_single_simulation(
                adjusted_home, adjusted_away, base_score, score_std, min_score, max_score, sport
            )
            simulations.append(sim_result)

        # Calculate statistics
        return self._calculate_summary(simulations, sport)

    def _run_single_simulation(
        self,
        home_strength: float,
        away_strength: float,
        base_score: float,
        score_std: float,
        min_score: float,
        max_score: float,
        sport: str
    ) -> SimulationResult:
        """Run a single game simulation."""
        # Calculate expected scores based on team strengths
        strength_diff = home_strength - away_strength

        # Home team expected score with random variation
        home_expected = base_score + (strength_diff * 0.5)
        home_score = np.random.normal(home_expected, score_std)
        home_score = max(min_score, min(max_score, home_score))

        # Away team expected score with random variation
        away_expected = base_score - (strength_diff * 0.5)
        away_score = np.random.normal(away_expected, score_std)
        away_score = max(min_score, min(max_score, away_score))

        # Round to appropriate precision based on sport
        if sport in ['soccer', 'mls', 'nhl']:
            # Goals are integers
            home_score = round(home_score)
            away_score = round(away_score)
        elif sport == 'nfl':
            # Football scores are multiples of 1 (field goals/touchdowns)
            home_score = round(home_score)
            away_score = round(away_score)
        else:
            # Basketball/Baseball allow more granular scoring
            home_score = round(home_score, 1)
            away_score = round(away_score, 1)

        home_win = home_score > away_score
        margin = home_score - away_score

        return SimulationResult(home_score, away_score, home_win, margin)

    def _get_sport_parameters(self, sport: str) -> Dict:
        """Get sport-specific scoring parameters."""
        params = {
            'nfl': {
                'base_score': 24.0,
                'score_std': 10.0,
                'min_score': 0.0,
                'max_score': 70.0
            },
            'nba': {
                'base_score': 110.0,
                'score_std': 12.0,
                'min_score': 70.0,
                'max_score': 160.0
            },
            'mlb': {
                'base_score': 4.5,
                'score_std': 2.5,
                'min_score': 0.0,
                'max_score': 25.0
            },
            'nhl': {
                'base_score': 3.0,
                'score_std': 1.5,
                'min_score': 0.0,
                'max_score': 12.0
            },
            'mls': {
                'base_score': 1.5,
                'score_std': 1.2,
                'min_score': 0.0,
                'max_score': 8.0
            },
            'soccer': {
                'base_score': 1.8,
                'score_std': 1.3,
                'min_score': 0.0,
                'max_score': 10.0
            }
        }
        return params.get(sport.lower(), params['nfl'])

    def _calculate_summary(
        self,
        simulations: List[SimulationResult],
        sport: str
    ) -> GameSimulationSummary:
        """Calculate summary statistics from simulations."""
        home_scores = [s.home_score for s in simulations]
        away_scores = [s.away_score for s in simulations]
        home_wins = sum(1 for s in simulations if s.home_win)
        away_wins = sum(1 for s in simulations if not s.home_win and s.away_score != s.home_score)
        ties = sum(1 for s in simulations if s.home_score == s.away_score)

        # Calculate percentiles
        percentiles = [10, 25, 50, 75, 90]
        home_percentiles = {p: np.percentile(home_scores, p) for p in percentiles}
        away_percentiles = {p: np.percentile(away_scores, p) for p in percentiles}

        return GameSimulationSummary(
            home_win_probability=home_wins / len(simulations),
            away_win_probability=away_wins / len(simulations),
            tie_probability=ties / len(simulations),
            expected_home_score=np.mean(home_scores),
            expected_away_score=np.mean(away_scores),
            expected_margin=np.mean([s.margin for s in simulations]),
            home_score_std=np.std(home_scores),
            away_score_std=np.std(away_scores),
            home_score_percentiles=home_percentiles,
            away_score_percentiles=away_percentiles,
            simulations_run=len(simulations),
            timestamp=datetime.now()
        )

    def simulate_season(
        self,
        teams: List[str],
        team_strengths: Dict[str, float],
        schedule: List[Tuple[str, str]],
        sport: str = 'nfl'
    ) -> Dict[str, Dict]:
        """
        Simulate an entire season using Monte Carlo methods.

        Args:
            teams: List of team names
            team_strengths: Dictionary mapping team names to power ratings
            schedule: List of (home_team, away_team) tuples
            sport: Sport type

        Returns:
            Dictionary with season simulation results per team
        """
        # Initialize team records
        team_records = {team: {
            'wins': [],
            'losses': [],
            'ties': [],
            'points_for': [],
            'points_against': []
        } for team in teams}

        # Run simulations
        for _ in range(self.num_simulations):
            season_results = {team: {
                'wins': 0, 'losses': 0, 'ties': 0, 'pf': 0, 'pa': 0
            } for team in teams}

            # Simulate each game in schedule
            for home_team, away_team in schedule:
                home_strength = team_strengths.get(home_team, 1500)
                away_strength = team_strengths.get(away_team, 1500)

                sim = self._run_single_simulation(
                    home_strength, away_strength,
                    self._get_sport_parameters(sport)['base_score'],
                    self._get_sport_parameters(sport)['score_std'],
                    self._get_sport_parameters(sport)['min_score'],
                    self._get_sport_parameters(sport)['max_score'],
                    sport
                )

                # Update records
                season_results[home_team]['pf'] += sim.home_score
                season_results[home_team]['pa'] += sim.away_score
                season_results[away_team]['pf'] += sim.away_score
                season_results[away_team]['pa'] += sim.home_score

                if sim.home_win:
                    season_results[home_team]['wins'] += 1
                    season_results[away_team]['losses'] += 1
                elif sim.home_score == sim.away_score:
                    season_results[home_team]['ties'] += 1
                    season_results[away_team]['ties'] += 1
                else:
                    season_results[home_team]['losses'] += 1
                    season_results[away_team]['wins'] += 1

            # Store this simulation's results
            for team in teams:
                team_records[team]['wins'].append(season_results[team]['wins'])
                team_records[team]['losses'].append(season_results[team]['losses'])
                team_records[team]['ties'].append(season_results[team]['ties'])
                team_records[team]['points_for'].append(season_results[team]['pf'])
                team_records[team]['points_against'].append(season_results[team]['pa'])

        # Calculate statistics
        season_projections = {}
        for team in teams:
            season_projections[team] = {
                'projected_wins': np.mean(team_records[team]['wins']),
                'projected_losses': np.mean(team_records[team]['losses']),
                'projected_ties': np.mean(team_records[team]['ties']),
                'win_distribution': np.bincount(team_records[team]['wins']),
                'playoff_probability': self._calculate_playoff_odds(
                    team_records[team]['wins'], sport
                ),
                'expected_points_for': np.mean(team_records[team]['points_for']),
                'expected_points_against': np.mean(team_records[team]['points_against'])
            }

        return season_projections

    def _calculate_playoff_odds(self, wins_distribution: List[int], sport: str) -> float:
        """Calculate playoff probability based on win distribution."""
        # Sport-specific playoff thresholds (simplified)
        thresholds = {
            'nfl': 9,   # ~9 wins typically makes playoffs
            'nba': 41,  # ~41 wins for playoffs
            'mlb': 85,  # ~85 wins for playoffs
            'nhl': 90,  # ~90 points (simplified to wins)
            'mls': 45   # ~45 points
        }

        threshold = thresholds.get(sport.lower(), 9)
        playoff_sims = sum(1 for wins in wins_distribution if wins >= threshold)
        return playoff_sims / len(wins_distribution)

    def calculate_upset_probability(
        self,
        favorite_strength: float,
        underdog_strength: float,
        sport: str = 'nfl',
        **kwargs
    ) -> Dict:
        """
        Calculate probability of an upset (underdog winning).

        Args:
            favorite_strength: Power rating of favored team
            underdog_strength: Power rating of underdog
            sport: Sport type
            **kwargs: Additional factors

        Returns:
            Dictionary with upset probability and related statistics
        """
        # Assume favorite is home team for simulation
        sim_result = self.simulate_game(
            favorite_strength, underdog_strength, sport, **kwargs
        )

        upset_probability = 1 - sim_result.home_win_probability

        return {
            'upset_probability': upset_probability,
            'expected_margin': abs(sim_result.expected_margin),
            'is_potential_upset': upset_probability >= 0.3,  # 30%+ chance
            'confidence_level': 'HIGH' if upset_probability >= 0.4 else
                              'MEDIUM' if upset_probability >= 0.25 else 'LOW',
            'simulation_summary': sim_result
        }
