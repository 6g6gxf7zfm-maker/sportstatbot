"""
Upset Probability Detector.

Identifies potential upset games and calculates upset likelihood.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UpsetAlert:
    """Alert for potential upset game."""
    home_team: str
    away_team: str
    favorite: str
    underdog: str
    favorite_rating: float
    underdog_rating: float
    rating_difference: float
    upset_probability: float
    upset_score: float  # 0-100 scale
    key_factors: List[str]
    confidence: str  # 'low', 'medium', 'high'
    game_date: Optional[str] = None
    spread: Optional[float] = None


class UpsetDetector:
    """
    Detects potential upset games based on multiple factors.

    Factors considered:
    - Rating/ranking differences
    - Recent momentum trends
    - Home/away performance splits
    - Injury impacts
    - Historical head-to-head
    - Situational factors (trap games, look-ahead spots)
    """

    def __init__(self):
        """Initialize upset detector."""
        # Thresholds for upset detection
        self.min_rating_difference = 100  # Minimum rating gap to consider upset
        self.high_upset_probability = 0.35  # 35%+ upset odds
        self.medium_upset_probability = 0.25  # 25-35% upset odds

    def detect_upset(
        self,
        home_team: str,
        away_team: str,
        home_rating: float,
        away_rating: float,
        home_form: Optional[Dict] = None,
        away_form: Optional[Dict] = None,
        injuries: Optional[Dict] = None,
        situational_factors: Optional[Dict] = None,
        game_date: Optional[str] = None,
        spread: Optional[float] = None
    ) -> Optional[UpsetAlert]:
        """
        Detect if game has upset potential.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_rating: Home team power rating
            away_rating: Away team power rating
            home_form: Recent form data for home team
            away_form: Recent form data for away team
            injuries: Injury impact data
            situational_factors: Other situational data
            game_date: Game date
            spread: Betting line spread

        Returns:
            UpsetAlert if upset potential detected, None otherwise
        """
        # Determine favorite and underdog
        if home_rating > away_rating:
            favorite = home_team
            underdog = away_team
            favorite_rating = home_rating
            underdog_rating = away_rating
            is_home_favorite = True
        else:
            favorite = away_team
            underdog = home_team
            favorite_rating = away_rating
            underdog_rating = home_rating
            is_home_favorite = False

        rating_diff = abs(favorite_rating - underdog_rating)

        # Only consider if there's a meaningful rating gap
        if rating_diff < self.min_rating_difference:
            return None

        # Calculate base upset probability
        upset_prob = self._calculate_base_upset_probability(
            favorite_rating, underdog_rating, is_home_favorite
        )

        # Adjust for various factors
        key_factors = []
        adjustments = 0.0

        # Recent form adjustment
        if home_form and away_form:
            form_adjustment = self._analyze_form_factor(
                home_form, away_form, is_home_favorite
            )
            if form_adjustment != 0:
                adjustments += form_adjustment
                if form_adjustment > 0:
                    key_factors.append(
                        f"{underdog} has strong recent form (+{form_adjustment:.1%})"
                    )

        # Injury impact
        if injuries:
            injury_adjustment = self._analyze_injury_impact(
                injuries, is_home_favorite
            )
            if injury_adjustment != 0:
                adjustments += injury_adjustment
                if injury_adjustment > 0:
                    key_factors.append(
                        f"{favorite} dealing with key injuries (+{injury_adjustment:.1%})"
                    )

        # Situational factors
        if situational_factors:
            situational_adjustment = self._analyze_situational_factors(
                situational_factors, is_home_favorite
            )
            if situational_adjustment != 0:
                adjustments += situational_adjustment
                key_factors.extend(situational_factors.get('factors', []))

        # Final upset probability
        final_upset_prob = min(0.49, upset_prob + adjustments)

        # Calculate upset score (0-100)
        upset_score = self._calculate_upset_score(
            rating_diff, final_upset_prob, len(key_factors)
        )

        # Determine confidence level
        confidence = self._determine_confidence(final_upset_prob, len(key_factors))

        # Only return if upset probability is meaningful
        if final_upset_prob < 0.20:  # Less than 20% upset odds
            return None

        return UpsetAlert(
            home_team=home_team,
            away_team=away_team,
            favorite=favorite,
            underdog=underdog,
            favorite_rating=favorite_rating,
            underdog_rating=underdog_rating,
            rating_difference=rating_diff,
            upset_probability=round(final_upset_prob * 100, 1),
            upset_score=upset_score,
            key_factors=key_factors,
            confidence=confidence,
            game_date=game_date,
            spread=spread
        )

    def detect_upsets_in_slate(
        self,
        games: List[Dict],
        team_ratings: Dict[str, float],
        additional_data: Optional[Dict] = None
    ) -> List[UpsetAlert]:
        """
        Detect all potential upsets in a slate of games.

        Args:
            games: List of game dictionaries with home/away team info
            team_ratings: Dictionary of team -> rating
            additional_data: Additional contextual data

        Returns:
            List of UpsetAlert objects sorted by upset score
        """
        upset_alerts = []

        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')

            if not home_team or not away_team:
                continue

            home_rating = team_ratings.get(home_team, 1500)
            away_rating = team_ratings.get(away_team, 1500)

            # Get additional data if available
            home_form = additional_data.get('form', {}).get(home_team) if additional_data else None
            away_form = additional_data.get('form', {}).get(away_team) if additional_data else None
            injuries = additional_data.get('injuries', {}).get(f"{home_team}_vs_{away_team}") if additional_data else None
            situational = additional_data.get('situational', {}).get(f"{home_team}_vs_{away_team}") if additional_data else None

            alert = self.detect_upset(
                home_team=home_team,
                away_team=away_team,
                home_rating=home_rating,
                away_rating=away_rating,
                home_form=home_form,
                away_form=away_form,
                injuries=injuries,
                situational_factors=situational,
                game_date=game.get('date'),
                spread=game.get('spread')
            )

            if alert:
                upset_alerts.append(alert)

        # Sort by upset score (highest first)
        upset_alerts.sort(key=lambda x: x.upset_score, reverse=True)

        return upset_alerts

    def _calculate_base_upset_probability(
        self,
        favorite_rating: float,
        underdog_rating: float,
        is_home_favorite: bool
    ) -> float:
        """Calculate base upset probability from ratings."""
        home_advantage = 50  # Rating points

        if is_home_favorite:
            adjusted_favorite = favorite_rating + home_advantage
            adjusted_underdog = underdog_rating
        else:
            adjusted_favorite = favorite_rating
            adjusted_underdog = underdog_rating + home_advantage

        # Elo-style probability
        rating_diff = adjusted_favorite - adjusted_underdog
        favorite_win_prob = 1 / (1 + 10 ** (-rating_diff / 400))
        upset_prob = 1 - favorite_win_prob

        return upset_prob

    def _analyze_form_factor(
        self,
        home_form: Dict,
        away_form: Dict,
        is_home_favorite: bool
    ) -> float:
        """Analyze recent form impact on upset odds."""
        # Form includes last N games performance
        home_recent = home_form.get('last_5_win_pct', 0.5)
        away_recent = away_form.get('last_5_win_pct', 0.5)

        # If underdog has better recent form, increase upset odds
        if is_home_favorite:
            form_diff = away_recent - home_recent
        else:
            form_diff = home_recent - away_recent

        # Convert to probability adjustment
        # Strong form divergence can add up to 10% to upset odds
        adjustment = form_diff * 0.10

        return max(-0.05, min(0.15, adjustment))

    def _analyze_injury_impact(
        self,
        injuries: Dict,
        is_home_favorite: bool
    ) -> float:
        """Analyze injury impact on upset odds."""
        home_injury_impact = injuries.get('home_impact', 0)
        away_injury_impact = injuries.get('away_impact', 0)

        # If favorite has more injuries, increase upset odds
        if is_home_favorite:
            injury_diff = home_injury_impact - away_injury_impact
        else:
            injury_diff = away_injury_impact - home_injury_impact

        # Major injuries to favorite can add up to 12% to upset odds
        adjustment = injury_diff * 0.08

        return max(0, min(0.15, adjustment))

    def _analyze_situational_factors(
        self,
        situational: Dict,
        is_home_favorite: bool
    ) -> float:
        """Analyze situational factors."""
        adjustment = 0.0

        # Look-ahead spot (favorite has big game next week)
        if situational.get('favorite_look_ahead'):
            adjustment += 0.05

        # Trap game (underdog desperate for win)
        if situational.get('underdog_desperate'):
            adjustment += 0.04

        # Back-to-back or schedule fatigue for favorite
        if situational.get('favorite_fatigued'):
            adjustment += 0.06

        # Revenge game for underdog
        if situational.get('revenge_game'):
            adjustment += 0.03

        return adjustment

    def _calculate_upset_score(
        self,
        rating_diff: float,
        upset_probability: float,
        num_factors: int
    ) -> float:
        """
        Calculate upset score (0-100 scale).

        Higher score = more compelling upset alert
        """
        # Base score from upset probability
        base_score = upset_probability * 100

        # Bonus for bigger rating gaps (bigger upset if it happens)
        rating_bonus = min(20, (rating_diff - 100) / 20)

        # Bonus for more supporting factors
        factor_bonus = min(15, num_factors * 3)

        total_score = base_score + rating_bonus + factor_bonus

        return min(100, max(0, total_score))

    def _determine_confidence(
        self,
        upset_probability: float,
        num_factors: int
    ) -> str:
        """Determine confidence level in upset prediction."""
        if upset_probability >= self.high_upset_probability and num_factors >= 3:
            return 'high'
        elif upset_probability >= self.medium_upset_probability or num_factors >= 2:
            return 'medium'
        else:
            return 'low'

    def get_historical_upset_rate(
        self,
        rating_difference: float,
        sport: str
    ) -> float:
        """
        Get historical upset rate for given rating difference.

        Args:
            rating_difference: Rating gap between teams
            sport: Sport type

        Returns:
            Historical upset percentage
        """
        # Rough historical upset rates by rating gap
        # These would ideally come from actual historical data
        upset_rates = {
            100: 0.40,   # Small gap: ~40% upset rate
            150: 0.30,   # Medium gap: ~30% upset rate
            200: 0.22,   # Large gap: ~22% upset rate
            250: 0.15,   # Very large: ~15% upset rate
            300: 0.10,   # Huge gap: ~10% upset rate
        }

        # Find closest rating difference
        for gap, rate in sorted(upset_rates.items()):
            if rating_difference <= gap:
                return rate * 100

        return 5.0  # 5% for massive gaps
