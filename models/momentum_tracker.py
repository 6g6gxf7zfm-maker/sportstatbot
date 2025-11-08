"""
Momentum Carryover Tracker.

Tracks momentum from recent games and back-to-back impacts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MomentumScore:
    """Momentum score for a team."""
    team: str
    momentum_rating: float  # -10 to +10
    recent_form: str  # 'hot', 'cold', 'neutral'
    last_5_record: str
    streak: str
    back_to_back_factor: float
    rest_days: int
    trend: str  # 'improving', 'declining', 'stable'


class MomentumTracker:
    """Tracks team momentum and carryover effects."""

    def __init__(self):
        """Initialize momentum tracker."""
        self.momentum_decay = 0.15  # Momentum decays 15% per game

    def calculate_momentum(
        self,
        team: str,
        recent_results: List[Dict],  # Last 10 games
        current_streak: int,  # Positive = win streak, negative = loss streak
        days_since_last_game: int,
        is_back_to_back: bool = False
    ) -> MomentumScore:
        """
        Calculate team's current momentum.

        Args:
            team: Team name
            recent_results: List of recent game results
            current_streak: Current win/loss streak
            days_since_last_game: Days of rest
            is_back_to_back: Playing back-to-back games

        Returns:
            MomentumScore with momentum metrics
        """
        # Calculate base momentum from recent results
        base_momentum = self._calculate_base_momentum(recent_results)

        # Streak bonus/penalty
        streak_impact = min(5, abs(current_streak)) * (1 if current_streak > 0 else -1)

        # Back-to-back penalty
        b2b_factor = -2.0 if is_back_to_back else 0

        # Rest factor
        rest_factor = self._calculate_rest_factor(days_since_last_game)

        # Total momentum
        total_momentum = base_momentum + streak_impact + b2b_factor + rest_factor

        # Determine form
        if total_momentum >= 4:
            form = 'hot'
        elif total_momentum <= -4:
            form = 'cold'
        else:
            form = 'neutral'

        # Last 5 record
        last_5 = recent_results[-5:] if len(recent_results) >= 5 else recent_results
        wins = sum(1 for game in last_5 if game.get('result') == 'W')
        losses = len(last_5) - wins
        last_5_record = f"{wins}-{losses}"

        # Trend
        if len(recent_results) >= 6:
            first_half = recent_results[:len(recent_results)//2]
            second_half = recent_results[len(recent_results)//2:]
            first_pct = sum(1 for g in first_half if g.get('result') == 'W') / len(first_half)
            second_pct = sum(1 for g in second_half if g.get('result') == 'W') / len(second_half)
            
            if second_pct > first_pct + 0.15:
                trend = 'improving'
            elif second_pct < first_pct - 0.15:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        return MomentumScore(
            team=team,
            momentum_rating=round(total_momentum, 1),
            recent_form=form,
            last_5_record=last_5_record,
            streak=f"{abs(current_streak)}W" if current_streak > 0 else f"{abs(current_streak)}L",
            back_to_back_factor=b2b_factor,
            rest_days=days_since_last_game,
            trend=trend
        )

    def _calculate_base_momentum(self, recent_results: List[Dict]) -> float:
        """Calculate base momentum from recent results."""
        if not recent_results:
            return 0

        momentum = 0
        weight = 1.0

        # Weight recent games more heavily
        for game in reversed(recent_results):
            if game.get('result') == 'W':
                momentum += weight * 1.5
            elif game.get('result') == 'L':
                momentum -= weight * 1.5

            # Blowout bonus/penalty
            margin = game.get('margin', 0)
            if abs(margin) >= 15:
                momentum += weight * 0.5 * (1 if margin > 0 else -1)

            weight *= (1 - self.momentum_decay)

        return momentum

    def _calculate_rest_factor(self, days_rest: int) -> float:
        """Calculate impact of rest days."""
        if days_rest >= 4:
            return 1.0  # Well rested
        elif days_rest <= 1:
            return -1.5  # Fatigued
        else:
            return 0


