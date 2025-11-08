#!/usr/bin/env python3
"""
Visualization CLI
=================
Command-line interface for SportStatBot visualization features.
"""

import argparse
import sys
from datetime import datetime
from visualizers.visualization_manager import VisualizationManager


def generate_demo_charts(sport='nba'):
    """Generate demo charts with sample data."""
    print(f"Generating demo visualizations for {sport.upper()}...")

    manager = VisualizationManager(sport=sport, output_dir='demo_visualizations')

    # Demo team analysis
    print("\n1. Generating team analysis charts...")
    team_data = {
        'offensive_ratings': [110, 112, 108, 115, 113, 109, 111, 114],
        'defensive_ratings': [105, 103, 107, 102, 104, 106, 103, 101],
        'metrics': {
            'Offense': 85,
            'Defense': 78,
            'Rebounding': 72,
            'Assists': 88,
            'Turnovers': 65,
            'FG%': 82
        },
        'recent_results': ['W', 'W', 'L', 'W', 'W', 'L', 'W', 'W'],
        'wins': 45,
        'losses': 20,
        'target_wins': 50,
        'playoff_threshold': 45
    }
    team_charts = manager.generate_team_analysis_suite('Demo Lakers', team_data)
    print(f"   Generated {len(team_charts)} team charts")

    # Demo matchup analysis
    print("\n2. Generating matchup analysis...")
    matchup_data = {
        'momentum_score': -35,
        'team_metrics': {
            'Demo Lakers': {'Offense': 85, 'Defense': 78, 'Pace': 75, 'Efficiency': 82, 'Shooting': 88, 'Rebounding': 72},
            'Demo Warriors': {'Offense': 90, 'Defense': 72, 'Pace': 85, 'Efficiency': 88, 'Shooting': 92, 'Rebounding': 68}
        }
    }
    matchup_charts = manager.generate_matchup_analysis('Demo Lakers', 'Demo Warriors', matchup_data)
    print(f"   Generated {len(matchup_charts)} matchup charts")

    # Demo betting analysis
    print("\n3. Generating betting analysis...")
    betting_data = {
        'edges': [
            {'game': 'LAL vs GSW', 'bet_type': 'Spread', 'edge': 4.2, 'recommended': 'LAL +5.5', 'confidence': 0.78},
            {'game': 'BOS vs MIA', 'bet_type': 'Spread', 'edge': 3.1, 'recommended': 'BOS -3', 'confidence': 0.72},
            {'game': 'MIL vs BKN', 'bet_type': 'Total', 'edge': 2.8, 'recommended': 'Over 220.5', 'confidence': 0.65},
            {'game': 'DAL vs PHX', 'bet_type': 'Spread', 'edge': 2.3, 'recommended': 'PHX -4', 'confidence': 0.68},
        ],
        'spreads': [
            {'game': 'LAL vs GSW', 'spread': -5.5, 'fair_line': -1.3},
            {'game': 'BOS vs MIA', 'spread': -3.0, 'fair_line': -6.1},
            {'game': 'MIL vs BKN', 'spread': 2.5, 'fair_line': 0.2},
        ]
    }
    betting_charts = manager.generate_betting_analysis(betting_data)
    print(f"   Generated {len(betting_charts)} betting charts")

    # Demo league overview
    print("\n4. Generating league overview...")
    league_data = {
        'team_strengths': {
            'Lakers': 88, 'Warriors': 92, 'Celtics': 90, 'Heat': 85,
            'Bucks': 89, 'Nets': 82, 'Mavs': 84, 'Suns': 87,
            'Nuggets': 91, 'Grizzlies': 86, '76ers': 83, 'Clippers': 88,
            'Kings': 78, 'Pelicans': 80, 'Knicks': 81, 'Cavaliers': 85
        },
        'injuries': {
            'Lakers': 5, 'Warriors': 2, 'Celtics': 1, 'Heat': 3,
            'Bucks': 0, 'Nets': 4, 'Mavs': 2, 'Suns': 6,
            'Nuggets': 1, 'Grizzlies': 7, '76ers': 4, 'Clippers': 8
        },
        'team_ratings': {
            'Lakers': 110.5, 'Warriors': 115.2, 'Celtics': 113.8, 'Heat': 108.3,
            'Bucks': 112.1, 'Nets': 106.7, 'Mavs': 107.9, 'Suns': 109.4
        }
    }
    league_charts = manager.generate_league_overview(league_data)
    print(f"   Generated {len(league_charts)} league overview charts")

    # Demo player cards
    print("\n5. Generating player cards...")
    player_data = {
        'name': 'LeBron James',
        'team': 'Lakers',
        'position': 'SF',
        'number': 23,
        'height': '6\'9"',
        'weight': '250 lbs',
        'stats': {'PPG': 27.5, 'RPG': 8.2, 'APG': 7.1, 'FG%': 52.3},
        'recent_form': [25, 32, 28, 30, 27],
        'season_avg': 27.5
    }
    player_charts = manager.generate_player_analysis(player_data)
    print(f"   Generated {len(player_charts)} player cards")

    # Generate comprehensive dashboard
    print("\n6. Generating comprehensive dashboard...")
    all_charts = manager.get_generated_charts()
    dashboard_config = {
        'title': f'SportStatBot {sport.upper()} Demo Dashboard',
        'subtitle': 'Comprehensive Visualization Suite',
        'metrics': {
            'Total Teams': 16,
            'Games Analyzed': 82,
            'Charts Generated': len(all_charts),
            'Betting Edges': 4
        },
        'charts': [
            {'title': f'Chart {i+1}', 'path': chart}
            for i, chart in enumerate(all_charts)
        ]
    }
    dashboard_path = manager.generate_comprehensive_dashboard(dashboard_config)
    print(f"   Dashboard saved to: {dashboard_path}")

    # Print summary
    print("\n" + "=" * 60)
    print(f"✅ Demo visualization complete!")
    print(f"   Total charts generated: {len(all_charts)}")
    print(f"   Output directory: demo_visualizations/")
    print(f"   Dashboard: {dashboard_path}")
    print("=" * 60)


def generate_custom_chart(args):
    """Generate a custom chart based on arguments."""
    manager = VisualizationManager(sport=args.sport, output_dir='custom_visualizations')

    if args.chart_type == 'team_radar':
        # Parse metrics from command line
        metrics = {}
        if args.metrics:
            for metric in args.metrics.split(','):
                name, value = metric.split('=')
                metrics[name.strip()] = float(value.strip())

        chart = manager.radar_charts.generate_team_radar(args.team_name, metrics)
        print(f"Generated team radar chart: {chart}")

    elif args.chart_type == 'form_pulse':
        results = list(args.results.upper())
        chart = manager.trend_charts.generate_form_pulse(args.team_name, results)
        print(f"Generated form pulse chart: {chart}")

    elif args.chart_type == 'season_progress':
        chart = manager.trend_charts.generate_season_progress(
            args.team_name,
            args.wins,
            args.losses,
            args.target_wins,
            args.playoff_threshold
        )
        print(f"Generated season progress chart: {chart}")

    else:
        print(f"Chart type '{args.chart_type}' not implemented yet.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SportStatBot Visualization CLI - Generate sports analytics visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate demo visualizations
  python visualization_cli.py --demo --sport nba

  # Generate custom team radar chart
  python visualization_cli.py --chart-type team_radar --team-name "Lakers" \\
    --metrics "Offense=85,Defense=78,Rebounding=72"

  # Generate form pulse chart
  python visualization_cli.py --chart-type form_pulse --team-name "Warriors" \\
    --results "WWLWWLW"

  # Generate season progress
  python visualization_cli.py --chart-type season_progress --team-name "Celtics" \\
    --wins 45 --losses 20 --target-wins 50
        """
    )

    parser.add_argument('--demo', action='store_true',
                       help='Generate demo visualizations with sample data')
    parser.add_argument('--sport', default='nba',
                       choices=['nba', 'nfl', 'mlb', 'nhl', 'mls', 'soccer'],
                       help='Sport for styling (default: nba)')
    parser.add_argument('--chart-type',
                       choices=['team_radar', 'form_pulse', 'season_progress',
                               'momentum_gauge', 'betting_edges'],
                       help='Type of chart to generate')
    parser.add_argument('--team-name', help='Team name for the chart')
    parser.add_argument('--metrics', help='Metrics in format "Name=Value,Name=Value"')
    parser.add_argument('--results', help='Game results as string (e.g., "WWLWL")')
    parser.add_argument('--wins', type=int, help='Number of wins')
    parser.add_argument('--losses', type=int, help='Number of losses')
    parser.add_argument('--target-wins', type=int, help='Target win total')
    parser.add_argument('--playoff-threshold', type=int, help='Playoff threshold')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Execute based on arguments
    if args.demo:
        generate_demo_charts(args.sport)
    elif args.chart_type:
        if not args.team_name:
            print("Error: --team-name is required for custom charts")
            sys.exit(1)
        generate_custom_chart(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
