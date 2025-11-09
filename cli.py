#!/usr/bin/env python3
"""Command-line interface for SportStatBot."""
import argparse
import sys
from typing import List, Optional

from report_generator import SportsReportGenerator
from presentation_config import PresentationConfig, ToneLevel, StyleTheme
from formatters.enhanced_formatter import EnhancedFormatter
from formatters.storybook_formatter import StorybookFormatter
from formatters.pdf_generator import PDFGenerator
from visualizers.chart_generator import ChartGenerator
from visualizers.timeline_generator import TimelineGenerator
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

    # Presentation options
    parser.add_argument(
        '--theme',
        choices=['espn', 'athletic', '538', 'bleacher'],
        default='espn',
        help='Style theme for report (default: espn)'
    )

    parser.add_argument(
        '--tone',
        choices=['professional', 'balanced', 'engaging', 'fun'],
        default='balanced',
        help='Tone level from professional to fun (default: balanced)'
    )

    parser.add_argument(
        '--colors',
        action='store_true',
        help='Enable terminal color coding for streaks'
    )

    parser.add_argument(
        '--no-openers',
        action='store_true',
        help='Disable randomized story openers'
    )

    parser.add_argument(
        '--header-style',
        choices=['standard', 'compact', 'bold', 'minimal'],
        default='standard',
        help='Header template style (default: standard)'
    )

    parser.add_argument(
        '--credits',
        action='store_true',
        help='Track and display agent credits'
    )

    parser.add_argument(
        '--storybook',
        action='store_true',
        help='Render report in storybook/feature article style'
    )

    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Generate PDF output in addition to markdown'
    )

    parser.add_argument(
        '--charts',
        action='store_true',
        help='Generate charts and embed them in the report'
    )

    parser.add_argument(
        '--timeline',
        action='store_true',
        help='Include timeline visualizations for storylines'
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

    # Initialize presentation config
    pres_config = PresentationConfig(
        tone=args.tone,
        theme=args.theme,
        use_colors=args.colors,
        use_random_openers=not args.no_openers,
        header_template=args.header_style,
        track_credits=args.credits
    )

    # Initialize generator
    generator = SportsReportGenerator()

    # Initialize enhanced formatter if presentation features are enabled
    use_enhanced = args.theme or args.tone != 'balanced' or args.colors or args.credits
    if use_enhanced or args.storybook:
        if args.storybook:
            formatter = StorybookFormatter(pres_config)
        else:
            formatter = EnhancedFormatter(pres_config)
    else:
        formatter = None

    # Initialize chart generator if requested
    chart_gen = ChartGenerator() if args.charts else None

    # Initialize timeline generator if requested
    timeline_gen = TimelineGenerator() if args.timeline else None

    # Initialize PDF generator if requested
    pdf_gen = PDFGenerator() if args.pdf else None

    try:
        # Generate report data
        if args.all:
            print("\n🏆 Generating full sports report for all leagues...\n")
            if formatter:
                # Use enhanced formatter
                data = {}
                for sport in config.SPORTS_CONFIG.keys():
                    sport_data = generator._generate_sport_data(sport)
                    if sport_data and (sport_data.get('trends') or sport_data.get('recent_games')):
                        data[sport] = sport_data

                if args.storybook:
                    # Format as storybook
                    reports_data = [{'sport': sport, 'data': sport_data} for sport, sport_data in data.items()]
                    report = formatter.format_storybook_view(reports_data)
                else:
                    report = formatter.format_full_report(data)
            else:
                report = generator.generate_full_report()

        elif args.sports:
            if len(args.sports) == 1 and args.quick:
                # Single sport quick update
                sport = args.sports[0]
                print(f"\n{config.SPORTS_CONFIG[sport]['emoji']} Generating quick {sport.upper()} update...\n")
                if formatter:
                    data = generator._generate_sport_data(sport)
                    report = formatter.format_sport_quick_update(sport, data)
                else:
                    report = generator.generate_sport_report(sport, quick=True)
            elif len(args.sports) == 1:
                # Single sport full report
                sport = args.sports[0]
                print(f"\n{config.SPORTS_CONFIG[sport]['emoji']} Generating full {sport.upper()} report...\n")
                if formatter:
                    data = generator._generate_sport_data(sport)
                    sport_data = {sport: data}
                    report = formatter.format_full_report(sport_data)

                    # Generate charts if requested
                    if chart_gen and data:
                        print(f"📊 Generating charts for {sport.upper()}...")
                        charts = chart_gen.generate_all_charts_for_report(data, sport)
                        if charts:
                            report += "\n\n## Charts & Visualizations\n\n"
                            for chart_path in charts:
                                report += chart_gen.embed_chart_in_markdown(chart_path)
                else:
                    report = generator.generate_sport_report(sport, quick=False)
            else:
                # Multiple sports
                print(f"\n🏆 Generating report for {len(args.sports)} sports...\n")
                if formatter:
                    data = {}
                    for sport in args.sports:
                        sport_data = generator._generate_sport_data(sport)
                        if sport_data and (sport_data.get('trends') or sport_data.get('recent_games')):
                            data[sport] = sport_data

                    if args.storybook:
                        reports_data = [{'sport': sport, 'data': sport_data} for sport, sport_data in data.items()]
                        report = formatter.format_storybook_view(reports_data)
                    else:
                        report = formatter.format_full_report(data)
                else:
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

                # Generate PDF if requested
                if pdf_gen:
                    pdf_filename = args.output.replace('.md', '.pdf') if args.output.endswith('.md') else args.output + '.pdf'
                    print(f"📄 Generating PDF: {pdf_filename}")
                    pdf_path = pdf_gen.markdown_to_pdf(
                        report,
                        pdf_filename,
                        theme=args.theme
                    )
                    print(f"✅ PDF saved to: {pdf_path}")

                # Also print to console
                print("\n" + "="*80)
                print(report)
                print("="*80 + "\n")
        else:
            # Print to console only
            print("\n" + "="*80)
            print(report)
            print("="*80 + "\n")

            # Generate PDF if requested (with default filename)
            if pdf_gen:
                from datetime import datetime
                pdf_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                print(f"\n📄 Generating PDF: {pdf_filename}")
                pdf_path = pdf_gen.markdown_to_pdf(
                    report,
                    pdf_filename,
                    theme=args.theme
                )
                print(f"✅ PDF saved to: {pdf_path}")

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
