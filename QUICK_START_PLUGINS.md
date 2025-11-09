# 🚀 Quick Start: Plugin System

Get started with SportStatBot's advanced plugin features in 5 minutes!

## Step 1: Try the Demo

Run the plugin demo to see what's available:

```bash
python demo_plugins.py
```

This will:
- Load all available plugins
- Show plugin statistics
- Run sample tests
- Display example outputs

## Step 2: Enable Plugins

Edit `config/plugins.yaml` to enable/disable features:

```yaml
plugins:
  # Enable game narrative detection
  game_narrative_detector:
    enabled: true

  # Enable historical matchup analysis
  historical_matchup_analyzer:
    enabled: true

  # Enable milestone tracking
  milestone_tracker:
    enabled: true
```

## Step 3: Use Plugins in Reports

Integrate plugins into your report generation:

```python
from plugins.plugin_manager import PluginManager
from plugins.base_plugin import PluginCategory

# Initialize plugin manager
manager = PluginManager()
manager.load_all_plugins()

# Your existing report data
report_data = {
    'sport': 'nfl',
    'sport_data': {
        'recent_games': [...],
        'must_watch': [...]
    }
}

# Execute analytics plugins
analytics_results = manager.execute_category(
    PluginCategory.ANALYTICS,
    report_data
)

# Execute generator plugins
generator_results = manager.execute_category(
    PluginCategory.GENERATOR,
    report_data
)

# Add plugin results to your report
print(analytics_results)
print(generator_results)
```

## Available Plugins

### 🎯 Game Narrative Detector
Classifies games automatically:
- **Blowout** - Dominant performance
- **Thriller** - Down-to-the-wire finish
- **Defensive Battle** - Low-scoring showcase
- **Shootout** - High-scoring explosion

### 📊 Historical Matchup Analyzer
Provides context for rivalries:
- All-time head-to-head records
- Recent trend analysis
- Average scoring patterns
- Playoff history

### 🏆 Milestone Tracker
Tracks players approaching:
- 10,000 career yards
- 500 career goals/home runs
- 1,000 career games
- Hall of Fame benchmarks

## Plugin Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Analytics** | Statistical analysis | Historical matchups, milestones |
| **Predictors** | Forecasting | Championship probability |
| **Generators** | Content creation | Game narratives, glossaries |
| **Visualizers** | Charts & graphs | Season graphs, timelines |

## Next Steps

1. **View the Roadmap**: See [FUTURE_FEATURES_ROADMAP.md](FUTURE_FEATURES_ROADMAP.md) for 30+ planned features

2. **Create Your Own Plugin**: Follow [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md)

3. **Configure Features**: Edit `config/plugins.yaml` to customize behavior

## Example: Create a Simple Plugin

```python
# plugins/analytics/my_stat.py
from ..base_plugin import BasePlugin, PluginCategory

class MyStatPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_stat"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "My custom stat analyzer"

    @property
    def category(self) -> PluginCategory:
        return PluginCategory.ANALYTICS

    def execute(self, data):
        # Your analysis logic
        return {'my_stat': 'calculated value'}
```

Then enable in `config/plugins.yaml`:

```yaml
plugins:
  my_stat:
    enabled: true
    priority: medium
```

That's it! 🎉

## Troubleshooting

**Plugins not loading?**
- Check file is in correct directory: `plugins/analytics/`, `plugins/generators/`, etc.
- Verify plugin inherits from `BasePlugin`
- Check `config/plugins.yaml` has plugin enabled

**Import errors?**
- Make sure `__init__.py` files exist in plugin directories
- Use relative imports: `from ..base_plugin import BasePlugin`

**Plugin execution fails?**
- Check plugin's `validate()` method returns `True`
- Verify required data sources are available
- Look at error messages in plugin's `on_error()` method

## Resources

- 📖 [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) - Complete developer guide
- 🗺️ [FUTURE_FEATURES_ROADMAP.md](FUTURE_FEATURES_ROADMAP.md) - Feature roadmap
- 📝 [README.md](README.md) - Main documentation
- 🧪 [demo_plugins.py](demo_plugins.py) - Example usage

---

**Need Help?** Open an issue in the repository!
