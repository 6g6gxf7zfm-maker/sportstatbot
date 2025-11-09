"""
Calibration Models

25. Adaptive win-prob calibration using recent data drift
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque


class AdaptiveWinProbCalibration:
    """
    Adaptive win-probability calibration using recent data drift.

    Continuously calibrates win probability models by detecting
    and adjusting for data drift in recent games.
    """

    def __init__(
        self,
        calibration_window: int = 100,
        drift_sensitivity: float = 0.05
    ):
        """
        Initialize adaptive calibration model.

        Args:
            calibration_window: Number of recent games for calibration
            drift_sensitivity: Threshold for detecting drift (0-1)
        """
        self.calibration_window = calibration_window
        self.drift_sensitivity = drift_sensitivity

        # Store recent predictions and outcomes
        self.prediction_history = deque(maxlen=calibration_window)
        self.calibration_curve = None

    def add_game_result(
        self,
        predicted_win_prob: float,
        actual_outcome: bool
    ):
        """
        Add a game result for calibration.

        Args:
            predicted_win_prob: Predicted win probability (0-1)
            actual_outcome: Actual result (True = win, False = loss)
        """
        self.prediction_history.append({
            'predicted': predicted_win_prob,
            'actual': 1.0 if actual_outcome else 0.0
        })

    def calibrate_probabilities(self) -> Dict:
        """
        Calibrate win probabilities using recent results.

        Returns:
            Calibration analysis
        """
        if len(self.prediction_history) < 20:
            return {
                'calibrated': False,
                'reason': 'Insufficient data',
                'sample_size': len(self.prediction_history)
            }

        # Group predictions into bins
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        bin_predictions = {i: [] for i in range(len(bins) - 1)}
        bin_outcomes = {i: [] for i in range(len(bins) - 1)}

        for record in self.prediction_history:
            pred = record['predicted']
            outcome = record['actual']

            # Find bin
            for i in range(len(bins) - 1):
                if bins[i] <= pred < bins[i + 1]:
                    bin_predictions[i].append(pred)
                    bin_outcomes[i].append(outcome)
                    break

        # Calculate calibration for each bin
        calibration_points = []

        for i in range(len(bins) - 1):
            if bin_predictions[i]:
                avg_predicted = np.mean(bin_predictions[i])
                avg_actual = np.mean(bin_outcomes[i])

                calibration_points.append({
                    'bin': f"{bins[i]:.1f}-{bins[i+1]:.1f}",
                    'avg_predicted': avg_predicted,
                    'avg_actual': avg_actual,
                    'calibration_error': avg_actual - avg_predicted,
                    'sample_size': len(bin_predictions[i])
                })

        # Overall calibration metrics
        all_predicted = [r['predicted'] for r in self.prediction_history]
        all_actual = [r['actual'] for r in self.prediction_history]

        brier_score = self._calculate_brier_score(all_predicted, all_actual)
        log_loss = self._calculate_log_loss(all_predicted, all_actual)

        # Detect drift
        drift_detected, drift_magnitude = self._detect_drift()

        self.calibration_curve = calibration_points

        return {
            'calibrated': True,
            'calibration_points': calibration_points,
            'brier_score': brier_score,
            'log_loss': log_loss,
            'drift_detected': drift_detected,
            'drift_magnitude': drift_magnitude,
            'calibration_quality': self._score_to_quality(brier_score)
        }

    def _calculate_brier_score(
        self,
        predictions: List[float],
        outcomes: List[float]
    ) -> float:
        """Calculate Brier score (lower is better)."""
        if not predictions:
            return 0.25

        squared_errors = [(p - o) ** 2 for p, o in zip(predictions, outcomes)]
        return np.mean(squared_errors)

    def _calculate_log_loss(
        self,
        predictions: List[float],
        outcomes: List[float]
    ) -> float:
        """Calculate log loss (lower is better)."""
        if not predictions:
            return 0.693  # log(2)

        epsilon = 1e-15  # Avoid log(0)
        log_losses = []

        for p, o in zip(predictions, outcomes):
            # Clip probabilities
            p = np.clip(p, epsilon, 1 - epsilon)

            if o == 1:
                log_losses.append(-np.log(p))
            else:
                log_losses.append(-np.log(1 - p))

        return np.mean(log_losses)

    def _detect_drift(self) -> Tuple[bool, float]:
        """
        Detect if recent data shows drift from calibration.

        Returns:
            (drift_detected, drift_magnitude)
        """
        if len(self.prediction_history) < 50:
            return (False, 0.0)

        # Split into recent and older data
        split_point = len(self.prediction_history) // 2
        recent = list(self.prediction_history)[split_point:]
        older = list(self.prediction_history)[:split_point]

        # Calculate Brier score for each
        recent_pred = [r['predicted'] for r in recent]
        recent_outcome = [r['actual'] for r in recent]
        recent_brier = self._calculate_brier_score(recent_pred, recent_outcome)

        older_pred = [r['predicted'] for r in older]
        older_outcome = [r['actual'] for r in older]
        older_brier = self._calculate_brier_score(older_pred, older_outcome)

        # Drift is significant change in Brier score
        drift_magnitude = abs(recent_brier - older_brier)
        drift_detected = drift_magnitude > self.drift_sensitivity

        return (drift_detected, drift_magnitude)

    def _score_to_quality(self, brier_score: float) -> str:
        """Convert Brier score to quality rating."""
        if brier_score < 0.10:
            return "Excellent"
        elif brier_score < 0.15:
            return "Good"
        elif brier_score < 0.20:
            return "Fair"
        else:
            return "Poor"

    def adjust_prediction(
        self,
        raw_win_prob: float
    ) -> float:
        """
        Adjust a raw win probability using calibration.

        Args:
            raw_win_prob: Raw predicted win probability

        Returns:
            Calibrated win probability
        """
        if self.calibration_curve is None:
            return raw_win_prob  # No calibration yet

        # Find appropriate calibration adjustment
        for point in self.calibration_curve:
            bin_range = point['bin'].split('-')
            bin_low = float(bin_range[0])
            bin_high = float(bin_range[1])

            if bin_low <= raw_win_prob < bin_high:
                # Apply calibration adjustment
                adjustment = point['calibration_error']
                calibrated = raw_win_prob + adjustment

                # Clip to valid probability range
                return np.clip(calibrated, 0.01, 0.99)

        # If outside all bins, return raw
        return raw_win_prob

    def evaluate_calibration_quality(self) -> Dict:
        """
        Evaluate overall quality of calibration.

        Returns:
            Quality metrics
        """
        if len(self.prediction_history) < 20:
            return {'quality': 'Insufficient data'}

        predictions = [r['predicted'] for r in self.prediction_history]
        outcomes = [r['actual'] for r in self.prediction_history]

        # Calculate metrics
        brier = self._calculate_brier_score(predictions, outcomes)
        log_loss = self._calculate_log_loss(predictions, outcomes)

        # Calibration slope (should be close to 1.0)
        # Simplified: correlation between predicted and actual
        if len(predictions) > 1:
            correlation = np.corrcoef(predictions, outcomes)[0, 1]
        else:
            correlation = 0.0

        # Resolution (ability to discriminate)
        # Higher variance in predictions = better resolution
        prediction_variance = np.var(predictions)

        return {
            'brier_score': brier,
            'log_loss': log_loss,
            'calibration_slope': correlation,
            'resolution': prediction_variance,
            'overall_quality': self._overall_quality(brier, correlation),
            'sample_size': len(self.prediction_history)
        }

    def _overall_quality(self, brier: float, correlation: float) -> str:
        """Determine overall calibration quality."""
        if brier < 0.15 and correlation > 0.3:
            return "Excellent"
        elif brier < 0.20 and correlation > 0.2:
            return "Good"
        elif brier < 0.25:
            return "Fair"
        else:
            return "Poor"

    def recommend_recalibration(self) -> Dict:
        """
        Recommend whether recalibration is needed.

        Returns:
            Recalibration recommendation
        """
        drift_detected, drift_magnitude = self._detect_drift()

        quality = self.evaluate_calibration_quality()
        brier_score = quality.get('brier_score', 0.25)

        # Recalibration needed if:
        # 1. Drift detected, or
        # 2. Poor calibration quality
        needs_recalibration = drift_detected or brier_score > 0.22

        reasons = []
        if drift_detected:
            reasons.append(f"Data drift detected (magnitude: {drift_magnitude:.3f})")
        if brier_score > 0.22:
            reasons.append(f"Poor calibration quality (Brier: {brier_score:.3f})")

        return {
            'needs_recalibration': needs_recalibration,
            'urgency': 'High' if drift_detected and brier_score > 0.25 else 'Moderate' if needs_recalibration else 'Low',
            'reasons': reasons if reasons else ['Calibration is adequate'],
            'current_brier_score': brier_score,
            'drift_magnitude': drift_magnitude
        }

    def confidence_interval(
        self,
        win_prob: float,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for win probability.

        Args:
            win_prob: Predicted win probability
            confidence_level: Confidence level (default 95%)

        Returns:
            (lower_bound, upper_bound)
        """
        # Use calibration quality to determine interval width
        quality = self.evaluate_calibration_quality()
        brier_score = quality.get('brier_score', 0.20)

        # Wider intervals for worse calibration
        base_width = brier_score * 2

        # Z-score for confidence level
        z_score = 1.96 if confidence_level == 0.95 else 2.58

        # Calculate bounds
        margin = z_score * base_width
        lower = max(0.01, win_prob - margin)
        upper = min(0.99, win_prob + margin)

        return (lower, upper)
