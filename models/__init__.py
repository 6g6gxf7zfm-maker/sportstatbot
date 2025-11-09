"""
Advanced Sports Analytics Models

This package contains 25 sophisticated analytical models for sports analysis:
1. Opponent strength weighting
2. Rolling form index
3. Spatial pressure-map regression
4. Cross-league skill transfer
5. Bayesian team power scores
6. Expected penalty value
7. Fatigue-adjusted pace
8. Injury-impact elasticity
9. Home-field variance decomposition
10. Referee decision entropy
11. Weather-normalized shot quality
12. Dynamic luck index
13. Lineup optimization
14. Opponent style clustering
15. Rest differential predictor
16. Possession value network
17. Tactical similarity scoring
18. Expected tempo estimator
19. Regression to mean detector
20. Travel-fatigue penalty
21. Substitution impact regression
22. Clutch index
23. Game volatility index
24. Multi-metric composite ranking
25. Adaptive win-prob calibration
"""

from .strength_models import OpponentStrengthWeighting, BayesianTeamPowerScores
from .form_models import RollingFormIndex, RegressionToMeanDetector
from .spatial_models import SpatialPressureMapRegression, TacticalSimilarityScoring
from .transfer_models import CrossLeagueSkillTransfer
from .penalty_models import ExpectedPenaltyValue
from .fatigue_models import FatigueAdjustedPace, RestDifferentialPredictor, TravelFatiguePenalty
from .injury_models import InjuryImpactElasticity
from .venue_models import HomeFieldVarianceDecomposition, WeatherNormalizedShotQuality
from .referee_models import RefereeDecisionEntropy
from .luck_models import DynamicLuckIndex
from .optimization_models import LineupOptimization
from .clustering_models import OpponentStyleClustering
from .possession_models import PossessionValueNetwork
from .tempo_models import ExpectedTempoEstimator
from .substitution_models import SubstitutionImpactRegression
from .clutch_models import ClutchIndex
from .volatility_models import GameVolatilityIndex
from .ranking_models import MultiMetricCompositeRanking
from .calibration_models import AdaptiveWinProbCalibration

__all__ = [
    'OpponentStrengthWeighting',
    'RollingFormIndex',
    'SpatialPressureMapRegression',
    'CrossLeagueSkillTransfer',
    'BayesianTeamPowerScores',
    'ExpectedPenaltyValue',
    'FatigueAdjustedPace',
    'InjuryImpactElasticity',
    'HomeFieldVarianceDecomposition',
    'RefereeDecisionEntropy',
    'WeatherNormalizedShotQuality',
    'DynamicLuckIndex',
    'LineupOptimization',
    'OpponentStyleClustering',
    'RestDifferentialPredictor',
    'PossessionValueNetwork',
    'TacticalSimilarityScoring',
    'ExpectedTempoEstimator',
    'RegressionToMeanDetector',
    'TravelFatiguePenalty',
    'SubstitutionImpactRegression',
    'ClutchIndex',
    'GameVolatilityIndex',
    'MultiMetricCompositeRanking',
    'AdaptiveWinProbCalibration',
]
