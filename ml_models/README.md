# ML Models Directory

This directory contains machine learning models and advanced analytics for SportStatBot.

## Structure

```
ml_models/
├── __init__.py
├── README.md
├── base/                          # Base classes and utilities
│   ├── __init__.py
│   ├── base_model.py             # Abstract base model class
│   └── feature_engineering.py    # Common feature engineering
├── predictive/                    # Predictive models
│   ├── __init__.py
│   ├── injury_predictor.py       # LSTM injury recurrence model
│   ├── market_value.py           # Player market value estimator
│   ├── shot_quality.py           # Expected goals/points model
│   └── stability_index.py        # Performance stability analyzer
├── contextual/                    # Contextual adjustment models
│   ├── __init__.py
│   ├── travel_fatigue.py         # Travel impact model
│   ├── home_advantage.py         # Dynamic home court/field advantage
│   └── luck_adjustment.py        # Luck-corrected rankings
├── simulation/                    # Simulation engines
│   ├── __init__.py
│   ├── championship_simulator.py # Monte Carlo championship odds
│   ├── decision_model.py         # Coaching decision simulator
│   └── power_rating.py           # Power rating trajectory
├── advanced/                      # Advanced analytics
│   ├── __init__.py
│   ├── betting_detector.py       # Sharp money detector
│   ├── chemistry_cluster.py      # Team chemistry visualization
│   ├── scout_report.py           # AI-generated scouting reports
│   └── ref_analysis.py           # Referee impact analysis
└── artifacts/                     # Saved model weights
    ├── .gitignore
    └── README.md
```

## Model Development Workflow

1. **Create Model Class**
   - Inherit from `BaseModel` in `base/base_model.py`
   - Implement `train()`, `predict()`, and `evaluate()` methods

2. **Feature Engineering**
   - Use utilities in `base/feature_engineering.py`
   - Add sport-specific features as needed

3. **Training**
   - Use historical data from `data/historical/`
   - Save trained models to `artifacts/`

4. **Testing**
   - Write unit tests in `tests/ml_models/`
   - Validate on holdout data

5. **Integration**
   - Import model in analyzers or report generator
   - Add to CLI options if user-facing

## Getting Started

### Quick Example: Stability Index

```python
from ml_models.predictive.stability_index import PerformanceStabilityAnalyzer

# Initialize analyzer
analyzer = PerformanceStabilityAnalyzer()

# Get player game logs
game_logs = [
    {'points': 25, 'rebounds': 8, 'assists': 5},
    {'points': 30, 'rebounds': 7, 'assists': 6},
    # ... more games
]

# Calculate stability
result = analyzer.calculate_stability_index(game_logs, metric='points')

print(f"Stability Index: {result['stability_index']:.1f}/100")
print(f"Rating: {result['consistency_rating']}")
```

## Dependencies

Additional packages required for ML features:

```bash
# Install ML dependencies
pip install numpy pandas scikit-learn
pip install tensorflow  # or pytorch
pip install xgboost lightgbm
pip install statsmodels
pip install matplotlib seaborn plotly
```

## Contributing

When adding new models:

1. Follow the directory structure above
2. Inherit from `BaseModel` when applicable
3. Include docstrings with examples
4. Add unit tests
5. Update this README
6. Document in `DATA_SCIENCE_ROADMAP.md`
