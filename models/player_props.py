"""
Player Prop Line Model.

Predicts individual player performance for props betting.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class PlayerPropPrediction:
    """Prediction for a player prop."""
    player_name: str
    team: str
    opponent: str
    stat_type: str  # 'points', 'rebounds', 'assists', 'yards', 'goals', etc.
    predicted_value: float
    confidence_interval: Tuple[float, float]
    over_probability: float
    under_probability: float
    market_line: Optional[float] = None
    value_rating: Optional[str] = None  # 'strong_over', 'lean_over', 'no_value', etc.
    adjustment_factors: Optional[List[str]] = None


class PlayerPropModel:
    """
    Predicts player prop lines for betting.

    Features:
    - Statistical projections for individual players
    - Matchup-based adjustments
    - Injury/rest considerations
    - Usage rate and opportunity modeling
    - Historical vs opponent performance
    """

    def __init__(self):
        """Initialize player prop model."""
        # Sport-specific configurations
        self.sport_stat_configs = {
            'nfl': {
                'passing_yards': {'avg': 250, 'std': 50, 'key_factors': ['defense_rank', 'weather']},
                'rushing_yards': {'avg': 80, 'std': 30, 'key_factors': ['defense_rank', 'game_script']},
                'receiving_yards': {'avg': 60, 'std': 25, 'key_factors': ['target_share', 'matchup']},
                'touchdowns': {'avg': 1.5, 'std': 1.0, 'key_factors': ['red_zone_usage']},
            },
            'nba': {
                'points': {'avg': 20, 'std': 8, 'key_factors': ['usage_rate', 'pace']},
                'rebounds': {'avg': 8, 'std': 3, 'key_factors': ['position', 'opponent_size']},
                'assists': {'avg': 5, 'std': 2.5, 'key_factors': ['pace', 'ball_handler']},
                'threes': {'avg': 2.5, 'std': 1.5, 'key_factors': ['volume', 'defense']},
            },
            'mlb': {
                'strikeouts': {'avg': 6, 'std': 2, 'key_factors': ['opponent_k_rate']},
                'hits': {'avg': 1.2, 'std': 0.8, 'key_factors': ['batting_avg', 'pitcher']},
                'rbis': {'avg': 0.8, 'std': 0.9, 'key_factors': ['lineup_spot', 'obp']},
            },
            'nhl': {
                'goals': {'avg': 0.5, 'std': 0.7, 'key_factors': ['shot_rate', 'shooting_pct']},
                'assists': {'avg': 0.6, 'std': 0.8, 'key_factors': ['ice_time', 'linemates']},
                'shots': {'avg': 3.0, 'std': 1.5, 'key_factors': ['ice_time', 'opponent']},
            },
            'soccer': {
                'goals': {'avg': 0.4, 'std': 0.6, 'key_factors': ['xG', 'opponent_defense']},
                'assists': {'avg': 0.3, 'std': 0.5, 'key_factors': ['position', 'team_style']},
                'shots': {'avg': 2.5, 'std': 1.2, 'key_factors': ['position', 'opponent']},
            }
        }

    def predict_prop(
        self,
        player_name: str,
        team: str,
        opponent: str,
        stat_type: str,
        sport: str,
        recent_performance: List[float],
        season_average: float,
        matchup_data: Optional[Dict] = None,
        market_line: Optional[float] = None,
        adjustments: Optional[Dict] = None
    ) -> PlayerPropPrediction:
        """
        Predict a player prop line.

        Args:
            player_name: Player name
            team: Player's team
            opponent: Opponent team
            stat_type: Type of stat (points, yards, goals, etc.)
            sport: Sport type
            recent_performance: List of recent game performances
            season_average: Season average for this stat
            matchup_data: Historical performance vs this opponent
            market_line: Current market prop line
            adjustments: Additional adjustments (injury, rest, etc.)

        Returns:
            PlayerPropPrediction with prediction details
        """
        # Get baseline prediction
        baseline = self._calculate_baseline_prediction(
            recent_performance, season_average, stat_type, sport
        )

        # Apply matchup adjustments
        matchup_adj = self._apply_matchup_adjustments(
            baseline, opponent, stat_type, matchup_data
        )

        # Apply situational adjustments
        situation_adj = self._apply_situational_adjustments(
            matchup_adj, adjustments or {}
        )

        final_prediction = situation_adj
        adjustment_factors = []

        # Track adjustment factors
        if adjustments:
            if adjustments.get('injury_concern'):
                adjustment_factors.append("Dealing with minor injury")
            if adjustments.get('rest_advantage'):
                adjustment_factors.append("Well-rested")
            if adjustments.get('favorable_matchup'):
                adjustment_factors.append("Favorable matchup")
            if adjustments.get('high_pace'):
                adjustment_factors.append("High-pace game expected")

        # Calculate confidence interval
        stat_config = self._get_stat_config(stat_type, sport)
        std_dev = stat_config['std']

        # Adjust std based on consistency
        if recent_performance and len(recent_performance) >= 5:
            actual_std = statistics.stdev(recent_performance)
            std_dev = (std_dev + actual_std) / 2  # Blend model and actual

        confidence_interval = (
            max(0, final_prediction - 1.5 * std_dev),
            final_prediction + 1.5 * std_dev
        )

        # Calculate over/under probabilities
        if market_line:
            over_prob, under_prob = self._calculate_over_under_probabilities(
                final_prediction, market_line, std_dev
            )
            value_rating = self._assess_value(
                final_prediction, market_line, over_prob
            )
        else:
            over_prob = 0.5
            under_prob = 0.5
            value_rating = None

        return PlayerPropPrediction(
            player_name=player_name,
            team=team,
            opponent=opponent,
            stat_type=stat_type,
            predicted_value=round(final_prediction, 1),
            confidence_interval=(
                round(confidence_interval[0], 1),
                round(confidence_interval[1], 1)
            ),
            over_probability=round(over_prob * 100, 1),
            under_probability=round(under_prob * 100, 1),
            market_line=market_line,
            value_rating=value_rating,
            adjustment_factors=adjustment_factors if adjustment_factors else None
        )

    def predict_multiple_props(
        self,
        props: List[Dict],
        market_lines: Optional[Dict[str, float]] = None
    ) -> List[PlayerPropPrediction]:
        """
        Predict multiple player props.

        Args:
            props: List of prop dictionaries with player/stat info
            market_lines: Dictionary of prop_id -> market line

        Returns:
            List of PlayerPropPrediction objects
        """
        predictions = []

        for prop in props:
            prop_id = f"{prop['player']}_{prop['stat_type']}"
            market_line = market_lines.get(prop_id) if market_lines else None

            prediction = self.predict_prop(
                player_name=prop['player'],
                team=prop['team'],
                opponent=prop['opponent'],
                stat_type=prop['stat_type'],
                sport=prop['sport'],
                recent_performance=prop.get('recent', []),
                season_average=prop.get('season_avg', 0),
                matchup_data=prop.get('matchup_data'),
                market_line=market_line,
                adjustments=prop.get('adjustments')
            )

            predictions.append(prediction)

        return predictions

    def find_value_props(
        self,
        predictions: List[PlayerPropPrediction],
        min_edge: float = 5.0
    ) -> List[PlayerPropPrediction]:
        """
        Find props with betting value.

        Args:
            predictions: List of prop predictions
            min_edge: Minimum edge percentage to flag

        Returns:
            List of value props sorted by edge
        """
        value_props = []

        for pred in predictions:
            if not pred.value_rating:
                continue

            # Strong value ratings
            if 'strong' in pred.value_rating.lower():
                value_props.append(pred)
            # Lean ratings with sufficient edge
            elif 'lean' in pred.value_rating.lower():
                if pred.over_probability >= 55 or pred.under_probability >= 55:
                    value_props.append(pred)

        # Sort by probability (higher edge first)
        value_props.sort(
            key=lambda x: max(x.over_probability, x.under_probability),
            reverse=True
        )

        return value_props

    def _calculate_baseline_prediction(
        self,
        recent_performance: List[float],
        season_average: float,
        stat_type: str,
        sport: str
    ) -> float:
        """Calculate baseline prediction from historical data."""
        if not recent_performance:
            return season_average

        # Weight recent games more heavily
        weights = [0.35, 0.25, 0.20, 0.12, 0.08]  # Last 5 games
        weighted_recent = sum(
            perf * weight
            for perf, weight in zip(
                recent_performance[-5:],
                weights[:len(recent_performance[-5:])]
            )
        )

        # Blend recent and season average (70% recent, 30% season)
        if len(recent_performance) >= 5:
            baseline = weighted_recent * 0.70 + season_average * 0.30
        else:
            # Less recent data, weight season average more
            baseline = weighted_recent * 0.50 + season_average * 0.50

        return baseline

    def _apply_matchup_adjustments(
        self,
        baseline: float,
        opponent: str,
        stat_type: str,
        matchup_data: Optional[Dict]
    ) -> float:
        """Apply matchup-based adjustments."""
        if not matchup_data:
            return baseline

        # Historical performance vs this opponent
        vs_opponent_avg = matchup_data.get('vs_opponent_avg')
        if vs_opponent_avg:
            # Blend baseline with historical matchup (60/40)
            adjusted = baseline * 0.60 + vs_opponent_avg * 0.40
        else:
            adjusted = baseline

        # Opponent defensive ranking adjustment
        opponent_def_rank = matchup_data.get('opponent_defense_rank')
        if opponent_def_rank:
            # Top 10 defense: reduce by 10%
            # Bottom 10 defense: increase by 10%
            if opponent_def_rank <= 10:
                adjusted *= 0.90
            elif opponent_def_rank >= 22:
                adjusted *= 1.10

        return adjusted

    def _apply_situational_adjustments(
        self,
        baseline: float,
        adjustments: Dict
    ) -> float:
        """Apply situational adjustments."""
        adjusted = baseline

        # Injury concern
        if adjustments.get('injury_concern'):
            adjusted *= 0.85  # Reduce by 15%

        # Rest advantage
        if adjustments.get('rest_advantage'):
            adjusted *= 1.05  # Increase by 5%

        # Pace factor (high pace games)
        pace_factor = adjustments.get('pace_factor', 1.0)
        adjusted *= pace_factor

        # Usage rate changes
        usage_change = adjustments.get('usage_change', 0)
        adjusted *= (1 + usage_change)

        # Weather (for outdoor sports)
        if adjustments.get('bad_weather'):
            adjusted *= 0.90  # Reduce by 10%

        return adjusted

    def _get_stat_config(self, stat_type: str, sport: str) -> Dict:
        """Get configuration for a stat type."""
        sport_config = self.sport_stat_configs.get(sport, {})
        return sport_config.get(
            stat_type,
            {'avg': 10, 'std': 5, 'key_factors': []}
        )

    def _calculate_over_under_probabilities(
        self,
        prediction: float,
        market_line: float,
        std_dev: float
    ) -> Tuple[float, float]:
        """
        Calculate probability of over/under for a market line.

        Uses normal distribution approximation.
        """
        import math

        # Z-score for market line
        z_score = (market_line - prediction) / std_dev

        # Convert to probability using error function approximation
        # P(X > line) = P(Z > z_score)
        def normal_cdf(z):
            """Cumulative distribution function for standard normal."""
            return 0.5 * (1 + math.erf(z / math.sqrt(2)))

        under_prob = normal_cdf(z_score)
        over_prob = 1 - under_prob

        return (over_prob, under_prob)

    def _assess_value(
        self,
        prediction: float,
        market_line: float,
        over_probability: float
    ) -> str:
        """Assess betting value for a prop."""
        diff = prediction - market_line
        diff_pct = (diff / market_line * 100) if market_line > 0 else 0

        # Strong over value
        if diff_pct >= 15 and over_probability >= 0.60:
            return "strong_over"
        # Lean over
        elif diff_pct >= 8 and over_probability >= 0.55:
            return "lean_over"
        # Strong under value
        elif diff_pct <= -15 and over_probability <= 0.40:
            return "strong_under"
        # Lean under
        elif diff_pct <= -8 and over_probability <= 0.45:
            return "lean_under"
        else:
            return "no_value"

    def get_prop_correlations(
        self,
        predictions: List[PlayerPropPrediction]
    ) -> Dict:
        """
        Identify correlated props for parlay building.

        Returns:
            Dictionary of correlated prop groups
        """
        correlations = {
            'positive': [],  # Props that tend to hit together
            'negative': []   # Props that tend to be negatively correlated
        }

        # Positive correlations
        # Same team props often correlate
        team_props = {}
        for pred in predictions:
            if pred.team not in team_props:
                team_props[pred.team] = []
            team_props[pred.team].append(pred)

        for team, props in team_props.items():
            if len(props) >= 2:
                correlations['positive'].append({
                    'type': 'same_team',
                    'props': [f"{p.player_name} {p.stat_type}" for p in props],
                    'note': f"Same team ({team}) props often correlate"
                })

        # Negative correlations
        # Opposing teams' scoring props
        opponent_pairs = {}
        for pred in predictions:
            if 'points' in pred.stat_type.lower() or 'goals' in pred.stat_type.lower():
                key = tuple(sorted([pred.team, pred.opponent]))
                if key not in opponent_pairs:
                    opponent_pairs[key] = []
                opponent_pairs[key].append(pred)

        for (team1, team2), props in opponent_pairs.items():
            if len(props) >= 2:
                correlations['negative'].append({
                    'type': 'opposing_offense',
                    'props': [f"{p.player_name} {p.stat_type}" for p in props],
                    'note': "Opposing offensive props may be negatively correlated"
                })

        return correlations
