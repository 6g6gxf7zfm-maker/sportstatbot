#!/usr/bin/env python3
"""
Command-line interface for SportStatBot Modeling & Simulation System.

Access predictive models, simulations, and forecasting tools.
"""

import argparse
import json
from datetime import datetime
from models.orchestrator import ModelOrchestrator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SportStatBot Predictive Modeling & Simulation System'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze game command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single game')
    analyze_parser.add_argument('--home', required=True, help='Home team name')
    analyze_parser.add_argument('--away', required=True, help='Away team name')
    analyze_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer'])
    analyze_parser.add_argument('--output', help='Output file path (JSON)')

    # Power rankings command
    rankings_parser = subparsers.add_parser('rankings', help='Get power rankings')
    rankings_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer'])
    rankings_parser.add_argument('--top', type=int, default=25, help='Number of teams to show')

    # Season projection command
    season_parser = subparsers.add_parser('season', help='Project season outcomes')
    season_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer'])
    season_parser.add_argument('--team', help='Specific team to project')

    # Upset alerts command
    upset_parser = subparsers.add_parser('upsets', help='Find potential upsets')
    upset_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer'])
    upset_parser.add_argument('--date', help='Date for games (YYYY-MM-DD)')

    # Betting edge command
    edge_parser = subparsers.add_parser('edge', help='View betting edge tracking')
    edge_parser.add_argument('--days', type=int, help='Last N days')

    # Playoff simulator command
    playoff_parser = subparsers.add_parser('playoffs', help='Simulate playoff bracket')
    playoff_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls'])

    # Daily report command
    report_parser = subparsers.add_parser('report', help='Generate daily predictive report')
    report_parser.add_argument('--sport', required=True, choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer'])
    report_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize orchestrator
    orchestrator = ModelOrchestrator()

    if args.command == 'analyze':
        # Analyze single game
        print(f"\n🔮 Analyzing {args.away} @ {args.home} ({args.sport.upper()})\n")
        print("Running comprehensive analysis...")
        print("  ⚡ Monte Carlo simulation (10,000 runs)")
        print("  📊 Power index calculations")
        print("  🎯 Spread model predictions")
        print("  ⚠️  Upset probability detection")
        print("  📈 Momentum & fatigue analysis\n")

        analysis = orchestrator.analyze_game(
            home_team=args.home,
            away_team=args.away,
            sport=args.sport
        )

        # Display results
        if analysis.monte_carlo_results:
            mc = analysis.monte_carlo_results
            print("━━━ MONTE CARLO SIMULATION RESULTS ━━━")
            print(f"  {args.home} win probability: {mc.home_win_probability*100:.1f}%")
            print(f"  {args.away} win probability: {mc.away_win_probability*100:.1f}%")
            print(f"  Expected score: {args.home} {mc.expected_home_score} - {args.away} {mc.expected_away_score}")
            print(f"  Projected spread: {mc.expected_spread:+.1f} (from {args.home} perspective)")
            print(f"  Over/Under: {mc.over_under_suggestion}")
            print(f"  Most likely score: {mc.most_likely_score[0]}-{mc.most_likely_score[1]}")
            print()

        if analysis.spread_predictions:
            sp = analysis.spread_predictions
            print("━━━ SPREAD MODEL PREDICTIONS ━━━")
            print(f"  Fair spread: {sp.fair_spread:+.1f}")
            print(f"  Fair moneyline: {args.home} ({sp.fair_moneyline_home:+d}) / {args.away} ({sp.fair_moneyline_away:+d})")
            print(f"  Fair total: {sp.fair_total}")
            if sp.recommendation:
                print(f"  💡 {sp.recommendation}")
            print()

        if analysis.upset_alerts:
            print("━━━ UPSET ALERT ━━━")
            for alert in analysis.upset_alerts:
                print(f"  ⚠️  Potential upset detected!")
                print(f"  Favorite: {alert.favorite} (Rating: {alert.favorite_rating:.0f})")
                print(f"  Underdog: {alert.underdog} (Rating: {alert.underdog_rating:.0f})")
                print(f"  Upset probability: {alert.upset_probability:.1f}%")
                print(f"  Upset score: {alert.upset_score:.0f}/100")
                print(f"  Confidence: {alert.confidence}")
                if alert.key_factors:
                    print("  Key factors:")
                    for factor in alert.key_factors:
                        print(f"    • {factor}")
            print()

        if analysis.momentum_scores:
            print("━━━ MOMENTUM ANALYSIS ━━━")
            for team, momentum in analysis.momentum_scores.items():
                print(f"  {team}:")
                print(f"    Momentum rating: {momentum.momentum_rating:+.1f}")
                print(f"    Recent form: {momentum.recent_form.upper()} ({momentum.last_5_record})")
                print(f"    Current streak: {momentum.streak}")
                print(f"    Trend: {momentum.trend}")
            print()

        if analysis.fatigue_assessments:
            print("━━━ FATIGUE ASSESSMENT ━━━")
            for team, fatigue in analysis.fatigue_assessments.items():
                print(f"  {team}:")
                print(f"    Fatigue level: {fatigue.fatigue_level:.1f}/100")
                print(f"    Performance multiplier: {fatigue.performance_multiplier:.3f}x")
                print(f"    Recovery status: {fatigue.recovery_status}")
                print(f"    Games last 7 days: {fatigue.games_in_last_7_days}")
            print()

        # Export if requested
        if args.output:
            orchestrator.export_analysis(analysis, args.output)

    elif args.command == 'rankings':
        # Power rankings
        print(f"\n📊 {args.sport.upper()} Power Rankings (Top {args.top})\n")
        rankings = orchestrator.get_power_rankings(args.sport, args.top)

        if rankings:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"{'Rank':<6}{'Team':<25}{'Rating':<10}{'Record':<10}{'Trend'}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            for i, team in enumerate(rankings, 1):
                trend_icon = '📈' if team.rating_trend == 'rising' else '📉' if team.rating_trend == 'falling' else '➡️'
                record = f"{team.wins}-{team.losses}" if team.wins is not None else "N/A"
                print(f"{i:<6}{team.team_name:<25}{team.rating:<10.0f}{record:<10}{trend_icon} {team.rating_trend}")

            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            print("No rankings available. Update ratings from game results first.")

    elif args.command == 'edge':
        # Betting edge summary
        print("\n💰 Betting Edge Tracking Summary\n")
        summary = orchestrator.get_betting_summary()

        if summary['total_bets'] > 0:
            print("━━━ PERFORMANCE METRICS ━━━")
            print(f"  Total tracked bets: {summary['total_bets']}")
            print(f"  Winning bets: {summary['winning_bets']}")
            print(f"  Losing bets: {summary['losing_bets']}")
            print(f"  Win rate: {summary['win_rate']:.1f}%")
            print(f"  Average edge: {summary['avg_edge']:.2f} points")
            print(f"  ROI: {summary['roi']:+.1f}%")
            print()
        else:
            print("No betting edge data tracked yet.")

    elif args.command == 'report':
        # Daily report
        print(f"\n📋 Daily Predictive Report - {args.sport.upper()}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # This would normally fetch today's games
        # For demo, using empty list
        report = orchestrator.generate_daily_report(args.sport, [])

        print("━━━ POWER RANKINGS (Top 10) ━━━")
        for i, team in enumerate(report['power_rankings'][:10], 1):
            print(f"  {i}. {team.team_name} ({team.rating:.0f})")

        print()
        print("Run 'models_cli.py analyze' for specific game predictions")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\nReport saved to {args.output}")

    print("\n✅ Done!\n")


if __name__ == '__main__':
    main()
