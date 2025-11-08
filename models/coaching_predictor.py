"""
Coaching Change Predictor.

Predicts likelihood of coaching changes based on performance delta.
"""

from typing import Dict, Optional
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CoachingChangePrediction:
    """Prediction for coaching change."""
    team: str
    coach: str
    change_probability: float  # 0-100
    key_factors: List[str]
    risk_level: str  # 'safe', 'warm_seat', 'hot_seat', 'imminent'
    record_delta: float  # Difference from expectations


class CoachingChangePredictor:
    """Predicts coaching change likelihood."""

    def __init__(self):
        """Initialize coaching change predictor."""
        pass

    def predict_change(
        self,
        team: str,
        coach: str,
        current_record: tuple,  # (wins, losses)
        expected_record: tuple,
        years_with_team: int,
        recent_playoff_appearances: int,
        owner_patience_rating: float = 50
    ) -> CoachingChangePrediction:
        """
        Predict likelihood of coaching change.

        Args:
            team: Team name
            coach: Coach name
            current_record: Current win-loss record
            expected_record: Expected record
            years_with_team: Years as head coach
            recent_playoff_appearances: Playoff trips last 3 years
            owner_patience_rating: Owner patience (0-100)

        Returns:
            CoachingChangePrediction
        """
        current_wins, current_losses = current_record
        expected_wins, expected_losses = expected_record

        # Record delta
        win_delta = current_wins - expected_wins
        total_games = current_wins + current_losses
        win_pct = current_wins / total_games if total_games > 0 else 0

        # Base probability from record
        if win_pct < 0.30:
            base_prob = 70
        elif win_pct < 0.40:
            base_prob = 45
        elif win_pct < 0.45:
            base_prob = 25
        else:
            base_prob = 10

        # Adjust for expectations
        if win_delta < -5:
            base_prob += 25
        elif win_delta < -3:
            base_prob += 15

        # Tenure adjustment
        if years_with_team < 2:
            base_prob -= 15  # New coaches get more time
        elif years_with_team > 5:
            base_prob += 10  # Long tenure increases risk

        # Recent success
        base_prob -= (recent_playoff_appearances * 10)

        # Owner patience
        patience_adj = (50 - owner_patience_rating) / 5
        base_prob += patience_adj

        final_prob = max(0, min(100, base_prob))

        # Risk level
        if final_prob >= 70:
            risk_level = 'imminent'
        elif final_prob >= 50:
            risk_level = 'hot_seat'
        elif final_prob >= 25:
            risk_level = 'warm_seat'
        else:
            risk_level = 'safe'

        # Key factors
        factors = []
        if win_delta < -3:
            factors.append(f"Underperforming expectations by {abs(win_delta)} wins")
        if win_pct < 0.35:
            factors.append(f"Poor record ({win_pct:.1%})")
        if recent_playoff_appearances == 0:
            factors.append("No recent playoff success")

        return CoachingChangePrediction(
            team=team,
            coach=coach,
            change_probability=round(final_prob, 1),
            key_factors=factors,
            risk_level=risk_level,
            record_delta=win_delta
        )


