# 🔮 SportStatBot - Modeling, Forecasting & Simulation Guide

Complete predictive analytics and simulation system for sports betting and analysis.

## 🎯 Overview

SportStatBot's modeling system provides 20 comprehensive prediction and simulation tools:

### Core Prediction Models
1. **Monte Carlo Simulation Engine** - 10,000+ simulations per game
2. **Power Index Ratings** - Elo-like team strength ratings updated daily
3. **Dynamic Spread Model** - Fair betting lines recalculated hourly
4. **Player Prop Predictor** - Individual player performance predictions
5. **Upset Probability Detector** - Flags potential shocking results

### Season & Playoff Projections
6. **Season Projector** - Win totals, playoff odds, championship probability
7. **Playoff Bracket Simulator** - Daily-updated playoff scenarios
8. **Coaching Change Predictor** - Likelihood of coaching changes

### Performance Analysis
9. **Momentum Tracker** - Recent form and back-to-back impacts
10. **Fatigue Decay Model** - Performance decline from exhaustion
11. **Travel Penalty Calculator** - Impact of travel distance and time zones
12. **Team Chemistry Model** - Optimal lineup combinations
13. **Injury Simulator** - Expected drop-off from injuries

### Sport-Specific Models
14. **Possession Simulator** - Soccer/hockey possession and scoring chances
15. **Player Regression Model** - Who's due to bounce back or decline

### Betting & Validation
16. **Betting Edge Tracker** - Historical model accuracy vs markets
17. **Live Game Predictor** - In-game probability updates
18. **Real-time Probability Graphs** - Win probability visualizations
19. **Historical Model Validator** - Backtesting and accuracy metrics
20. **Heat Surge Detector** - Teams outperforming expected metrics

---

## 🚀 Quick Start

### Command Line Interface

```bash
# Analyze a single game
python models_cli.py analyze --home "Kansas City Chiefs" --away "Buffalo Bills" --sport nfl

# View power rankings
python models_cli.py rankings --sport nfl --top 25

# Generate daily report
python models_cli.py report --sport nfl --output daily_report.json

# Check betting edge performance
python models_cli.py edge --days 30
```

### Python API

```python
from models.orchestrator import ModelOrchestrator

# Initialize
orchestrator = ModelOrchestrator()

# Analyze a game
analysis = orchestrator.analyze_game(
    home_team="Kansas City Chiefs",
    away_team="Buffalo Bills",
    sport="nfl"
)

# Access results
print(f"Home win probability: {analysis.monte_carlo_results.home_win_probability}")
print(f"Expected spread: {analysis.spread_predictions.fair_spread}")
print(f"Upset alerts: {analysis.upset_alerts}")
```

---

## 📊 Core Models

### 1. Monte Carlo Simulation Engine

Runs 10,000 simulations per game incorporating:
- Team power ratings
- Home field advantage
- Offensive/defensive matchups
- Injuries and fatigue
- Momentum factors
- Weather conditions
- Travel impact

**Example:**
```python
from models.monte_carlo_engine import MonteCarloSimulator, GameSimulationInput

simulator = MonteCarloSimulator(num_simulations=10000)

sim_input = GameSimulationInput(
    home_team="Chiefs",
    away_team="Bills",
    home_power_rating=1650,
    away_power_rating=1620,
    home_offensive_rating=115,
    away_offensive_rating=110,
    home_defensive_rating=105,
    away_defensive_rating=108,
    sport="nfl"
)

result = simulator.simulate_game(sim_input)

print(f"Chiefs win probability: {result.home_win_probability*100:.1f}%")
print(f"Expected score: {result.expected_home_score} - {result.expected_away_score}")
print(f"Over/Under suggestion: {result.over_under_suggestion}")
```

**Output:**
- Win probabilities for each team
- Expected final scores with confidence intervals
- Most likely score
- Spread prediction
- Over/under line
- Blowout/close game probabilities

---

### 2. Power Index Ratings (Elo System)

Dynamic team strength ratings updated after every game.

**Features:**
- Elo-style rating calculations
- Separate offensive and defensive ratings
- Home field advantage adjustments
- Margin of victory considerations
- Historical tracking
- Rating trends (rising/falling/stable)

**Example:**
```python
from models.power_index import PowerIndexRatings

ratings = PowerIndexRatings()

# Initialize teams
ratings.initialize_team("Chiefs", "nfl")
ratings.initialize_team("Bills", "nfl")

# Update after game
ratings.update_ratings(
    home_team="Chiefs",
    away_team="Bills",
    home_score=31,
    away_score=28,
    sport="nfl"
)

# Get rankings
top_teams = ratings.get_rankings("nfl", top_n=10)

for rank, team in enumerate(top_teams, 1):
    print(f"{rank}. {team.team_name}: {team.rating:.0f} ({team.wins}-{team.losses})")
```

---

### 3. Dynamic Spread Model

Calculates fair betting lines updated hourly.

**Outputs:**
- Fair point spread
- Fair moneyline odds (American format)
- Fair over/under total
- Confidence intervals
- Value detection (vs market lines)
- Alternate spreads
- Team totals
- First half lines

**Example:**
```python
from models.spread_model import DynamicSpreadModel

spread_model = DynamicSpreadModel()

prediction = spread_model.calculate_spread(
    home_team="Chiefs",
    away_team="Bills",
    home_rating=1650,
    away_rating=1620,
    home_offensive=115,
    away_offensive=110,
    home_defensive=105,
    away_defensive=108,
    sport="nfl",
    market_spread=-2.5  # Current market line
)

print(f"Fair spread: Chiefs {prediction.fair_spread:+.1f}")
print(f"Market spread: Chiefs {prediction.market_spread:+.1f}")
print(f"Value: {prediction.spread_value:+.1f} points")
print(f"Recommendation: {prediction.recommendation}")
```

---

### 4. Upset Probability Detector

Identifies games where underdogs have realistic chances.

**Factors Analyzed:**
- Rating/ranking gaps
- Recent momentum divergence
- Home/away splits
- Key injuries
- Situational spots (trap games, look-ahead spots)
- Rest advantages

**Example:**
```python
from models.upset_detector import UpsetDetector

detector = UpsetDetector()

alert = detector.detect_upset(
    home_team="Underdog Team",
    away_team="Favorite Team",
    home_rating=1450,
    away_rating=1650,
    home_form={'last_5_win_pct': 0.60},
    away_form={'last_5_win_pct': 0.40},
    injuries={'home_impact': 0, 'away_impact': 15}
)

if alert:
    print(f"🚨 UPSET ALERT!")
    print(f"Upset probability: {alert.upset_probability:.1f}%")
    print(f"Upset score: {alert.upset_score}/100")
    print(f"Key factors:")
    for factor in alert.key_factors:
        print(f"  • {factor}")
```

---

### 5. Player Prop Line Model

Predicts individual player performance for props betting.

**Supported Stats:**
- **NFL**: Passing/rushing/receiving yards, touchdowns
- **NBA**: Points, rebounds, assists, threes made
- **MLB**: Hits, RBIs, strikeouts
- **NHL**: Goals, assists, shots on goal
- **Soccer**: Goals, assists, shots

**Example:**
```python
from models.player_props import PlayerPropModel

props = PlayerPropModel()

prediction = props.predict_prop(
    player_name="Patrick Mahomes",
    team="Chiefs",
    opponent="Bills",
    stat_type="passing_yards",
    sport="nfl",
    recent_performance=[295, 315, 268, 342, 289],
    season_average=285,
    market_line=275.5
)

print(f"Predicted: {prediction.predicted_value} yards")
print(f"Over probability: {prediction.over_probability:.1f}%")
print(f"Value rating: {prediction.value_rating}")
```

---

## 🏆 Season Projections

### Season Projector

Projects win totals, playoff odds, and championship probabilities.

**Example:**
```python
from models.season_projector import SeasonProjector

projector = SeasonProjector()

projection = projector.project_season(
    team_name="Chiefs",
    sport="nfl",
    current_record=(10, 3),
    team_rating=1650,
    remaining_schedule=[
        {'opponent': 'Bills', 'is_home': True},
        {'opponent': 'Bengals', 'is_home': False},
        # ... more games
    ],
    opponent_ratings={'Bills': 1620, 'Bengals': 1590}
)

print(f"Projected wins: {projection.projected_wins}")
print(f"Playoff probability: {projection.playoff_probability:.1f}%")
print(f"Championship probability: {projection.championship_probability:.1f}%")
```

---

### Playoff Bracket Simulator

Simulates full playoff brackets with championship odds.

```python
from models.playoff_simulator import PlayoffBracketSimulator

simulator = PlayoffBracketSimulator(num_simulations=10000)

projection = simulator.simulate_playoffs(
    sport="nfl",
    seeds={
        1: "Chiefs",
        2: "Bills",
        3: "Ravens",
        4: "Jaguars",
        # ... all seeds
    },
    team_ratings={
        "Chiefs": 1650,
        "Bills": 1620,
        # ... all teams
    }
)

print("Championship Odds:")
for team, odds in sorted(projection.championship_odds.items(),
                         key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {team}: {odds:.1f}%")
```

---

## 📈 Performance Tracking

### Momentum Tracker

Tracks recent form and back-to-back game impacts.

```python
from models.momentum_tracker import MomentumTracker

tracker = MomentumTracker()

momentum = tracker.calculate_momentum(
    team="Chiefs",
    recent_results=[
        {'result': 'W', 'margin': 10},
        {'result': 'W', 'margin': 3},
        {'result': 'L', 'margin': -7},
        {'result': 'W', 'margin': 14},
        {'result': 'W', 'margin': 21}
    ],
    current_streak=4,  # 4-game win streak
    days_since_last_game=2
)

print(f"Momentum rating: {momentum.momentum_rating:+.1f}")
print(f"Recent form: {momentum.recent_form}")
print(f"Last 5: {momentum.last_5_record}")
```

---

### Fatigue Decay Model

Models performance decline from exhaustion.

```python
from models.fatigue_model import FatigueDecayModel

fatigue = FatigueDecayModel()

assessment = fatigue.assess_fatigue(
    team="Chiefs",
    games_last_7_days=3,
    days_since_last_game=1,
    travel_miles_last_week=2500,
    back_to_back_games=True
)

print(f"Fatigue level: {assessment.fatigue_level}/100")
print(f"Performance multiplier: {assessment.performance_multiplier}x")
print(f"Recovery status: {assessment.recovery_status}")
```

---

### Travel Penalty Calculator

Calculates fatigue from travel distance and time zones.

```python
from models.travel_penalty import TravelPenaltyCalculator

travel = TravelPenaltyCalculator()

impact = travel.calculate_travel_impact(
    team="Chiefs",
    origin_city="Los Angeles",
    destination_city="New York",
    days_since_travel=0
)

print(f"Miles traveled: {impact.miles_traveled}")
print(f"Time zones crossed: {impact.time_zones_crossed}")
print(f"Fatigue penalty: {impact.fatigue_penalty} rating points")
print(f"Performance impact: {impact.performance_impact}%")
```

---

## 🎲 Advanced Simulators

### Injury Replacement Simulator

Simulates expected drop-off when key players are injured.

```python
from models.injury_simulator import InjuryReplacementSimulator

injury_sim = InjuryReplacementSimulator()

impact = injury_sim.simulate_injury_impact(
    player_name="Patrick Mahomes",
    team="Chiefs",
    position="QB",
    sport="nfl",
    player_value=95,  # Elite player
    team_depth=70,    # Good backup
    games_expected_missed=4
)

print(f"Importance score: {impact.importance_score}/100")
print(f"Talent dropoff: {impact.talent_dropoff}%")
print(f"Rating impact: -{impact.rating_impact} points")
print(f"Severity: {impact.severity}")
```

---

### Player Regression Model

Identifies players likely to bounce back or regress.

```python
from models.player_regression import PlayerRegressionModel

regression = PlayerRegressionModel()

prediction = regression.predict_regression(
    player_name="Patrick Mahomes",
    team="Chiefs",
    current_season_stats={'passing_yards': 3200},
    career_averages={'passing_yards': 4500},
    recent_form=[220, 245, 268, 195, 310],
    age=28
)

print(f"Direction: {prediction.regression_direction}")
print(f"Expected performance: {prediction.expected_performance}")
print(f"Current: {prediction.current_performance}")
print(f"Confidence: {prediction.confidence}%")
```

---

## 💰 Betting Tools

### Betting Edge Tracker

Tracks model performance vs betting markets.

```python
from models.betting_edge import BettingEdgeTracker

tracker = BettingEdgeTracker()

# Record prediction
tracker.record_prediction(
    game_id="chiefs_bills_2024_01_15",
    home_team="Chiefs",
    away_team="Bills",
    model_spread=-3.5,
    market_spread=-2.5
)

# Update with result
tracker.update_result(
    game_id="chiefs_bills_2024_01_15",
    actual_result=-7  # Chiefs won by 7
)

# Get summary
summary = tracker.get_summary(days=30)
print(f"Win rate: {summary.win_rate}%")
print(f"ROI: {summary.roi}%")
```

---

### Live Game Predictor

Real-time in-game predictions.

```python
from models.live_predictor import LiveGamePredictor

live = LiveGamePredictor()

prediction = live.predict_live(
    game_id="chiefs_bills_live",
    home_team="Chiefs",
    away_team="Bills",
    current_home_score=21,
    current_away_score=17,
    time_remaining_pct=0.25,  # 25% of game left
    pregame_ratings={'Chiefs': 1650, 'Bills': 1620},
    live_line=-3.5
)

print(f"Live win probability: Chiefs {prediction.model_win_prob_home}%")
print(f"Model line: {prediction.model_line}")
print(f"Line delta: {prediction.line_delta}")
print(f"Recommendation: {prediction.recommendation}")
```

---

## 🎨 Visualization

### Probability Graph Generator

Creates win probability curves over time.

```python
from models.probability_graphs import ProbabilityGraphGenerator

graph_gen = ProbabilityGraphGenerator()

curve = graph_gen.generate_live_probability_curve(
    game_events=[
        {'time_elapsed': 0, 'score_home': 0, 'score_away': 0},
        {'time_elapsed': 15, 'score_home': 7, 'score_away': 0, 'type': 'touchdown'},
        {'time_elapsed': 30, 'score_home': 7, 'score_away': 7},
        {'time_elapsed': 45, 'score_home': 14, 'score_away': 10},
        # ... more events
    ],
    initial_home_prob=0.52,
    initial_away_prob=0.48
)

# Plot with matplotlib or export to JSON for visualization
```

---

## 🔍 Validation & Alerts

### Model Validator

Backtests model predictions vs actual results.

```python
from models.model_validator import ModelValidator

validator = ModelValidator()

metrics = validator.validate_predictions(
    predictions=[
        {'predicted_winner': 'Chiefs', 'predicted_spread': -3.5, 'win_probability': 0.65},
        # ... more predictions
    ],
    actuals=[
        {'winner': 'Chiefs', 'actual_spread': -7},
        # ... actual results
    ]
)

print(f"Accuracy: {metrics.accuracy_percentage}%")
print(f"Mean Absolute Error: {metrics.mean_absolute_error}")
print(f"Brier Score: {metrics.brier_score}")
```

---

### Heat Surge Detector

Flags teams significantly outperforming expectations.

```python
from models.heat_surge import HeatSurgeDetector

surge = HeatSurgeDetector()

alert = surge.detect_surge(
    team="Hot Team",
    sport="nfl",
    expected_metrics={
        'win_pct': 0.50,
        'points_per_game': 24,
        'yards_per_game': 350
    },
    actual_metrics={
        'win_pct': 0.75,
        'points_per_game': 32,
        'yards_per_game': 420
    }
)

if alert:
    print(f"🔥 HEAT SURGE ALERT!")
    print(f"Surge score: {alert.surge_score}/100")
    print(f"Sustainability: {alert.sustainability_rating}")
    print(f"Alert level: {alert.alert_level}")
```

---

## 📚 Complete Example

```python
from models.orchestrator import ModelOrchestrator

# Initialize
orchestrator = ModelOrchestrator()

# Update ratings from recent games
results = [
    {'home_team': 'Chiefs', 'away_team': 'Bills', 'home_score': 31, 'away_score': 28},
    {'home_team': 'Ravens', 'away_team': 'Bengals', 'home_score': 24, 'away_score': 20},
    # ... more results
]
orchestrator.update_ratings_from_results(results, 'nfl')

# Analyze today's game
analysis = orchestrator.analyze_game(
    home_team="Chiefs",
    away_team="49ers",
    sport="nfl",
    game_data={
        'home_recent_results': [{'result': 'W'}, {'result': 'W'}, {'result': 'W'}],
        'away_recent_results': [{'result': 'W'}, {'result': 'L'}, {'result': 'W'}],
        'home_rest_days': 7,
        'away_rest_days': 6
    }
)

# Export results
orchestrator.export_analysis(analysis, 'game_analysis.json')

# Generate daily report
report = orchestrator.generate_daily_report('nfl', [])
print(json.dumps(report, indent=2, default=str))
```

---

## 🛠️ Installation & Setup

### Requirements

```bash
pip install numpy
```

### Directory Structure

```
sportstatbot/
├── models/
│   ├── __init__.py
│   ├── orchestrator.py           # Main coordinator
│   ├── monte_carlo_engine.py     # Simulations
│   ├── power_index.py            # Team ratings
│   ├── spread_model.py           # Betting lines
│   ├── upset_detector.py         # Upset alerts
│   ├── player_props.py           # Player predictions
│   ├── season_projector.py       # Season outlook
│   ├── playoff_simulator.py      # Playoff brackets
│   ├── momentum_tracker.py       # Recent form
│   ├── fatigue_model.py          # Fatigue analysis
│   ├── travel_penalty.py         # Travel impact
│   ├── injury_simulator.py       # Injury effects
│   ├── chemistry_model.py        # Lineup synergy
│   ├── possession_simulator.py   # Possession-based
│   ├── betting_edge.py           # Performance tracking
│   ├── live_predictor.py         # In-game predictions
│   ├── probability_graphs.py     # Visualizations
│   ├── model_validator.py        # Backtesting
│   ├── heat_surge.py             # Performance alerts
│   ├── coaching_predictor.py     # Coaching changes
│   └── player_regression.py      # Player trends
├── models_cli.py                  # Command-line interface
└── data/                          # Stored ratings/history
```

---

## 📖 Documentation

For more details:
- Main README: `README.md`
- Usage Guide: `USAGE_GUIDE.md`
- API Documentation: See inline docstrings in each module

---

## 🤝 Contributing

Ideas for enhancements:
- Machine learning integration
- Additional sports
- Advanced visualizations
- Real-time data feeds
- Web dashboard
- Mobile app

---

## ⚖️ Disclaimer

**For educational and entertainment purposes only.**

This modeling system is provided for analysis and research. Always gamble responsibly if using for betting purposes. Past performance does not guarantee future results.

---

**Built with ❤️ for sports analytics enthusiasts**
