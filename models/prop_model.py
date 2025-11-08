"""Player prop line model for points, rebounds, goals, assists predictions."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics


class PlayerPropModel:
    """
    Model for predicting player prop lines (points, rebounds, goals, assists, etc.)

    Uses historical averages, recent form, matchup data, and contextual factors
    to generate fair lines for player props.
    """

    def __init__(self, lookback_games: int = 10):
        """
        Initialize player prop model.

        Args:
            lookback_games: Number of recent games to consider for predictions
        """
        self.lookback_games = lookback_games

    def predict_points(
        self,
        player_name: str,
        player_stats: List[Dict],
        opponent: str,
        sport: str,
        **context
    ) -> Dict:
        """
        Predict player points/goals for upcoming game.

        Args:
            player_name: Player name
            player_stats: List of recent game stats
            opponent: Opponent team
            sport: Sport type
            **context: Additional context (home/away, injury status, etc.)

        Returns:
            Dictionary with prediction and confidence
        """
        if not player_stats:
            return self._default_prediction(player_name, 'points', sport)

        # Extract recent points/goals
        recent_games = player_stats[-self.lookback_games:]
        points_list = [game.get('points', 0) for game in recent_games]

        # Calculate base statistics
        season_avg = statistics.mean([game.get('points', 0) for game in player_stats])
        recent_avg = statistics.mean(points_list)
        std_dev = statistics.stdev(points_list) if len(points_list) > 1 else 5.0

        # Weight recent form more heavily
        weighted_avg = (recent_avg * 0.7) + (season_avg * 0.3)

        # Apply contextual adjustments
        adjustments = 0
        confidence_factors = []

        # Home/away adjustment
        is_home = context.get('is_home', True)
        if is_home:
            adjustments += 1.5 if sport in ['nba', 'nfl'] else 0.3
            confidence_factors.append(('home_advantage', 0.05))
        else:
            adjustments -= 0.5
            confidence_factors.append(('away_penalty', -0.02))

        # Matchup difficulty
        opponent_def_rank = context.get('opponent_defense_rank', 16)  # 1-30 scale
        if opponent_def_rank <= 10:
            adjustments -= 2.0  # Tough matchup
            confidence_factors.append(('tough_defense', -0.1))
        elif opponent_def_rank >= 25:
            adjustments += 2.0  # Favorable matchup
            confidence_factors.append(('weak_defense', 0.1))

        # Recent trend
        if len(points_list) >= 3:
            last_3_avg = statistics.mean(points_list[-3:])
            trend = last_3_avg - season_avg
            if abs(trend) > 3:
                adjustments += trend * 0.3
                confidence_factors.append(('trend', 0.08 if trend > 0 else -0.08))

        # Minutes projection
        projected_minutes = context.get('projected_minutes')
        season_avg_minutes = context.get('season_avg_minutes', 30)
        if projected_minutes and season_avg_minutes:
            minutes_factor = projected_minutes / season_avg_minutes
            adjustments *= minutes_factor

        # Calculate final prediction
        predicted_line = weighted_avg + adjustments

        # Calculate confidence (0-1 scale)
        base_confidence = 0.6
        confidence_adjustment = sum(factor for _, factor in confidence_factors)
        consistency_bonus = max(0, 0.2 - (std_dev / season_avg)) if season_avg > 0 else 0
        confidence = min(0.95, max(0.3, base_confidence + confidence_adjustment + consistency_bonus))

        return {
            'player': player_name,
            'prop_type': 'points' if sport in ['nba', 'nfl'] else 'goals',
            'predicted_line': round(predicted_line, 1),
            'season_average': round(season_avg, 1),
            'recent_average': round(recent_avg, 1),
            'standard_deviation': round(std_dev, 1),
            'confidence': round(confidence, 2),
            'over_recommendation': predicted_line > context.get('market_line', predicted_line),
            'market_line': context.get('market_line'),
            'edge': round(predicted_line - context.get('market_line', predicted_line), 1) if context.get('market_line') else None,
            'contextual_factors': confidence_factors,
            'sport': sport,
            'opponent': opponent,
            'timestamp': datetime.now().isoformat()
        }

    def predict_rebounds(
        self,
        player_name: str,
        player_stats: List[Dict],
        opponent: str,
        **context
    ) -> Dict:
        """Predict player rebounds (basketball)."""
        if not player_stats:
            return self._default_prediction(player_name, 'rebounds', 'nba')

        recent_games = player_stats[-self.lookback_games:]
        rebounds_list = [game.get('rebounds', 0) for game in recent_games]

        season_avg = statistics.mean([game.get('rebounds', 0) for game in player_stats])
        recent_avg = statistics.mean(rebounds_list)
        std_dev = statistics.stdev(rebounds_list) if len(rebounds_list) > 1 else 2.0

        weighted_avg = (recent_avg * 0.7) + (season_avg * 0.3)

        # Matchup-specific adjustments
        adjustments = 0
        opponent_rebounding_rank = context.get('opponent_rebounding_rank', 16)
        if opponent_rebounding_rank >= 25:
            adjustments += 1.5  # Weak rebounding team
        elif opponent_rebounding_rank <= 10:
            adjustments -= 1.0  # Strong rebounding team

        predicted_line = weighted_avg + adjustments
        confidence = 0.65 if std_dev < 3 else 0.5

        return {
            'player': player_name,
            'prop_type': 'rebounds',
            'predicted_line': round(predicted_line, 1),
            'season_average': round(season_avg, 1),
            'recent_average': round(recent_avg, 1),
            'confidence': round(confidence, 2),
            'market_line': context.get('market_line'),
            'edge': round(predicted_line - context.get('market_line', predicted_line), 1) if context.get('market_line') else None,
            'opponent': opponent,
            'timestamp': datetime.now().isoformat()
        }

    def predict_assists(
        self,
        player_name: str,
        player_stats: List[Dict],
        opponent: str,
        sport: str = 'nba',
        **context
    ) -> Dict:
        """Predict player assists."""
        if not player_stats:
            return self._default_prediction(player_name, 'assists', sport)

        recent_games = player_stats[-self.lookback_games:]
        assists_list = [game.get('assists', 0) for game in recent_games]

        season_avg = statistics.mean([game.get('assists', 0) for game in player_stats])
        recent_avg = statistics.mean(assists_list)
        std_dev = statistics.stdev(assists_list) if len(assists_list) > 1 else 1.5

        weighted_avg = (recent_avg * 0.7) + (season_avg * 0.3)

        # Pace adjustment
        adjustments = 0
        game_pace = context.get('expected_pace', 100)  # Possessions per game
        avg_pace = context.get('season_avg_pace', 100)
        pace_factor = (game_pace - avg_pace) / avg_pace
        adjustments += weighted_avg * pace_factor * 0.5

        predicted_line = weighted_avg + adjustments
        confidence = 0.6 if std_dev < 2 else 0.45

        return {
            'player': player_name,
            'prop_type': 'assists',
            'predicted_line': round(predicted_line, 1),
            'season_average': round(season_avg, 1),
            'recent_average': round(recent_avg, 1),
            'confidence': round(confidence, 2),
            'market_line': context.get('market_line'),
            'edge': round(predicted_line - context.get('market_line', predicted_line), 1) if context.get('market_line') else None,
            'opponent': opponent,
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }

    def predict_multi_prop(
        self,
        player_name: str,
        player_stats: List[Dict],
        prop_types: List[str],
        opponent: str,
        sport: str,
        **context
    ) -> Dict:
        """
        Predict multiple props for a player (e.g., points + rebounds + assists).

        Args:
            player_name: Player name
            player_stats: Historical stats
            prop_types: List of prop types to predict
            opponent: Opponent team
            sport: Sport type
            **context: Additional context

        Returns:
            Dictionary with all prop predictions
        """
        predictions = {}

        for prop_type in prop_types:
            if prop_type in ['points', 'goals']:
                predictions[prop_type] = self.predict_points(
                    player_name, player_stats, opponent, sport, **context
                )
            elif prop_type == 'rebounds':
                predictions[prop_type] = self.predict_rebounds(
                    player_name, player_stats, opponent, **context
                )
            elif prop_type == 'assists':
                predictions[prop_type] = self.predict_assists(
                    player_name, player_stats, opponent, sport, **context
                )

        # Calculate combined prop if applicable (e.g., PRA in basketball)
        if sport == 'nba' and all(p in predictions for p in ['points', 'rebounds', 'assists']):
            combined_line = (
                predictions['points']['predicted_line'] +
                predictions['rebounds']['predicted_line'] +
                predictions['assists']['predicted_line']
            )
            predictions['points_rebounds_assists'] = {
                'player': player_name,
                'prop_type': 'PRA',
                'predicted_line': round(combined_line, 1),
                'confidence': min([predictions[p]['confidence'] for p in ['points', 'rebounds', 'assists']]),
                'timestamp': datetime.now().isoformat()
            }

        return {
            'player': player_name,
            'opponent': opponent,
            'sport': sport,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        }

    def _default_prediction(self, player_name: str, prop_type: str, sport: str) -> Dict:
        """Return default prediction when no data available."""
        defaults = {
            'nba': {'points': 15, 'rebounds': 5, 'assists': 3},
            'nfl': {'points': 12, 'yards': 60, 'touchdowns': 0.5},
            'nhl': {'goals': 0.5, 'assists': 0.5, 'points': 1.0},
            'mlb': {'hits': 1.0, 'runs': 0.5, 'rbis': 0.5}
        }

        default_value = defaults.get(sport, {}).get(prop_type, 10)

        return {
            'player': player_name,
            'prop_type': prop_type,
            'predicted_line': default_value,
            'confidence': 0.3,
            'note': 'Insufficient data - using default prediction',
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }
