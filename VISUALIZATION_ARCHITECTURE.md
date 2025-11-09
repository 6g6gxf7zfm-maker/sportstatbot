# Sports Analytics Visualization Architecture

## Technology Stack

### Core Visualization Libraries
- **Plotly** - Primary interactive visualization library
  - Supports real-time updates, animations, 3D charts
  - Web-based, works with dashboards
  - Export to HTML, images, and videos

- **Matplotlib + Seaborn** - Static high-quality charts
  - Custom overlays and field graphics
  - Heatmaps and density plots

- **Bokeh** - Real-time streaming dashboards
  - Server-based interactive visualizations
  - Custom JavaScript callbacks

### Supporting Libraries
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations
- **Pillow (PIL)** - Image processing and overlays
- **imageio** - GIF/video generation
- **scipy** - Statistical calculations, Voronoi diagrams
- **networkx** - Flow diagrams and network visualizations

### Dashboard Framework
- **Dash by Plotly** - Web dashboard framework
  - Real-time updates
  - Interactive callbacks
  - Mobile-responsive layouts

## Module Structure

```
visualizations/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base_viz.py          # Base visualization class
│   ├── colors.py             # Color schemes and themes
│   ├── layouts.py            # Layout templates
│   └── utils.py              # Helper functions
├── field_graphics/
│   ├── __init__.py
│   ├── football_field.py     # NFL field overlay
│   ├── basketball_court.py   # NBA court overlay
│   ├── soccer_pitch.py       # Soccer field overlay
│   ├── baseball_diamond.py   # MLB diamond overlay
│   └── hockey_rink.py        # NHL rink overlay
├── charts/
│   ├── __init__.py
│   ├── heatmaps.py           # EPA heatmaps, calendar heatmaps (#26, #42)
│   ├── trajectories.py       # Shot trajectories (#27)
│   ├── timelines.py          # Momentum timelines (#28)
│   ├── scatter_plots.py      # Luck vs skill (#29)
│   ├── probability_charts.py # Fan charts, playoff odds (#30, #43)
│   ├── radar_charts.py       # Player comparisons (#31)
│   ├── worm_graphs.py        # Score tracking (#32)
│   ├── tree_maps.py          # Lineup usage (#33)
│   ├── flow_diagrams.py      # Turnover flows, ball movement (#34, #40)
│   ├── xg_visualizations.py  # Expected goals (#35, #39)
│   ├── depth_charts.py       # Team depth (#38)
│   ├── progress_bars.py      # Season progress (#41)
│   ├── histograms.py         # Shot distances (#48)
│   └── voronoi_maps.py       # Area control (#47)
├── animations/
│   ├── __init__.py
│   ├── clock_sync.py         # Clock-synchronized animations
│   ├── win_path.py           # Win path videos (#36)
│   ├── play_sequences.py     # Play-by-play animations (#49)
│   └── gif_exporter.py       # GIF generation
├── overlays/
│   ├── __init__.py
│   ├── broadcast_overlay.py  # Broadcast graphics (#37)
│   ├── confidence_glow.py    # Confidence visualization (#46)
│   └── ticker.py             # Probability ticker (#43)
├── dashboard/
│   ├── __init__.py
│   ├── app.py                # Main Dash app
│   ├── components.py         # Reusable components
│   ├── callbacks.py          # Interactive callbacks
│   ├── layouts.py            # Dashboard layouts
│   └── studio_view.py        # Large-screen view (#44)
└── integrations/
    ├── __init__.py
    ├── apple_notes.py        # Apple Notes integration (#50)
    └── export_manager.py     # Export to various formats
```

## Feature Implementation Map

### Real-time & Interactive (Features 26-50)

| # | Feature | Primary Library | Components |
|---|---------|----------------|------------|
| 26 | EPA heatmaps + clock sync | Plotly + Matplotlib | heatmaps.py, clock_sync.py |
| 27 | Shot trajectory replay | Plotly + field graphics | trajectories.py, field overlays |
| 28 | Momentum timeline | Plotly | timelines.py |
| 29 | Luck vs skill scatter | Plotly | scatter_plots.py |
| 30 | Playoff probability fan | Plotly | probability_charts.py |
| 31 | Radar player comparison | Plotly | radar_charts.py |
| 32 | Score worm graph | Plotly | worm_graphs.py |
| 33 | Lineup treemap | Plotly | tree_maps.py |
| 34 | Turnover flow diagram | Plotly + NetworkX | flow_diagrams.py |
| 35 | xG difference field | Plotly + Matplotlib | xg_visualizations.py |
| 36 | Win path video | Matplotlib + imageio | win_path.py |
| 37 | Broadcast overlay | Pillow + Plotly | broadcast_overlay.py |
| 38 | Depth chart | Plotly | depth_charts.py |
| 39 | Run/goal density surface | Plotly 3D | xg_visualizations.py |
| 40 | Ball movement chord | Plotly | flow_diagrams.py |
| 41 | Season progress bar | Plotly | progress_bars.py |
| 42 | Calendar heatmap | Plotly + Matplotlib | heatmaps.py |
| 43 | Probability ticker | Dash + Plotly | ticker.py |
| 44 | Dynamic font scaling | CSS + Dash | studio_view.py |
| 45 | Side-by-side compare | Dash | layouts.py |
| 46 | Confidence glow | Plotly + CSS | confidence_glow.py |
| 47 | Voronoi area control | SciPy + Plotly | voronoi_maps.py |
| 48 | Shot distance histogram | Plotly | histograms.py |
| 49 | Play sequence GIF | imageio + Matplotlib | gif_exporter.py |
| 50 | Chart-to-note link | AppleScript/JavaScript | apple_notes.py |

## Data Flow

```
Data Sources (ESPN API, etc.)
    ↓
Data Fetchers (existing)
    ↓
Analyzers (existing + new metrics)
    ↓
Visualization Generators (new)
    ↓
Dashboard / Export (new)
```

## Color Scheme

### Primary Colors
- **Win/Positive**: `#00C853` (Green)
- **Loss/Negative**: `#D32F2F` (Red)
- **Neutral**: `#607D8B` (Blue Gray)

### Heat Intensity
- Low: `#FFF9C4` (Light Yellow)
- Medium: `#FF9800` (Orange)
- High: `#D32F2F` (Red)

### Confidence Levels
- Very Low: `#FFCDD2` (Light Red, 20% opacity)
- Low: `#FFE082` (Light Orange, 40% opacity)
- Medium: `#FFF59D` (Light Yellow, 60% opacity)
- High: `#AED581` (Light Green, 80% opacity)
- Very High: `#66BB6A` (Green, 100% opacity)

### Team Colors
- Dynamically loaded based on team data
- Fallback to league defaults

## Performance Considerations

1. **Lazy Loading**: Load visualizations on demand
2. **Caching**: Cache generated charts for repeated requests
3. **Streaming**: Use Dash streaming for real-time updates
4. **Compression**: Compress images and videos for web delivery
5. **Responsive**: Mobile-first design, scales to large displays

## Export Formats

- **HTML**: Interactive, embeddable charts
- **PNG/JPG**: Static images for sharing
- **GIF**: Short animations
- **MP4**: Longer video sequences
- **JSON**: Chart data for external use
- **SVG**: Vector graphics for print quality

## Integration Points

1. **CLI**: `python cli.py --visualize --sport nfl --type heatmap`
2. **Dashboard**: `python dashboard.py` (new web server)
3. **API**: REST endpoints for chart generation
4. **Slack**: Embed chart images in reports
5. **Apple Notes**: Direct integration via AppleScript

## Next Steps

1. Install dependencies
2. Create base module structure
3. Implement field graphics (foundation)
4. Build each visualization feature
5. Create dashboard application
6. Add export capabilities
7. Integrate with existing report system
