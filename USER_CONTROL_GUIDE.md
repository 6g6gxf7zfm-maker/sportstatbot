# 🎮 SportStatBot User Control Interface Guide

Complete guide to the interactive control interface for SportStatBot.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Control Panel](#control-panel)
- [Dashboard & Metrics](#dashboard--metrics)
- [League Management](#league-management)
- [Experiment Mode](#experiment-mode)
- [Workflow Archive](#workflow-archive)
- [Manual Editor Notes](#manual-editor-notes)
- [Advanced Features](#advanced-features)

---

## Overview

The User Control Interface provides comprehensive control over SportStatBot operations through an interactive command-line interface. Features include:

- **Command interface** - Execute commands like "Generate all digests" or "Export last 24h"
- **League toggles** - Enable/disable coverage for specific leagues
- **Priority ranking** - Set manual priority ordering (e.g., "NBA > NHL tonight")
- **Data window selection** - Choose lookback period (3, 5, 10 days)
- **Output length control** - Set brief/medium/in-depth reports
- **Dashboard** - Monitor which agents ran last and their performance
- **Agent metrics** - Track accuracy and timeliness
- **Manual notes** - Add human editor notes before publishing
- **Experiment mode** - Test new prompt variations safely
- **Workflow archive** - Version control for workflows with notes

---

## Getting Started

### Starting Interactive Mode

```bash
python interactive_control.py
```

You'll see the interactive prompt:

```
🎮 SportStatBot Interactive Control Panel
Type 'help' for available commands or 'exit' to quit

sportstat>
```

### Quick Status Check

```bash
# Show current status
python interactive_control.py --status

# Show dashboard
python interactive_control.py --dashboard
```

### Execute Single Command

```bash
# Execute a command without entering interactive mode
python interactive_control.py --command "generate-all"
python interactive_control.py --command "toggle nfl"
```

---

## Control Panel

The control panel is your main interface for managing SportStatBot operations.

### Quick Commands

#### Generate All Digests

Generate reports for all currently enabled leagues:

```
sportstat> generate-all
```

#### Export Last 24 Hours

Export all reports from the last 24 hours:

```
sportstat> export-24h
```

#### View Status

See current system configuration and recent activity:

```
sportstat> status
```

Example output:

```
======================================================================
🎮 SPORTSTATBOT CONTROL PANEL
======================================================================

📊 LEAGUE STATUS:
  1. ✅ 🏈 NFL (nfl)
  2. ✅ 🏀 NBA (nba)
  3. ❌ ⚾ MLB (mlb)
  4. ✅ 🏒 NHL (nhl)
  5. ✅ ⚽ MLS (mls)

⚙️  SETTINGS:
  Data Window: 3 days
  Output Length: medium
  Max Lines: 150

🤖 RECENT AGENT ACTIVITY:
  ✅ report_generator - 2025-11-09 14:30
  ✅ analyzer - 2025-11-09 14:15
======================================================================
```

---

## Dashboard & Metrics

Monitor agent performance and system health.

### Full Dashboard

```
sportstat> dashboard
sportstat> dashboard 48    # Last 48 hours
```

Shows:
- Performance metrics (success rate, execution time)
- League coverage statistics
- Recent activity log
- Errors and failures
- Timeliness score

### Compact Dashboard

Quick overview without details:

```
sportstat> compact
sportstat> compact 24
```

### System Alerts

Check for issues requiring attention:

```
sportstat> alerts
```

Example output:

```
⚠️  ALERTS:
  ⚠️  Low success rate: 75% (3 failures)
  ⚠️  No coverage for enabled leagues: mlb
```

---

## League Management

### Toggle Leagues

Enable or disable individual leagues:

```
sportstat> toggle nfl
✅ 🏈 NFL (nfl) is now enabled

sportstat> toggle mlb
✅ ⚾ MLB (mlb) is now disabled
```

### Set Priority Ranking

Define which leagues get priority (highest to lowest):

```
sportstat> priority nfl nba nhl mlb mls soccer golf
✅ Priority ranking updated: nfl > nba > nhl > mlb > mls > soccer > golf
```

This affects:
- Order in which reports are generated
- Resource allocation for analysis
- Display order in combined reports

### Custom Data Window

Set how many days back to analyze:

```
sportstat> window 5
✅ Data window set to 5 days

sportstat> window 10
✅ Data window set to 10 days
```

Common windows:
- **3 days** - Recent trends, quick updates
- **5 days** - Weekly analysis
- **10 days** - Extended trends
- **14 days** - Two-week patterns
- **30 days** - Monthly overview

### Output Length Control

Choose report detail level:

```
sportstat> length brief
✅ Output length set to 'brief' (max 50 lines)

sportstat> length medium
✅ Output length set to 'medium' (max 150 lines)

sportstat> length in-depth
✅ Output length set to 'in-depth' (max 500 lines)
```

**Brief** - Quick headlines and scores
**Medium** - Standard analysis with key insights
**In-depth** - Comprehensive analysis with detailed stats

---

## Experiment Mode

Safely test new prompt variations without affecting production.

### Create New Experiment

```
sportstat> experiment create "Better injury analysis"
Enter description:
  > Test more detailed injury impact analysis with return timeline predictions
Enter prompt variation (or 'default' to use current):
  > Analyze each injury with 3 factors: severity, timeline, team impact. Include historical recovery data.

✅ Created experiment: better_injury_analysis_20251109_143000
```

### List Experiments

```
sportstat> list-experiments
sportstat> list-experiments active      # Only active
sportstat> list-experiments completed   # Only completed
```

Example output:

```
🔬 EXPERIMENTS:
  🟢 better_injury_analysis_20251109_143000 - Better injury analysis (3 runs)
  📝 new_betting_insights_20251108_120000 - Enhanced betting insights (0 runs)
  ✅ player_stats_v2_20251107_090000 - Player stats v2 (12 runs)
```

### Activate Experiment

```
sportstat> experiment activate better_injury_analysis_20251109_143000
✅ Activated experiment: better_injury_analysis_20251109_143000
```

### View Experiment Details

```
sportstat> experiment show better_injury_analysis_20251109_143000
```

### Compare Experiments

Compare results between two experiments:

```
sportstat> experiment compare better_injury_analysis_20251109_143000 baseline_20251101_100000
```

Example output:

```
🔬 EXPERIMENT COMPARISON:
Experiment: better_injury_analysis_20251109_143000
Baseline: baseline_20251101_100000

Differences:
  📈 accuracy: 92 vs 85 (+8.2%)
  📉 execution_time: 12.5 vs 10.2 (+22.5%)
  ➡️  report_length: 145 vs 145 (0.0%)
```

---

## Workflow Archive

Version control for workflows with detailed notes.

### List Workflows

```
sportstat> list-workflows
```

Example output:

```
📚 ARCHIVED WORKFLOWS:
  • nfl_report_workflow
  • injury_analysis_workflow
  • betting_insights_workflow
```

### View Workflow Versions

```
sportstat> archive list nfl_report_workflow
```

Example output:

```
📚 VERSIONS: nfl_report_workflow
  ✅ v3_20251109_140000 - 2025-11-09 14:00 by john
  🗄️  v2_20251108_100000 - 2025-11-08 10:00 by jane
  🗄️  v1_20251107_090000 - 2025-11-07 09:00 by system
```

### View Version Notes

```
sportstat> archive show nfl_report_workflow
sportstat> archive show nfl_report_workflow v2_20251108_100000
```

Example output:

```
📚 VERSION HISTORY: nfl_report_workflow

v3_20251109_140000 - ✅ ACTIVE
  Date: 2025-11-09 14:00:00
  Author: john
  Notes: Added playoff implications analysis and improved QB rating calculations

v2_20251108_100000 - 🗄️  ARCHIVED
  Date: 2025-11-08 10:00:00
  Author: jane
  Notes: Enhanced injury report integration

v1_20251107_090000 - 🗄️  ARCHIVED
  Date: 2025-11-07 09:00:00
  Author: system
  Notes: Initial workflow version
```

### Export Workflow

```
sportstat> archive export nfl_report_workflow
✅ Exported to: exports/nfl_report_workflow_20251109_143000.json
```

---

## Manual Editor Notes

Add human editor notes that can be included in reports.

### Add a Note

```
sportstat> note Remember to highlight the Chiefs playoff clinch scenario
✅ Note added

sportstat> note Check latest Mahomes injury status nfl
✅ Note added for nfl
```

### View Pending Notes

```
sportstat> notes
sportstat> notes nfl    # Only NFL notes
```

Example output:

```
📝 PENDING NOTES:
  [ALL] 2025-11-09 14:30: Remember to highlight the Chiefs playoff clinch scenario
  [nfl] 2025-11-09 14:32: Check latest Mahomes injury status
```

Notes are marked as "pending" until applied to a report.

---

## Advanced Features

### Voice Input Support (Future Feature)

While voice input is planned for future releases, you can prepare for it by:

1. Using consistent command syntax
2. Keeping notes concise and clear
3. Following the command patterns shown in this guide

### Integration with Report Generator

The control panel integrates with the report generator:

```python
from user_interface import ControlPanel

panel = ControlPanel()
config = panel.get_current_config()

# Use config in report generation
enabled_leagues = config['enabled_leagues']
priority_order = config['priority_ranking']
data_window = config['data_window_days']
output_level = config['output_level']
```

### Programmatic Access

Use control panel features in your own scripts:

```python
from user_interface import ControlPanel, Dashboard, ExperimentMode

# Control panel
panel = ControlPanel()
panel.preferences.toggle_league('nfl', True)
panel.preferences.set_priority_ranking(['nfl', 'nba', 'mlb'])

# Dashboard
dashboard = Dashboard()
print(dashboard.render_compact_dashboard(24))
alerts = dashboard.get_alerts(24)

# Experiments
experiments = ExperimentMode()
exp_id = experiments.create_experiment(
    name="New Analysis",
    description="Testing enhanced analysis",
    prompt_variation="New prompt here"
)
experiments.activate_experiment(exp_id)
```

---

## Command Reference

### Control Panel
| Command | Args | Description |
|---------|------|-------------|
| `generate-all` | - | Generate all digests |
| `export-24h` | - | Export last 24h reports |
| `toggle` | `<league>` | Toggle league on/off |
| `priority` | `<leagues...>` | Set priority order |
| `window` | `<days>` | Set data window |
| `length` | `<level>` | Set output length |
| `status` | - | Show status |

### Dashboard
| Command | Args | Description |
|---------|------|-------------|
| `dashboard` | `[hours]` | Full dashboard |
| `compact` | `[hours]` | Compact dashboard |
| `alerts` | - | System alerts |

### Experiments
| Command | Args | Description |
|---------|------|-------------|
| `experiment create` | `<name>` | Create experiment |
| `experiment activate` | `<id>` | Activate experiment |
| `experiment show` | `<id>` | Show details |
| `experiment compare` | `<id1> <id2>` | Compare experiments |
| `list-experiments` | `[status]` | List experiments |

### Archive
| Command | Args | Description |
|---------|------|-------------|
| `archive list` | `<workflow>` | List versions |
| `archive show` | `<workflow> [ver]` | Show version notes |
| `archive export` | `<workflow>` | Export workflow |
| `list-workflows` | - | List all workflows |

### Notes
| Command | Args | Description |
|---------|------|-------------|
| `note` | `<text> [league]` | Add manual note |
| `notes` | `[league]` | Show pending notes |

### General
| Command | Args | Description |
|---------|------|-------------|
| `help` | - | Show help |
| `exit` / `quit` | - | Exit interface |

---

## Tips & Best Practices

### Performance Optimization

1. **Use priority ranking** - Put most important leagues first
2. **Adjust data window** - Smaller windows = faster processing
3. **Choose appropriate output length** - Brief for quick updates

### Workflow Management

1. **Archive before major changes** - Always save versions
2. **Document changes** - Use detailed version notes
3. **Test with experiments** - Never change production directly

### Monitoring

1. **Check dashboard daily** - Monitor success rates
2. **Review alerts** - Address issues promptly
3. **Track agent performance** - Identify bottlenecks

### Experimentation

1. **Start with small changes** - Test one variable at a time
2. **Compare with baseline** - Always measure improvement
3. **Document results** - Record what works and what doesn't

---

## Troubleshooting

### Commands Not Working

```bash
# Check if you're in interactive mode
sportstat> help

# If outside interactive mode, use:
python interactive_control.py --command "status"
```

### Preferences Not Saving

```bash
# Check data directory exists
ls -la data/

# Recreate if needed
mkdir -p data
```

### Dashboard Shows No Data

```bash
# Check if agents have run
sportstat> dashboard 168  # Check last week

# Run a report to generate data
sportstat> generate-all
```

---

## Examples

### Daily Morning Routine

```bash
# Start interactive control
python interactive_control.py

# Check overnight activity
sportstat> dashboard
sportstat> alerts

# Review pending notes
sportstat> notes

# Set priorities for today
sportstat> priority nfl nba nhl
sportstat> window 3

# Generate reports
sportstat> generate-all

sportstat> exit
```

### Testing New Analysis

```bash
sportstat> experiment create "Enhanced playoff analysis"
# ... enter details ...

sportstat> experiment activate enhanced_playoff_analysis_20251109_100000

# Run test
sportstat> generate-all

# Check results
sportstat> experiment show enhanced_playoff_analysis_20251109_100000

# Compare with baseline
sportstat> experiment compare enhanced_playoff_analysis_20251109_100000 baseline_v1
```

### Weekly Maintenance

```bash
sportstat> dashboard 168  # Check week

# Export metrics
sportstat> export-24h

# Archive current workflows
sportstat> archive show nfl_report_workflow

# Clean up old experiments
sportstat> list-experiments completed
```

---

## Integration with Cursor

The control interface is designed to work seamlessly inside Cursor IDE:

1. Open integrated terminal in Cursor
2. Run `python interactive_control.py`
3. Use commands while developing
4. Quick status checks: `python interactive_control.py --status`

---

For more information, see the main [README.md](README.md) and [USAGE_GUIDE.md](USAGE_GUIDE.md).

**Questions or Issues?** Create an issue in the repository.
