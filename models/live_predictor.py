"""
Live Game Predictor (In-game prediction engine).

Compares live lines vs model predictions in real-time.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LivePrediction:
    """Live in-game prediction."""
    game_id: str
    home_team: str
    away_team: str
    current_score_home: int
    current_score_away: int
    time_remaining: float  # Percentage
    model_win_prob_home: float
    model_win_prob_away: float
    live_line: Optional[float]
    model_line: float
    line_delta: float
    recommendation: str
    last_updated: str


class LiveGamePredictor:
    """Provides in-game predictions and line comparisons."""

    def __init__(self):
        """Initialize live predictor."""
        pass

    def predict_live(
        self,
        game_id: str,
        home_team: str,
        away_team: str,
        current_home_score: int,
        current_away_score: int,
        time_remaining_pct: float,
        pregame_ratings: Dict,
        live_line: Optional[float] = None
    ) -> LivePrediction:
        """
        Generate live in-game prediction.

        Args:
            game_id: Game identifier
            home_team: Home team name
            away_team: Away team name
            current_home_score: Current home score
            current_away_score: Current away score
            time_remaining_pct: Percentage of game remaining
            pregame_ratings: Pregame power ratings
            live_line: Current live betting line

        Returns:
            LivePrediction with current assessment
        """
        score_diff = current_home_score - current_away_score

        # Calculate current win probability
        # Heavily influenced by current score + time remaining
        base_prob = 0.50 + (score_diff / 30)

        # Adjust for time remaining
        certainty = 1 - time_remaining_pct
        home_prob = base_prob + (base_prob - 0.5) * certainty

        home_prob = max(0.01, min(0.99, home_prob))
        away_prob = 1 - home_prob

        # Model line (spread to cover from current score)
        model_line = score_diff + (time_remaining_pct * 3)

        # Line delta
        line_delta = (model_line - live_line) if live_line else 0

        # Recommendation
        if abs(line_delta) < 2:
            recommendation = "No strong edge"
        elif line_delta > 2:
            recommendation = f"Model favors HOME by {line_delta:.1f}"
        else:
            recommendation = f"Model favors AWAY by {abs(line_delta):.1f}"

        return LivePrediction(
            game_id=game_id,
            home_team=home_team,
            away_team=away_team,
            current_score_home=current_home_score,
            current_score_away=current_away_score,
            time_remaining=time_remaining_pct,
            model_win_prob_home=round(home_prob * 100, 1),
            model_win_prob_away=round(away_prob * 100, 1),
            live_line=live_line,
            model_line=round(model_line, 1),
            line_delta=round(line_delta, 1),
            recommendation=recommendation,
            last_updated=datetime.now().isoformat()
        )


