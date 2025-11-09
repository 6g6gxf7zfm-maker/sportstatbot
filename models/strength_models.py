"""
Opponent Strength and Team Power Models

1. Adaptive opponent-strength weighting per possession
5. Bayesian updating of team power scores after each game
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class OpponentStrengthWeighting:
    """
    Adaptive opponent-strength weighting per possession.

    Adjusts performance metrics based on opponent quality, with weights
    that adapt throughout the game based on score differential and momentum.
    """

    def __init__(self, base_strength_range: Tuple[float, float] = (0.5, 1.5)):
        """
        Initialize opponent strength weighting model.

        Args:
            base_strength_range: (min, max) multiplier for opponent strength
        """
        self.min_strength = base_strength_range[0]
        self.max_strength = base_strength_range[1]
        self.opponent_ratings = {}

    def calculate_opponent_strength(
        self,
        opponent_id: str,
        opponent_record: Dict[str, int],
        opponent_stats: Dict[str, float],
        league_average: Dict[str, float]
    ) -> float:
        """
        Calculate opponent strength rating.

        Args:
            opponent_id: Unique opponent identifier
            opponent_record: Win-loss record {'wins': int, 'losses': int}
            opponent_stats: Key performance stats
            league_average: League average stats for normalization

        Returns:
            Strength rating (0.5 = weak, 1.0 = average, 1.5 = elite)
        """
        # Calculate win percentage component
        total_games = opponent_record['wins'] + opponent_record['losses']
        win_pct = opponent_record['wins'] / max(total_games, 1)

        # Calculate statistical component (normalized against league average)
        stat_scores = []
        for stat_key in ['points_per_game', 'points_allowed', 'point_differential']:
            if stat_key in opponent_stats and stat_key in league_average:
                league_avg = league_average[stat_key]
                if league_avg > 0:
                    normalized = opponent_stats[stat_key] / league_avg
                    stat_scores.append(normalized)

        stat_component = np.mean(stat_scores) if stat_scores else 1.0

        # Combine components (60% record, 40% stats)
        base_strength = (0.6 * (win_pct * 2) + 0.4 * stat_component)

        # Clamp to valid range
        strength = np.clip(base_strength, self.min_strength, self.max_strength)

        self.opponent_ratings[opponent_id] = strength
        return strength

    def weight_possession_value(
        self,
        possession_value: float,
        opponent_strength: float,
        game_context: Dict
    ) -> float:
        """
        Weight a possession's value by opponent strength and game context.

        Args:
            possession_value: Raw possession value (points expected)
            opponent_strength: Opponent strength rating
            game_context: {'score_diff': int, 'time_remaining': float, 'momentum': float}

        Returns:
            Adjusted possession value
        """
        # Base adjustment by opponent strength
        adjusted_value = possession_value * opponent_strength

        # Context adjustments
        score_diff = game_context.get('score_diff', 0)
        time_remaining = game_context.get('time_remaining', 1.0)  # 0-1 normalized
        momentum = game_context.get('momentum', 0)  # -1 to 1

        # Increase weight in close games late
        if abs(score_diff) <= 7 and time_remaining < 0.25:
            adjusted_value *= 1.2

        # Momentum factor (slight adjustment)
        momentum_factor = 1.0 + (momentum * 0.1)
        adjusted_value *= momentum_factor

        return adjusted_value

    def get_strength_of_schedule(
        self,
        opponents_faced: List[str]
    ) -> float:
        """
        Calculate strength of schedule from faced opponents.

        Args:
            opponents_faced: List of opponent IDs

        Returns:
            Average opponent strength
        """
        if not opponents_faced:
            return 1.0

        strengths = [
            self.opponent_ratings.get(opp_id, 1.0)
            for opp_id in opponents_faced
        ]

        return np.mean(strengths)


class BayesianTeamPowerScores:
    """
    Bayesian updating of team power scores after each game.

    Uses Bayesian inference to continuously update team strength ratings,
    with priors based on historical performance and likelihood from game results.
    """

    def __init__(
        self,
        prior_mean: float = 1500.0,
        prior_variance: float = 200.0,
        k_factor: float = 32.0
    ):
        """
        Initialize Bayesian team power model.

        Args:
            prior_mean: Initial mean rating for all teams
            prior_variance: Initial variance (uncertainty)
            k_factor: Learning rate for updates
        """
        self.prior_mean = prior_mean
        self.prior_variance = prior_variance
        self.k_factor = k_factor

        # Store team ratings as (mean, variance) tuples
        self.team_ratings: Dict[str, Tuple[float, float]] = {}
        self.rating_history: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    def initialize_team(self, team_id: str, historical_record: Optional[Dict] = None):
        """
        Initialize a team's rating with prior.

        Args:
            team_id: Unique team identifier
            historical_record: Optional historical data to inform prior
        """
        if historical_record:
            # Adjust prior based on historical performance
            win_pct = historical_record.get('win_pct', 0.5)
            # Convert win% to rating (50% = 1500, 100% = 2000, 0% = 1000)
            adjusted_mean = self.prior_mean + ((win_pct - 0.5) * 1000)
            # Reduce variance if we have historical data
            adjusted_variance = self.prior_variance * 0.7
            self.team_ratings[team_id] = (adjusted_mean, adjusted_variance)
        else:
            self.team_ratings[team_id] = (self.prior_mean, self.prior_variance)

        self.rating_history[team_id].append(self.team_ratings[team_id])

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for team A vs team B.

        Args:
            rating_a: Team A's rating
            rating_b: Team B's rating

        Returns:
            Expected score (0 to 1, where 0.5 is even matchup)
        """
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(
        self,
        team_a_id: str,
        team_b_id: str,
        score_a: int,
        score_b: int,
        home_advantage: float = 50.0
    ) -> Dict[str, Tuple[float, float]]:
        """
        Update team ratings after a game using Bayesian updating.

        Args:
            team_a_id: Team A identifier
            team_b_id: Team B identifier
            score_a: Team A's score
            score_b: Team B's score
            home_advantage: Rating points for home team

        Returns:
            Updated ratings dict {team_id: (mean, variance)}
        """
        # Initialize teams if needed
        if team_a_id not in self.team_ratings:
            self.initialize_team(team_a_id)
        if team_b_id not in self.team_ratings:
            self.initialize_team(team_b_id)

        # Get current ratings
        rating_a, var_a = self.team_ratings[team_a_id]
        rating_b, var_b = self.team_ratings[team_b_id]

        # Apply home advantage to team A (assuming team A is home)
        rating_a_adj = rating_a + home_advantage

        # Calculate expected outcome
        expected_a = self.expected_score(rating_a_adj, rating_b)

        # Calculate actual outcome (normalized to 0-1)
        total_score = score_a + score_b
        actual_a = score_a / max(total_score, 1) if total_score > 0 else 0.5

        # Margin of victory multiplier
        score_diff = abs(score_a - score_b)
        mov_multiplier = np.log(max(score_diff, 1) + 1)

        # Update ratings using modified Elo with Bayesian variance
        prediction_error = actual_a - expected_a

        # Adaptive K-factor based on uncertainty (higher variance = larger updates)
        k_a = self.k_factor * (var_a / self.prior_variance)
        k_b = self.k_factor * (var_b / self.prior_variance)

        # Update means
        new_rating_a = rating_a + (k_a * mov_multiplier * prediction_error)
        new_rating_b = rating_b - (k_b * mov_multiplier * prediction_error)

        # Update variances (reduce after each game - we're more certain)
        new_var_a = var_a * 0.95
        new_var_b = var_b * 0.95

        # Store updated ratings
        self.team_ratings[team_a_id] = (new_rating_a, new_var_a)
        self.team_ratings[team_b_id] = (new_rating_b, new_var_b)

        # Record history
        self.rating_history[team_a_id].append((new_rating_a, new_var_a))
        self.rating_history[team_b_id].append((new_rating_b, new_var_b))

        return {
            team_a_id: (new_rating_a, new_var_a),
            team_b_id: (new_rating_b, new_var_b)
        }

    def get_win_probability(
        self,
        team_a_id: str,
        team_b_id: str,
        home_team: str = None
    ) -> float:
        """
        Calculate win probability for team A vs team B.

        Args:
            team_a_id: Team A identifier
            team_b_id: Team B identifier
            home_team: Which team is home (team_a_id or team_b_id)

        Returns:
            Win probability for team A (0 to 1)
        """
        if team_a_id not in self.team_ratings or team_b_id not in self.team_ratings:
            return 0.5

        rating_a, _ = self.team_ratings[team_a_id]
        rating_b, _ = self.team_ratings[team_b_id]

        # Apply home advantage
        if home_team == team_a_id:
            rating_a += 50
        elif home_team == team_b_id:
            rating_b += 50

        return self.expected_score(rating_a, rating_b)

    def get_confidence_interval(
        self,
        team_id: str,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Get confidence interval for team rating.

        Args:
            team_id: Team identifier
            confidence_level: Confidence level (default 95%)

        Returns:
            (lower_bound, upper_bound) rating range
        """
        if team_id not in self.team_ratings:
            return (self.prior_mean, self.prior_mean)

        mean, variance = self.team_ratings[team_id]
        std_dev = np.sqrt(variance)

        # Z-score for confidence level
        z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%

        lower = mean - (z_score * std_dev)
        upper = mean + (z_score * std_dev)

        return (lower, upper)
