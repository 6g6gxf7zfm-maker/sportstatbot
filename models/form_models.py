"""
Form and Momentum Models

2. Rolling form index blending short-term streaks and long-term baseline
19. Regression to mean detector with confidence weighting
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import deque


class RollingFormIndex:
    """
    Rolling form index blending short-term streaks and long-term baseline.

    Combines recent performance (hot/cold streaks) with season-long baseline
    to create a comprehensive form metric.
    """

    def __init__(
        self,
        short_term_window: int = 5,
        long_term_window: int = 20,
        short_term_weight: float = 0.65,
        decay_factor: float = 0.95
    ):
        """
        Initialize rolling form index.

        Args:
            short_term_window: Games for short-term form (recent streak)
            long_term_window: Games for long-term baseline
            short_term_weight: Weight given to short-term vs long-term (0-1)
            decay_factor: Exponential decay for older games
        """
        self.short_window = short_term_window
        self.long_window = long_term_window
        self.short_weight = short_term_weight
        self.long_weight = 1.0 - short_term_weight
        self.decay_factor = decay_factor

        self.team_results: Dict[str, deque] = {}

    def add_game_result(
        self,
        team_id: str,
        result: Dict
    ):
        """
        Add a game result for a team.

        Args:
            team_id: Team identifier
            result: Game result dict with 'win', 'score_for', 'score_against', 'opponent_strength'
        """
        if team_id not in self.team_results:
            self.team_results[team_id] = deque(maxlen=self.long_window)

        self.team_results[team_id].append(result)

    def calculate_form_index(
        self,
        team_id: str,
        normalize: bool = True
    ) -> float:
        """
        Calculate composite form index for a team.

        Args:
            team_id: Team identifier
            normalize: Normalize to 0-100 scale

        Returns:
            Form index (higher = better form)
        """
        if team_id not in self.team_results or len(self.team_results[team_id]) == 0:
            return 50.0 if normalize else 0.0

        results = list(self.team_results[team_id])

        # Calculate short-term form (recent games)
        short_term_results = results[-self.short_window:]
        short_term_score = self._calculate_weighted_performance(short_term_results)

        # Calculate long-term baseline
        long_term_score = self._calculate_weighted_performance(results)

        # Blend short and long term
        composite = (
            self.short_weight * short_term_score +
            self.long_weight * long_term_score
        )

        if normalize:
            # Normalize to 0-100 scale (assuming composite is in -1 to 1 range)
            return (composite + 1) * 50
        return composite

    def _calculate_weighted_performance(
        self,
        results: List[Dict]
    ) -> float:
        """
        Calculate weighted performance score from results.

        Args:
            results: List of game results

        Returns:
            Performance score (-1 to 1)
        """
        if not results:
            return 0.0

        weighted_sum = 0.0
        weight_total = 0.0

        for i, result in enumerate(reversed(results)):
            # Exponential decay weight (more recent = higher weight)
            weight = self.decay_factor ** i

            # Win component (1 for win, -1 for loss)
            win_value = 1.0 if result.get('win', False) else -1.0

            # Performance component (score differential adjusted for opponent)
            score_diff = result.get('score_for', 0) - result.get('score_against', 0)
            opponent_strength = result.get('opponent_strength', 1.0)

            # Normalize score differential (-30 to 30 typical range)
            normalized_diff = np.clip(score_diff / 30.0, -1, 1)

            # Adjust by opponent strength
            adjusted_diff = normalized_diff * opponent_strength

            # Combine win and performance (70% win, 30% margin)
            game_score = 0.7 * win_value + 0.3 * adjusted_diff

            weighted_sum += weight * game_score
            weight_total += weight

        return weighted_sum / weight_total if weight_total > 0 else 0.0

    def get_momentum_indicator(
        self,
        team_id: str
    ) -> str:
        """
        Get textual momentum indicator.

        Args:
            team_id: Team identifier

        Returns:
            Momentum description (e.g., "Hot", "Cold", "Neutral")
        """
        form_index = self.calculate_form_index(team_id)

        if form_index >= 70:
            return "🔥 Hot"
        elif form_index >= 55:
            return "↗️ Rising"
        elif form_index >= 45:
            return "→ Neutral"
        elif form_index >= 30:
            return "↘️ Declining"
        else:
            return "❄️ Cold"

    def compare_form(
        self,
        team_a_id: str,
        team_b_id: str
    ) -> Dict:
        """
        Compare form between two teams.

        Args:
            team_a_id: Team A identifier
            team_b_id: Team B identifier

        Returns:
            Comparison dict with form indices and advantage
        """
        form_a = self.calculate_form_index(team_a_id)
        form_b = self.calculate_form_index(team_b_id)

        return {
            'team_a_form': form_a,
            'team_b_form': form_b,
            'form_advantage': form_a - form_b,
            'advantage_team': team_a_id if form_a > form_b else team_b_id
        }


class RegressionToMeanDetector:
    """
    Regression to mean detector with confidence weighting.

    Identifies teams/players likely experiencing unsustainable performance
    and estimates reversion to true talent level.
    """

    def __init__(
        self,
        min_sample_size: int = 10,
        confidence_threshold: float = 0.8
    ):
        """
        Initialize regression to mean detector.

        Args:
            min_sample_size: Minimum games needed for reliable detection
            confidence_threshold: Confidence level for significance
        """
        self.min_sample = min_sample_size
        self.confidence_threshold = confidence_threshold

    def detect_regression_candidate(
        self,
        observed_performance: List[float],
        expected_performance: float,
        variance: float
    ) -> Dict:
        """
        Detect if performance is likely to regress to mean.

        Args:
            observed_performance: Recent performance metrics
            expected_performance: Expected/baseline performance level
            variance: Expected variance in performance

        Returns:
            Detection result with regression prediction
        """
        if len(observed_performance) < self.min_sample:
            return {
                'sufficient_data': False,
                'regression_likely': False,
                'confidence': 0.0
            }

        observed_mean = np.mean(observed_performance)
        observed_std = np.std(observed_performance)

        # Calculate z-score (how many standard deviations from expected)
        if variance > 0:
            std_dev = np.sqrt(variance)
            z_score = (observed_mean - expected_performance) / std_dev
        else:
            z_score = 0.0

        # Calculate confidence that this is unsustainable
        # Higher absolute z-score = more likely to regress
        confidence = self._calculate_regression_confidence(
            z_score,
            len(observed_performance),
            observed_std
        )

        # Predict regressed performance (weighted average of observed and expected)
        # More games = more weight to observed performance
        sample_weight = min(len(observed_performance) / 30.0, 0.8)
        predicted_performance = (
            sample_weight * observed_mean +
            (1 - sample_weight) * expected_performance
        )

        return {
            'sufficient_data': True,
            'regression_likely': abs(z_score) > 1.5 and confidence > self.confidence_threshold,
            'z_score': z_score,
            'confidence': confidence,
            'observed_mean': observed_mean,
            'expected_performance': expected_performance,
            'predicted_performance': predicted_performance,
            'regression_amount': observed_mean - predicted_performance,
            'direction': 'downward' if observed_mean > expected_performance else 'upward'
        }

    def _calculate_regression_confidence(
        self,
        z_score: float,
        sample_size: int,
        observed_std: float
    ) -> float:
        """
        Calculate confidence that regression will occur.

        Args:
            z_score: Standard deviations from expected
            sample_size: Number of observations
            observed_std: Standard deviation of observations

        Returns:
            Confidence score (0 to 1)
        """
        # Larger absolute z-score = higher confidence
        z_component = min(abs(z_score) / 3.0, 1.0)

        # Smaller sample size = higher confidence in regression
        # (less evidence of true talent change)
        sample_component = max(0, 1.0 - (sample_size / 50.0))

        # Higher variance in observations = less confidence
        # (suggests inconsistent performance, not sustainable outlier)
        variance_component = max(0, 1.0 - (observed_std / 2.0))

        # Weighted combination
        confidence = (
            0.5 * z_component +
            0.3 * sample_component +
            0.2 * variance_component
        )

        return np.clip(confidence, 0, 1)

    def calculate_true_talent_estimate(
        self,
        observed_performance: List[float],
        league_average: float,
        league_std: float
    ) -> Tuple[float, float]:
        """
        Estimate true talent level accounting for sample size.

        Args:
            observed_performance: Observed performance data
            league_average: League average performance
            league_std: League standard deviation

        Returns:
            (true_talent_estimate, confidence_interval_width)
        """
        if len(observed_performance) < 3:
            return (league_average, league_std * 2)

        observed_mean = np.mean(observed_performance)
        n = len(observed_performance)

        # Bayesian estimate: weight observed mean with league average
        # More games = more weight to observed
        reliability = n / (n + 10)  # 10 is prior strength

        true_talent = (
            reliability * observed_mean +
            (1 - reliability) * league_average
        )

        # Confidence interval shrinks with more data
        ci_width = league_std / np.sqrt(n)

        return (true_talent, ci_width)
