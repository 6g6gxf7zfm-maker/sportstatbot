## Sports Analytics Visualizations Guide

Complete guide for all 25 advanced visualization features (26-50).

## Table of Contents

1. [Quick Start](#quick-start)
2. [Visualization Features](#visualization-features)
3. [Dashboard Usage](#dashboard-usage)
4. [API Reference](#api-reference)
5. [Examples](#examples)

## Quick Start

### Installation

```bash
# Install visualization dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from visualizations.charts.heatmaps import EPAHeatmap

# Create EPA heatmap
heatmap = EPAHeatmap(title="Chiefs EPA Analysis", dark_mode=False)
fig = heatmap.create(data={'plays': plays_data, 'team_name': 'Kansas City Chiefs'})

# Save to file
heatmap.save('chiefs_epa', format='html')

# Display
heatmap.show()
```

### Run Dashboard

```bash
python visualizations/dashboard/app.py
```

Open browser to `http://localhost:8050`

---

## Visualization Features

### Feature 26: Animated EPA Heatmaps

**Clock-synchronized EPA visualization over field**

```python
from visualizations.charts.heatmaps import EPAHeatmap

epa = EPAHeatmap()
fig = epa.create(
    data={
        'plays': [
            {'x': 50, 'y': 26, 'epa': 0.5, 'quarter': 1, 'game_seconds': 120},
            # ... more plays
        ],
        'team_name': 'Team Name'
    },
    animate=True,
    frame_duration=500  # milliseconds
)
```

**Features:**
- Real-time clock synchronization
- Play-by-play animation
- Interactive timeline scrubbing
- Field overlay with yard lines

---

### Feature 27: Interactive Shot Trajectories

**Shot trajectory replay with arc visualization**

```python
from visualizations.charts.trajectories import ShotTrajectory

trajectory = ShotTrajectory(sport='basketball')
fig = trajectory.create(
    data={
        'shots': [
            {'x_start': 20, 'y_start': 15, 'x_end': 5, 'y_end': 25,
             'made': True, 'player': 'Curry', 'distance': 22.5},
            # ... more shots
        ],
        'sport': 'basketball',
        'team_name': 'Warriors'
    },
    animate=True
)
```

**Features:**
- Parabolic arc visualization
- Make/miss color coding
- Interactive replay animation
- Court/field overlay

---

### Feature 28: Momentum Timeline

**Timeline ribbon showing momentum swings**

```python
from visualizations.charts.timelines import MomentumTimeline

timeline = MomentumTimeline()
fig = timeline.create(
    data={
        'events': [
            {'time': 5, 'momentum': 10, 'score_a': 7, 'score_b': 0,
             'event_desc': 'Touchdown'},
            # ... more events
        ],
        'team_a_name': 'Chiefs',
        'team_b_name': 'Bills'
    }
)
```

**Features:**
- Area chart showing momentum swings
- Key moments highlighted
- Hover statistics
- Quarter markers

---

### Feature 29: Luck vs Skill Scatter

**Dual-axis analysis dashboard**

```python
from visualizations.charts.scatter_plots import LuckVsSkillScatter

scatter = LuckVsSkillScatter()
fig = scatter.create(
    data={
        'teams': [
            {'name': 'Chiefs', 'luck_score': 65, 'skill_score': 88,
             'wins': 12, 'losses': 5, 'expected_wins': 11.2},
            # ... more teams
        ]
    }
)
```

**Features:**
- Quadrant analysis
- Size-coded wins
- Expected vs actual performance
- Interactive tooltips

---

### Feature 30: Playoff Probability Fan Chart

**Uncertainty visualization for playoff odds**

```python
from visualizations.charts.probability_charts import PlayoffProbabilityFan

fan_chart = PlayoffProbabilityFan()
fig = fan_chart.create(
    data={
        'team_name': 'Chiefs',
        'projections': [
            {'week': 1, 'prob_10': 30, 'prob_25': 40, 'prob_50': 50,
             'prob_75': 60, 'prob_90': 70},
            # ... more weeks
        ]
    }
)
```

**Features:**
- Confidence bands (10th-90th percentile)
- Median projection line
- Weekly progression
- 50% threshold marker

---

### Feature 31: Player Radar Comparison

**Multi-stat radar charts**

```python
from visualizations.charts.radar_charts import PlayerRadarComparison

radar = PlayerRadarComparison()
fig = radar.create(
    data={
        'player1': {
            'name': 'Patrick Mahomes',
            'stats': {'Passing': 92, 'Rushing': 65, 'Accuracy': 88}
        },
        'player2': {
            'name': 'Josh Allen',
            'stats': {'Passing': 88, 'Rushing': 85, 'Accuracy': 80}
        },
        'categories': ['Passing', 'Rushing', 'Accuracy']
    }
)
```

**Features:**
- Multi-stat overlay
- Category comparison
- Head-to-head summary
- Customizable metrics

---

### Feature 32: Score Worm Graph

**Multi-game score tracking**

```python
from visualizations.charts.worm_graphs import ScoreWormGraph

worm = ScoreWormGraph()
fig = worm.create(
    data={
        'games': [
            {
                'team_a': 'Chiefs', 'team_b': 'Bills',
                'scoring_plays': [
                    {'time': 0, 'score_a': 0, 'score_b': 0, 'description': 'Start'},
                    # ... more plays
                ]
            }
        ]
    }
)
```

**Features:**
- Multiple concurrent games
- Score progression lines
- Event markers
- Synchronized timelines

---

### Feature 33: Lineup Tree Map

**Hierarchical lineup usage visualization**

```python
from visualizations.charts.tree_maps import LineupTreeMap

treemap = LineupTreeMap()
fig = treemap.create(
    data={
        'team_name': 'Warriors',
        'lineups': [
            {
                'players': ['Curry', 'Thompson', 'Green'],
                'minutes': 45.2,
                'plus_minus': 12.5,
                'games': 15
            }
        ]
    }
)
```

**Features:**
- Plus/minus color coding
- Hierarchical layout
- Usage percentage
- Interactive drill-down

---

### Feature 34: Turnover Flow Diagram

**Sankey diagram of possession chains**

```python
from visualizations.charts.flow_diagrams import TurnoverFlowDiagram

flow = TurnoverFlowDiagram()
fig = flow.create(
    data={
        'turnovers': [
            {'source': 'Team A Possession', 'target': 'Interception',
             'count': 2, 'label': 'INTs'},
            # ... more flows
        ],
        'team_a_name': 'Chiefs',
        'team_b_name': 'Bills'
    }
)
```

**Features:**
- Possession flow visualization
- Turnover categorization
- Team color coding
- Flow quantities

---

### Feature 35: xG Difference Field

**Multi-layer expected goals visualization**

```python
from visualizations.charts.xg_visualizations import XGDifferenceField

xg_viz = XGDifferenceField()
fig = xg_viz.create(
    data={
        'team_a_shots': [
            {'x': 95, 'y': 34, 'xg': 0.75},
            # ... more shots
        ],
        'team_b_shots': [...],
        'team_a_name': 'Liverpool',
        'team_b_name': 'Man City'
    }
)
```

**Features:**
- Shot location markers
- xG-sized bubbles
- Pitch overlay
- Team totals

---

### Feature 36: Win Path Video

**Animated turning points summary**

```python
from visualizations.animations.win_path import WinPathVideo

win_path = WinPathVideo()
fig = win_path.create(
    data={
        'game_events': [
            {'time': 5, 'win_prob_a': 55, 'win_prob_b': 45,
             'event_desc': 'Touchdown', 'is_turning_point': True},
            # ... more events
        ],
        'team_a_name': 'Chiefs',
        'team_b_name': 'Bills'
    }
)

# Export as video/GIF
win_path.export_video('chiefs_vs_bills')
```

**Features:**
- Win probability timeline
- Turning point markers
- Event annotations
- Video/GIF export

---

### Feature 37: Broadcast Overlay Pack

**Professional broadcast graphics**

```python
from visualizations.overlays.broadcast_overlay import BroadcastOverlay

overlay = BroadcastOverlay()

# Scoreboard
scoreboard = overlay.create_scoreboard(
    data={
        'team_a': {'name': 'Chiefs', 'score': 28, 'record': '10-3'},
        'team_b': {'name': 'Bills', 'score': 24, 'record': '9-4'},
        'quarter': 4,
        'time_remaining': '5:23',
        'possession': 'A'
    }
)

# Stat ticker
ticker = overlay.create_stat_ticker(
    data={
        'stats': [
            {'label': 'Total Yards', 'team_a_value': 345, 'team_b_value': 289}
        ]
    }
)
```

**Features:**
- Customizable overlays
- Possession indicators
- Stat comparisons
- Transparent backgrounds

---

### Feature 38: Depth Chart Visualization

**Dynamic depth chart with injuries**

```python
from visualizations.charts.depth_charts import DepthChartVisualization

depth_chart = DepthChartVisualization()
fig = depth_chart.create(
    data={
        'positions': {
            'QB': [
                {'name': 'Mahomes', 'status': 'healthy', 'stats': '300 YPG'},
                {'name': 'Backup', 'status': 'healthy', 'stats': ''}
            ],
            # ... more positions
        },
        'team_name': 'Chiefs'
    }
)
```

**Features:**
- Injury status indicators
- Depth ordering
- Player statistics
- Color-coded health status

---

### Feature 39: Expected Goal Density Surface

**3D heat surface visualization**

```python
from visualizations.charts.xg_visualizations import ExpectedGoalDensity

density = ExpectedGoalDensity()
fig = density.create(
    data={
        'shots': [
            {'x': 95, 'y': 34, 'xg': 0.75},
            # ... more shots
        ],
        'team_name': 'Liverpool'
    }
)
```

**Features:**
- 3D surface plot
- Density gradient
- Interactive rotation
- Hot zones highlighted

---

### Feature 40: Ball Movement Chord Diagram

**Pass network visualization**

```python
from visualizations.charts.flow_diagrams import BallMovementChord

chord = BallMovementChord()
fig = chord.create(
    data={
        'passes': [
            {'from_player': 'Curry', 'to_player': 'Thompson',
             'count': 25, 'success_rate': 0.92},
            # ... more passes
        ],
        'team_name': 'Warriors'
    }
)
```

**Features:**
- Player connection network
- Pass frequency sizing
- Success rate visualization
- Interactive nodes

---

### Feature 41: Season Progress Bar

**Milestone tracking visualization**

```python
from visualizations.charts.progress_bars import SeasonProgressBar

progress = SeasonProgressBar()
fig = progress.create(
    data={
        'team_name': 'Chiefs',
        'current_week': 10,
        'total_weeks': 18,
        'milestones': [
            {'week': 4, 'title': 'First Quarter', 'achieved': True},
            # ... more milestones
        ],
        'record': {'wins': 7, 'losses': 3, 'ties': 0}
    }
)
```

**Features:**
- Progress visualization
- Milestone markers
- Record summary
- Achievement tracking

---

### Feature 42: Calendar Heatmap

**Daily team form visualization**

```python
from visualizations.charts.heatmaps import CalendarHeatmap

calendar = CalendarHeatmap()
fig = calendar.create(
    data={
        'games': [
            {'date': '2025-01-15', 'result': 'W', 'score_diff': 14},
            # ... more games
        ],
        'team_name': 'Chiefs'
    }
)
```

**Features:**
- Calendar grid layout
- Win/loss color coding
- Score differentials
- Season view

---

### Feature 43: Rolling Probability Ticker

**Live probability updates**

```python
from visualizations.charts.probability_charts import ProbabilityTicker

ticker = ProbabilityTicker()
fig = ticker.create(
    data={
        'events': [
            {'name': 'Chiefs Win Super Bowl', 'probability': 75.5, 'change': 2.3},
            # ... more events
        ]
    }
)
```

**Features:**
- Real-time updates
- Change indicators
- Gradient coloring
- Horizontal bars

---

### Feature 44: Dynamic Font Scaling

**Large-screen studio view**

```python
from visualizations.dashboard.studio_view import StudioView

studio = StudioView(dark_mode=False)
layout = studio.create_layout()

# Or run full dashboard
from visualizations.dashboard.app import run_dashboard
run_dashboard(port=8050)
```

**Features:**
- Responsive font sizing
- Optimized for large displays
- Multi-panel layout
- Professional styling

---

### Feature 45: Side-by-Side Compare

**Dual visualization comparison**

```python
# Available in dashboard
# Access via "Side-by-Side Compare" button
```

**Features:**
- Two charts simultaneously
- Synchronized interactions
- Comparison mode
- Independent controls

---

### Feature 46: Confidence Glow

**Visual confidence indicators**

```python
from visualizations.overlays.confidence_glow import ConfidenceGlow

glow = ConfidenceGlow()
fig = glow.create(
    data={
        'predictions': [
            {'name': 'Prediction 1', 'value': 75, 'confidence': 0.9},
            # ... more predictions
        ]
    }
)
```

**Features:**
- Glow intensity = confidence
- Color coding
- Multi-layer effects
- Interactive markers

---

### Feature 47: Voronoi Area Control

**Positional dominance visualization**

```python
from visualizations.charts.voronoi_maps import PositionalAreaControl

voronoi = PositionalAreaControl()
fig = voronoi.create(
    data={
        'team_a_positions': [
            {'x': 30, 'y': 34, 'player_name': 'Player 1'},
            # ... more positions
        ],
        'team_b_positions': [...],
        'team_a_name': 'Team A',
        'team_b_name': 'Team B',
        'sport': 'soccer'
    }
)
```

**Features:**
- Voronoi tessellation
- Area control percentages
- Player positioning
- Team territories

---

### Feature 48: Shot Distance Histogram

**Shot distribution analysis**

```python
from visualizations.charts.histograms import ShotDistanceHistogram

histogram = ShotDistanceHistogram()
fig = histogram.create(
    data={
        'shots': [
            {'player': 'Curry', 'distance': 25.5, 'made': True},
            # ... more shots
        ],
        'player_name': 'Curry'  # Optional: specific player
    }
)
```

**Features:**
- Make/miss overlay
- Success rate by distance
- Distribution analysis
- Player-specific view

---

### Feature 49: Play Sequence GIF

**Animated play export**

```python
from visualizations.animations.gif_exporter import PlaySequenceGIF

gif_exporter = PlaySequenceGIF()
gif_path = gif_exporter.create_gif(
    data={
        'plays': [
            {
                'frame_num': 0,
                'player_positions': [
                    {'x': 50, 'y': 25, 'team': 'A', 'player_id': 1},
                    # ... more positions
                ],
                'event_desc': 'Play 1'
            }
        ],
        'field_type': 'football',
        'team_a_name': 'Chiefs',
        'team_b_name': 'Bills'
    },
    filename='touchdown_play',
    fps=2
)
```

**Features:**
- Frame-by-frame animation
- Field overlay
- Player tracking
- GIF export

---

### Feature 50: Apple Notes Integration

**Direct export to Notes**

```python
from visualizations.integrations.apple_notes import AppleNotesIntegration

notes = AppleNotesIntegration()

# Export chart to Notes
success = notes.export_to_notes(
    chart_path='/path/to/chart.png',
    note_title='Chiefs EPA Analysis',
    note_body='Week 10 performance analysis',
    folder='Sports Analytics'
)
```

**Features:**
- macOS integration
- Automatic folder creation
- Image attachment
- Note organization

---

## Dashboard Usage

### Start Dashboard

```bash
python visualizations/dashboard/app.py
```

### Features

- **Single View**: Focus on one visualization
- **Side-by-Side**: Compare two charts
- **Studio Mode**: Large-screen optimized layout
- **Font Scaling**: Adjust for screen size
- **Theme**: Light/dark mode toggle

---

## API Reference

### BaseVisualization

All visualization classes inherit from `BaseVisualization`:

```python
class BaseVisualization:
    def __init__(self, title="", dark_mode=False, width=1200, height=600, sport="nfl"):
        ...

    def create(self, data, **kwargs) -> go.Figure:
        # Implement in subclass
        ...

    def save(self, filename, format='html', output_dir='visualizations/output'):
        ...

    def show(self):
        ...
```

### ColorScheme

Centralized color management:

```python
from visualizations.core.colors import ColorScheme

colors = ColorScheme()
colors.WIN  # '#00C853'
colors.LOSS  # '#D32F2F'
colors.get_team_color('KC')  # Team-specific color
colors.get_probability_gradient(0.75)  # Gradient color
```

---

## Examples

See `/home/user/sportstatbot/examples/visualization_examples.py` for complete usage examples.

---

## Support

For issues or questions:
1. Check this guide
2. Review example code
3. Inspect visualization source code in `/visualizations/`

---

**Built with Plotly, Dash, and Python** 🐍📊
