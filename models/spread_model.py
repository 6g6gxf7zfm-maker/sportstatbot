"""Dynamic spread model with hourly recalculation capabilities."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os


class DynamicSpreadModel:
    """
    Dynamic point spread model that recalculates fair lines based on current data.

    Updates spreads hourly based on:
    - Power ratings
    - Recent performance
    - Injuries
    - Weather conditions
    - Public betting percentages
    - Line movement
    """

    def __init__(
        self,
        power_rating_system=None,
        storage_path: str = './data/spreads'
    ):
        """
        Initialize dynamic spread model.

        Args:
            power_rating_system: PowerRatingSystem instance
            storage_path: Path to store spread data
        """
        self.power_rating_system = power_rating_system
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

        self.spread_cache = {}  # {game_id: spread_data}

    def calculate_fair_spread(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        **adjustments
    ) -> Dict:
        """
        Calculate fair point spread for a game.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            **adjustments: Various adjustment factors

        Returns:
            Dictionary with spread calculations
        """
        # Get base power ratings
        if self.power_rating_system:
            home_rating = self.power_rating_system.get_rating(home_team, sport)
            away_rating = self.power_rating_system.get_rating(away_team, sport)
        else:
            home_rating = 1500
            away_rating = 1500

        # Calculate base spread (25 rating points ~= 1 point spread)
        rating_diff = home_rating - away_rating
        base_spread = rating_diff / 25

        # Apply adjustments
        home_advantage = adjustments.get('home_advantage', 2.5)
        injury_impact = adjustments.get('injury_impact', 0)  # Negative for injured team
        rest_advantage = adjustments.get('rest_advantage', 0)  # Home team rest advantage
        weather_impact = adjustments.get('weather_impact', 0)
        public_betting = adjustments.get('public_betting_pct', 50)  # % on home team
        recent_form = adjustments.get('recent_form_diff', 0)  # Home form - away form

        # Calculate adjusted spread
        adjusted_spread = (
            base_spread +
            home_advantage +
            injury_impact +
            rest_advantage +
            weather_impact +
            recent_form * 0.3  # Recent form has moderate impact
        )

        # Adjust for sharp money (public betting creates value)
        # If public is heavily on one side, line might be inflated
        public_bias = (public_betting - 50) * 0.02  # Max ±1 point adjustment
        fair_spread = adjusted_spread - public_bias

        return {
            'home_team': home_team,
            'away_team': away_team,
            'fair_spread': round(fair_spread, 1),
            'base_spread': round(base_spread, 1),
            'adjustments': {
                'home_advantage': home_advantage,
                'injury_impact': injury_impact,
                'rest_advantage': rest_advantage,
                'weather_impact': weather_impact,
                'recent_form': recent_form,
                'public_bias': round(public_bias, 1)
            },
            'timestamp': datetime.now().isoformat(),
            'sport': sport
        }

    def calculate_total(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        **adjustments
    ) -> Dict:
        """
        Calculate over/under total for a game.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            **adjustments: Various adjustment factors

        Returns:
            Dictionary with total calculations
        """
        # Base totals by sport
        base_totals = {
            'nfl': 45.0,
            'nba': 220.0,
            'mlb': 9.0,
            'nhl': 6.0,
            'mls': 2.5,
            'soccer': 2.5
        }

        base_total = base_totals.get(sport.lower(), 45.0)

        # Get team scoring averages if available
        home_avg = adjustments.get('home_scoring_avg', base_total / 2)
        away_avg = adjustments.get('away_scoring_avg', base_total / 2)

        # Calculate base total from team averages
        calculated_total = home_avg + away_avg

        # Apply adjustments
        pace_factor = adjustments.get('pace_factor', 1.0)  # Multiplier for pace
        weather_impact = adjustments.get('weather_total_impact', 0)  # -/+ for weather
        defense_adjustment = adjustments.get('defense_adjustment', 0)

        # Adjusted total
        adjusted_total = (
            calculated_total * pace_factor +
            weather_impact +
            defense_adjustment
        )

        return {
            'home_team': home_team,
            'away_team': away_team,
            'fair_total': round(adjusted_total, 1),
            'base_total': round(calculated_total, 1),
            'adjustments': {
                'pace_factor': pace_factor,
                'weather_impact': weather_impact,
                'defense_adjustment': defense_adjustment
            },
            'timestamp': datetime.now().isoformat(),
            'sport': sport
        }

    def compare_to_market(
        self,
        game_id: str,
        home_team: str,
        away_team: str,
        sport: str,
        market_spread: float,
        market_total: float,
        **adjustments
    ) -> Dict:
        """
        Compare model's fair lines to market lines to find betting value.

        Args:
            game_id: Unique game identifier
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            market_spread: Current market spread
            market_total: Current market total
            **adjustments: Adjustment factors

        Returns:
            Dictionary with value analysis
        """
        fair_spread_data = self.calculate_fair_spread(
            home_team, away_team, sport, **adjustments
        )
        fair_total_data = self.calculate_total(
            home_team, away_team, sport, **adjustments
        )

        fair_spread = fair_spread_data['fair_spread']
        fair_total = fair_total_data['fair_total']

        # Calculate edge
        spread_edge = market_spread - fair_spread  # Positive means value on underdog
        total_edge = market_total - fair_total  # Positive means value on under

        # Determine if there's betting value (>2 point edge)
        value_threshold = 2.0 if sport == 'nfl' else 3.0 if sport == 'nba' else 1.5

        spread_value = None
        if abs(spread_edge) >= value_threshold:
            if spread_edge > 0:
                spread_value = f"{away_team} {market_spread:+.1f}"
            else:
                spread_value = f"{home_team} {-market_spread:+.1f}"

        total_value = None
        if abs(total_edge) >= value_threshold:
            if total_edge > 0:
                total_value = f"UNDER {market_total}"
            else:
                total_value = f"OVER {market_total}"

        result = {
            'game_id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            'fair_spread': fair_spread,
            'market_spread': market_spread,
            'spread_edge': round(spread_edge, 1),
            'fair_total': fair_total,
            'market_total': market_total,
            'total_edge': round(total_edge, 1),
            'spread_value_pick': spread_value,
            'total_value_pick': total_value,
            'has_value': spread_value is not None or total_value is not None,
            'timestamp': datetime.now().isoformat()
        }

        # Cache the result
        self.spread_cache[game_id] = result
        self._save_spread_data(game_id, result)

        return result

    def track_line_movement(
        self,
        game_id: str,
        current_spread: float,
        current_total: float
    ) -> Dict:
        """
        Track how lines have moved since opening.

        Args:
            game_id: Unique game identifier
            current_spread: Current spread
            current_total: Current total

        Returns:
            Dictionary with line movement analysis
        """
        history = self._load_spread_history(game_id)

        if not history:
            # First data point
            history = {
                'game_id': game_id,
                'opening_spread': current_spread,
                'opening_total': current_total,
                'movements': [(datetime.now().isoformat(), current_spread, current_total)]
            }
        else:
            # Add new data point
            history['movements'].append(
                (datetime.now().isoformat(), current_spread, current_total)
            )

        # Calculate movement
        spread_movement = current_spread - history['opening_spread']
        total_movement = current_total - history['opening_total']

        # Determine sharp money direction
        sharp_indicator = None
        if abs(spread_movement) >= 1.5:
            sharp_indicator = "Sharp money likely on " + (
                "favorite" if spread_movement > 0 else "underdog"
            )

        result = {
            'game_id': game_id,
            'opening_spread': history['opening_spread'],
            'current_spread': current_spread,
            'spread_movement': round(spread_movement, 1),
            'opening_total': history['opening_total'],
            'current_total': current_total,
            'total_movement': round(total_movement, 1),
            'movement_count': len(history['movements']),
            'sharp_indicator': sharp_indicator,
            'timestamp': datetime.now().isoformat()
        }

        # Save updated history
        self._save_spread_history(game_id, history)

        return result

    def _save_spread_data(self, game_id: str, data: Dict):
        """Save spread data to disk."""
        filepath = os.path.join(self.storage_path, f'{game_id}_spread.json')
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving spread data: {e}")

    def _save_spread_history(self, game_id: str, history: Dict):
        """Save spread movement history to disk."""
        filepath = os.path.join(self.storage_path, f'{game_id}_history.json')
        try:
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving spread history: {e}")

    def _load_spread_history(self, game_id: str) -> Optional[Dict]:
        """Load spread movement history from disk."""
        filepath = os.path.join(self.storage_path, f'{game_id}_history.json')
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading spread history: {e}")
            return None
