"""
Betting Edge Tracker.

Tracks historical accuracy of model predictions vs betting lines.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class BettingEdgeRecord:
    """Record of a betting prediction."""
    game_id: str
    date: str
    home_team: str
    away_team: str
    model_spread: float
    market_spread: float
    edge: float
    actual_result: Optional[float] = None
    profitable: Optional[bool] = None


@dataclass
class EdgeTrackingSummary:
    """Summary of betting edge tracking."""
    total_bets: int
    winning_bets: int
    losing_bets: int
    win_rate: float
    avg_edge: float
    roi: float
    best_edge_games: List[BettingEdgeRecord]
    worst_edge_games: List[BettingEdgeRecord]


class BettingEdgeTracker:
    """Tracks model performance vs betting markets."""

    def __init__(self, storage_path: str = './data/betting_edge.json'):
        """Initialize edge tracker."""
        self.storage_path = storage_path
        self.records: List[BettingEdgeRecord] = []
        self._load_records()

    def record_prediction(
        self,
        game_id: str,
        home_team: str,
        away_team: str,
        model_spread: float,
        market_spread: float,
        date: Optional[str] = None
    ):
        """Record a model prediction."""
        edge = model_spread - market_spread

        record = BettingEdgeRecord(
            game_id=game_id,
            date=date or datetime.now().isoformat(),
            home_team=home_team,
            away_team=away_team,
            model_spread=model_spread,
            market_spread=market_spread,
            edge=edge
        )

        self.records.append(record)
        self._save_records()

    def update_result(
        self,
        game_id: str,
        actual_result: float
    ):
        """Update with actual game result."""
        for record in self.records:
            if record.game_id == game_id:
                record.actual_result = actual_result
                
                # Determine if bet would have been profitable
                # If we bet on home team and they covered our spread
                record.profitable = (
                    (actual_result > record.model_spread and record.edge > 0) or
                    (actual_result < record.model_spread and record.edge < 0)
                )

        self._save_records()

    def get_summary(self, days: Optional[int] = None) -> EdgeTrackingSummary:
        """Get summary of tracking performance."""
        records = self.records

        if days:
            cutoff = datetime.now().timestamp() - (days * 86400)
            records = [
                r for r in records
                if datetime.fromisoformat(r.date).timestamp() > cutoff
            ]

        completed = [r for r in records if r.profitable is not None]

        if not completed:
            return EdgeTrackingSummary(
                total_bets=0,
                winning_bets=0,
                losing_bets=0,
                win_rate=0,
                avg_edge=0,
                roi=0,
                best_edge_games=[],
                worst_edge_games=[]
            )

        winning = sum(1 for r in completed if r.profitable)
        losing = len(completed) - winning
        win_rate = winning / len(completed) if completed else 0

        avg_edge = sum(abs(r.edge) for r in completed) / len(completed)

        # Simple ROI calculation (assuming -110 odds)
        roi = ((winning * 0.91) - losing) / len(completed) * 100

        # Best and worst
        sorted_by_edge = sorted(completed, key=lambda x: abs(x.edge), reverse=True)
        best = sorted_by_edge[:5]
        worst = sorted_by_edge[-5:]

        return EdgeTrackingSummary(
            total_bets=len(completed),
            winning_bets=winning,
            losing_bets=losing,
            win_rate=round(win_rate * 100, 1),
            avg_edge=round(avg_edge, 2),
            roi=round(roi, 1),
            best_edge_games=best,
            worst_edge_games=worst
        )

    def _save_records(self):
        """Save records to disk."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = [
                {
                    'game_id': r.game_id,
                    'date': r.date,
                    'home_team': r.home_team,
                    'away_team': r.away_team,
                    'model_spread': r.model_spread,
                    'market_spread': r.market_spread,
                    'edge': r.edge,
                    'actual_result': r.actual_result,
                    'profitable': r.profitable
                }
                for r in self.records
            ]

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving betting edge records: {e}")

    def _load_records(self):
        """Load records from disk."""
        try:
            if not os.path.exists(self.storage_path):
                return

            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            self.records = [BettingEdgeRecord(**r) for r in data]

        except Exception as e:
            print(f"Error loading betting edge records: {e}")


