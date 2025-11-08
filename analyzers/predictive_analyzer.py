"""Predictive analyzer that integrates all modeling and simulation components."""
from typing import Dict, List, Optional
from datetime import datetime

# Import all modeling components
from models.power_rating import PowerRatingSystem
from models.spread_model import DynamicSpreadModel
from models.prop_model import PlayerPropModel
from simulations.monte_carlo import MonteCarloEngine
from simulations.season_projector import SeasonProjector
from simulations.playoff_simulator import PlayoffSimulator
from simulations.possession_simulator import PossessionSimulator
from predictors.upset_detector import UpsetProbabilityDetector
from predictors.injury_impact import InjuryReplacementSimulator
from predictors.regression_model import PlayerRegressionModel
from predictors.coaching_predictor import CoachingChangePredictor
from predictors.heat_surge_detector import HeatSurgeDetector
from utils.fatigue_model import FatigueDecayCurve
from utils.momentum_tracker import MomentumCarryoverTracker
from utils.travel_calculator import TravelPenaltyCalculator
from utils.chemistry_model import TeamChemistryModel
from validators.edge_tracker import BettingEdgeTracker
from validators.model_validator import HistoricalModelValidator


class PredictiveAnalyzer:
    """
    Unified interface for all predictive modeling and simulation features.

    Integrates Monte Carlo simulations, power ratings, spread models, player props,
    and all other predictive components into a single cohesive system.
    """

    def __init__(self):
        """Initialize all predictive components."""
        # Core models
        self.power_rating = PowerRatingSystem()
        self.monte_carlo = MonteCarloEngine(num_simulations=10000)
        self.spread_model = DynamicSpreadModel(power_rating_system=self.power_rating)
        self.prop_model = PlayerPropModel()

        # Simulation engines
        self.season_projector = SeasonProjector(
            monte_carlo_engine=self.monte_carlo
        )
        self.playoff_simulator = PlayoffSimulator(
            monte_carlo_engine=self.monte_carlo,
            power_rating_system=self.power_rating
        )
        self.possession_simulator = PossessionSimulator()

        # Predictors
        self.upset_detector = UpsetProbabilityDetector(
            monte_carlo_engine=self.monte_carlo,
            power_rating_system=self.power_rating
        )
        self.injury_simulator = InjuryReplacementSimulator()
        self.regression_model = PlayerRegressionModel()
        self.coaching_predictor = CoachingChangePredictor()
        self.heat_surge_detector = HeatSurgeDetector()

        # Utility models
        self.fatigue_model = FatigueDecayCurve()
        self.momentum_tracker = MomentumCarryoverTracker()
        self.travel_calculator = TravelPenaltyCalculator()
        self.chemistry_model = TeamChemistryModel()

        # Validators
        self.edge_tracker = BettingEdgeTracker()
        self.model_validator = HistoricalModelValidator()

    def generate_game_prediction(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        game_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive prediction for a game.

        Args:
            home_team: Home team name
            away_team: Away team name
            sport: Sport type
            game_context: Additional game context (injuries, rest, etc.)

        Returns:
            Dictionary with all predictions and analysis
        """
        context = game_context or {}

        # Get power ratings
        home_rating = self.power_rating.get_rating(home_team, sport)
        away_rating = self.power_rating.get_rating(away_team, sport)

        # Calculate contextual factors
        factors = self._calculate_game_factors(home_team, away_team, sport, context)

        # Run Monte Carlo simulation
        monte_carlo_result = self.monte_carlo.simulate_game(
            home_rating,
            away_rating,
            sport,
            **factors
        )

        # Calculate spread and total
        spread_analysis = self.spread_model.calculate_fair_spread(
            home_team, away_team, sport, **factors
        )

        total_analysis = self.spread_model.calculate_total(
            home_team, away_team, sport, **factors
        )

        # Check for upset potential
        upset_analysis = self.upset_detector.detect_upsets(
            [{'home_team': home_team, 'away_team': away_team, 'adjustments': factors}],
            sport
        )

        return {
            'home_team': home_team,
            'away_team': away_team,
            'sport': sport,
            'power_ratings': {
                'home': home_rating,
                'away': away_rating,
                'difference': home_rating - away_rating
            },
            'win_probability': {
                'home': round(monte_carlo_result.home_win_probability, 3),
                'away': round(monte_carlo_result.away_win_probability, 3)
            },
            'predicted_score': {
                'home': round(monte_carlo_result.expected_home_score, 1),
                'away': round(monte_carlo_result.expected_away_score, 1)
            },
            'spread': {
                'fair_line': spread_analysis['fair_spread'],
                'confidence': 'HIGH' if abs(spread_analysis['fair_spread']) > 7 else 'MODERATE'
            },
            'total': {
                'fair_line': total_analysis['fair_total'],
                'over_under': 'OVER' if total_analysis['fair_total'] > 220 else 'UNDER'
            },
            'upset_alert': upset_analysis[0] if upset_analysis else None,
            'contextual_factors': factors,
            'simulations_run': monte_carlo_result.simulations_run,
            'timestamp': datetime.now().isoformat()
        }

    def generate_player_prop_predictions(
        self,
        player_name: str,
        player_stats: List[Dict],
        opponent: str,
        sport: str,
        **context
    ) -> Dict:
        """
        Generate player prop predictions.

        Args:
            player_name: Player name
            player_stats: Historical player stats
            opponent: Opponent team
            sport: Sport type
            **context: Additional context

        Returns:
            Prop predictions
        """
        prop_types = ['points', 'rebounds', 'assists'] if sport == 'nba' else ['points']

        predictions = self.prop_model.predict_multi_prop(
            player_name,
            player_stats,
            prop_types,
            opponent,
            sport,
            **context
        )

        return predictions

    def generate_season_projections(
        self,
        sport: str,
        teams: List[str],
        team_ratings: Dict[str, float],
        remaining_schedule: List[Dict],
        current_records: Dict[str, Dict]
    ) -> Dict:
        """
        Generate season projections for all teams.

        Args:
            sport: Sport type
            teams: List of teams
            team_ratings: Current power ratings
            remaining_schedule: Remaining games
            current_records: Current records

        Returns:
            Season projections
        """
        projections = self.season_projector.project_season(
            sport,
            teams,
            team_ratings,
            remaining_schedule,
            current_records
        )

        # Add heat surge detection
        teams_data = [
            {
                'team_name': team,
                'actual_wins': current_records.get(team, {}).get('wins', 0),
                'expected_wins': projections[team]['projected_wins'],
                'last_10_wins': current_records.get(team, {}).get('last_10_wins', 5)
            }
            for team in teams
        ]

        heat_surges = self.heat_surge_detector.detect_heat_surges(teams_data, sport)

        return {
            'projections': projections,
            'heat_surges': heat_surges,
            'sport': sport,
            'timestamp': datetime.now().isoformat()
        }

    def identify_betting_edges(
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
        Identify betting value by comparing model to market.

        Args:
            game_id: Game identifier
            home_team: Home team
            away_team: Away team
            sport: Sport type
            market_spread: Market spread line
            market_total: Market total line
            **adjustments: Adjustment factors

        Returns:
            Betting edge analysis
        """
        edge_analysis = self.spread_model.compare_to_market(
            game_id,
            home_team,
            away_team,
            sport,
            market_spread,
            market_total,
            **adjustments
        )

        # Log edge if significant
        if edge_analysis.get('has_value'):
            if edge_analysis.get('spread_value_pick'):
                self.edge_tracker.log_betting_edge(
                    game_id,
                    'spread',
                    edge_analysis['spread_value_pick'],
                    edge_analysis['fair_spread'],
                    market_spread,
                    abs(edge_analysis['spread_edge']),
                    0.7,  # Confidence
                    sport
                )

            if edge_analysis.get('total_value_pick'):
                self.edge_tracker.log_betting_edge(
                    game_id,
                    'total',
                    edge_analysis['total_value_pick'],
                    edge_analysis['fair_total'],
                    market_total,
                    abs(edge_analysis['total_edge']),
                    0.7,
                    sport
                )

        return edge_analysis

    def get_comprehensive_insights(
        self,
        sport: str,
        games: List[Dict],
        team_data: Dict
    ) -> Dict:
        """
        Generate comprehensive insights for multiple games.

        Args:
            sport: Sport type
            games: List of upcoming games
            team_data: Team statistics and context

        Returns:
            Comprehensive predictive insights
        """
        insights = {
            'upset_alerts': [],
            'heat_surge_teams': [],
            'coaching_changes_watch': [],
            'bounce_back_candidates': [],
            'game_predictions': []
        }

        # Generate predictions for each game
        for game in games:
            prediction = self.generate_game_prediction(
                game['home_team'],
                game['away_team'],
                sport,
                game.get('context')
            )
            insights['game_predictions'].append(prediction)

        # Detect upsets across all games
        upset_alerts = self.upset_detector.detect_upsets(games, sport)
        insights['upset_alerts'] = upset_alerts

        # Detect heat surges
        if team_data:
            teams_list = [team_data[team] for team in team_data]
            heat_surges = self.heat_surge_detector.detect_heat_surges(teams_list, sport)
            insights['heat_surge_teams'] = heat_surges

        return insights

    def _calculate_game_factors(
        self,
        home_team: str,
        away_team: str,
        sport: str,
        context: Dict
    ) -> Dict:
        """Calculate all contextual factors for game simulation."""
        factors = {}

        # Rest/fatigue
        home_rest = context.get('home_days_rest', 2)
        away_rest = context.get('away_days_rest', 2)

        home_fatigue = self.fatigue_model.calculate_fatigue_impact(
            home_rest, sport,
            back_to_back=context.get('home_back_to_back', False)
        )
        away_fatigue = self.fatigue_model.calculate_fatigue_impact(
            away_rest, sport,
            back_to_back=context.get('away_back_to_back', False)
        )

        factors['home_fatigue'] = home_fatigue['performance_penalty_pct'] / 100
        factors['away_fatigue'] = away_fatigue['performance_penalty_pct'] / 100

        # Travel impact
        if context.get('away_team_travel_origin'):
            travel_impact = self.travel_calculator.calculate_travel_penalty(
                context['away_team_travel_origin'],
                context.get('game_city', home_team),
                sport
            )
            factors['travel_penalty'] = travel_impact['total_penalty']

        # Injuries
        factors['home_injuries'] = context.get('home_injury_impact', 0)
        factors['away_injuries'] = context.get('away_injury_impact', 0)

        # Momentum
        if context.get('home_recent_results'):
            home_momentum = self.momentum_tracker.calculate_momentum(
                context['home_recent_results'],
                sport
            )
            factors['home_momentum'] = home_momentum.get('momentum_score', 0) / 20

        if context.get('away_recent_results'):
            away_momentum = self.momentum_tracker.calculate_momentum(
                context['away_recent_results'],
                sport
            )
            factors['away_momentum'] = away_momentum.get('momentum_score', 0) / 20

        return factors
