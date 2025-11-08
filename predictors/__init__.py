"""Prediction engines for various scenarios."""

from .upset_detector import UpsetProbabilityDetector
from .injury_impact import InjuryReplacementSimulator
from .regression_model import PlayerRegressionModel
from .coaching_predictor import CoachingChangePredictor

__all__ = [
    'UpsetProbabilityDetector',
    'InjuryReplacementSimulator',
    'PlayerRegressionModel',
    'CoachingChangePredictor'
]
