#!/usr/bin/env python3
"""Command-line interface for SportStatBot."""
import argparse
import sys
from typing import List, Optional

from report_generator import SportsReportGenerator
import config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SportStatBot - Your expert sports analyst for NFL, NBA, MLB, NHL, MLS, Soccer, and Golf',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report for all sports
  python cli.py --all

  # Generate report for specific sports
  python cli.py --sports nfl nba mlb

  # Generate quick update for NFL only
  python cli.py --sports nfl --quick

  # Save report to file
  python cli.py --all --output today_report.md

  # Just print available sports
  python cli.py --list-sports
        """
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate report for all sports'
    )

    parser.add_argument(
        '--sports',
        nargs='+',
        choices=['nfl', 'nba', 'mlb', 'nhl', 'mls', 'soccer', 'golf'],
        help='Specific sports to include in report'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Generate quick update instead of full detailed report'
    )

    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Save report to specified file'
    )

    parser.add_argument(
        '--list-sports',
        action='store_true',
        help='List all available sports'
    )

    args = parser.parse_args()

    # Handle list sports
    if args.list_sports:
        print("\nAvailable sports:")
        for sport_key, sport_config in config.SPORTS_CONFIG.items():
            emoji = sport_config.get('emoji', '')
            name = sport_config.get('display_name', sport_key.upper())
            print(f"  {emoji} {sport_key:10} - {name}")
        print()
        return 0

    # Validate arguments
    if not args.all and not args.sports:
        parser.print_help()
        print("\nError: Must specify either --all or --sports")
        return 1

    # Initialize generator
    generator = SportsReportGenerator()

    try:
        # Generate report
        if args.all:
            print("\n🏆 Generating full sports report for all leagues...\n")
            report = generator.generate_full_report()
        elif args.sports:
            if len(args.sports) == 1 and args.quick:
                # Single sport quick update
                sport = args.sports[0]
                print(f"\n{config.SPORTS_CONFIG[sport]['emoji']} Generating quick {sport.upper()} update...\n")
                report = generator.generate_sport_report(sport, quick=True)
            elif len(args.sports) == 1:
                # Single sport full report
                sport = args.sports[0]
                print(f"\n{config.SPORTS_CONFIG[sport]['emoji']} Generating full {sport.upper()} report...\n")
                report = generator.generate_sport_report(sport, quick=False)
            else:
                # Multiple sports
                print(f"\n🏆 Generating report for {len(args.sports)} sports...\n")
                report = generator.generate_full_report(args.sports)
        else:
            print("Error: Invalid arguments")
            return 1

        # Output report
        if args.output:
            # Save to file
            saved_path = generator.save_report(report, args.output)
            if saved_path:
                print(f"\n✅ Report saved to: {saved_path}")

                # Also print to console
                print("\n" + "="*80)
                print(report)
                print("="*80 + "\n")
        else:
            # Print to console only
            print("\n" + "="*80)
            print(report)
            print("="*80 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nReport generation cancelled by user.")
        return 130

    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
