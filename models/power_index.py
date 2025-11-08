"""
Power Index Rating System (Elo-like ratings for teams).

Tracks team strength over time with daily updates based on game results.
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os


@dataclass
class TeamRating:
    """Team rating information."""
    team_name: str
    sport: str
    rating: float
    offensive_rating: float
    defensive_rating: float
    games_played: int
    wins: int
    losses: int
    last_updated: str
    peak_rating: float
    lowest_rating: float
    rating_trend: str  # 'rising', 'falling', 'stable'
    rank: Optional[int] = None


@dataclass
class RatingHistory:
    """Historical rating data for a team."""
    team_name: str
    dates: List[str]
    ratings: List[float]
    offensive_ratings: List[float]
    defensive_ratings: List[float]


class PowerIndexRatings:
    """
    Elo-like power rating system for sports teams.

    Features:
    - Daily rating updates based on game results
    - Separate offensive and defensive ratings
    - Home field advantage adjustment
    - Margin of victory consideration
    - Rating trend detection
    - Historical tracking
    """

    def __init__(self, k_factor: float = 32.0, storage_path: str = './data/power_ratings.json'):
        """
        Initialize the power index rating system.

        Args:
            k_factor: Sensitivity to new results (higher = more volatile)
            storage_path: Path to store ratings data
        """
        self.k_factor = k_factor
        self.storage_path = storage_path
        self.ratings: Dict[str, Dict[str, TeamRating]] = {}  # sport -> team -> rating
        self.history: Dict[str, Dict[str, RatingHistory]] = {}  # sport -> team -> history

        # Sport-specific base ratings and parameters
        self.sport_configs = {
            'nfl': {'base_rating': 1500, 'home_advantage': 65, 'mov_multiplier': 1.0},
            'nba': {'base_rating': 1500, 'home_advantage': 100, 'mov_multiplier': 0.5},
            'mlb': {'base_rating': 1500, 'home_advantage': 30, 'mov_multiplier': 0.8},
            'nhl': {'base_rating': 1500, 'home_advantage': 50, 'mov_multiplier': 1.2},
            'mls': {'base_rating': 1500, 'home_advantage': 60, 'mov_multiplier': 1.5},
            'soccer': {'base_rating': 1500, 'home_advantage': 60, 'mov_multiplier': 1.5},
        }

        self._load_ratings()

    def initialize_team(
        self,
        team_name: str,
        sport: str,
        initial_rating: Optional[float] = None
    ) -> TeamRating:
        """
        Initialize a new team's rating.

        Args:
            team_name: Name of the team
            sport: Sport type
            initial_rating: Optional initial rating (defaults to base rating)

        Returns:
            TeamRating object
        """
        if sport not in self.ratings:
            self.ratings[sport] = {}
            self.history[sport] = {}

        config = self.sport_configs.get(sport, self.sport_configs['nfl'])
        base_rating = initial_rating or config['base_rating']

        team_rating = TeamRating(
            team_name=team_name,
            sport=sport,
            rating=base_rating,
            offensive_rating=100.0,  # Normalized to 100
            defensive_rating=100.0,
            games_played=0,
            wins=0,
            losses=0,
            last_updated=datetime.now().isoformat(),
            peak_rating=base_rating,
            lowest_rating=base_rating,
            rating_trend='stable'
        )

        self.ratings[sport][team_name] = team_rating

        # Initialize history
        self.history[sport][team_name] = RatingHistory(
            team_name=team_name,
            dates=[datetime.now().isoformat()],
            ratings=[base_rating],
            offensive_ratings=[100.0],
            defensive_ratings=[100.0]
        )

        return team_rating

    def update_ratings(
        self,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        sport: str,
        is_playoff: bool = False,
        importance_multiplier: float = 1.0
    ) -> Tuple[TeamRating, TeamRating]:
        """
        Update team ratings based on game result.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_score: Home team score
            away_score: Away team score
            sport: Sport type
            is_playoff: Whether this is a playoff game (higher weight)
            importance_multiplier: Additional importance factor

        Returns:
            Tuple of updated (home_rating, away_rating)
        """
        # Ensure teams are initialized
        if sport not in self.ratings or home_team not in self.ratings[sport]:
            self.initialize_team(home_team, sport)
        if away_team not in self.ratings[sport]:
            self.initialize_team(away_team, sport)

        home_rating_obj = self.ratings[sport][home_team]
        away_rating_obj = self.ratings[sport][away_team]

        config = self.sport_configs.get(sport, self.sport_configs['nfl'])

        # Get current ratings
        home_rating = home_rating_obj.rating
        away_rating = away_rating_obj.rating

        # Expected scores (with home advantage)
        home_expected = self._expected_score(
            home_rating + config['home_advantage'],
            away_rating
        )
        away_expected = 1 - home_expected

        # Actual result (1 for win, 0.5 for tie, 0 for loss)
        if home_score > away_score:
            home_actual = 1.0
            away_actual = 0.0
            home_rating_obj.wins += 1
            away_rating_obj.losses += 1
        elif away_score > home_score:
            home_actual = 0.0
            away_actual = 1.0
            away_rating_obj.wins += 1
            home_rating_obj.losses += 1
        else:
            home_actual = 0.5
            away_actual = 0.5

        # Margin of victory adjustment
        score_diff = abs(home_score - away_score)
        mov_factor = math.log(max(score_diff, 1) + 1) * config['mov_multiplier']

        # Calculate K-factor with adjustments
        k = self.k_factor * importance_multiplier
        if is_playoff:
            k *= 1.5

        # Update ratings
        home_change = k * mov_factor * (home_actual - home_expected)
        away_change = k * mov_factor * (away_actual - away_expected)

        home_rating_obj.rating += home_change
        away_rating_obj.rating += away_change

        # Update offensive/defensive ratings
        self._update_offensive_defensive_ratings(
            home_rating_obj, away_rating_obj,
            home_score, away_score, sport
        )

        # Update metadata
        home_rating_obj.games_played += 1
        away_rating_obj.games_played += 1
        home_rating_obj.last_updated = datetime.now().isoformat()
        away_rating_obj.last_updated = datetime.now().isoformat()

        # Update peaks
        home_rating_obj.peak_rating = max(home_rating_obj.peak_rating, home_rating_obj.rating)
        home_rating_obj.lowest_rating = min(home_rating_obj.lowest_rating, home_rating_obj.rating)
        away_rating_obj.peak_rating = max(away_rating_obj.peak_rating, away_rating_obj.rating)
        away_rating_obj.lowest_rating = min(away_rating_obj.lowest_rating, away_rating_obj.rating)

        # Update trends
        home_rating_obj.rating_trend = self._calculate_trend(home_team, sport)
        away_rating_obj.rating_trend = self._calculate_trend(away_team, sport)

        # Add to history
        self._add_to_history(home_team, sport, home_rating_obj)
        self._add_to_history(away_team, sport, away_rating_obj)

        # Save ratings
        self._save_ratings()

        return home_rating_obj, away_rating_obj

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score using Elo formula."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def _update_offensive_defensive_ratings(
        self,
        home_team: TeamRating,
        away_team: TeamRating,
        home_score: int,
        away_score: int,
        sport: str
    ):
        """Update offensive and defensive ratings based on scoring."""
        config = self.sport_configs.get(sport, self.sport_configs['nfl'])
        league_avg = config['base_rating'] / 15  # Rough league average points

        # Update offensive ratings (based on points scored)
        home_off_performance = (home_score / max(league_avg, 1)) * 100
        away_off_performance = (away_score / max(league_avg, 1)) * 100

        home_team.offensive_rating = (
            home_team.offensive_rating * 0.9 +
            home_off_performance * 0.1
        )
        away_team.offensive_rating = (
            away_team.offensive_rating * 0.9 +
            away_off_performance * 0.1
        )

        # Update defensive ratings (based on points allowed - lower is better)
        home_def_performance = max(50, 150 - (away_score / max(league_avg, 1)) * 100)
        away_def_performance = max(50, 150 - (home_score / max(league_avg, 1)) * 100)

        home_team.defensive_rating = (
            home_team.defensive_rating * 0.9 +
            home_def_performance * 0.1
        )
        away_team.defensive_rating = (
            away_team.defensive_rating * 0.9 +
            away_def_performance * 0.1
        )

    def _calculate_trend(self, team_name: str, sport: str) -> str:
        """Calculate rating trend for a team."""
        if sport not in self.history or team_name not in self.history[sport]:
            return 'stable'

        history = self.history[sport][team_name]
        if len(history.ratings) < 5:
            return 'stable'

        recent_ratings = history.ratings[-5:]
        first_half_avg = sum(recent_ratings[:3]) / 3
        second_half_avg = sum(recent_ratings[-3:]) / 3

        diff = second_half_avg - first_half_avg

        if diff > 20:
            return 'rising'
        elif diff < -20:
            return 'falling'
        else:
            return 'stable'

    def _add_to_history(self, team_name: str, sport: str, rating: TeamRating):
        """Add current rating to history."""
        if sport not in self.history:
            self.history[sport] = {}

        if team_name not in self.history[sport]:
            self.history[sport][team_name] = RatingHistory(
                team_name=team_name,
                dates=[],
                ratings=[],
                offensive_ratings=[],
                defensive_ratings=[]
            )

        history = self.history[sport][team_name]
        history.dates.append(datetime.now().isoformat())
        history.ratings.append(rating.rating)
        history.offensive_ratings.append(rating.offensive_rating)
        history.defensive_ratings.append(rating.defensive_rating)

        # Keep last 365 days only
        if len(history.dates) > 365:
            history.dates = history.dates[-365:]
            history.ratings = history.ratings[-365:]
            history.offensive_ratings = history.offensive_ratings[-365:]
            history.defensive_ratings = history.defensive_ratings[-365:]

    def get_team_rating(self, team_name: str, sport: str) -> Optional[TeamRating]:
        """Get current rating for a team."""
        return self.ratings.get(sport, {}).get(team_name)

    def get_rankings(self, sport: str, top_n: Optional[int] = None) -> List[TeamRating]:
        """
        Get ranked list of teams by rating.

        Args:
            sport: Sport type
            top_n: Optional limit to top N teams

        Returns:
            List of TeamRating objects sorted by rating
        """
        if sport not in self.ratings:
            return []

        ranked = sorted(
            self.ratings[sport].values(),
            key=lambda x: x.rating,
            reverse=True
        )

        # Add rank numbers
        for i, team in enumerate(ranked, 1):
            team.rank = i

        if top_n:
            return ranked[:top_n]
        return ranked

    def get_rating_history(self, team_name: str, sport: str) -> Optional[RatingHistory]:
        """Get rating history for a team."""
        return self.history.get(sport, {}).get(team_name)

    def predict_matchup(
        self,
        home_team: str,
        away_team: str,
        sport: str
    ) -> Dict:
        """
        Predict matchup outcome based on ratings.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type

        Returns:
            Dictionary with prediction details
        """
        home_rating = self.get_team_rating(home_team, sport)
        away_rating = self.get_team_rating(away_team, sport)

        if not home_rating or not away_rating:
            return {'error': 'One or both teams not found'}

        config = self.sport_configs.get(sport, self.sport_configs['nfl'])

        home_win_prob = self._expected_score(
            home_rating.rating + config['home_advantage'],
            away_rating.rating
        )
        away_win_prob = 1 - home_win_prob

        rating_diff = home_rating.rating - away_rating.rating + config['home_advantage']
        expected_spread = rating_diff / 25  # Rough conversion to point spread

        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_rating': home_rating.rating,
            'away_rating': away_rating.rating,
            'home_win_probability': round(home_win_prob * 100, 1),
            'away_win_probability': round(away_win_prob * 100, 1),
            'expected_spread': round(expected_spread, 1),
            'rating_advantage': round(rating_diff, 1),
            'home_offensive_rating': home_rating.offensive_rating,
            'away_offensive_rating': away_rating.offensive_rating,
            'home_defensive_rating': home_rating.defensive_rating,
            'away_defensive_rating': away_rating.defensive_rating,
        }

    def _save_ratings(self):
        """Save ratings to disk."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

            data = {
                'ratings': {
                    sport: {
                        team: asdict(rating)
                        for team, rating in teams.items()
                    }
                    for sport, teams in self.ratings.items()
                },
                'last_updated': datetime.now().isoformat()
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving ratings: {e}")

    def _load_ratings(self):
        """Load ratings from disk."""
        try:
            if not os.path.exists(self.storage_path):
                return

            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            ratings_data = data.get('ratings', {})
            for sport, teams in ratings_data.items():
                self.ratings[sport] = {}
                for team_name, rating_dict in teams.items():
                    self.ratings[sport][team_name] = TeamRating(**rating_dict)

        except Exception as e:
            print(f"Error loading ratings: {e}")

    def reset_sport_ratings(self, sport: str):
        """Reset all ratings for a sport (e.g., at season start)."""
        if sport in self.ratings:
            del self.ratings[sport]
        if sport in self.history:
            del self.history[sport]
        self._save_ratings()
