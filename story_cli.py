"""
Story Automation CLI - Command-line interface for story creation features
"""

import argparse
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

from story_automation.generators.story_generator import StoryGenerator
from story_automation.generators.title_generator import TitleGenerator
from story_automation.generators.summary_generator import SummaryGenerator
from story_automation.generators.sidebar_generator import SidebarGenerator
from story_automation.generators.pullquote_generator import PullQuoteGenerator
from story_automation.generators.trivia_generator import TriviaGenerator
from story_automation.generators.timeline_generator import TimelineGenerator

from story_automation.formatters.markdown_converter import MarkdownConverter
from story_automation.formatters.stat_highlighter import StatHighlighter
from story_automation.formatters.footnote_inserter import FootnoteInserter

from story_automation.exporters.google_docs_exporter import GoogleDocsExporter
from story_automation.exporters.apple_notes_syncer import AppleNotesSyncer

from story_automation.analyzers.story_rater import StoryRater
from story_automation.analyzers.diff_analyzer import DiffAnalyzer
from story_automation.analyzers.context_manager import ContextManager

from report_generator import ReportGenerator


class StoryAutomationCLI:
    """CLI for story automation features"""

    def __init__(self):
        self.story_gen = StoryGenerator()
        self.title_gen = TitleGenerator()
        self.summary_gen = SummaryGenerator()
        self.sidebar_gen = SidebarGenerator()
        self.pullquote_gen = PullQuoteGenerator()
        self.trivia_gen = TriviaGenerator()
        self.timeline_gen = TimelineGenerator()

        self.markdown_conv = MarkdownConverter()
        self.stat_highlighter = StatHighlighter()
        self.footnote_inserter = FootnoteInserter()

        self.google_exporter = GoogleDocsExporter()
        self.apple_syncer = AppleNotesSyncer()

        self.story_rater = StoryRater()
        self.diff_analyzer = DiffAnalyzer()
        self.context_manager = ContextManager()

        self.report_gen = ReportGenerator()

    def generate_story(
        self,
        sports: List[str],
        style: str = 'analytical',
        perspective: Optional[str] = None,
        headline_tone: str = 'neutral',
        include_sidebars: bool = True,
        include_pullquotes: bool = True,
        include_trivia: bool = False,
        export_format: Optional[str] = None,
        rate_story: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a complete story with all features

        Args:
            sports: List of sports to generate stories for
            style: Writing style
            perspective: Optional perspective
            headline_tone: Headline tone
            include_sidebars: Include sidebars
            include_pullquotes: Include pull quotes
            include_trivia: Include trivia
            export_format: Export format (google_docs, apple_notes, local)
            rate_story: Rate the generated story

        Returns:
            Generated stories dictionary
        """
        results = {}

        for sport in sports:
            print(f"\nGenerating story for {sport.upper()}...")

            # Get sport data
            sport_data = self.report_gen._generate_sport_data(sport)

            if not sport_data.get('enabled', False):
                print(f"  {sport.upper()} not available")
                continue

            # Generate story
            story = self.story_gen.generate_story(
                sport_data=sport_data,
                sport_name=sport,
                style=style,
                perspective=perspective,
                headline_tone=headline_tone,
                include_sidebar=include_sidebars,
                include_pullquotes=include_pullquotes,
                include_trivia=include_trivia
            )

            # Rate story if requested
            if rate_story:
                rating = self.story_rater.rate_story(story, sport_data)
                story['rating'] = rating
                print(f"  Story Rating: {rating['letter_grade']} ({rating['overall_score']:.1f})")

            # Save context for narrative continuity
            self.context_manager.add_story_context(story, sport, sport_data)

            # Export if requested
            if export_format:
                export_result = self._export_story(story, sport, export_format)
                story['export'] = export_result

                if export_result.get('success'):
                    if export_format == 'google_docs':
                        print(f"  Exported to Google Docs: {export_result.get('url', 'N/A')}")
                    elif export_format == 'apple_notes':
                        print(f"  Synced to Apple Notes: {export_result.get('folder', 'N/A')}")
                    else:
                        print(f"  Saved to: {export_result.get('file_path', 'N/A')}")

            results[sport] = story
            print(f"  ✓ Story generated successfully")

        return results

    def recast_story(
        self,
        sport: str,
        styles: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Recast a story into multiple styles

        Args:
            sport: Sport name
            styles: List of styles to recast into

        Returns:
            Dictionary mapping styles to recast stories
        """
        print(f"\nGenerating original story for {sport.upper()}...")

        # Get sport data
        sport_data = self.report_gen._generate_sport_data(sport)

        # Generate base story
        base_story = self.story_gen.generate_story(
            sport_data=sport_data,
            sport_name=sport
        )

        print(f"Recasting story into {len(styles)} styles...")

        # Recast into multiple styles
        recast_versions = self.story_gen.recast_story(base_story, styles)

        return recast_versions

    def compare_stories(
        self,
        version_1: str,
        version_2: str,
        sport: str
    ) -> Dict[str, Any]:
        """
        Compare two story versions

        Args:
            version_1: First version ID
            version_2: Second version ID
            sport: Sport name

        Returns:
            Comparison results
        """
        comparison = self.diff_analyzer.compare_versions(version_1, version_2, sport)

        # Generate diff view
        diff_view = self.diff_analyzer.generate_diff_view(comparison, 'markdown')

        print(diff_view)

        return comparison

    def _export_story(
        self,
        story: Dict[str, Any],
        sport: str,
        export_format: str
    ) -> Dict[str, Any]:
        """Export story to specified format"""
        story_type = story.get('type', 'digests')

        if export_format == 'google_docs':
            return self.google_exporter.export_story(
                story, sport, story_type
            )
        elif export_format == 'apple_notes':
            return self.apple_syncer.sync_story(
                story, sport, story_type.replace('_', '')
            )
        else:  # local
            return self.google_exporter.export_story(
                story, sport, story_type
            )

    def print_story(self, story: Dict[str, Any]):
        """Print story to console"""
        print("\n" + "="*80)

        if story.get('headline'):
            print(f"\n# {story['headline']}\n")

        if story.get('subhead'):
            print(f"_{story['subhead']}_\n")

        if story.get('tldr'):
            print(f"{story['tldr']}\n")

        if story.get('body'):
            print(story['body'])

        # Print sidebars
        if story.get('sidebars'):
            for sidebar in story['sidebars']:
                print(self.sidebar_gen.format_sidebar(sidebar, 'markdown'))

        # Print pull quotes
        if story.get('pullquotes'):
            print("\n## Key Quotes\n")
            for quote in story['pullquotes']:
                quote_text = quote.get('text', quote) if isinstance(quote, dict) else quote
                print(f"> {quote_text}\n")

        if story.get('conclusion'):
            print(f"\n{story['conclusion']}\n")

        # Print metadata
        if story.get('metadata'):
            print("\n" + "-"*80)
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            if story['metadata'].get('data_sources'):
                print(f"Sources: {', '.join(story['metadata']['data_sources'])}")

        print("\n" + "="*80 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='SportStatBot Story Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate analytical story for NFL
  python story_cli.py --sports nfl --style analytical

  # Generate story with all features
  python story_cli.py --sports nba --style storytelling --sidebars --pullquotes --trivia

  # Generate and export to Google Docs
  python story_cli.py --sports nfl --export google_docs

  # Generate with specific perspective
  python story_cli.py --sports nba --perspective coach_lens --headline-tone bold

  # Recast story into multiple styles
  python story_cli.py --sports nfl --recast analytical storytelling fan_voice

  # Rate a generated story
  python story_cli.py --sports nba --rate
        """
    )

    parser.add_argument(
        '--sports',
        nargs='+',
        choices=['nfl', 'nba', 'mlb', 'nhl', 'soccer', 'ncaaf', 'ncaab'],
        required=True,
        help='Sports to generate stories for'
    )

    parser.add_argument(
        '--style',
        choices=['analytical', 'storytelling', 'fan_voice'],
        default='analytical',
        help='Writing style (default: analytical)'
    )

    parser.add_argument(
        '--perspective',
        choices=['coach_lens', 'casual_fan', 'academic'],
        help='Optional perspective overlay'
    )

    parser.add_argument(
        '--headline-tone',
        choices=['neutral', 'bold', 'tabloid', 'poetic', 'data_driven'],
        default='neutral',
        help='Headline tone (default: neutral)'
    )

    parser.add_argument(
        '--sidebars',
        action='store_true',
        help='Include dynamic sidebars'
    )

    parser.add_argument(
        '--pullquotes',
        action='store_true',
        help='Include pull quotes'
    )

    parser.add_argument(
        '--trivia',
        action='store_true',
        help='Include trivia facts'
    )

    parser.add_argument(
        '--export',
        choices=['google_docs', 'apple_notes', 'local'],
        help='Export format'
    )

    parser.add_argument(
        '--rate',
        action='store_true',
        help='Rate the generated story'
    )

    parser.add_argument(
        '--recast',
        nargs='+',
        choices=['analytical', 'storytelling', 'fan_voice', 'coach_lens', 'casual_fan', 'academic'],
        help='Recast story into multiple styles'
    )

    parser.add_argument(
        '--output',
        help='Output file path'
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = StoryAutomationCLI()

    # Handle recast mode
    if args.recast:
        if len(args.sports) > 1:
            print("Error: Recast mode only supports single sport")
            sys.exit(1)

        recast_versions = cli.recast_story(args.sports[0], args.recast)

        print(f"\nGenerated {len(recast_versions)} recast versions")

        for style, story in recast_versions.items():
            print(f"\n{'='*80}\n{style.upper()} VERSION\n{'='*80}")
            cli.print_story(story)

        return

    # Generate stories
    stories = cli.generate_story(
        sports=args.sports,
        style=args.style,
        perspective=args.perspective,
        headline_tone=args.headline_tone,
        include_sidebars=args.sidebars,
        include_pullquotes=args.pullquotes,
        include_trivia=args.trivia,
        export_format=args.export,
        rate_story=args.rate
    )

    # Print stories
    for sport, story in stories.items():
        cli.print_story(story)

        # Print rating if available
        if story.get('rating'):
            rating = story['rating']
            print(f"\n📊 STORY RATING: {rating['letter_grade']} ({rating['overall_score']:.1f}/100)")
            print("\nScore Breakdown:")
            for metric, score in rating['scores'].items():
                print(f"  {metric.capitalize()}: {score:.1f}")

            if rating.get('feedback'):
                print("\nFeedback:")
                for item in rating['feedback']:
                    print(f"  • {item}")

    # Save to file if requested
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(stories, f, indent=2, default=str)
        print(f"\n✓ Saved stories to {args.output}")


if __name__ == '__main__':
    main()
