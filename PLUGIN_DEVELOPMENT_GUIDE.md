# 🔌 SportStatBot Plugin Development Guide

This guide explains how to develop custom plugins for SportStatBot to add advanced features and capabilities.

## Table of Contents

1. [Plugin Architecture Overview](#plugin-architecture-overview)
2. [Creating Your First Plugin](#creating-your-first-plugin)
3. [Plugin Categories](#plugin-categories)
4. [Plugin Lifecycle](#plugin-lifecycle)
5. [Best Practices](#best-practices)
6. [Testing Plugins](#testing-plugins)
7. [Examples](#examples)

---

## Plugin Architecture Overview

SportStatBot uses a modular plugin system that allows you to extend functionality without modifying core code. Plugins are:

- **Modular**: Each plugin is self-contained
- **Configurable**: Enable/disable via YAML config
- **Categorized**: Organized by function (analytics, predictors, generators, visualizers)
- **Prioritized**: Execute in order of importance
- **Validated**: Automatic validation before execution

### Directory Structure

```
sportstatbot/
├── plugins/
│   ├── __init__.py
│   ├── base_plugin.py          # Abstract base class
│   ├── plugin_manager.py       # Plugin loading and execution
│   ├── analytics/              # Analytics plugins
│   │   ├── __init__.py
│   │   ├── historical_matchup_analyzer.py
│   │   └── milestone_tracker.py
│   ├── predictors/             # Prediction plugins
│   │   └── __init__.py
│   ├── generators/             # Content generation plugins
│   │   ├── __init__.py
│   │   └── narrative_detector.py
│   └── visualizers/            # Visualization plugins
│       └── __init__.py
└── config/
    └── plugins.yaml            # Plugin configuration
```

---

## Creating Your First Plugin

### Step 1: Choose a Category

Decide which category your plugin belongs to:
- **Analytics**: Statistical analysis and metrics
- **Predictors**: Forecasting and probability
- **Generators**: Content and narrative creation
- **Visualizers**: Charts and graphs
- **Validators**: Data quality checks
- **Exporters**: Data export formats

### Step 2: Create Your Plugin File

Create a new Python file in the appropriate category directory:

```bash
# Example: Creating a new analytics plugin
touch plugins/analytics/my_custom_analyzer.py
```

### Step 3: Implement the BasePlugin Interface

```python
"""My Custom Analyzer Plugin."""
from typing import Dict, Any, List
from ..base_plugin import BasePlugin, PluginCategory, PluginPriority


class MyCustomAnalyzer(BasePlugin):
    """
    Brief description of what your plugin does.
    """

    @property
    def name(self) -> str:
        """Unique identifier for your plugin."""
        return "my_custom_analyzer"

    @property
    def version(self) -> str:
        """Plugin version (semantic versioning)."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Short description of plugin functionality."""
        return "Analyzes custom metrics for advanced insights"

    @property
    def category(self) -> PluginCategory:
        """Plugin category."""
        return PluginCategory.ANALYTICS

    @property
    def priority(self) -> PluginPriority:
        """Execution priority (HIGH, MEDIUM, LOW)."""
        return PluginPriority.MEDIUM

    @property
    def required_data_sources(self) -> List[str]:
        """List of required data sources (optional)."""
        return ['espn_api']

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main plugin logic.

        Args:
            data: Input data containing:
                - sport: Sport identifier (nfl, nba, etc.)
                - sport_data: Current sport data
                - scoreboard: Recent games
                - standings: Current standings
                - news: Recent news articles

        Returns:
            Dictionary with your analysis results
        """
        sport = data.get('sport')
        sport_data = data.get('sport_data', {})

        # Your custom analysis logic here
        results = self._analyze(sport_data)

        return {
            'custom_metric': results
        }

    def _analyze(self, sport_data: Dict[str, Any]) -> Any:
        """Private helper method for analysis."""
        # Implementation details
        pass
```

### Step 4: Configure Your Plugin

Add your plugin configuration to `config/plugins.yaml`:

```yaml
plugins:
  my_custom_analyzer:
    enabled: true
    priority: medium
    description: "Analyzes custom metrics for advanced insights"
    # Add any custom configuration options
    custom_setting: value
```

### Step 5: Test Your Plugin

Create a test script to verify your plugin works:

```python
from plugins.plugin_manager import PluginManager

# Initialize plugin manager
manager = PluginManager()

# Load your plugin
manager.load_plugin('plugins.analytics.my_custom_analyzer')

# Test execution
test_data = {
    'sport': 'nfl',
    'sport_data': {
        'recent_games': [],
        'standings': []
    }
}

result = manager.execute_plugin('my_custom_analyzer', test_data)
print(result)
```

---

## Plugin Categories

### Analytics Plugins
**Purpose**: Perform statistical analysis and generate metrics

**Common Use Cases**:
- Team style analysis (offensive/defensive patterns)
- Player performance metrics
- Historical trend analysis
- Efficiency ratings

**Example**: `milestone_tracker.py` - Tracks players approaching career milestones

### Predictor Plugins
**Purpose**: Generate forecasts and probability calculations

**Common Use Cases**:
- Championship probability
- Game outcome prediction
- Streak likelihood
- Performance forecasting

**Example**: Coming soon - `championship_predictor.py`

### Generator Plugins
**Purpose**: Create content and narratives

**Common Use Cases**:
- Game narrative classification
- Story theme detection
- Automated glossaries
- Commentary generation

**Example**: `narrative_detector.py` - Classifies games as Comeback, Blowout, etc.

### Visualizer Plugins
**Purpose**: Create visual representations of data

**Common Use Cases**:
- Season trajectory graphs
- Performance heatmaps
- Timeline visualizations
- Statistical charts

**Example**: Coming soon - `season_graph.py`

---

## Plugin Lifecycle

### 1. Discovery
Plugin manager scans plugin directories for valid plugin files.

### 2. Loading
Plugins are imported and instantiated:
```python
manager = PluginManager(config)
manager.load_all_plugins()
```

### 3. Configuration
Plugin receives configuration from `plugins.yaml`:
```python
plugin.configure(config_dict)
```

### 4. Validation
Plugin validates it can execute properly:
```python
if plugin.validate():
    # Plugin is ready
```

### 5. Execution
Plugin processes data:
```python
result = plugin.execute(data)
```

### 6. Cleanup
Plugin cleans up resources:
```python
plugin.cleanup()
```

---

## Best Practices

### Code Organization

1. **One Plugin Per File**: Each plugin should be in its own file
2. **Clear Naming**: Use descriptive names (e.g., `historical_matchup_analyzer.py`)
3. **Documentation**: Include docstrings for all methods
4. **Type Hints**: Use type hints for better IDE support

### Error Handling

```python
def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Your logic
        result = self._process(data)
        return result
    except Exception as e:
        # Log error and return graceful failure
        print(f"Error in {self.name}: {e}")
        return self.on_error(e)
```

### Configuration

```python
def configure(self, config: Dict[str, Any]) -> None:
    """Configure plugin with settings."""
    super().configure(config)

    # Extract custom settings
    self.threshold = config.get('threshold', 0.95)
    self.max_results = config.get('max_results', 10)
```

### Performance

1. **Cache Results**: Cache expensive computations
2. **Lazy Loading**: Only load data when needed
3. **Timeouts**: Set timeouts for API calls
4. **Batch Processing**: Process multiple items efficiently

```python
def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
    # Check cache first
    cache_key = f"{self.name}_{data.get('sport')}"
    if cache_key in self._cache:
        return self._cache[cache_key]

    # Compute and cache
    result = self._compute(data)
    self._cache[cache_key] = result
    return result
```

---

## Testing Plugins

### Unit Testing

Create test files for your plugins:

```python
# tests/test_my_plugin.py
import unittest
from plugins.analytics.my_custom_analyzer import MyCustomAnalyzer


class TestMyCustomAnalyzer(unittest.TestCase):

    def setUp(self):
        self.plugin = MyCustomAnalyzer()

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.name, "my_custom_analyzer")
        self.assertEqual(self.plugin.version, "1.0.0")

    def test_execution(self):
        test_data = {
            'sport': 'nfl',
            'sport_data': {}
        }
        result = self.plugin.execute(test_data)
        self.assertIsInstance(result, dict)

    def test_validation(self):
        self.assertTrue(self.plugin.validate())
```

### Integration Testing

Test plugins with real data:

```python
# test_integration.py
from plugins.plugin_manager import PluginManager
from report_generator import SportsReportGenerator

# Initialize
manager = PluginManager()
generator = SportsReportGenerator()

# Load plugins
manager.load_all_plugins()

# Generate report with plugins
report_data = generator._generate_sport_data('nfl')

# Execute plugin category
results = manager.execute_category(
    PluginCategory.ANALYTICS,
    {'sport': 'nfl', 'sport_data': report_data}
)

print(f"Plugin results: {results}")
```

---

## Examples

### Example 1: Simple Analytics Plugin

```python
"""Win Probability Calculator Plugin."""
from typing import Dict, Any
from ..base_plugin import BasePlugin, PluginCategory, PluginPriority


class WinProbabilityCalculator(BasePlugin):
    """Calculates live win probability based on game state."""

    @property
    def name(self) -> str:
        return "win_probability_calculator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Calculates win probability for in-progress games"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.ANALYTICS

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        games = data.get('sport_data', {}).get('recent_games', [])
        probabilities = []

        for game in games:
            if game.get('status') == 'in_progress':
                prob = self._calculate_probability(game)
                probabilities.append({
                    'game': game.get('matchup'),
                    'home_win_prob': prob,
                    'away_win_prob': 1 - prob
                })

        return {'win_probabilities': probabilities}

    def _calculate_probability(self, game: Dict[str, Any]) -> float:
        # Simplified calculation
        score_diff = game.get('home_score', 0) - game.get('away_score', 0)
        time_remaining = game.get('time_remaining', 60)

        # Very basic model - real implementation would be more sophisticated
        base_prob = 0.5
        score_factor = score_diff * 0.05
        time_factor = (60 - time_remaining) / 60 * 0.3

        return max(0.0, min(1.0, base_prob + score_factor + time_factor))
```

### Example 2: Predictor Plugin with ML

```python
"""Game Outcome Predictor using ML."""
from typing import Dict, Any
from ..base_plugin import BasePlugin, PluginCategory, PluginPriority


class GameOutcomePredictor(BasePlugin):
    """Predicts game outcomes using machine learning."""

    @property
    def name(self) -> str:
        return "game_outcome_predictor"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Predicts game outcomes using historical data and ML"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.PREDICTOR

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.HIGH

    def __init__(self):
        super().__init__()
        self.model = None

    def configure(self, config: Dict[str, Any]) -> None:
        super().configure(config)
        # Load ML model
        model_path = config.get('model_path', 'models/predictor.pkl')
        self._load_model(model_path)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        upcoming_games = data.get('sport_data', {}).get('must_watch', [])
        predictions = []

        for game in upcoming_games:
            features = self._extract_features(game, data)
            prediction = self._predict(features)
            predictions.append({
                'game': game.get('matchup'),
                'predicted_winner': prediction['winner'],
                'confidence': prediction['confidence']
            })

        return {'predictions': predictions}

    def _load_model(self, path: str):
        # Load your ML model here
        # For example: self.model = joblib.load(path)
        pass

    def _extract_features(self, game: Dict, data: Dict) -> Dict:
        # Extract features for ML model
        return {}

    def _predict(self, features: Dict) -> Dict:
        # Make prediction using ML model
        return {'winner': 'home', 'confidence': 0.65}
```

---

## Advanced Topics

### Plugin Dependencies

If your plugin depends on another plugin:

```python
@property
def dependencies(self) -> List[str]:
    return ['historical_matchup_analyzer']
```

The plugin manager will ensure dependencies are loaded first.

### Custom Data Sources

To integrate custom data sources:

```python
@property
def required_data_sources(self) -> List[str]:
    return ['custom_api', 'local_database']

def validate(self) -> bool:
    # Check if data sources are available
    if not self._check_api_access():
        print(f"{self.name}: Required API not accessible")
        return False
    return super().validate()
```

### Async Plugins

For plugins that need async operations:

```python
import asyncio

class AsyncPlugin(BasePlugin):
    async def fetch_data(self):
        # Async API calls
        pass

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Run async code synchronously
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.fetch_data())
        return result
```

---

## Plugin Management Commands

### List All Plugins

```python
from plugins.plugin_manager import PluginManager

manager = PluginManager()
manager.load_all_plugins()

# Get plugin stats
stats = manager.get_stats()
print(f"Total plugins: {stats['total_plugins']}")
print(f"Enabled: {stats['enabled_plugins']}")

# List all plugins
for plugin_info in manager.list_plugins():
    print(f"{plugin_info['name']}: {plugin_info['description']}")
```

### Enable/Disable Plugins

```python
# Disable a plugin
manager.disable_plugin('my_custom_analyzer')

# Enable a plugin
manager.enable_plugin('my_custom_analyzer')
```

---

## Contributing Plugins

Want to contribute your plugin to SportStatBot?

1. **Fork the repository**
2. **Create your plugin** following this guide
3. **Write tests** for your plugin
4. **Update documentation** in `FUTURE_FEATURES_ROADMAP.md`
5. **Submit a pull request**

### Contribution Checklist

- [ ] Plugin follows BasePlugin interface
- [ ] Clear docstrings and type hints
- [ ] Unit tests included
- [ ] Configuration in plugins.yaml
- [ ] README update if needed
- [ ] Example usage provided

---

## Resources

- **BasePlugin API**: See `plugins/base_plugin.py`
- **Plugin Manager**: See `plugins/plugin_manager.py`
- **Example Plugins**: See `plugins/*/` directories
- **Configuration**: See `config/plugins.yaml`
- **Roadmap**: See `FUTURE_FEATURES_ROADMAP.md`

---

**Happy Plugin Development! 🚀**

For questions or issues, please open an issue in the repository.
