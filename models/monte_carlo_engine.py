"""
Monte Carlo Simulation Engine for game outcome prediction.

Runs 10,000+ simulations per game to predict outcomes and probabilities.
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class GameSimulationInput:
    """Input parameters for game simulation."""
    home_team: str
    away_team: str
    home_power_rating: float
    away_power_rating: float
    home_offensive_rating: float
    away_offensive_rating: float
    home_defensive_rating: float
    away_defensive_rating: float
    sport: str
    home_advantage: float = 3.0  # Points/goals home advantage
    injury_impact_home: float = 0.0  # Negative impact
    injury_impact_away: float = 0.0
    fatigue_factor_home: float = 1.0  # Multiplier (1.0 = normal)
    fatigue_factor_away: float = 1.0
    momentum_home: float = 0.0  # Recent performance adjustment
    momentum_away: float = 0.0
    weather_impact: Optional[Dict] = None
    travel_penalty_home: float = 0.0
    travel_penalty_away: float = 0.0


@dataclass
class SimulationResult:
    """Result of Monte Carlo simulation."""
    home_team: str
    away_team: str
    home_win_probability: float
    away_win_probability: float
    tie_probability: float
    expected_home_score: float
    expected_away_score: float
    expected_spread: float  # From home team perspective
    home_score_distribution: List[int]
    away_score_distribution: List[int]
    confidence_interval_home: Tuple[float, float]  # 95% CI
    confidence_interval_away: Tuple[float, float]
    upset_probability: float  # If underdog wins
    blowout_probability: float  # Win by 14+ points (or sport equivalent)
    close_game_probability: float  # Within 3 points/1 goal
    over_under_suggestion: float
    most_likely_score: Tuple[int, int]


class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for sports game predictions.

    Runs 10,000+ simulations incorporating multiple factors:
    - Team power ratings
    - Home field advantage
    - Injuries and fatigue
    - Momentum and recent performance
    - Weather conditions
    - Travel impact
    """

    def __init__(self, num_simulations: int = 10000):
        """
        Initialize the simulator.

        Args:
            num_simulations: Number of simulations to run (default 10,000)
        """
        self.num_simulations = num_simulations
        self.random_seed = None

        # Sport-specific parameters
        self.sport_configs = {
            'nfl': {
                'base_score': 24,
                'score_variance': 10,
                'blowout_threshold': 14,
                'close_threshold': 3,
                'home_advantage': 2.5,
                'possession_based': False
            },
            'nba': {
                'base_score': 110,
                'score_variance': 15,
                'blowout_threshold': 15,
                'close_threshold': 5,
                'home_advantage': 3.5,
                'possession_based': False
            },
            'mlb': {
                'base_score': 4.5,
                'score_variance': 2.5,
                'blowout_threshold': 5,
                'close_threshold': 1,
                'home_advantage': 0.3,
                'possession_based': False
            },
            'nhl': {
                'base_score': 3.0,
                'score_variance': 1.8,
                'blowout_threshold': 3,
                'close_threshold': 1,
                'home_advantage': 0.4,
                'possession_based': True
            },
            'mls': {
                'base_score': 1.5,
                'score_variance': 1.2,
                'blowout_threshold': 3,
                'close_threshold': 1,
                'home_advantage': 0.5,
                'possession_based': True
            },
            'soccer': {
                'base_score': 1.8,
                'score_variance': 1.3,
                'blowout_threshold': 3,
                'close_threshold': 1,
                'home_advantage': 0.45,
                'possession_based': True
            }
        }

    def simulate_game(self, game_input: GameSimulationInput) -> SimulationResult:
        """
        Run Monte Carlo simulation for a single game.

        Args:
            game_input: Game parameters for simulation

        Returns:
            SimulationResult with probabilities and predictions
        """
        if self.random_seed:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        sport_config = self.sport_configs.get(game_input.sport, self.sport_configs['nfl'])

        home_scores = []
        away_scores = []
        home_wins = 0
        away_wins = 0
        ties = 0

        for _ in range(self.num_simulations):
            home_score, away_score = self._simulate_single_game(game_input, sport_config)

            home_scores.append(home_score)
            away_scores.append(away_score)

            if home_score > away_score:
                home_wins += 1
            elif away_score > home_score:
                away_wins += 1
            else:
                ties += 1

        # Calculate statistics
        home_win_prob = home_wins / self.num_simulations
        away_win_prob = away_wins / self.num_simulations
        tie_prob = ties / self.num_simulations

        expected_home = np.mean(home_scores)
        expected_away = np.mean(away_scores)
        expected_spread = expected_home - expected_away

        # Confidence intervals (95%)
        home_ci = (np.percentile(home_scores, 2.5), np.percentile(home_scores, 97.5))
        away_ci = (np.percentile(away_scores, 2.5), np.percentile(away_scores, 97.5))

        # Calculate special probabilities
        upset_prob = self._calculate_upset_probability(
            game_input, home_win_prob, away_win_prob
        )

        blowout_prob = sum(
            1 for h, a in zip(home_scores, away_scores)
            if abs(h - a) >= sport_config['blowout_threshold']
        ) / self.num_simulations

        close_prob = sum(
            1 for h, a in zip(home_scores, away_scores)
            if abs(h - a) <= sport_config['close_threshold']
        ) / self.num_simulations

        # Most likely score
        score_combos = Counter(zip(home_scores, away_scores))
        most_likely = score_combos.most_common(1)[0][0]

        # Over/under suggestion
        over_under = expected_home + expected_away

        return SimulationResult(
            home_team=game_input.home_team,
            away_team=game_input.away_team,
            home_win_probability=home_win_prob,
            away_win_probability=away_win_prob,
            tie_probability=tie_prob,
            expected_home_score=round(expected_home, 1),
            expected_away_score=round(expected_away, 1),
            expected_spread=round(expected_spread, 1),
            home_score_distribution=home_scores,
            away_score_distribution=away_scores,
            confidence_interval_home=home_ci,
            confidence_interval_away=away_ci,
            upset_probability=upset_prob,
            blowout_probability=blowout_prob,
            close_game_probability=close_prob,
            over_under_suggestion=round(over_under, 1),
            most_likely_score=most_likely
        )

    def _simulate_single_game(
        self,
        game_input: GameSimulationInput,
        sport_config: Dict
    ) -> Tuple[int, int]:
        """
        Simulate a single game instance.

        Args:
            game_input: Game parameters
            sport_config: Sport-specific configuration

        Returns:
            Tuple of (home_score, away_score)
        """
        # Calculate effective ratings with all adjustments
        home_rating = (
            game_input.home_power_rating +
            sport_config['home_advantage'] +
            game_input.home_advantage +
            game_input.momentum_home -
            game_input.injury_impact_home -
            game_input.travel_penalty_home
        ) * game_input.fatigue_factor_home

        away_rating = (
            game_input.away_power_rating +
            game_input.momentum_away -
            game_input.injury_impact_away -
            game_input.travel_penalty_away
        ) * game_input.fatigue_factor_away

        # Calculate expected scores with offensive/defensive adjustments
        home_offensive_factor = game_input.home_offensive_rating / 100
        away_defensive_factor = game_input.away_defensive_rating / 100
        home_expected = (
            sport_config['base_score'] *
            (1 + (home_rating - away_rating) / 25) *
            home_offensive_factor *
            (2 - away_defensive_factor)
        )

        away_offensive_factor = game_input.away_offensive_rating / 100
        home_defensive_factor = game_input.home_defensive_rating / 100
        away_expected = (
            sport_config['base_score'] *
            (1 + (away_rating - home_rating) / 25) *
            away_offensive_factor *
            (2 - home_defensive_factor)
        )

        # Add random variance
        home_score = max(0, np.random.normal(
            home_expected,
            sport_config['score_variance']
        ))
        away_score = max(0, np.random.normal(
            away_expected,
            sport_config['score_variance']
        ))

        # Round to integers (or appropriate precision for sport)
        if sport_config.get('possession_based'):
            # Soccer/hockey can have more precise intermediate scores
            home_score = max(0, round(home_score))
            away_score = max(0, round(away_score))
        else:
            home_score = max(0, int(round(home_score)))
            away_score = max(0, int(round(away_score)))

        return home_score, away_score

    def _calculate_upset_probability(
        self,
        game_input: GameSimulationInput,
        home_win_prob: float,
        away_win_prob: float
    ) -> float:
        """Calculate probability of an upset occurring."""
        # Determine favorite based on power ratings
        if game_input.home_power_rating > game_input.away_power_rating:
            # Home is favorite, upset if away wins
            return away_win_prob
        elif game_input.away_power_rating > game_input.home_power_rating:
            # Away is favorite, upset if home wins
            return home_win_prob
        else:
            # Even matchup, no real upset
            return 0.0

    def simulate_multiple_games(
        self,
        games: List[GameSimulationInput]
    ) -> List[SimulationResult]:
        """
        Simulate multiple games efficiently.

        Args:
            games: List of game inputs to simulate

        Returns:
            List of simulation results
        """
        return [self.simulate_game(game) for game in games]

    def get_win_probability_by_score(
        self,
        game_input: GameSimulationInput,
        current_home_score: int,
        current_away_score: int,
        time_remaining: float  # As percentage (0-1)
    ) -> Dict[str, float]:
        """
        Calculate win probability given current score and time remaining.
        Used for live game predictions.

        Args:
            game_input: Original game parameters
            current_home_score: Current home team score
            current_away_score: Current away team score
            time_remaining: Percentage of game remaining (0.0 to 1.0)

        Returns:
            Dictionary with updated win probabilities
        """
        # Adjust simulation to account for current state
        adjusted_simulations = 0
        home_wins = 0
        away_wins = 0

        sport_config = self.sport_configs.get(
            game_input.sport,
            self.sport_configs['nfl']
        )

        for _ in range(self.num_simulations):
            # Simulate only the remaining portion
            home_additional, away_additional = self._simulate_single_game(
                game_input, sport_config
            )

            # Scale by time remaining
            home_additional = int(home_additional * time_remaining)
            away_additional = int(away_additional * time_remaining)

            final_home = current_home_score + home_additional
            final_away = current_away_score + away_additional

            if final_home > final_away:
                home_wins += 1
            elif final_away > final_home:
                away_wins += 1

            adjusted_simulations += 1

        return {
            'home_win_probability': home_wins / adjusted_simulations,
            'away_win_probability': away_wins / adjusted_simulations,
            'current_score_diff': current_home_score - current_away_score,
            'time_remaining_pct': time_remaining
        }

    def set_random_seed(self, seed: int):
        """Set random seed for reproducible simulations."""
        self.random_seed = seed
