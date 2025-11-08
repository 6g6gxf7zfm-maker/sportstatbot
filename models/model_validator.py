"""
Historical Model Validation Dashboard.

Backtests model performance and calculates accuracy metrics.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import statistics


@dataclass
class ValidationMetrics:
    """Validation metrics for model performance."""
    model_name: str
    total_predictions: int
    correct_predictions: int
    accuracy_percentage: float
    mean_absolute_error: float
    root_mean_squared_error: float
    brier_score: float  # For probabilistic predictions
    sharpe_ratio: Optional[float]  # For betting performance
    calibration_score: float


class ModelValidator:
    """Validates and backtests model predictions."""

    def __init__(self):
        """Initialize model validator."""
        pass

    def validate_predictions(
        self,
        predictions: List[Dict],
        actuals: List[Dict]
    ) -> ValidationMetrics:
        """
        Validate model predictions against actual results.

        Args:
            predictions: List of model predictions
            actuals: List of actual game results

        Returns:
            ValidationMetrics with accuracy stats
        """
        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have same length")

        correct = 0
        errors = []
        squared_errors = []
        brier_scores = []

        for pred, actual in zip(predictions, actuals):
            pred_winner = pred.get('predicted_winner')
            actual_winner = actual.get('winner')

            if pred_winner == actual_winner:
                correct += 1

            # Calculate errors for spread predictions
            pred_spread = pred.get('predicted_spread', 0)
            actual_spread = actual.get('actual_spread', 0)
            
            error = abs(pred_spread - actual_spread)
            errors.append(error)
            squared_errors.append(error ** 2)

            # Brier score for probability predictions
            pred_prob = pred.get('win_probability', 0.5)
            actual_outcome = 1 if pred_winner == actual_winner else 0
            brier_scores.append((pred_prob - actual_outcome) ** 2)

        accuracy = (correct / len(predictions)) * 100
        mae = statistics.mean(errors) if errors else 0
        rmse = (statistics.mean(squared_errors) ** 0.5) if squared_errors else 0
        brier = statistics.mean(brier_scores) if brier_scores else 0

        # Calibration score (how well probabilities match reality)
        calibration = 1 - brier  # Inverse of Brier score

        return ValidationMetrics(
            model_name="SportStatBot Model",
            total_predictions=len(predictions),
            correct_predictions=correct,
            accuracy_percentage=round(accuracy, 1),
            mean_absolute_error=round(mae, 2),
            root_mean_squared_error=round(rmse, 2),
            brier_score=round(brier, 4),
            sharpe_ratio=None,
            calibration_score=round(calibration, 4)
        )


