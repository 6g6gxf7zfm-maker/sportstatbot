"""
Dynamic Spread Model.

Calculates fair betting lines and point spreads with hourly updates.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class SpreadPrediction:
    """Spread prediction for a game."""
    home_team: str
    away_team: str
    fair_spread: float  # From home team perspective
    confidence_interval: Tuple[float, float]
    fair_moneyline_home: int
    fair_moneyline_away: int
    fair_total: float  # Over/under
    total_confidence: Tuple[float, float]
    last_updated: str
    market_spread: Optional[float] = None
    spread_value: Optional[float] = None  # Difference from market
    recommendation: Optional[str] = None


@dataclass
class LineMovement:
    """Track betting line movement."""
    game_id: str
    timestamps: List[str]
    spreads: List[float]
    totals: List[float]
    movement_direction: str  # 'towards_home', 'towards_away', 'stable'
    sharp_money_indicator: bool


class DynamicSpreadModel:
    """
    Dynamic spread and totals prediction model.

    Features:
    - Fair line calculations based on power ratings
    - Hourly recalculation
    - Market comparison and value detection
    - Line movement tracking
    - Sharp money indicators
    """

    def __init__(self):
        """Initialize spread model."""
        self.line_history: Dict[str, LineMovement] = {}

        # Sport-specific parameters
        self.sport_configs = {
            'nfl': {
                'rating_to_spread': 25,  # Rating points per point spread
                'typical_total': 45,
                'home_advantage': 2.5
            },
            'nba': {
                'rating_to_spread': 28,
                'typical_total': 220,
                'home_advantage': 3.5
            },
            'mlb': {
                'rating_to_spread': 35,
                'typical_total': 9.0,
                'home_advantage': 0.3
            },
            'nhl': {
                'rating_to_spread': 40,
                'typical_total': 6.0,
                'home_advantage': 0.4
            },
            'mls': {
                'rating_to_spread': 45,
                'typical_total': 3.0,
                'home_advantage': 0.5
            },
            'soccer': {
                'rating_to_spread': 45,
                'typical_total': 2.8,
                'home_advantage': 0.45
            }
        }

    def calculate_spread(
        self,
        home_team: str,
        away_team: str,
        home_rating: float,
        away_rating: float,
        home_offensive: float,
        away_offensive: float,
        home_defensive: float,
        away_defensive: float,
        sport: str,
        adjustments: Optional[Dict] = None,
        market_spread: Optional[float] = None
    ) -> SpreadPrediction:
        """
        Calculate fair spread and total for a game.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_rating: Home team power rating
            away_rating: Away team power rating
            home_offensive: Home offensive rating (normalized to 100)
            away_offensive: Away offensive rating
            home_defensive: Home defensive rating
            away_defensive: Away defensive rating
            sport: Sport type
            adjustments: Optional adjustments (injuries, weather, etc.)
            market_spread: Current market spread for comparison

        Returns:
            SpreadPrediction with all predictions
        """
        config = self.sport_configs.get(sport, self.sport_configs['nfl'])

        # Apply adjustments
        if adjustments:
            home_rating += adjustments.get('home_rating_adj', 0)
            away_rating += adjustments.get('away_rating_adj', 0)

        # Calculate base spread
        rating_diff = home_rating - away_rating + config['home_advantage']
        fair_spread = rating_diff / config['rating_to_spread']

        # Calculate confidence interval (±1.5 * standard deviation)
        # Spread uncertainty typically ~3-4 points in NFL, scaled by sport
        spread_std = 3.5 * (config['rating_to_spread'] / 25)
        spread_ci = (
            fair_spread - 1.5 * spread_std,
            fair_spread + 1.5 * spread_std
        )

        # Calculate fair moneylines
        home_ml, away_ml = self._spread_to_moneyline(fair_spread)

        # Calculate fair total (over/under)
        fair_total = self._calculate_total(
            home_offensive, away_offensive,
            home_defensive, away_defensive,
            config['typical_total']
        )

        # Total confidence interval
        total_std = config['typical_total'] * 0.15  # ~15% variance
        total_ci = (
            fair_total - 1.5 * total_std,
            fair_total + 1.5 * total_std
        )

        # Compare to market and make recommendation
        spread_value = None
        recommendation = None

        if market_spread is not None:
            spread_value = market_spread - fair_spread
            recommendation = self._generate_recommendation(
                spread_value, fair_spread, market_spread
            )

        return SpreadPrediction(
            home_team=home_team,
            away_team=away_team,
            fair_spread=round(fair_spread, 1),
            confidence_interval=(round(spread_ci[0], 1), round(spread_ci[1], 1)),
            fair_moneyline_home=home_ml,
            fair_moneyline_away=away_ml,
            fair_total=round(fair_total, 1),
            total_confidence=(round(total_ci[0], 1), round(total_ci[1], 1)),
            last_updated=datetime.now().isoformat(),
            market_spread=market_spread,
            spread_value=round(spread_value, 2) if spread_value else None,
            recommendation=recommendation
        )

    def track_line_movement(
        self,
        game_id: str,
        current_spread: float,
        current_total: float
    ):
        """
        Track betting line movement over time.

        Args:
            game_id: Unique game identifier
            current_spread: Current market spread
            current_total: Current market total
        """
        timestamp = datetime.now().isoformat()

        if game_id not in self.line_history:
            self.line_history[game_id] = LineMovement(
                game_id=game_id,
                timestamps=[timestamp],
                spreads=[current_spread],
                totals=[current_total],
                movement_direction='stable',
                sharp_money_indicator=False
            )
        else:
            movement = self.line_history[game_id]
            movement.timestamps.append(timestamp)
            movement.spreads.append(current_spread)
            movement.totals.append(current_total)

            # Update movement direction
            movement.movement_direction = self._analyze_movement_direction(
                movement.spreads
            )

            # Detect sharp money (sudden significant moves)
            movement.sharp_money_indicator = self._detect_sharp_money(
                movement.spreads, movement.timestamps
            )

    def get_line_movement(self, game_id: str) -> Optional[LineMovement]:
        """Get line movement history for a game."""
        return self.line_history.get(game_id)

    def find_betting_value(
        self,
        predictions: List[SpreadPrediction],
        value_threshold: float = 2.0
    ) -> List[SpreadPrediction]:
        """
        Find games with betting value (model disagrees with market).

        Args:
            predictions: List of spread predictions
            value_threshold: Minimum point difference to flag as value

        Returns:
            List of predictions with significant value
        """
        value_plays = []

        for pred in predictions:
            if pred.spread_value and abs(pred.spread_value) >= value_threshold:
                value_plays.append(pred)

        # Sort by absolute value
        value_plays.sort(key=lambda x: abs(x.spread_value or 0), reverse=True)

        return value_plays

    def _spread_to_moneyline(self, spread: float) -> Tuple[int, int]:
        """
        Convert point spread to fair moneyline odds.

        Args:
            spread: Point spread (from home perspective)

        Returns:
            Tuple of (home_moneyline, away_moneyline)
        """
        # Approximate conversion (not exact, but reasonable)
        # Spread of -3 is roughly -150/+130

        if spread == 0:
            return (-110, -110)

        # Calculate implied probability
        if spread > 0:
            # Home is underdog
            home_prob = 0.50 - (spread * 0.025)
        else:
            # Home is favorite
            home_prob = 0.50 + (abs(spread) * 0.025)

        home_prob = max(0.1, min(0.9, home_prob))
        away_prob = 1 - home_prob

        # Convert probability to American odds
        def prob_to_american(prob):
            if prob >= 0.50:
                return int(-prob / (1 - prob) * 100)
            else:
                return int((1 - prob) / prob * 100)

        home_ml = prob_to_american(home_prob)
        away_ml = prob_to_american(away_prob)

        return (home_ml, away_ml)

    def _calculate_total(
        self,
        home_offensive: float,
        away_offensive: float,
        home_defensive: float,
        away_defensive: float,
        typical_total: float
    ) -> float:
        """
        Calculate expected total points/goals.

        Args:
            home_offensive: Home offensive rating (normalized to 100)
            away_offensive: Away offensive rating
            home_defensive: Home defensive rating
            away_defensive: Away defensive rating
            typical_total: Typical total for sport

        Returns:
            Expected total
        """
        # Calculate expected home score
        # Strong offense vs weak defense = more points
        home_expected = (
            typical_total / 2 *
            (home_offensive / 100) *
            ((200 - away_defensive) / 100)
        )

        # Calculate expected away score
        away_expected = (
            typical_total / 2 *
            (away_offensive / 100) *
            ((200 - home_defensive) / 100)
        )

        total = home_expected + away_expected

        return total

    def _generate_recommendation(
        self,
        spread_value: float,
        fair_spread: float,
        market_spread: float
    ) -> str:
        """Generate betting recommendation."""
        if abs(spread_value) < 1.5:
            return "No strong lean - lines are efficient"

        if spread_value > 1.5:
            # Market spread is higher than our fair spread
            # Home team is getting too many points
            return f"VALUE: Home team ({market_spread:+.1f}) - Model has {fair_spread:+.1f}"
        else:
            # Market spread is lower than our fair spread
            # Away team is getting too many points
            return f"VALUE: Away team ({-market_spread:+.1f}) - Model has {-fair_spread:+.1f}"

    def _analyze_movement_direction(self, spreads: List[float]) -> str:
        """Analyze direction of line movement."""
        if len(spreads) < 3:
            return 'stable'

        recent = spreads[-5:]  # Last 5 updates

        start_avg = sum(recent[:2]) / 2 if len(recent) >= 2 else recent[0]
        end_avg = sum(recent[-2:]) / 2 if len(recent) >= 2 else recent[-1]

        diff = end_avg - start_avg

        if diff > 0.5:
            return 'towards_away'  # Spread increasing (more points to away)
        elif diff < -0.5:
            return 'towards_home'  # Spread decreasing (more points to home)
        else:
            return 'stable'

    def _detect_sharp_money(
        self,
        spreads: List[float],
        timestamps: List[str]
    ) -> bool:
        """
        Detect sharp money movement.

        Sharp money is characterized by:
        - Significant line move (1.5+ points)
        - Happening quickly (within short timeframe)
        - Often reverse of public betting
        """
        if len(spreads) < 3:
            return False

        # Check for significant rapid movement
        for i in range(len(spreads) - 1):
            move = abs(spreads[i + 1] - spreads[i])
            if move >= 1.5:
                return True

        # Check for sustained movement in one direction
        if len(spreads) >= 5:
            total_move = abs(spreads[-1] - spreads[0])
            if total_move >= 2.5:
                return True

        return False

    def calculate_derivative_lines(
        self,
        spread: SpreadPrediction
    ) -> Dict:
        """
        Calculate derivative betting lines.

        Includes:
        - Alternate spreads
        - Team totals
        - First half lines
        """
        # Alternate spreads (adjust probability)
        alt_spreads = {}
        for adj in [-3, -1.5, 1.5, 3]:
            alt_line = spread.fair_spread + adj
            home_ml, away_ml = self._spread_to_moneyline(alt_line)
            alt_spreads[f"{alt_line:+.1f}"] = {
                'home_ml': home_ml,
                'away_ml': away_ml
            }

        # Team totals (rough split of total)
        home_team_total = spread.fair_total * 0.52  # Home slight advantage
        away_team_total = spread.fair_total * 0.48

        # First half lines (typically ~55% of full game)
        first_half_spread = spread.fair_spread * 0.55
        first_half_total = spread.fair_total * 0.48

        return {
            'alternate_spreads': alt_spreads,
            'team_totals': {
                'home': round(home_team_total, 1),
                'away': round(away_team_total, 1)
            },
            'first_half': {
                'spread': round(first_half_spread, 1),
                'total': round(first_half_total, 1)
            }
        }
