# Advanced Sports Analytics Models

This directory contains 25 sophisticated analytical models for comprehensive sports analysis. These models provide cutting-edge analytics capabilities for the SportStatBot platform.

## Model Categories

### 1. Strength & Power Models
- **OpponentStrengthWeighting** (`strength_models.py`)
  - Adaptive opponent-strength weighting per possession
  - Adjusts performance metrics based on opponent quality
  - Usage: Calculate strength-adjusted statistics

- **BayesianTeamPowerScores** (`strength_models.py`)
  - Bayesian updating of team power scores after each game
  - Continuous rating updates with confidence intervals
  - Usage: Team power rankings with uncertainty quantification

### 2. Form & Momentum Models
- **RollingFormIndex** (`form_models.py`)
  - Blends short-term streaks with long-term baseline
  - Identifies hot/cold teams with momentum indicators
  - Usage: Form-based predictions and betting insights

- **RegressionToMeanDetector** (`form_models.py`)
  - Identifies unsustainable performance with confidence weighting
  - Predicts performance regression to true talent level
  - Usage: Identify buy-low/sell-high opportunities

### 3. Spatial & Tactical Models
- **SpatialPressureMapRegression** (`spatial_models.py`)
  - Defensive coverage heat maps
  - Predicts success probability by field location
  - Usage: Tactical analysis and play calling optimization

- **TacticalSimilarityScoring** (`spatial_models.py`)
  - Quantifies playing style similarity between teams
  - Identifies tactical archetypes and matchup dynamics
  - Usage: Matchup analysis and scouting reports

### 4. Transfer & League Models
- **CrossLeagueSkillTransfer** (`transfer_models.py`)
  - Estimates performance translation across leagues
  - Risk assessment for player transfers
  - Usage: Player acquisition analysis

### 5. Penalty & Special Situations
- **ExpectedPenaltyValue** (`penalty_models.py`)
  - Expected value models for penalties, power plays, field goals
  - Context-adjusted conversion rates
  - Usage: Special teams analysis and game situations

### 6. Fatigue & Rest Models
- **FatigueAdjustedPace** (`fatigue_models.py`)
  - Pace adjustments for back-to-back games
  - Accounts for overtime and travel
  - Usage: Betting edges on schedule spots

- **RestDifferentialPredictor** (`fatigue_models.py`)
  - Win probability shifts from rest advantages
  - Impact on point spreads
  - Usage: Line shopping and situational betting

- **TravelFatiguePenalty** (`fatigue_models.py`)
  - Performance penalties per time zone crossed
  - Circadian rhythm impact analysis
  - Usage: Road game adjustments

### 7. Injury Impact Models
- **InjuryImpactElasticity** (`injury_models.py`)
  - Points lost per absence day with elasticity curves
  - Replacement value estimation
  - Recovery trajectory prediction
  - Usage: Injury impact quantification

### 8. Venue & Environmental Models
- **HomeFieldVarianceDecomposition** (`venue_models.py`)
  - Separates altitude, crowd, travel, familiarity effects
  - Venue-specific advantage breakdown
  - Usage: Detailed home-field advantage analysis

- **WeatherNormalizedShotQuality** (`venue_models.py`)
  - Adjusts performance for weather conditions
  - Temperature, wind, precipitation impacts
  - Usage: Outdoor game adjustments

### 9. Referee Analysis
- **RefereeDecisionEntropy** (`referee_models.py`)
  - Measures referee consistency using information entropy
  - Home bias detection and penalty predictions
  - Usage: Referee-adjusted predictions

### 10. Luck & Variance Models
- **DynamicLuckIndex** (`luck_models.py`)
  - Expected vs actual scoring differential
  - Identifies lucky/unlucky teams
  - Future performance regression predictions
  - Usage: Value betting on over/underperforming teams

### 11. Optimization Models
- **LineupOptimization** (`optimization_models.py`)
  - Constrained linear programming for lineup selection
  - DFS optimization with stacking strategies
  - Chemistry scoring
  - Usage: Daily fantasy sports and lineup construction

### 12. Clustering & Classification
- **OpponentStyleClustering** (`clustering_models.py`)
  - Unsupervised learning to group team styles
  - Tactical archetype classification
  - Matchup mismatch identification
  - Usage: Scouting and game planning

### 13. Possession Value Models
- **PossessionValueNetwork** (`possession_models.py`)
  - Markov chain transitions for possession value
  - Expected points per possession
  - Strategy comparison
  - Usage: Play-by-play value assessment

### 14. Tempo Models
- **ExpectedTempoEstimator** (`tempo_models.py`)
  - Predicts game tempo from early sequences
  - Identifies tempo drivers
  - Pace matchup predictions
  - Usage: In-game totals betting

### 15. Substitution Models
- **SubstitutionImpactRegression** (`substitution_models.py`)
  - Player impact per minute played
  - Optimal substitution timing
  - Lineup combination analysis
  - Usage: Coaching decisions and rotation optimization

### 16. Clutch Performance
- **ClutchIndex** (`clutch_models.py`)
  - Usage-adjusted clutch performance
  - Win probability added in clutch situations
  - Leverage-weighted performance
  - Usage: Late-game predictions and player evaluation

### 17. Volatility Models
- **GameVolatilityIndex** (`volatility_models.py`)
  - Score differential standard deviation
  - Entertainment value calculation
  - Game flow classification
  - Usage: Excitement prediction and viewership

### 18. Ranking Models
- **MultiMetricCompositeRanking** (`ranking_models.py`)
  - Weighted PCA for multi-metric rankings
  - Tier classification
  - Key driver identification
  - Usage: Power rankings and team evaluation

### 19. Calibration Models
- **AdaptiveWinProbCalibration** (`calibration_models.py`)
  - Continuous calibration with drift detection
  - Brier score and log loss tracking
  - Probability adjustment
  - Usage: Accurate win probability predictions

## Installation

Install required dependencies:

```bash
pip install numpy scipy scikit-learn
```

## Quick Start

```python
from models import (
    BayesianTeamPowerScores,
    RollingFormIndex,
    DynamicLuckIndex,
    LineupOptimization
)

# Initialize models
power_scores = BayesianTeamPowerScores()
form_index = RollingFormIndex()

# Use models
power_scores.initialize_team('LAL', {'win_pct': 0.650})
power_scores.update_ratings('LAL', 'BOS', 110, 105)
win_prob = power_scores.get_win_probability('LAL', 'BOS', home_team='LAL')

print(f"Win Probability: {win_prob:.2%}")
```

## Model Integration

All models are designed to work together. Example workflow:

1. **Team Evaluation**
   - BayesianTeamPowerScores for base ratings
   - RollingFormIndex for current form
   - DynamicLuckIndex for regression candidates

2. **Game Prediction**
   - OpponentStrengthWeighting for matchup adjustments
   - FatigueAdjustedPace for schedule considerations
   - TacticalSimilarityScoring for style matchups
   - AdaptiveWinProbCalibration for final probability

3. **In-Game Analysis**
   - ExpectedTempoEstimator for live pace
   - ClutchIndex for late-game situations
   - GameVolatilityIndex for excitement tracking

## Data Requirements

Models expect data in dictionary format with standard keys:

```python
team_data = {
    'id': 'LAL',
    'wins': 45,
    'losses': 20,
    'offensive_rating': 115.2,
    'defensive_rating': 108.5,
    'pace': 101.3,
    # ... additional stats
}

game_data = {
    'home_team': 'LAL',
    'away_team': 'BOS',
    'home_score': 110,
    'away_score': 105,
    # ... additional stats
}
```

## Performance Considerations

- Most models operate in O(n) or O(n log n) time
- PCA-based models (clustering, ranking) may be slower for large datasets
- Consider caching model outputs for frequently accessed data
- Use incremental updates where possible (e.g., Bayesian updates)

## Contributing

When adding new models:
1. Follow existing naming conventions
2. Include comprehensive docstrings
3. Add type hints
4. Include usage examples
5. Update this README

## References

These models implement techniques from:
- Sports analytics research papers
- Machine learning best practices
- Professional sports analytics systems
- Bayesian inference methods
- Time series analysis

## License

Part of SportStatBot - Expert sports analysis tool

## Version

Version 1.0.0 - Initial release with 25 advanced models
