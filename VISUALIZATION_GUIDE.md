# SportStatBot Visualization & Reporting Guide

## 📊 Overview

The SportStatBot visualization system provides comprehensive charting and reporting capabilities for sports analytics. This guide covers all available visualization types and how to use them.

## 🎨 Features

### Chart Types

1. **Rating Charts**
   - Rolling offensive/defensive ratings
   - Rating distributions
   - Rating heatmaps
   - Off/Def comparison charts

2. **Spatial Charts**
   - Shot heatmaps (basketball, hockey, soccer)
   - Injury cluster maps
   - Zone efficiency maps

3. **Comparison Charts**
   - Expected vs actual metrics
   - Spread vs fair line delta
   - Scatter comparisons
   - Performance matrices

4. **Radar Charts**
   - Team performance radars (6+ metrics)
   - Multi-team comparisons
   - Offense/defense split radars

5. **Trend Charts**
   - Form pulse graphs (win/loss trends)
   - Season progress bars
   - Momentum gauges
   - League parity charts

6. **Betting Charts**
   - Line movement graphs
   - Win probability timelines
   - Top edges of the day
   - Odds comparison across bookmakers

7. **Player Cards**
   - Individual player cards
   - Player comparisons
   - Team roster cards

8. **Dashboards**
   - Interactive HTML dashboards
   - Notion-compatible exports
   - Multi-section layouts

---

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install -r requirements.txt
```

### Generate Demo Visualizations

```bash
# Generate demo charts for NBA
python visualization_cli.py --demo --sport nba

# Generate for other sports
python visualization_cli.py --demo --sport nfl
python visualization_cli.py --demo --sport mlb
```

### Run Example Scripts

```bash
# Run all visualization examples
python examples/visualization_examples.py
```

---

## 📖 Usage Examples

### 1. Team Performance Analysis

```python
from visualizers.visualization_manager import VisualizationManager

manager = VisualizationManager(sport='nba', output_dir='my_charts')

team_data = {
    'offensive_ratings': [110, 112, 108, 115, 113],
    'defensive_ratings': [105, 103, 107, 102, 104],
    'metrics': {
        'Offense': 85,
        'Defense': 78,
        'Rebounding': 72,
        'Assists': 88,
        'Turnovers': 65,
        'FG%': 82
    },
    'recent_results': ['W', 'W', 'L', 'W', 'W'],
    'wins': 45,
    'losses': 20
}

charts = manager.generate_team_analysis_suite('Lakers', team_data)
```

### 2. Head-to-Head Matchup

```python
matchup_data = {
    'momentum_score': -35,  # Negative = Team 1 favor
    'team_metrics': {
        'Lakers': {'Offense': 85, 'Defense': 78, 'Pace': 75},
        'Warriors': {'Offense': 90, 'Defense': 72, 'Pace': 85}
    }
}

charts = manager.generate_matchup_analysis('Lakers', 'Warriors', matchup_data)
```

### 3. Betting Analysis

```python
betting_data = {
    'edges': [
        {
            'game': 'LAL vs GSW',
            'bet_type': 'Spread',
            'edge': 4.2,
            'recommended': 'LAL +5.5',
            'confidence': 0.78
        }
    ],
    'spreads': [
        {'game': 'LAL vs GSW', 'spread': -5.5, 'fair_line': -1.3}
    ]
}

charts = manager.generate_betting_analysis(betting_data)
```

### 4. Interactive Dashboard

```python
dashboard_config = {
    'title': 'NBA Game Day Dashboard',
    'subtitle': 'Live Analysis',
    'metrics': {
        'Games Today': 8,
        'Teams Analyzed': 16,
        'Betting Edges': 4
    },
    'charts': [
        {'title': 'Team Ratings', 'path': 'path/to/chart.png'}
    ]
}

dashboard_path = manager.generate_comprehensive_dashboard(dashboard_config)
```

---

## 🎯 Chart Generator Reference

### RatingChartGenerator

```python
from visualizers.rating_charts import RatingChartGenerator

gen = RatingChartGenerator(sport='nba')

# Rolling ratings
gen.generate_rolling_ratings(
    {'Lakers': [110, 112, 108], 'Warriors': [115, 113, 116]},
    metric='offensive_rating',
    window=5
)

# Off/Def comparison
gen.generate_off_def_comparison(
    'Lakers',
    offensive_ratings=[110, 112, 108],
    defensive_ratings=[105, 103, 107]
)

# League distribution
gen.generate_rating_distribution(
    {'Lakers': 110.5, 'Warriors': 115.2},
    team_highlight='Warriors'
)
```

### SpatialChartGenerator

```python
from visualizers.spatial_charts import SpatialChartGenerator

gen = SpatialChartGenerator(sport='nba')

# Shot heatmap
shot_data = [
    {'x': 10, 'y': 20, 'made': True},
    {'x': 15, 'y': 25, 'made': False}
]
gen.generate_shot_heatmap(shot_data, court_type='basketball')

# Injury cluster map
gen.generate_injury_cluster_map({'Lakers': 5, 'Warriors': 2})
```

### RadarChartGenerator

```python
from visualizers.radar_charts import RadarChartGenerator

gen = RadarChartGenerator(sport='nba')

# Single team radar
gen.generate_team_radar(
    'Lakers',
    {'Offense': 85, 'Defense': 78, 'Rebounding': 72}
)

# Team comparison
gen.generate_comparison_radar({
    'Lakers': {'Offense': 85, 'Defense': 78},
    'Warriors': {'Offense': 90, 'Defense': 72}
})
```

### TrendChartGenerator

```python
from visualizers.trend_charts import TrendChartGenerator

gen = TrendChartGenerator(sport='nba')

# Form pulse
gen.generate_form_pulse('Lakers', ['W', 'W', 'L', 'W', 'W'])

# Season progress
gen.generate_season_progress(
    'Lakers',
    current_wins=45,
    current_losses=20,
    target_wins=50,
    playoff_threshold=45
)

# Momentum gauge
gen.generate_momentum_gauge('Lakers', 'Warriors', momentum_score=-35)

# League parity
gen.generate_league_parity_chart({'Lakers': 88, 'Warriors': 95})
```

### BettingChartGenerator

```python
from visualizers.betting_charts import BettingChartGenerator
from datetime import datetime, timedelta

gen = BettingChartGenerator(sport='nba')

# Line movement
timestamps = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -4)]
gen.generate_line_movement(
    'LAL vs GSW',
    timestamps=timestamps,
    opening_lines=[-6.0] * 6,
    current_lines=[-6.0, -6.5, -7.0, -7.5, -8.0, -8.5]
)

# Top edges
edges = [
    {'game': 'LAL vs GSW', 'edge': 4.2, 'recommended': 'LAL +5.5', 'confidence': 0.78}
]
gen.generate_top_edges(edges)

# Win probability
timeline = [
    {'time': '1Q 10:00', 'team1_prob': 0.50, 'team2_prob': 0.50},
    {'time': '2Q 5:30', 'team1_prob': 0.62, 'team2_prob': 0.38}
]
gen.generate_win_probability_timeline('LAL vs GSW', timeline)
```

### PlayerCardGenerator

```python
from visualizers.player_cards import PlayerCardGenerator

gen = PlayerCardGenerator(sport='nba')

# Single player card
player_data = {
    'name': 'LeBron James',
    'team': 'Lakers',
    'number': 23,
    'stats': {'PPG': 27.5, 'RPG': 8.2, 'APG': 7.1},
    'recent_form': [25, 32, 28, 30, 27],
    'season_avg': 27.5
}
gen.generate_player_card(player_data)

# Player comparison
gen.generate_comparison_card(player1_data, player2_data)
```

---

## 🎨 Customization

### Sport Colors

Each sport has a predefined color scheme:

```python
SPORT_COLORS = {
    'nfl': {'primary': '#013369', 'secondary': '#D50A0A', 'accent': '#FFB612'},
    'nba': {'primary': '#17408B', 'secondary': '#C9082A', 'accent': '#FDB927'},
    'mlb': {'primary': '#041E42', 'secondary': '#BF0D3E', 'accent': '#FFFFFF'},
    'nhl': {'primary': '#000000', 'secondary': '#C8102E', 'accent': '#FCB514'},
}
```

### Chart Styles

Three built-in styles:

- `dark`: Dark background, light text
- `light`: Light background, dark text
- `sports`: Sports-themed (default)

```python
from visualizers.chart_utils import setup_chart_style

setup_chart_style('dark', sport='nba')
```

---

## 📱 Dashboard Features

### Interactive Elements

- **Plotly Integration**: Interactive hover effects, zoom, pan
- **Responsive Design**: Mobile-friendly layouts
- **Data Tables**: Sortable, filterable tables
- **Key Metrics**: Highlighted statistics cards

### Export Formats

1. **Full HTML Dashboard**
   - Standalone HTML file
   - Embedded charts
   - Interactive elements

2. **Notion-Compatible**
   - Simplified HTML
   - Base64 embedded images
   - Copy-paste into Notion

---

## 🔧 CLI Commands

### Demo Generation

```bash
# Generate all demo charts
python visualization_cli.py --demo --sport nba

# Other sports
python visualization_cli.py --demo --sport nfl
python visualization_cli.py --demo --sport mlb
python visualization_cli.py --demo --sport nhl
```

### Custom Charts

```bash
# Team radar
python visualization_cli.py --chart-type team_radar \
  --team-name "Lakers" \
  --metrics "Offense=85,Defense=78,Rebounding=72"

# Form pulse
python visualization_cli.py --chart-type form_pulse \
  --team-name "Warriors" \
  --results "WWLWWLW"

# Season progress
python visualization_cli.py --chart-type season_progress \
  --team-name "Celtics" \
  --wins 45 --losses 20 --target-wins 50
```

---

## 📊 Output Directories

```
sportstatbot/
├── charts/              # Static chart images
├── dashboards/          # HTML dashboards
├── visualizations/      # Main output directory
│   ├── charts/
│   └── dashboards/
└── examples/
    └── output/          # Example outputs
```

---

## 🎯 Best Practices

1. **Data Preparation**
   - Ensure data is in correct format
   - Handle missing values
   - Normalize metrics to 0-100 for radars

2. **Chart Selection**
   - Use radars for multi-metric comparison
   - Use trends for time-series data
   - Use heatmaps for spatial analysis

3. **Dashboard Design**
   - Group related charts
   - Highlight key metrics
   - Use consistent colors

4. **Performance**
   - Generate charts in batches
   - Reuse manager instances
   - Cache frequently used data

---

## 🔗 Integration with Report Generator

```python
from report_generator import SportsReportGenerator
from visualizers.visualization_manager import VisualizationManager

# Generate report data
report_gen = SportsReportGenerator()
report_data = report_gen.generate_full_report(sports=['nba'])

# Generate visualizations
viz_manager = VisualizationManager(sport='nba')
charts = viz_manager.generate_daily_report_visualizations(report_data)

# Create dashboard
dashboard = viz_manager.create_summary_report('Daily NBA Analysis')
```

---

## 📚 Additional Resources

- **Examples**: See `examples/visualization_examples.py`
- **Source Code**: Check `visualizers/` directory
- **Customization**: Modify chart templates in generator classes

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Charts not displaying properly
- **Solution**: Ensure matplotlib backend is set correctly
- Check: `import matplotlib; matplotlib.use('Agg')`

**Issue**: Missing dependencies
- **Solution**: `pip install -r requirements.txt`

**Issue**: Memory errors with large datasets
- **Solution**: Generate charts in smaller batches

---

## 🎉 Summary

The SportStatBot visualization system provides:

✅ 17+ different chart types
✅ Multi-sport support with custom styling
✅ Interactive HTML dashboards
✅ Notion-compatible exports
✅ Comprehensive betting analysis
✅ Player and team cards
✅ CLI and programmatic interfaces

Start generating professional sports visualizations today!
