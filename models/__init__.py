"""
Modeling, Forecasting & Simulation Module for SportStatBot.

This module provides comprehensive predictive analytics including:
- Monte Carlo simulations
- Power index ratings (Elo-based)
- Season projections
- Upset probability detection
- Dynamic spread models
- Player prop predictions
- And much more...
"""

from .monte_carlo_engine import MonteCarloSimulator
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

__all__ = [
    'MonteCarloSimulator',
    'PowerIndexRatings',
    'SeasonProjector',
    'UpsetDetector',
    'DynamicSpreadModel',
    'PlayerPropModel',
    'InjuryReplacementSimulator',
    'TeamChemistryModel',
    'PossessionSimulator',
    'MomentumTracker',
    'FatigueDecayModel',
    'BettingEdgeTracker',
    'ProbabilityGraphGenerator',
    'LiveGamePredictor',
    'ModelValidator',
    'HeatSurgeDetector',
    'CoachingChangePredictor',
    'PlayerRegressionModel',
    'PlayoffBracketSimulator',
    'TravelPenaltyCalculator',
]
