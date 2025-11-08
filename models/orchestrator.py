"""
Model Orchestrator.

Coordinates all modeling, forecasting, and simulation components.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from .monte_carlo_engine import MonteCarloSimulator, GameSimulationInput
from .power_index import PowerIndexRatings
from .season_projector import SeasonProjector
from .upset_detector import UpsetDetector
from .spread_model import DynamicSpreadModel
from .player_props import PlayerPropModel
from .injury_simulator import InjuryReplacementSimulator
from .chemistry_model import TeamChemistryModel
from .possession_simulator import PossessionSimulator
from .momentum_tracker import MomentumTracker
from .fatigue_model import FatigueDecayModel
from .betting_edge import BettingEdgeTracker
from .probability_graphs import ProbabilityGraphGenerator
from .live_predictor import LiveGamePredictor
from .model_validator import ModelValidator
from .heat_surge import HeatSurgeDetector
from .coaching_predictor import CoachingChangePredictor
from .player_regression import PlayerRegressionModel
from .playoff_simulator import PlayoffBracketSimulator
from .travel_penalty import TravelPenaltyCalculator


@dataclass
class ComprehensiveAnalysis:
    """Complete analysis for a game or slate."""
    monte_carlo_results: Optional[Any] = None
    spread_predictions: Optional[Any] = None
    upset_alerts: Optional[List] = None
    season_projections: Optional[Any] = None
    player_props: Optional[List] = None
    momentum_scores: Optional[Dict] = None
    fatigue_assessments: Optional[Dict] = None
    travel_impacts: Optional[Dict] = None
    betting_edges: Optional[List] = None
    heat_surge_alerts: Optional[List] = None
    coaching_changes: Optional[List] = None
    playoff_odds: Optional[Any] = None
    timestamp: str = None


class ModelOrchestrator:
    """
    Orchestrates all predictive models and simulations.

    This is the main interface for accessing all modeling capabilities.
    """

    def __init__(self):
        """Initialize all models."""
        self.monte_carlo = MonteCarloSimulator(num_simulations=10000)
        self.power_index = PowerIndexRatings()
        self.season_projector = SeasonProjector()
        self.upset_detector = UpsetDetector()
        self.spread_model = DynamicSpreadModel()
        self.player_props = PlayerPropModel()
        self.injury_simulator = InjuryReplacementSimulator()
        self.chemistry_model = TeamChemistryModel()
        self.possession_simulator = PossessionSimulator()
        self.momentum_tracker = MomentumTracker()
        self.fatigue_model = FatigueDecayModel()
        self.betting_edge = BettingEdgeTracker()
        self.probability_graphs = ProbabilityGraphGenerator()
        self.live_predictor = LiveGamePredictor()
        self.model_validator = ModelValidator()
        self.heat_surge = HeatSurgeDetector()
        self.coaching_predictor = CoachingChangePredictor()
        self.player_regression = PlayerRegressionModel()
        self.playoff_simulator = PlayoffBracketSimulator()
        self.travel_penalty = TravelPenaltyCalculator()

    def analyze_game(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        game_data: Optional[Dict] = None
    ) -> ComprehensiveAnalysis:
        """
        Run comprehensive analysis for a single game.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            game_data: Optional additional game data

        Returns:
            ComprehensiveAnalysis with all predictions
        """
        game_data = game_data or {}

        # Get power ratings
        home_rating_obj = self.power_index.get_team_rating(home_team, sport)
        away_rating_obj = self.power_index.get_team_rating(away_team, sport)

        # Initialize teams if not found
        if not home_rating_obj:
            home_rating_obj = self.power_index.initialize_team(home_team, sport)
        if not away_rating_obj:
            away_rating_obj = self.power_index.initialize_team(away_team, sport)

        # Monte Carlo simulation
        sim_input = GameSimulationInput(
            home_team=home_team,
            away_team=away_team,
            home_power_rating=home_rating_obj.rating,
            away_power_rating=away_rating_obj.rating,
            home_offensive_rating=home_rating_obj.offensive_rating,
            away_offensive_rating=away_rating_obj.offensive_rating,
            home_defensive_rating=home_rating_obj.defensive_rating,
            away_defensive_rating=away_rating_obj.defensive_rating,
            sport=sport
        )
        mc_result = self.monte_carlo.simulate_game(sim_input)

        # Spread prediction
        spread_pred = self.spread_model.calculate_spread(
            home_team=home_team,
            away_team=away_team,
            home_rating=home_rating_obj.rating,
            away_rating=away_rating_obj.rating,
            home_offensive=home_rating_obj.offensive_rating,
            away_offensive=away_rating_obj.offensive_rating,
            home_defensive=home_rating_obj.defensive_rating,
            away_defensive=away_rating_obj.defensive_rating,
            sport=sport
        )

        # Upset detection
        upset_alert = self.upset_detector.detect_upset(
            home_team=home_team,
            away_team=away_team,
            home_rating=home_rating_obj.rating,
            away_rating=away_rating_obj.rating
        )

        # Momentum tracking
        momentum_home = self.momentum_tracker.calculate_momentum(
            team=home_team,
            recent_results=game_data.get('home_recent_results', []),
            current_streak=game_data.get('home_streak', 0),
            days_since_last_game=game_data.get('home_rest_days', 3)
        )

        momentum_away = self.momentum_tracker.calculate_momentum(
            team=away_team,
            recent_results=game_data.get('away_recent_results', []),
            current_streak=game_data.get('away_streak', 0),
            days_since_last_game=game_data.get('away_rest_days', 3)
        )

        # Fatigue assessment
        fatigue_home = self.fatigue_model.assess_fatigue(
            team=home_team,
            games_last_7_days=game_data.get('home_games_last_week', 2),
            days_since_last_game=game_data.get('home_rest_days', 3),
            travel_miles_last_week=game_data.get('home_travel_miles', 0)
        )

        fatigue_away = self.fatigue_model.assess_fatigue(
            team=away_team,
            games_last_7_days=game_data.get('away_games_last_week', 2),
            days_since_last_game=game_data.get('away_rest_days', 3),
            travel_miles_last_week=game_data.get('away_travel_miles', 0)
        )

        return ComprehensiveAnalysis(
            monte_carlo_results=mc_result,
            spread_predictions=spread_pred,
            upset_alerts=[upset_alert] if upset_alert else [],
            momentum_scores={
                home_team: momentum_home,
                away_team: momentum_away
            },
            fatigue_assessments={
                home_team: fatigue_home,
                away_team: fatigue_away
            },
            timestamp=datetime.now().isoformat()
        )

    def analyze_slate(
        self,
        games: List[Dict],
        sport: str
    ) -> ComprehensiveAnalysis:
        """
        Analyze an entire slate of games.

        Args:
            games: List of game dictionaries
            sport: Sport type

        Returns:
            ComprehensiveAnalysis for the slate
        """
        all_upsets = []
        all_spreads = []
        all_mc_results = []

        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')

            if not home_team or not away_team:
                continue

            analysis = self.analyze_game(home_team, away_team, sport, game)

            if analysis.monte_carlo_results:
                all_mc_results.append(analysis.monte_carlo_results)

            if analysis.spread_predictions:
                all_spreads.append(analysis.spread_predictions)

            if analysis.upset_alerts:
                all_upsets.extend(analysis.upset_alerts)

        # Sort upsets by upset score
        all_upsets.sort(key=lambda x: x.upset_score, reverse=True)

        return ComprehensiveAnalysis(
            monte_carlo_results=all_mc_results,
            spread_predictions=all_spreads,
            upset_alerts=all_upsets[:10],  # Top 10 upsets
            timestamp=datetime.now().isoformat()
        )

    def update_ratings_from_results(
        self,
        results: List[Dict],
        sport: str
    ):
        """
        Update power ratings based on game results.

        Args:
            results: List of game results
            sport: Sport type
        """
        for result in results:
            home_team = result.get('home_team')
            away_team = result.get('away_team')
            home_score = result.get('home_score')
            away_score = result.get('away_score')

            if all([home_team, away_team, home_score is not None, away_score is not None]):
                self.power_index.update_ratings(
                    home_team=home_team,
                    away_team=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    sport=sport
                )

    def get_team_report(
        self,
        team: str,
        sport: str
    ) -> Dict:
        """
        Get comprehensive report for a single team.

        Args:
            team: Team name
            sport: Sport type

        Returns:
            Dictionary with team analysis
        """
        rating = self.power_index.get_team_rating(team, sport)

        if not rating:
            return {'error': f'Team {team} not found'}

        # Get rating history
        history = self.power_index.get_rating_history(team, sport)

        return {
            'team': team,
            'sport': sport,
            'current_rating': rating.rating,
            'rank': rating.rank,
            'record': f"{rating.wins}-{rating.losses}",
            'offensive_rating': rating.offensive_rating,
            'defensive_rating': rating.defensive_rating,
            'trend': rating.rating_trend,
            'peak_rating': rating.peak_rating,
            'rating_history': history
        }

    def get_power_rankings(
        self,
        sport: str,
        top_n: int = 25
    ) -> List:
        """Get power rankings for a sport."""
        rankings = self.power_index.get_rankings(sport, top_n)
        return rankings

    def simulate_season_outlook(
        self,
        sport: str,
        teams_data: Dict
    ):
        """
        Generate season outlook for all teams.

        Args:
            sport: Sport type
            teams_data: Dictionary of team data

        Returns:
            Season outlook with projections
        """
        return self.season_projector.project_full_season(sport, teams_data)

    def simulate_playoffs(
        self,
        sport: str,
        seeds: Dict[int, str],
        team_ratings: Dict[str, float]
    ):
        """
        Simulate playoff bracket.

        Args:
            sport: Sport type
            seeds: Current playoff seeding
            team_ratings: Team power ratings

        Returns:
            Playoff projection with championship odds
        """
        return self.playoff_simulator.simulate_playoffs(
            sport=sport,
            seeds=seeds,
            team_ratings=team_ratings
        )

    def get_betting_summary(self) -> Dict:
        """Get betting edge tracking summary."""
        summary = self.betting_edge.get_summary()
        return asdict(summary)

    def export_analysis(
        self,
        analysis: ComprehensiveAnalysis,
        filepath: str
    ):
        """
        Export analysis to JSON file.

        Args:
            analysis: ComprehensiveAnalysis object
            filepath: Output file path
        """
        try:
            # Convert to dict (handling dataclasses)
            data = asdict(analysis) if hasattr(analysis, '__dataclass_fields__') else analysis

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            print(f"Analysis exported to {filepath}")

        except Exception as e:
            print(f"Error exporting analysis: {e}")

    def generate_daily_report(
        self,
        sport: str,
        games_today: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive daily report.

        Args:
            sport: Sport type
            games_today: Today's games

        Returns:
            Dictionary with daily analysis
        """
        # Analyze slate
        slate_analysis = self.analyze_slate(games_today, sport)

        # Get top power rankings
        rankings = self.get_power_rankings(sport, top_n=10)

        # Detect heat surge teams
        heat_alerts = []
        for team_rating in rankings[:20]:
            # Check for teams outperforming
            expected_rating = 1500  # League average
            actual_rating = team_rating.rating

            if actual_rating > expected_rating * 1.1:
                alert = self.heat_surge.detect_surge(
                    team=team_rating.team_name,
                    sport=sport,
                    expected_metrics={'rating': expected_rating},
                    actual_metrics={'rating': actual_rating}
                )
                if alert:
                    heat_alerts.append(alert)

        return {
            'date': datetime.now().isoformat(),
            'sport': sport,
            'games_analyzed': len(games_today),
            'slate_analysis': slate_analysis,
            'power_rankings': rankings,
            'heat_surge_alerts': heat_alerts,
            'top_upsets': slate_analysis.upset_alerts[:5] if slate_analysis.upset_alerts else []
        }
