#!/usr/bin/env python3
"""
Demo script showing plugin system capabilities.

This script demonstrates how to:
1. Load and configure plugins
2. Execute plugins on sample data
3. Display plugin results
"""
from typing import Dict, Any
from plugins.plugin_manager import PluginManager
from plugins.base_plugin import PluginCategory
import json


def main():
    """Run plugin system demo."""
    print("=" * 80)
    print("🔌 SportStatBot Plugin System Demo")
    print("=" * 80)
    print()

    # Initialize plugin manager
    print("Initializing plugin manager...")
    manager = PluginManager()

    # Load all available plugins
    print("Loading plugins from plugins/ directory...")
    loaded = manager.load_all_plugins()
    print(f"✅ Loaded {loaded} plugin(s)\n")

    # Display plugin stats
    stats = manager.get_stats()
    print("📊 Plugin Statistics:")
    print(f"  Total Plugins: {stats['total_plugins']}")
    print(f"  Enabled: {stats['enabled_plugins']}")
    print(f"  Disabled: {stats['disabled_plugins']}")
    print(f"  By Category:")
    for category, count in stats['by_category'].items():
        if count > 0:
            print(f"    - {category}: {count}")
    print()

    # List all plugins
    print("📋 Available Plugins:")
    print("-" * 80)
    for plugin_info in manager.list_plugins():
        status = "✅" if plugin_info['enabled'] else "❌"
        print(f"{status} {plugin_info['name']}")
        print(f"   Version: {plugin_info['version']}")
        print(f"   Category: {plugin_info['category']}")
        print(f"   Priority: {plugin_info['priority']}")
        print(f"   Description: {plugin_info['description']}")
        print()

    # Create sample data
    print("=" * 80)
    print("🧪 Testing Plugins with Sample Data")
    print("=" * 80)
    print()

    sample_data = create_sample_data()

    # Test Game Narrative Detector
    print("1️⃣  Testing Game Narrative Detector...")
    print("-" * 80)
    narrative_results = manager.execute_plugin('game_narrative_detector', sample_data)
    if 'narratives' in narrative_results:
        for narrative in narrative_results['narratives']:
            print(f"   Game: {narrative['game']}")
            print(f"   Narrative: {narrative['narrative']}")
            print(f"   Description: {narrative['description']}")
            print(f"   Intensity: {narrative['intensity']}")
            print()
    else:
        print(f"   Result: {narrative_results}")
        print()

    # Test Historical Matchup Analyzer
    print("2️⃣  Testing Historical Matchup Analyzer...")
    print("-" * 80)
    historical_results = manager.execute_plugin('historical_matchup_analyzer', sample_data)
    if 'historical_analysis' in historical_results:
        for analysis in historical_results['historical_analysis']:
            print(f"   Matchup: {analysis['matchup']}")
            print(f"   All-time Record: {analysis['analysis']['all_time_record']['description']}")
            print()
    else:
        print(f"   Result: {historical_results}")
        print()

    # Test Milestone Tracker
    print("3️⃣  Testing Milestone Tracker...")
    print("-" * 80)
    milestone_results = manager.execute_plugin('milestone_tracker', sample_data)
    if 'approaching_milestones' in milestone_results:
        if milestone_results['approaching_milestones']:
            for milestone in milestone_results['approaching_milestones']:
                print(f"   Player: {milestone['player']} ({milestone['team']})")
                for m in milestone['milestones']:
                    print(f"   - {m['stat']}: {m['current']}/{m['milestone']}")
                    print(f"     Remaining: {m['remaining']}")
                    print(f"     Significance: {m['significance']}")
                print()
        else:
            print("   No players approaching milestones in sample data")
            print()
    else:
        print(f"   Result: {milestone_results}")
        print()

    # Execute entire category
    print("=" * 80)
    print("📦 Testing Plugin Category Execution")
    print("=" * 80)
    print()

    print("Executing all GENERATOR plugins...")
    generator_results = manager.execute_category(PluginCategory.GENERATOR, sample_data)
    print(f"Executed {len(generator_results)} generator plugin(s)")
    for plugin_name, result in generator_results.items():
        print(f"  - {plugin_name}: {list(result.keys())}")
    print()

    print("Executing all ANALYTICS plugins...")
    analytics_results = manager.execute_category(PluginCategory.ANALYTICS, sample_data)
    print(f"Executed {len(analytics_results)} analytics plugin(s)")
    for plugin_name, result in analytics_results.items():
        print(f"  - {plugin_name}: {list(result.keys())}")
    print()

    # Summary
    print("=" * 80)
    print("✅ Plugin Demo Complete!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. View FUTURE_FEATURES_ROADMAP.md for planned features")
    print("  2. Read PLUGIN_DEVELOPMENT_GUIDE.md to create your own plugins")
    print("  3. Configure plugins in config/plugins.yaml")
    print("  4. Integrate plugins into report_generator.py for production use")
    print()


def create_sample_data() -> Dict[str, Any]:
    """
    Create sample data for testing plugins.

    Returns:
        Sample data dictionary with games, players, etc.
    """
    return {
        'sport': 'nfl',
        'sport_data': {
            'recent_games': [
                {
                    'matchup': 'Chiefs vs Bills',
                    'home_team': 'Chiefs',
                    'away_team': 'Bills',
                    'home_score': 31,
                    'away_score': 28,
                    'status': 'final'
                },
                {
                    'matchup': 'Patriots vs Giants',
                    'home_team': 'Patriots',
                    'away_team': 'Giants',
                    'home_score': 45,
                    'away_score': 10,
                    'status': 'final'
                },
                {
                    'matchup': 'Ravens vs Steelers',
                    'home_team': 'Ravens',
                    'away_team': 'Steelers',
                    'home_score': 24,
                    'away_score': 23,
                    'status': 'final'
                },
                {
                    'matchup': 'Packers vs Bears',
                    'home_team': 'Packers',
                    'away_team': 'Bears',
                    'home_score': 13,
                    'away_score': 10,
                    'status': 'final'
                }
            ],
            'standout_players': [
                {
                    'name': 'Patrick Mahomes',
                    'team': 'Chiefs',
                    'stats': {
                        'passing_yards': 368,
                        'touchdowns': 3
                    }
                },
                {
                    'name': 'Josh Allen',
                    'team': 'Bills',
                    'stats': {
                        'passing_yards': 342,
                        'touchdowns': 2
                    }
                }
            ],
            'must_watch': [
                {
                    'home_team': 'Cowboys',
                    'away_team': 'Eagles',
                    'date': '2025-11-10',
                    'time': '8:20 PM'
                }
            ]
        }
    }


if __name__ == '__main__':
    main()
