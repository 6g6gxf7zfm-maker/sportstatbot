# 🚀 ML Models Quick Start Guide

## What's Been Implemented

### ✅ Working Models

1. **Performance Stability Index** (`ml_models/predictive/stability_index.py`)
   - Measures player performance consistency
   - Identifies reliable vs volatile performers
   - Provides 0-100 stability score with insights

2. **Travel Fatigue Model** (`ml_models/contextual/travel_fatigue.py`)
   - Quantifies impact of travel on performance
   - Considers distance, timezone, rest days, back-to-backs
   - Calculates performance impact percentage

### 📁 Project Structure

```
ml_models/
├── base/                    # Base classes and utilities
│   ├── base_model.py       # Abstract base for all models
│   └── feature_engineering.py  # Common feature engineering
├── predictive/              # Predictive models
│   └── stability_index.py  # ✅ Performance Stability (WORKING)
├── contextual/              # Contextual adjustments
│   └── travel_fatigue.py   # ✅ Travel Fatigue (WORKING)
├── simulation/              # Future: Championship odds, etc.
├── advanced/                # Future: AI scouting, betting analysis
└── artifacts/               # Trained model storage
```

## Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python ml_demo.py
```

This will showcase both working models with example data.

### 3. Use in Your Code

**Performance Stability Index:**
```python
from ml_models.predictive.stability_index import PerformanceStabilityAnalyzer

analyzer = PerformanceStabilityAnalyzer()

game_logs = [
    {'points': 28, 'date': '2024-11-01'},
    {'points': 31, 'date': '2024-11-03'},
    # ... more games
]

result = analyzer.calculate_stability_index(game_logs, metric='points')

print(f"Stability: {result['stability_index']}/100")
print(f"Rating: {result['consistency_rating']}")
print(f"Average: {result['mean_performance']} PPG")

# Generate full report
report = analyzer.generate_report("Player Name", game_logs)
print(report)
```

**Travel Fatigue Model:**
```python
from ml_models.contextual.travel_fatigue import TravelFatigueModel

model = TravelFatigueModel()

fatigue = model.calculate_fatigue_score(
    from_city='boston',
    to_city='los_angeles',
    rest_days=1
)

print(f"Fatigue Score: {fatigue['fatigue_score']}")
print(f"Impact: {fatigue['performance_impact_pct']}%")

# Generate report
report = model.generate_report("Team Name", "boston", "los_angeles", 1)
print(report)
```

## Next Steps

### Easy Wins (Implement Next)

1. **Home Advantage Quantifier** - Calculate dynamic home court/field advantage
2. **Luck Correction Ranking** - Compare expected vs actual results
3. **Performance by Context** - Analyze splits (home/away, vs opponent, etc.)

### Medium Complexity

4. **Player Market Value Estimator** - Predict contract value
5. **Power Rating Trajectory** - Elo-based or DVOA-style ratings
6. **Betting Line Analysis** - Track line movement patterns

### Advanced Features

7. **LSTM Injury Predictor** - Predict injury recurrence
8. **Shot Quality Model** - Expected points/goals model
9. **AI Scout Reports** - LLM-generated scouting reports
10. **Championship Simulator** - Monte Carlo simulation

See **DATA_SCIENCE_ROADMAP.md** for full details on all planned features.

## Integration with Main Bot

To integrate ML models into SportStatBot reports:

1. **Import model in analyzer:**
   ```python
   # In analyzers/player_analyzer.py
   from ml_models.predictive.stability_index import PerformanceStabilityAnalyzer
   ```

2. **Add to report generation:**
   ```python
   def analyze_player(player_data):
       # Existing analysis...

       # Add stability analysis
       stability_analyzer = PerformanceStabilityAnalyzer()
       stability = stability_analyzer.calculate_stability_index(
           player_data['game_logs'],
           metric='points'
       )

       return {
           'traditional_stats': ...,
           'stability': stability
       }
   ```

3. **Format in report:**
   ```python
   # In formatters/slack_formatter.py
   if 'stability' in player_analysis:
       stability = player_analysis['stability']
       report += f"• Consistency: {stability['consistency_rating']} "
       report += f"({stability['stability_index']}/100)\n"
   ```

## Development Workflow

### Adding a New Model

1. **Create model file** in appropriate directory (predictive/contextual/simulation/advanced)

2. **Inherit from BaseModel** (optional but recommended):
   ```python
   from ml_models.base import BaseModel, ModelConfig

   class MyModel(BaseModel):
       def __init__(self):
           config = ModelConfig(model_name="my_model", version="1.0")
           super().__init__(config)

       def train(self, data, labels=None):
           # Training logic
           pass

       def predict(self, data):
           # Prediction logic
           pass

       def evaluate(self, data, labels):
           # Evaluation logic
           pass
   ```

3. **Write tests** in `tests/ml_models/`

4. **Update documentation** in model file docstrings

5. **Add to package** `__init__.py`

## Testing Models

```bash
# Run individual model as script
python -m ml_models.predictive.stability_index

# Run demo
python ml_demo.py

# Run unit tests (when implemented)
pytest tests/ml_models/
```

## Data Requirements

Most models need historical data. Options:

1. **Fetch from APIs**
   - Use existing `data_fetchers/` modules
   - Add API calls for historical stats

2. **Scrape Sports Reference sites**
   - Basketball Reference, Pro Football Reference, etc.
   - Store in `data/historical/`

3. **Use CSV files**
   - Download season data
   - Parse and store in pandas DataFrames

4. **Database**
   - PostgreSQL for time-series data
   - Store player game logs, team stats, etc.

## Resources

- **DATA_SCIENCE_ROADMAP.md** - Full feature roadmap with implementation details
- **ml_models/README.md** - Developer guide and architecture
- **ml_demo.py** - Working examples with sample data
- Individual model files have detailed docstrings and usage examples

## FAQ

**Q: Do I need TensorFlow/PyTorch right now?**
A: No! The current working models (Stability Index, Travel Fatigue) only need numpy and basic Python. Install deep learning frameworks only when implementing LSTM/neural net models.

**Q: How do I get real player data?**
A: Start with ESPN API (already in `data_fetchers/espn_fetcher.py`). For historical data, consider Basketball Reference API or web scraping.

**Q: Can I use these models in production?**
A: The current models are statistical/rule-based and ready to use. ML models that require training should be validated on holdout data first.

**Q: Which feature should I implement next?**
A: Recommended order:
1. Home Advantage Quantifier (easy, high value)
2. Luck Correction Ranking (easy, interesting insights)
3. Player Market Value Estimator (medium, useful for fantasy)
4. LSTM Injury Predictor (advanced, requires data collection)

---

**Happy modeling! 🏆📊**
