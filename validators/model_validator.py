"""Historical model validation dashboard with backtests."""
from typing import Dict, List, Optional
from datetime import datetime
import statistics


class HistoricalModelValidator:
    """
    Validates model performance through historical backtesting.

    Compares model predictions to actual results to measure accuracy.
    """

    def __init__(self):
        """Initialize model validator."""
        self.validation_results = []

    def backtest_predictions(
        self,
        predictions: List[Dict],
        actual_results: List[Dict],
        prediction_type: str = 'spread'
    ) -> Dict:
        """
        Backtest model predictions against actual results.

        Args:
            predictions: List of model predictions
            actual_results: List of actual game results
            prediction_type: Type of prediction to validate

        Returns:
            Dictionary with validation metrics
        """
        matched_predictions = []

        for pred in predictions:
            # Find matching result
            result = next(
                (r for r in actual_results if r['game_id'] == pred['game_id']),
                None
            )

            if not result:
                continue

            error = self._calculate_prediction_error(pred, result, prediction_type)

            matched_predictions.append({
                'game_id': pred['game_id'],
                'predicted': pred.get('predicted_value'),
                'actual': result.get('actual_value'),
                'error': error,
                'absolute_error': abs(error),
                'squared_error': error ** 2
            })

        if not matched_predictions:
            return {'error': 'No matching predictions found'}

        # Calculate metrics
        errors = [m['error'] for m in matched_predictions]
        abs_errors = [m['absolute_error'] for m in matched_predictions]
        squared_errors = [m['squared_error'] for m in matched_predictions]

        mae = statistics.mean(abs_errors)  # Mean Absolute Error
        rmse = statistics.mean(squared_errors) ** 0.5  # Root Mean Squared Error
        bias = statistics.mean(errors)  # Model bias
        std_error = statistics.stdev(errors) if len(errors) > 1 else 0

        # Calculate accuracy within thresholds
        within_3 = sum(1 for e in abs_errors if e <= 3) / len(abs_errors)
        within_7 = sum(1 for e in abs_errors if e <= 7) / len(abs_errors)
        within_10 = sum(1 for e in abs_errors if e <= 10) / len(abs_errors)

        return {
            'prediction_type': prediction_type,
            'total_predictions': len(matched_predictions),
            'mean_absolute_error': round(mae, 2),
            'root_mean_squared_error': round(rmse, 2),
            'bias': round(bias, 2),
            'std_error': round(std_error, 2),
            'accuracy_within_3': round(within_3, 3),
            'accuracy_within_7': round(within_7, 3),
            'accuracy_within_10': round(within_10, 3),
            'validation_date': datetime.now().isoformat()
        }

    def validate_win_probability(
        self,
        probability_predictions: List[Dict],
        actual_outcomes: List[Dict]
    ) -> Dict:
        """
        Validate win probability predictions.

        Uses Brier Score and calibration analysis.

        Args:
            probability_predictions: List of win probability predictions
            actual_outcomes: List of actual game outcomes

        Returns:
            Dictionary with probability validation metrics
        """
        matched = []

        for pred in probability_predictions:
            result = next(
                (r for r in actual_outcomes if r['game_id'] == pred['game_id']),
                None
            )

            if not result:
                continue

            predicted_prob = pred['home_win_probability']
            actual_outcome = 1 if result['home_team_won'] else 0

            brier_score = (predicted_prob - actual_outcome) ** 2

            matched.append({
                'predicted_prob': predicted_prob,
                'actual_outcome': actual_outcome,
                'brier_score': brier_score
            })

        if not matched:
            return {'error': 'No matching predictions'}

        # Calculate overall Brier Score
        avg_brier = statistics.mean([m['brier_score'] for m in matched])

        # Calculate calibration
        calibration = self._calculate_calibration(matched)

        # Calculate discrimination (how well model separates wins from losses)
        discrimination = self._calculate_discrimination(matched)

        return {
            'total_predictions': len(matched),
            'brier_score': round(avg_brier, 4),
            'brier_skill_score': round(1 - (avg_brier / 0.25), 3),  # 0.25 = baseline
            'calibration_error': round(calibration, 4),
            'discrimination_score': round(discrimination, 3),
            'rating': self._rate_probability_model(avg_brier, calibration),
            'validation_date': datetime.now().isoformat()
        }

    def _calculate_prediction_error(
        self,
        prediction: Dict,
        actual: Dict,
        pred_type: str
    ) -> float:
        """Calculate prediction error."""
        if pred_type == 'spread':
            predicted_margin = prediction.get('predicted_margin', 0)
            actual_margin = actual.get('actual_margin', 0)
            return predicted_margin - actual_margin

        elif pred_type == 'total':
            predicted_total = prediction.get('predicted_total', 0)
            actual_total = actual.get('actual_total', 0)
            return predicted_total - actual_total

        elif pred_type == 'player_points':
            predicted_points = prediction.get('predicted_points', 0)
            actual_points = actual.get('actual_points', 0)
            return predicted_points - actual_points

        return 0

    def _calculate_calibration(self, matched: List[Dict]) -> float:
        """
        Calculate calibration error.

        Measures how well predicted probabilities match actual frequencies.
        """
        # Group predictions into bins
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        calibration_error = 0

        for i in range(len(bins) - 1):
            bin_low, bin_high = bins[i], bins[i + 1]

            # Find predictions in this bin
            in_bin = [
                m for m in matched
                if bin_low <= m['predicted_prob'] < bin_high
            ]

            if not in_bin:
                continue

            # Average predicted probability in bin
            avg_predicted = statistics.mean([m['predicted_prob'] for m in in_bin])

            # Actual win rate in bin
            actual_rate = statistics.mean([m['actual_outcome'] for m in in_bin])

            # Add to calibration error
            calibration_error += abs(avg_predicted - actual_rate) * len(in_bin)

        return calibration_error / len(matched) if matched else 0

    def _calculate_discrimination(self, matched: List[Dict]) -> float:
        """
        Calculate discrimination score.

        Measures separation between wins and losses.
        """
        wins = [m['predicted_prob'] for m in matched if m['actual_outcome'] == 1]
        losses = [m['predicted_prob'] for m in matched if m['actual_outcome'] == 0]

        if not wins or not losses:
            return 0

        avg_win_prob = statistics.mean(wins)
        avg_loss_prob = statistics.mean(losses)

        return avg_win_prob - avg_loss_prob

    def _rate_probability_model(self, brier_score: float, calibration: float) -> str:
        """Rate overall model quality."""
        if brier_score < 0.15 and calibration < 0.05:
            return "EXCELLENT"
        elif brier_score < 0.20 and calibration < 0.08:
            return "GOOD"
        elif brier_score < 0.23:
            return "AVERAGE"
        else:
            return "POOR"
