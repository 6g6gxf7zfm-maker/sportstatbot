"""Model accuracy tracker for real-time performance monitoring."""
from typing import Dict, List
from datetime import datetime, timedelta
import json
import os


class ModelAccuracyTracker:
    """
    Tracks model accuracy in real-time.

    Maintains rolling windows of performance metrics.
    """

    def __init__(self, storage_path: str = './data/accuracy'):
        """
        Initialize accuracy tracker.

        Args:
            storage_path: Path to store accuracy data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.predictions = []
        self.results = []

    def track_prediction(
        self,
        prediction_id: str,
        model_type: str,
        predicted_value: float,
        confidence: float,
        metadata: Dict
    ):
        """
        Track a new prediction.

        Args:
            prediction_id: Unique prediction identifier
            model_type: Type of model making prediction
            predicted_value: Predicted value
            confidence: Model confidence
            metadata: Additional metadata
        """
        self.predictions.append({
            'id': prediction_id,
            'model_type': model_type,
            'predicted_value': predicted_value,
            'confidence': confidence,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })

    def record_result(
        self,
        prediction_id: str,
        actual_value: float
    ):
        """
        Record actual result for a prediction.

        Args:
            prediction_id: Prediction identifier
            actual_value: Actual outcome value
        """
        prediction = next(
            (p for p in self.predictions if p['id'] == prediction_id),
            None
        )

        if not prediction:
            return

        error = abs(predicted_value - actual_value)

        self.results.append({
            'prediction_id': prediction_id,
            'model_type': prediction['model_type'],
            'predicted_value': prediction['predicted_value'],
            'actual_value': actual_value,
            'error': error,
            'confidence': prediction['confidence'],
            'timestamp': datetime.now().isoformat()
        })

    def get_recent_accuracy(
        self,
        model_type: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Get accuracy metrics for recent period.

        Args:
            model_type: Filter by model type
            days: Number of days to look back

        Returns:
            Accuracy metrics
        """
        cutoff = datetime.now() - timedelta(days=days)

        filtered = [
            r for r in self.results
            if datetime.fromisoformat(r['timestamp']) >= cutoff
            and (not model_type or r['model_type'] == model_type)
        ]

        if not filtered:
            return {'error': 'No results in period'}

        errors = [r['error'] for r in filtered]
        mean_error = sum(errors) / len(errors)

        return {
            'period_days': days,
            'total_predictions': len(filtered),
            'mean_absolute_error': round(mean_error, 2),
            'accuracy_rate': self._calculate_accuracy_rate(filtered),
            'model_type': model_type or 'ALL'
        }

    def _calculate_accuracy_rate(self, results: List[Dict]) -> float:
        """Calculate percentage of accurate predictions."""
        accurate = sum(1 for r in results if r['error'] <= 3)
        return round(accurate / len(results), 3) if results else 0
