"""Betting edge tracker with historical accuracy metrics."""
from typing import Dict, List
from datetime import datetime
import json
import os


class BettingEdgeTracker:
    """
    Tracks betting edges and historical accuracy of model predictions.

    Maintains record of all betting recommendations and their outcomes
    to measure model performance.
    """

    def __init__(self, storage_path: str = './data/betting_edges'):
        """
        Initialize betting edge tracker.

        Args:
            storage_path: Path to store edge tracking data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.edges = []

    def log_betting_edge(
        self,
        game_id: str,
        edge_type: str,
        recommendation: str,
        model_line: float,
        market_line: float,
        edge_value: float,
        confidence: float,
        sport: str
    ) -> Dict:
        """
        Log a betting edge recommendation.

        Args:
            game_id: Unique game identifier
            edge_type: Type of bet ('spread', 'total', 'moneyline', 'prop')
            recommendation: Betting recommendation
            model_line: Model's fair line
            market_line: Market's current line
            edge_value: Size of edge
            confidence: Model confidence (0-1)
            sport: Sport type

        Returns:
            Dictionary with logged edge
        """
        edge_record = {
            'game_id': game_id,
            'edge_type': edge_type,
            'recommendation': recommendation,
            'model_line': model_line,
            'market_line': market_line,
            'edge_value': edge_value,
            'confidence': confidence,
            'sport': sport,
            'timestamp': datetime.now().isoformat(),
            'result': None,  # To be filled in after game
            'won': None,
            'roi': None
        }

        self.edges.append(edge_record)
        self._save_edge(edge_record)

        return edge_record

    def update_edge_result(
        self,
        game_id: str,
        actual_result: Dict
    ) -> Dict:
        """
        Update edge with actual game result.

        Args:
            game_id: Game identifier
            actual_result: Actual game outcome

        Returns:
            Updated edge record with result
        """
        edge = next((e for e in self.edges if e['game_id'] == game_id), None)

        if not edge:
            return {'error': 'Edge not found'}

        # Determine if bet won
        won = self._determine_bet_result(edge, actual_result)

        # Calculate ROI (assuming -110 odds)
        if won:
            roi = 0.91  # Win $100 on $110 bet
        else:
            roi = -1.0  # Lose $110

        edge['result'] = actual_result
        edge['won'] = won
        edge['roi'] = roi

        self._save_edge(edge)

        return edge

    def get_edge_performance(
        self,
        edge_type: Optional[str] = None,
        sport: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> Dict:
        """
        Get performance metrics for betting edges.

        Args:
            edge_type: Filter by edge type (optional)
            sport: Filter by sport (optional)
            min_confidence: Minimum confidence threshold

        Returns:
            Dictionary with performance metrics
        """
        # Filter edges
        filtered_edges = [
            e for e in self.edges
            if e.get('won') is not None  # Only completed bets
            and (not edge_type or e.get('edge_type') == edge_type)
            and (not sport or e.get('sport') == sport)
            and e.get('confidence', 0) >= min_confidence
        ]

        if not filtered_edges:
            return {'error': 'No qualifying edges found'}

        # Calculate metrics
        total_bets = len(filtered_edges)
        wins = sum(1 for e in filtered_edges if e['won'])
        losses = total_bets - wins

        win_rate = wins / total_bets
        total_roi = sum(e['roi'] for e in filtered_edges)
        avg_roi = total_roi / total_bets

        # Breakdown by confidence tier
        high_conf_edges = [e for e in filtered_edges if e['confidence'] >= 0.7]
        med_conf_edges = [e for e in filtered_edges if 0.5 <= e['confidence'] < 0.7]
        low_conf_edges = [e for e in filtered_edges if e['confidence'] < 0.5]

        return {
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 3),
            'total_roi': round(total_roi, 2),
            'avg_roi_per_bet': round(avg_roi, 3),
            'roi_percentage': round(avg_roi * 100, 1),
            'high_confidence_record': f"{sum(1 for e in high_conf_edges if e['won'])}-{len(high_conf_edges) - sum(1 for e in high_conf_edges if e['won'])}",
            'medium_confidence_record': f"{sum(1 for e in med_conf_edges if e['won'])}-{len(med_conf_edges) - sum(1 for e in med_conf_edges if e['won'])}",
            'low_confidence_record': f"{sum(1 for e in low_conf_edges if e['won'])}-{len(low_conf_edges) - sum(1 for e in low_conf_edges if e['won'])}",
            'filters': {
                'edge_type': edge_type,
                'sport': sport,
                'min_confidence': min_confidence
            }
        }

    def get_best_edge_types(self) -> List[Dict]:
        """Get performance breakdown by edge type."""
        edge_types = set(e['edge_type'] for e in self.edges if e.get('won') is not None)

        performance_by_type = []

        for edge_type in edge_types:
            perf = self.get_edge_performance(edge_type=edge_type)
            if 'error' not in perf:
                perf['edge_type'] = edge_type
                performance_by_type.append(perf)

        # Sort by ROI
        performance_by_type.sort(key=lambda x: x['avg_roi_per_bet'], reverse=True)

        return performance_by_type

    def get_profit_loss_timeline(self) -> List[Dict]:
        """Get cumulative profit/loss over time."""
        sorted_edges = sorted(
            [e for e in self.edges if e.get('won') is not None],
            key=lambda x: x['timestamp']
        )

        cumulative_roi = 0
        timeline = []

        for edge in sorted_edges:
            cumulative_roi += edge['roi']
            timeline.append({
                'date': edge['timestamp'][:10],  # Just date
                'game_id': edge['game_id'],
                'bet': edge['recommendation'],
                'won': edge['won'],
                'roi': edge['roi'],
                'cumulative_roi': round(cumulative_roi, 2)
            })

        return timeline

    def _determine_bet_result(self, edge: Dict, actual_result: Dict) -> bool:
        """Determine if bet won based on actual result."""
        edge_type = edge['edge_type']
        recommendation = edge['recommendation']

        if edge_type == 'spread':
            # Parse recommendation (e.g., "Team +7")
            if 'OVER' in recommendation.upper():
                return False  # Simplified
            # Would need actual spread calculation
            return True  # Placeholder

        elif edge_type == 'total':
            actual_total = actual_result.get('total_score', 0)
            market_line = edge['market_line']

            if 'OVER' in recommendation.upper():
                return actual_total > market_line
            else:  # UNDER
                return actual_total < market_line

        elif edge_type == 'moneyline':
            recommended_team = recommendation
            winner = actual_result.get('winner')
            return recommended_team == winner

        return False  # Default

    def _save_edge(self, edge: Dict):
        """Save edge to disk."""
        filepath = os.path.join(
            self.storage_path,
            f"{edge['game_id']}_edge.json"
        )
        try:
            with open(filepath, 'w') as f:
                json.dump(edge, f, indent=2)
        except Exception as e:
            print(f"Error saving edge: {e}")
