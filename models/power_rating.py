"""Power index rating system (Elo-like) for team strength tracking."""
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import math


@dataclass
class TeamRating:
    """Team power rating at a point in time."""
    team_name: str
    rating: float
    games_played: int
    last_updated: str
    rating_history: List[Tuple[str, float]]  # (date, rating) pairs
    sport: str


class PowerRatingSystem:
    """
    Elo-like power rating system for tracking team strength over time.

    Updates ratings after each game and maintains historical ratings for analysis.
    Ratings are sport-specific and updated daily.
    """

    def __init__(
        self,
        k_factor: float = 32,
        base_rating: float = 1500,
        home_advantage: float = 100,
        margin_of_victory_multiplier: float = 1.0,
        storage_path: str = './data/power_ratings'
    ):
        """
        Initialize power rating system.

        Args:
            k_factor: Learning rate (higher = more volatile ratings)
            base_rating: Starting rating for new teams
            home_advantage: Rating points added for home field advantage
            margin_of_victory_multiplier: How much MOV affects rating change
            storage_path: Path to store rating data
        """
        self.k_factor = k_factor
        self.base_rating = base_rating
        self.home_advantage = home_advantage
        self.mov_multiplier = margin_of_victory_multiplier
        self.storage_path = storage_path

        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)

        # In-memory rating cache
        self.ratings: Dict[str, Dict[str, TeamRating]] = {}  # {sport: {team: rating}}

    def get_rating(self, team: str, sport: str) -> float:
        """
        Get current power rating for a team.

        Args:
            team: Team name
            sport: Sport type

        Returns:
            Current power rating (defaults to base rating for new teams)
        """
        if sport not in self.ratings:
            self._load_ratings(sport)

        if team not in self.ratings.get(sport, {}):
            return self.base_rating

        return self.ratings[sport][team].rating

    def get_team_rating_object(self, team: str, sport: str) -> TeamRating:
        """Get full TeamRating object for a team."""
        if sport not in self.ratings:
            self._load_ratings(sport)

        if team not in self.ratings.get(sport, {}):
            # Create new team rating
            return TeamRating(
                team_name=team,
                rating=self.base_rating,
                games_played=0,
                last_updated=datetime.now().isoformat(),
                rating_history=[],
                sport=sport
            )

        return self.ratings[sport][team]

    def update_ratings(
        self,
        home_team: str,
        away_team: str,
        home_score: float,
        away_score: float,
        sport: str,
        game_date: Optional[datetime] = None,
        playoff_game: bool = False
    ) -> Tuple[float, float]:
        """
        Update team ratings after a game.

        Args:
            home_team: Home team name
            away_team: Away team name
            home_score: Home team score
            away_score: Away team score
            sport: Sport type
            game_date: Date of game (defaults to now)
            playoff_game: Whether this is a playoff game (higher k-factor)

        Returns:
            Tuple of (home_rating_change, away_rating_change)
        """
        if game_date is None:
            game_date = datetime.now()

        if sport not in self.ratings:
            self._load_ratings(sport)
            if sport not in self.ratings:
                self.ratings[sport] = {}

        # Get current ratings
        home_rating_obj = self.get_team_rating_object(home_team, sport)
        away_rating_obj = self.get_team_rating_object(away_team, sport)

        home_rating = home_rating_obj.rating
        away_rating = away_rating_obj.rating

        # Calculate expected win probabilities
        home_expected = self._expected_score(home_rating + self.home_advantage, away_rating)
        away_expected = 1 - home_expected

        # Determine actual outcome
        if home_score > away_score:
            home_actual = 1.0
            away_actual = 0.0
        elif away_score > home_score:
            home_actual = 0.0
            away_actual = 1.0
        else:
            home_actual = 0.5
            away_actual = 0.5

        # Calculate margin of victory multiplier
        margin = abs(home_score - away_score)
        mov_factor = self._margin_multiplier(margin, sport)

        # Adjust k-factor for playoff games
        k = self.k_factor * 1.5 if playoff_game else self.k_factor

        # Calculate rating changes
        home_change = k * mov_factor * (home_actual - home_expected)
        away_change = k * mov_factor * (away_actual - away_expected)

        # Update ratings
        new_home_rating = home_rating + home_change
        new_away_rating = away_rating + away_change

        # Update rating objects
        home_rating_obj.rating = new_home_rating
        home_rating_obj.games_played += 1
        home_rating_obj.last_updated = game_date.isoformat()
        home_rating_obj.rating_history.append((game_date.isoformat(), new_home_rating))

        away_rating_obj.rating = new_away_rating
        away_rating_obj.games_played += 1
        away_rating_obj.last_updated = game_date.isoformat()
        away_rating_obj.rating_history.append((game_date.isoformat(), new_away_rating))

        # Store updated ratings
        self.ratings[sport][home_team] = home_rating_obj
        self.ratings[sport][away_team] = away_rating_obj

        # Persist to disk
        self._save_ratings(sport)

        return home_change, away_change

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected win probability for team A.

        Uses standard Elo formula: 1 / (1 + 10^((rating_b - rating_a) / 400))
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def _margin_multiplier(self, margin: float, sport: str) -> float:
        """
        Calculate margin of victory multiplier.

        Larger margins should have diminishing returns on rating changes.
        """
        # Sport-specific margin scaling
        if sport in ['nfl']:
            # NFL: 3-point margin = 1.0x, 14-point margin = 1.5x, 28+ = 2.0x
            return min(2.0, 1 + (margin / 28))
        elif sport in ['nba']:
            # NBA: 10-point margin = 1.0x, 20-point = 1.3x, 40+ = 2.0x
            return min(2.0, 1 + (margin / 40))
        elif sport in ['mlb']:
            # MLB: 3-run margin = 1.0x, 6-run = 1.5x, 12+ = 2.0x
            return min(2.0, 1 + (margin / 12))
        elif sport in ['nhl', 'mls', 'soccer']:
            # Hockey/Soccer: 1-goal margin = 1.0x, 3-goal = 1.5x, 5+ = 2.0x
            return min(2.0, 1 + (margin / 5))
        else:
            return 1.0 + (margin / 20)  # Generic formula

    def get_top_teams(self, sport: str, limit: int = 25) -> List[TeamRating]:
        """
        Get top-rated teams for a sport.

        Args:
            sport: Sport type
            limit: Number of teams to return

        Returns:
            List of TeamRating objects sorted by rating (highest first)
        """
        if sport not in self.ratings:
            self._load_ratings(sport)

        if sport not in self.ratings:
            return []

        sorted_teams = sorted(
            self.ratings[sport].values(),
            key=lambda x: x.rating,
            reverse=True
        )

        return sorted_teams[:limit]

    def get_ranking(self, team: str, sport: str) -> int:
        """
        Get team's ranking within sport.

        Args:
            team: Team name
            sport: Sport type

        Returns:
            Ranking (1-indexed), or -1 if team not found
        """
        top_teams = self.get_top_teams(sport, limit=1000)
        for i, team_rating in enumerate(top_teams, 1):
            if team_rating.team_name == team:
                return i
        return -1

    def predict_game(
        self,
        home_team: str,
        away_team: str,
        sport: str
    ) -> Dict:
        """
        Predict game outcome based on power ratings.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type

        Returns:
            Dictionary with predictions
        """
        home_rating = self.get_rating(home_team, sport)
        away_rating = self.get_rating(away_team, sport)

        # Calculate win probabilities
        home_win_prob = self._expected_score(
            home_rating + self.home_advantage,
            away_rating
        )
        away_win_prob = 1 - home_win_prob

        # Estimate point spread (rating difference translates to points)
        # Roughly 25 rating points = 1 point spread
        spread = (home_rating - away_rating + self.home_advantage) / 25

        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_rating': home_rating,
            'away_rating': away_rating,
            'home_win_probability': home_win_prob,
            'away_win_probability': away_win_prob,
            'predicted_spread': spread,
            'favorite': home_team if spread > 0 else away_team,
            'confidence': abs(home_win_prob - 0.5) * 2  # 0 to 1 scale
        }

    def _load_ratings(self, sport: str):
        """Load ratings from disk for a sport."""
        filepath = os.path.join(self.storage_path, f'{sport}_ratings.json')

        if not os.path.exists(filepath):
            self.ratings[sport] = {}
            return

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.ratings[sport] = {}
            for team_name, team_data in data.items():
                self.ratings[sport][team_name] = TeamRating(**team_data)

        except Exception as e:
            print(f"Error loading ratings for {sport}: {e}")
            self.ratings[sport] = {}

    def _save_ratings(self, sport: str):
        """Save ratings to disk for a sport."""
        if sport not in self.ratings:
            return

        filepath = os.path.join(self.storage_path, f'{sport}_ratings.json')

        try:
            data = {
                team: asdict(rating)
                for team, rating in self.ratings[sport].items()
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving ratings for {sport}: {e}")

    def decay_ratings(self, sport: str, days_since_last_game: int = 30):
        """
        Apply rating decay for teams that haven't played recently.

        Brings inactive team ratings closer to mean (regression to mean).
        """
        if sport not in self.ratings:
            self._load_ratings(sport)

        if sport not in self.ratings:
            return

        current_time = datetime.now()
        mean_rating = self.base_rating

        for team, rating_obj in self.ratings[sport].items():
            last_update = datetime.fromisoformat(rating_obj.last_updated)
            days_inactive = (current_time - last_update).days

            if days_inactive >= days_since_last_game:
                # Apply decay toward mean
                decay_factor = min(0.1, days_inactive / 365)  # Max 10% decay per year
                rating_obj.rating = (
                    rating_obj.rating * (1 - decay_factor) +
                    mean_rating * decay_factor
                )
                rating_obj.last_updated = current_time.isoformat()

        self._save_ratings(sport)

    def get_rating_trend(self, team: str, sport: str, days: int = 30) -> List[Tuple[str, float]]:
        """
        Get rating trend for a team over specified days.

        Args:
            team: Team name
            sport: Sport type
            days: Number of days to look back

        Returns:
            List of (date, rating) tuples
        """
        rating_obj = self.get_team_rating_object(team, sport)
        cutoff_date = datetime.now() - timedelta(days=days)

        trend = [
            (date_str, rating)
            for date_str, rating in rating_obj.rating_history
            if datetime.fromisoformat(date_str) >= cutoff_date
        ]

        return trend
