#!/usr/bin/env python3
"""
Test script for presentation features
Demonstrates all the new creative and presentation enhancements
"""

from presentation_config import (
    PresentationConfig, ToneLevel, StyleTheme,
    get_random_opener, HEADER_TEMPLATES
)
from formatters.enhanced_formatter import EnhancedFormatter
from formatters.storybook_formatter import StorybookFormatter
from visualizers.chart_generator import ChartGenerator
from visualizers.timeline_generator import TimelineGenerator
from visualizers.image_fetcher import ImageFetcher


def test_tone_levels():
    """Test different tone levels"""
    print("\n" + "="*70)
    print("TESTING TONE LEVELS")
    print("="*70)

    tones = [
        ToneLevel.PROFESSIONAL,
        ToneLevel.BALANCED,
        ToneLevel.ENGAGING,
        ToneLevel.FUN
    ]

    for tone in tones:
        config = PresentationConfig(tone=tone)
        print(f"\n{tone.upper()}:")
        print(f"  Fire emoji: '{config.get_emoji('fire')}'")
        print(f"  Trophy emoji: '{config.get_emoji('trophy')}'")
        print(f"  Star emoji: '{config.get_emoji('star')}'")


def test_style_themes():
    """Test different style themes"""
    print("\n" + "="*70)
    print("TESTING STYLE THEMES")
    print("="*70)

    themes = [
        StyleTheme.ESPN,
        StyleTheme.THE_ATHLETIC,
        StyleTheme.FIVETHIRTYEIGHT,
        StyleTheme.BLEACHER_REPORT
    ]

    for theme in themes:
        config = PresentationConfig(theme=theme)
        print(f"\n{config.style['name']}:")
        print(f"  Description: {config.style['description']}")
        print(f"  Divider: {config.style['section_divider'][:20]}...")
        print(f"  Color Scheme: {config.style['color_scheme']}")


def test_random_openers():
    """Test randomized story openers"""
    print("\n" + "="*70)
    print("TESTING RANDOM STORY OPENERS")
    print("="*70)

    sports = ['nfl', 'nba', 'mlb', 'nhl']

    for sport in sports:
        print(f"\n{sport.upper()}:")
        for i in range(3):
            opener = get_random_opener(sport)
            print(f"  {i+1}. {opener}")


def test_header_templates():
    """Test header templates"""
    print("\n" + "="*70)
    print("TESTING HEADER TEMPLATES")
    print("="*70)

    from datetime import datetime
    date = datetime.now().strftime('%B %d, %Y')

    for template_name, template in HEADER_TEMPLATES.items():
        print(f"\n{template_name.upper()}:")
        header = template.format(
            sport_emoji='🏀',
            sport_name='NBA',
            date=date
        )
        print(header)


def test_color_coding():
    """Test color coding for streaks"""
    print("\n" + "="*70)
    print("TESTING COLOR CODING")
    print("="*70)

    config = PresentationConfig(use_colors=True)

    test_cases = [
        ("Lakers on 5-game win streak", 5, 0),
        ("Warriors on 3-game win streak", 3, 0),
        ("Spurs on 3-game losing streak", 0, 3),
        ("Rockets on 6-game losing streak", 0, 6),
        ("Nuggets 2-2 in last 4", 2, 2)
    ]

    for text, wins, losses in test_cases:
        colored = config.colorize_streak(text, wins, losses)
        print(f"  {colored}")


def test_enhanced_formatter():
    """Test enhanced formatter with sample data"""
    print("\n" + "="*70)
    print("TESTING ENHANCED FORMATTER")
    print("="*70)

    # Sample data
    sample_data = {
        'nba': {
            'trends': [
                'Lakers have won their last 5 games',
                'Celtics lead the Eastern Conference'
            ],
            'recent_games': [
                {
                    'home_team': 'Los Angeles Lakers',
                    'away_team': 'Boston Celtics',
                    'home_score': 115,
                    'away_score': 110,
                    'notes': [],
                    'leaders': ['LeBron James: 28 PTS, 8 REB, 7 AST']
                }
            ],
            'standout_players': [
                {
                    'name': 'LeBron James',
                    'team': 'Lakers',
                    'stats': '28 PTS, 8 REB, 7 AST'
                }
            ],
            'injuries': [],
            'roster_changes': [],
            'betting_insights': {},
            'must_watch': []
        }
    }

    # Test with different themes
    for theme in [StyleTheme.ESPN, StyleTheme.THE_ATHLETIC]:
        print(f"\n--- {theme.upper()} THEME ---")
        config = PresentationConfig(theme=theme, tone=ToneLevel.BALANCED)
        formatter = EnhancedFormatter(config)
        report = formatter.format_full_report(sample_data)
        print(report[:500] + "...")


def test_chart_generator():
    """Test chart generation"""
    print("\n" + "="*70)
    print("TESTING CHART GENERATOR")
    print("="*70)

    chart_gen = ChartGenerator()

    # Test streak chart
    try:
        chart_path = chart_gen.generate_streak_chart(
            "Los Angeles Lakers",
            wins=5,
            losses=2,
            sport="NBA"
        )
        print(f"  ✓ Streak chart generated: {chart_path}")
    except Exception as e:
        print(f"  ✗ Streak chart failed: {e}")

    # Test standings chart
    try:
        sample_standings = [
            {'team': 'Lakers', 'wins': 10, 'losses': 3},
            {'team': 'Celtics', 'wins': 9, 'losses': 4},
            {'team': 'Nuggets', 'wins': 8, 'losses': 5}
        ]
        chart_path = chart_gen.generate_standings_chart(
            sample_standings,
            sport="NBA",
            division="Western Conference"
        )
        print(f"  ✓ Standings chart generated: {chart_path}")
    except Exception as e:
        print(f"  ✗ Standings chart failed: {e}")


def test_timeline_generator():
    """Test timeline generation"""
    print("\n" + "="*70)
    print("TESTING TIMELINE GENERATOR")
    print("="*70)

    timeline_gen = TimelineGenerator()

    # Test streak timeline
    from datetime import datetime, timedelta

    sample_games = [
        {
            'date': datetime.now() - timedelta(days=i),
            'opponent': f'Team {i}',
            'result': 'W' if i % 2 == 0 else 'L',
            'score': f'{100 + i}-{95 + i}'
        }
        for i in range(5)
    ]

    timeline = timeline_gen.generate_streak_timeline(
        "Los Angeles Lakers",
        sample_games,
        limit=5
    )
    print(timeline)


def test_credits_system():
    """Test auto-credits system"""
    print("\n" + "="*70)
    print("TESTING AUTO-CREDITS SYSTEM")
    print("="*70)

    config = PresentationConfig(track_credits=True)

    # Add some credits
    config.add_credit('game_analyzer', 'NBA Game Analysis')
    config.add_credit('player_analyzer', 'Top Performers')
    config.add_credit('formatter', 'Report Generation')

    # Get credits section
    credits = config.get_credits_section()
    print(credits)


def test_storybook_formatter():
    """Test storybook formatter"""
    print("\n" + "="*70)
    print("TESTING STORYBOOK FORMATTER")
    print("="*70)

    sample_reports = [
        {
            'sport': 'nba',
            'data': {
                'trends': ['Lakers winning streak continues'],
                'recent_games': [{
                    'home_team': 'Lakers',
                    'away_team': 'Celtics',
                    'home_score': 115,
                    'away_score': 110,
                    'notes': [],
                    'leaders': []
                }],
                'standout_players': [],
                'injuries': [],
                'roster_changes': [],
                'betting_insights': {},
                'must_watch': []
            }
        }
    ]

    config = PresentationConfig(theme=StyleTheme.ESPN)
    formatter = StorybookFormatter(config)

    storybook = formatter.format_storybook_view(
        sample_reports,
        title="Weekly Sports Digest"
    )
    print(storybook[:800] + "...")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  SPORTSTATBOT PRESENTATION FEATURES TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")

    tests = [
        test_tone_levels,
        test_style_themes,
        test_random_openers,
        test_header_templates,
        test_color_coding,
        test_enhanced_formatter,
        test_chart_generator,
        test_timeline_generator,
        test_credits_system,
        test_storybook_formatter
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"TESTS COMPLETE: {passed} passed, {failed} failed")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
