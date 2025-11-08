"""Momentum carryover tracker for back-to-back game impacts."""
from typing import Dict, List
from datetime import datetime, timedelta


class MomentumCarryoverTracker:
    """
    Tracks team momentum and its carryover effects between games.

    Analyzes winning/losing streaks, recent performance trends,
    and how they impact upcoming games.
    """

    def __init__(self, lookback_games: int = 10):
        """
        Initialize momentum tracker.

        Args:
            lookback_games: Number of recent games to analyze
        """
        self.lookback_games = lookback_games

    def calculate_momentum(
        self,
        recent_results: List[Dict],
        sport: str
    ) -> Dict:
        """
        Calculate current team momentum.

        Args:
            recent_results: List of recent game results (most recent last)
            sport: Sport type

        Returns:
            Dictionary with momentum analysis
        """
        if not recent_results:
            return self._no_data_response()

        # Limit to lookback window
        relevant_games = recent_results[-self.lookback_games:]

        # Calculate basic metrics
        wins = sum(1 for g in relevant_games if g.get('won', False))
        losses = len(relevant_games) - wins
        win_pct = wins / len(relevant_games)

        # Identify current streak
        current_streak = self._identify_streak(relevant_games)

        # Calculate weighted momentum (recent games weighted more)
        momentum_score = self._calculate_weighted_momentum(relevant_games)

        # Analyze scoring trends
        scoring_trend = self._analyze_scoring_trend(relevant_games)

        # Calculate momentum level
        momentum_level = self._determine_momentum_level(
            momentum_score, current_streak, win_pct
        )

        # Calculate expected carryover
        carryover_impact = self._calculate_carryover(
            momentum_level, current_streak, sport
        )

        return {
            'games_analyzed': len(relevant_games),
            'record': f"{wins}-{losses}",
            'win_percentage': round(win_pct, 3),
            'current_streak': current_streak,
            'momentum_score': round(momentum_score, 1),
            'momentum_level': momentum_level,
            'scoring_trend': scoring_trend,
            'carryover_impact': carryover_impact,
            'confidence': self._calculate_confidence(len(relevant_games)),
            'sport': sport
        }

    def predict_next_game_impact(
        self,
        momentum_data: Dict,
        opponent_momentum: Dict,
        sport: str
    ) -> Dict:
        """
        Predict how momentum will impact next game.

        Args:
            momentum_data: Team's momentum data
            opponent_momentum: Opponent's momentum data
            sport: Sport type

        Returns:
            Prediction of momentum impact
        """
        team_score = momentum_data.get('momentum_score', 0)
        opponent_score = opponent_momentum.get('momentum_score', 0)

        momentum_differential = team_score - opponent_score

        # Convert to expected point impact
        point_impact = self._momentum_to_points(momentum_differential, sport)

        # Determine psychological edge
        psychological_edge = self._determine_psychological_edge(
            momentum_data, opponent_momentum
        )

        return {
            'team_momentum': round(team_score, 1),
            'opponent_momentum': round(opponent_score, 1),
            'momentum_differential': round(momentum_differential, 1),
            'expected_point_impact': round(point_impact, 1),
            'psychological_edge': psychological_edge,
            'recommendation': self._generate_momentum_recommendation(
                momentum_differential, psychological_edge
            ),
            'sport': sport
        }

    def _identify_streak(self, games: List[Dict]) -> Dict:
        """Identify current win/loss streak."""
        if not games:
            return {'type': 'NONE', 'length': 0}

        # Start from most recent game
        current_result = games[-1].get('won', False)
        streak_type = 'W' if current_result else 'L'
        streak_length = 1

        # Count backwards
        for i in range(len(games) - 2, -1, -1):
            if games[i].get('won', False) == current_result:
                streak_length += 1
            else:
                break

        return {
            'type': streak_type,
            'length': streak_length,
            'description': f"{streak_length}-game {'winning' if streak_type == 'W' else 'losing'} streak"
        }

    def _calculate_weighted_momentum(self, games: List[Dict]) -> float:
        """
        Calculate weighted momentum score.

        Recent games weighted more heavily than older games.
        """
        score = 0
        total_weight = 0

        for i, game in enumerate(games):
            # Weight increases for more recent games
            weight = i + 1

            # Win/loss component
            if game.get('won', False):
                score += 10 * weight
            else:
                score -= 10 * weight

            # Margin of victory/defeat component
            margin = game.get('margin', 0)
            if abs(margin) > 20:  # Blowout
                score += (margin / 4) * weight
            else:
                score += (margin / 8) * weight

            total_weight += weight

        # Normalize to -100 to +100 scale
        normalized_score = (score / total_weight) if total_weight > 0 else 0

        return max(-100, min(100, normalized_score))

    def _analyze_scoring_trend(self, games: List[Dict]) -> Dict:
        """Analyze scoring trend over recent games."""
        if len(games) < 3:
            return {'trend': 'INSUFFICIENT_DATA'}

        # Get points scored in each game
        points = [g.get('points_for', 0) for g in games]

        # Compare first half to second half of sample
        mid_point = len(points) // 2
        first_half_avg = sum(points[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(points[mid_point:]) / (len(points) - mid_point)

        trend_diff = second_half_avg - first_half_avg

        if trend_diff > 5:
            trend = "IMPROVING"
        elif trend_diff < -5:
            trend = "DECLINING"
        else:
            trend = "STABLE"

        return {
            'trend': trend,
            'recent_avg': round(second_half_avg, 1),
            'previous_avg': round(first_half_avg, 1),
            'change': round(trend_diff, 1)
        }

    def _determine_momentum_level(
        self,
        score: float,
        streak: Dict,
        win_pct: float
    ) -> str:
        """Determine momentum level classification."""
        streak_length = streak.get('length', 0)
        streak_type = streak.get('type')

        if streak_type == 'W' and streak_length >= 5:
            return "RED_HOT"
        elif score >= 60 and win_pct >= 0.7:
            return "HOT"
        elif score >= 30 or (win_pct >= 0.6 and streak_type == 'W'):
            return "POSITIVE"
        elif -30 < score < 30:
            return "NEUTRAL"
        elif score <= -30 or (win_pct <= 0.4 and streak_type == 'L'):
            return "NEGATIVE"
        elif streak_type == 'L' and streak_length >= 5:
            return "ICE_COLD"
        else:
            return "COLD"

    def _calculate_carryover(
        self,
        momentum_level: str,
        streak: Dict,
        sport: str
    ) -> Dict:
        """Calculate expected carryover impact to next game."""
        impact_values = {
            'RED_HOT': 2.5,
            'HOT': 1.5,
            'POSITIVE': 0.8,
            'NEUTRAL': 0,
            'NEGATIVE': -0.8,
            'COLD': -1.5,
            'ICE_COLD': -2.5
        }

        base_impact = impact_values.get(momentum_level, 0)

        # Streak bonus
        streak_bonus = min(1.0, streak.get('length', 0) * 0.2)
        if streak.get('type') == 'L':
            streak_bonus = -streak_bonus

        total_impact = base_impact + streak_bonus

        return {
            'rating_adjustment': round(total_impact, 1),
            'confidence_boost': self._get_confidence_boost(momentum_level),
            'expected_description': self._describe_impact(total_impact)
        }

    def _momentum_to_points(self, momentum_diff: float, sport: str) -> float:
        """Convert momentum differential to expected point impact."""
        # Sport-specific conversion
        if sport == 'nba':
            return momentum_diff * 0.05  # 5 points per 100 momentum
        elif sport == 'nfl':
            return momentum_diff * 0.03  # 3 points per 100 momentum
        elif sport in ['nhl', 'mls', 'soccer']:
            return momentum_diff * 0.01  # 1 goal per 100 momentum
        else:
            return momentum_diff * 0.02

    def _determine_psychological_edge(
        self,
        team_data: Dict,
        opponent_data: Dict
    ) -> str:
        """Determine which team has psychological edge."""
        team_level = team_data.get('momentum_level')
        opp_level = opponent_data.get('momentum_level')

        hot_levels = ['RED_HOT', 'HOT', 'POSITIVE']
        cold_levels = ['NEGATIVE', 'COLD', 'ICE_COLD']

        if team_level in hot_levels and opp_level in cold_levels:
            return "STRONG_TEAM_EDGE"
        elif team_level in hot_levels:
            return "MODERATE_TEAM_EDGE"
        elif opp_level in hot_levels:
            return "MODERATE_OPPONENT_EDGE"
        elif opp_level in hot_levels and team_level in cold_levels:
            return "STRONG_OPPONENT_EDGE"
        else:
            return "NEUTRAL"

    def _generate_momentum_recommendation(
        self,
        differential: float,
        psychological_edge: str
    ) -> str:
        """Generate recommendation based on momentum analysis."""
        if "STRONG_TEAM" in psychological_edge:
            return "Strong momentum advantage - team likely to cover spread"
        elif "MODERATE_TEAM" in psychological_edge:
            return "Moderate momentum advantage - slight edge to team"
        elif "STRONG_OPPONENT" in psychological_edge:
            return "Opponent has strong momentum - be cautious"
        elif differential > 20:
            return "Team riding positive momentum"
        elif differential < -20:
            return "Team struggling with negative momentum"
        else:
            return "Momentum roughly neutral"

    def _calculate_confidence(self, sample_size: int) -> float:
        """Calculate confidence based on sample size."""
        return min(0.95, 0.5 + (sample_size * 0.05))

    def _get_confidence_boost(self, momentum_level: str) -> str:
        """Get expected confidence boost for team."""
        boosts = {
            'RED_HOT': 'MAJOR',
            'HOT': 'SIGNIFICANT',
            'POSITIVE': 'MODERATE',
            'NEUTRAL': 'NONE',
            'NEGATIVE': 'REDUCED',
            'COLD': 'LOW',
            'ICE_COLD': 'VERY_LOW'
        }
        return boosts.get(momentum_level, 'UNKNOWN')

    def _describe_impact(self, impact: float) -> str:
        """Describe momentum impact in words."""
        if impact >= 2:
            return "Major positive impact expected"
        elif impact >= 1:
            return "Moderate positive impact expected"
        elif impact > 0:
            return "Slight positive impact expected"
        elif impact == 0:
            return "Neutral impact"
        elif impact > -1:
            return "Slight negative impact expected"
        elif impact > -2:
            return "Moderate negative impact expected"
        else:
            return "Major negative impact expected"

    def _no_data_response(self) -> Dict:
        """Return response when no data available."""
        return {
            'momentum_level': 'UNKNOWN',
            'momentum_score': 0,
            'note': 'Insufficient game data'
        }
