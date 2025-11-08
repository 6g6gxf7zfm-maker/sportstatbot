#!/usr/bin/env python3
"""
Visualization Examples
======================
Example scripts demonstrating all visualization features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from visualizers.visualization_manager import VisualizationManager
from datetime import datetime, timedelta


def example_1_team_performance_suite():
    """Example 1: Complete team performance analysis."""
    print("=" * 70)
    print("EXAMPLE 1: Complete Team Performance Analysis")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/team_analysis')

    # Sample team data
    lakers_data = {
        'offensive_ratings': [112, 115, 110, 118, 113, 109, 114, 116, 111, 117],
        'defensive_ratings': [108, 105, 110, 103, 107, 109, 104, 106, 108, 102],
        'metrics': {
            'Offense': 88,
            'Defense': 82,
            'Rebounding': 75,
            'Assists': 90,
            'Turnovers': 70,
            'Three-Point%': 85
        },
        'recent_results': ['W', 'W', 'L', 'W', 'W', 'W', 'L', 'W', 'W', 'W'],
        'wins': 48,
        'losses': 22,
        'target_wins': 52,
        'playoff_threshold': 45
    }

    charts = manager.generate_team_analysis_suite('Los Angeles Lakers', lakers_data)

    print(f"\n✅ Generated {len(charts)} team analysis charts:")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {os.path.basename(chart)}")

    return charts


def example_2_head_to_head_matchup():
    """Example 2: Head-to-head matchup analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Head-to-Head Matchup Analysis")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/matchups')

    # Sample matchup data
    matchup_data = {
        'momentum_score': 42,  # Warriors favor
        'team_metrics': {
            'Lakers': {
                'Offense': 88,
                'Defense': 82,
                'Pace': 78,
                'Efficiency': 85,
                'Shooting': 87,
                'Rebounding': 75
            },
            'Warriors': {
                'Offense': 95,
                'Defense': 79,
                'Pace': 92,
                'Efficiency': 93,
                'Shooting': 96,
                'Rebounding': 72
            }
        },
        'offensive_ratings': [110.5, 115.8],
        'defensive_ratings': [106.2, 108.3]
    }

    charts = manager.generate_matchup_analysis('Lakers', 'Warriors', matchup_data)

    print(f"\n✅ Generated {len(charts)} matchup charts:")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {os.path.basename(chart)}")

    return charts


def example_3_betting_insights():
    """Example 3: Betting insights and edge analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Betting Insights & Edge Analysis")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/betting')

    # Sample betting data
    betting_data = {
        'edges': [
            {
                'game': 'Lakers vs Warriors',
                'bet_type': 'Spread',
                'edge': 5.2,
                'recommended': 'Lakers +8.5',
                'confidence': 0.82
            },
            {
                'game': 'Celtics vs Heat',
                'bet_type': 'Total',
                'edge': 3.8,
                'recommended': 'Under 215.5',
                'confidence': 0.75
            },
            {
                'game': 'Bucks vs Nets',
                'bet_type': 'Spread',
                'edge': 3.1,
                'recommended': 'Bucks -5',
                'confidence': 0.71
            },
            {
                'game': 'Suns vs Mavs',
                'bet_type': 'Moneyline',
                'edge': 2.5,
                'recommended': 'Suns ML',
                'confidence': 0.68
            },
        ],
        'spreads': [
            {'game': 'Lakers vs Warriors', 'spread': -8.5, 'fair_line': -3.3},
            {'game': 'Celtics vs Heat', 'spread': 3.0, 'fair_line': -0.8},
            {'game': 'Bucks vs Nets', 'spread': -5.0, 'fair_line': -8.1},
        ],
        'line_movement': [
            {
                'game': 'Lakers vs Warriors',
                'timestamps': [
                    datetime.now() - timedelta(hours=72),
                    datetime.now() - timedelta(hours=48),
                    datetime.now() - timedelta(hours=24),
                    datetime.now() - timedelta(hours=12),
                    datetime.now() - timedelta(hours=2),
                    datetime.now()
                ],
                'opening_lines': [-6.0] * 6,
                'current_lines': [-6.0, -6.5, -7.0, -7.5, -8.0, -8.5],
                'line_type': 'spread'
            }
        ]
    }

    charts = manager.generate_betting_analysis(betting_data)

    print(f"\n✅ Generated {len(charts)} betting charts:")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {os.path.basename(chart)}")

    return charts


def example_4_league_overview():
    """Example 4: League-wide overview and trends."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: League Overview & Trends")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/league')

    # Sample league data
    league_data = {
        'team_strengths': {
            'Lakers': 88, 'Warriors': 95, 'Celtics': 92, 'Heat': 85,
            'Bucks': 91, 'Nets': 83, 'Mavs': 86, 'Suns': 89,
            'Nuggets': 93, 'Grizzlies': 87, '76ers': 84, 'Clippers': 88,
            'Kings': 78, 'Pelicans': 81, 'Knicks': 82, 'Cavaliers': 86,
            'Hawks': 80, 'Bulls': 79, 'Raptors': 77, 'Wizards': 75,
            'Hornets': 72, 'Magic': 70, 'Pistons': 68, 'Rockets': 71,
            'Spurs': 73, 'Thunder': 74, 'Trail Blazers': 76, 'Timberwolves': 85,
            'Jazz': 81, 'Pacers': 83
        },
        'injuries': {
            'Lakers': 5, 'Warriors': 2, 'Celtics': 1, 'Heat': 3,
            'Bucks': 0, 'Nets': 6, 'Mavs': 2, 'Suns': 7,
            'Nuggets': 1, 'Grizzlies': 8, '76ers': 4, 'Clippers': 9,
            'Kings': 3, 'Pelicans': 2, 'Knicks': 4, 'Cavaliers': 1
        },
        'team_ratings': {
            'Lakers': 110.5, 'Warriors': 118.2, 'Celtics': 115.8, 'Heat': 108.3,
            'Bucks': 114.1, 'Nets': 106.7, 'Mavs': 109.4, 'Suns': 111.2,
            'Nuggets': 116.5, 'Grizzlies': 110.8, '76ers': 107.9, 'Clippers': 110.5
        },
        'team_metrics': {
            'Lakers': {'Points': 115.2, 'Rebounds': 45.3, 'Assists': 26.8, 'FG%': 47.5},
            'Warriors': {'Points': 118.5, 'Rebounds': 42.8, 'Assists': 29.2, 'FG%': 49.1},
            'Celtics': {'Points': 117.1, 'Rebounds': 46.2, 'Assists': 25.9, 'FG%': 48.3},
            'Heat': {'Points': 110.8, 'Rebounds': 43.5, 'Assists': 24.7, 'FG%': 46.2}
        },
        'highlight_team': 'Warriors'
    }

    charts = manager.generate_league_overview(league_data)

    print(f"\n✅ Generated {len(charts)} league overview charts:")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {os.path.basename(chart)}")

    return charts


def example_5_player_cards():
    """Example 5: Player cards and comparisons."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Player Cards & Comparisons")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/players')

    # Single player card
    print("\nGenerating single player card...")
    lebron_data = {
        'name': 'LeBron James',
        'team': 'Lakers',
        'position': 'SF',
        'number': 23,
        'height': '6\'9"',
        'weight': '250 lbs',
        'stats': {'PPG': 28.7, 'RPG': 8.3, 'APG': 6.8, 'FG%': 51.2},
        'recent_form': [32, 28, 35, 26, 30],
        'season_avg': 28.7
    }
    chart1 = manager.generate_player_analysis(lebron_data)

    # Player comparison
    print("Generating player comparison...")
    comparison_data = {
        'comparison': True,
        'player1': {
            'name': 'LeBron James',
            'team': 'Lakers',
            'stats': {'PPG': 28.7, 'RPG': 8.3, 'APG': 6.8, 'FG%': 51.2}
        },
        'player2': {
            'name': 'Stephen Curry',
            'team': 'Warriors',
            'stats': {'PPG': 29.4, 'RPG': 6.1, 'APG': 6.3, 'FG%': 48.5}
        }
    }
    chart2 = manager.generate_player_analysis(comparison_data)

    charts = chart1 + chart2

    print(f"\n✅ Generated {len(charts)} player visualization charts:")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {os.path.basename(chart)}")

    return charts


def example_6_comprehensive_dashboard():
    """Example 6: Create a comprehensive HTML dashboard."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Comprehensive HTML Dashboard")
    print("=" * 70)

    manager = VisualizationManager(sport='nba', output_dir='examples/output/dashboard_demo')

    # Run all previous examples to generate charts
    all_charts = []
    all_charts.extend(example_1_team_performance_suite())
    all_charts.extend(example_2_head_to_head_matchup())
    all_charts.extend(example_3_betting_insights())

    # Create dashboard
    dashboard_config = {
        'title': 'NBA Analytics Dashboard',
        'subtitle': 'Comprehensive Game Day Analysis',
        'metrics': {
            'Games Today': 8,
            'Teams Analyzed': 16,
            'Betting Edges': 4,
            'Hot Teams': 5,
            'Top Performers': 12
        },
        'charts': [
            {'title': os.path.basename(chart).replace('_', ' ').replace('.png', '').title(), 'path': chart}
            for chart in all_charts
        ],
        'tables': [
            {
                'title': 'Top Performers Today',
                'headers': ['Player', 'Team', 'Points', 'Rebounds', 'Assists'],
                'rows': [
                    ['LeBron James', 'Lakers', '32', '8', '7'],
                    ['Stephen Curry', 'Warriors', '35', '6', '9'],
                    ['Jayson Tatum', 'Celtics', '28', '10', '5'],
                    ['Giannis Antetokounmpo', 'Bucks', '30', '12', '6']
                ]
            }
        ]
    }

    dashboard_path = manager.generate_comprehensive_dashboard(dashboard_config)

    print(f"\n✅ Dashboard generated: {dashboard_path}")
    print(f"   Open in browser to view interactive dashboard")

    # Also generate Notion-compatible export
    notion_path = manager.dashboard.generate_notion_compatible_export(dashboard_config)
    print(f"\n✅ Notion-compatible export: {notion_path}")

    return dashboard_path


def run_all_examples():
    """Run all examples."""
    print("\n" + "🏀" * 35)
    print(" " * 20 + "SPORTSTATBOT VISUALIZATION EXAMPLES")
    print("🏀" * 35 + "\n")

    try:
        # Create output directory
        os.makedirs('examples/output', exist_ok=True)

        # Run examples
        example_1_team_performance_suite()
        example_2_head_to_head_matchup()
        example_3_betting_insights()
        example_4_league_overview()
        example_5_player_cards()
        dashboard_path = example_6_comprehensive_dashboard()

        # Final summary
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nOutput directory: examples/output/")
        print(f"Main dashboard: {dashboard_path}")
        print("\nExplore the generated visualizations in the output directories!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_examples()
