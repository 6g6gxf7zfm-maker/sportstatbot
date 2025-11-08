#!/usr/bin/env python3
"""Generate a demo report with sample data."""
from formatters.slack_formatter import SlackFormatter
from datetime import datetime


def generate_demo_report():
    """Generate a demo report with sample data to showcase format."""

    formatter = SlackFormatter()

    # Sample data for demonstration
    demo_data = {
        'nfl': {
            'enabled': True,
            'trends': [
                {'type': 'hot_streak', 'team': 'Kansas City Chiefs', 'description': '5-game win streak'},
                {'type': 'hot_streak', 'team': 'San Francisco 49ers', 'description': '4-game win streak'},
                {'type': 'cold_streak', 'team': 'New York Giants', 'description': '4-game losing streak'},
            ],
            'recent_games': [
                {
                    'home_team': 'Kansas City Chiefs',
                    'away_team': 'Buffalo Bills',
                    'home_score': 31,
                    'away_score': 28,
                    'winner': 'Kansas City Chiefs',
                    'loser': 'Buffalo Bills',
                    'winner_score': 31,
                    'loser_score': 28,
                    'is_close': True,
                    'is_upset': False,
                    'is_blowout': False,
                    'leaders': {
                        'Passing': {'name': 'Patrick Mahomes', 'value': '368 YDS, 3 TD'},
                        'Rushing': {'name': 'James Cook', 'value': '87 YDS'}
                    }
                },
                {
                    'home_team': 'Miami Dolphins',
                    'away_team': 'Dallas Cowboys',
                    'home_score': 42,
                    'away_score': 17,
                    'winner': 'Miami Dolphins',
                    'loser': 'Dallas Cowboys',
                    'winner_score': 42,
                    'loser_score': 17,
                    'is_close': False,
                    'is_upset': False,
                    'is_blowout': True,
                    'leaders': {
                        'Passing': {'name': 'Tua Tagovailoa', 'value': '295 YDS, 4 TD'},
                        'Receiving': {'name': 'Tyreek Hill', 'value': '156 YDS, 2 TD'}
                    }
                }
            ],
            'standout_players': [
                {'player': 'Patrick Mahomes', 'team': 'Kansas City Chiefs', 'stat_category': 'passing', 'value': '368 YDS, 3 TD'},
                {'player': 'Christian McCaffrey', 'team': 'San Francisco 49ers', 'stat_category': 'rushing', 'value': '145 YDS, 2 TD'},
                {'player': 'Justin Jefferson', 'team': 'Minnesota Vikings', 'stat_category': 'receiving', 'value': '156 YDS, 1 TD'},
                {'player': 'Tua Tagovailoa', 'team': 'Miami Dolphins', 'stat_category': 'passing', 'value': '295 YDS, 4 TD'},
            ],
            'injuries': [
                {'headline': 'Aaron Rodgers questionable for Sunday with ankle injury'},
                {'headline': 'Travis Kelce returns to practice, expected to play'},
            ],
            'roster_changes': [
                {'headline': 'Patriots sign veteran linebacker from practice squad'},
            ],
            'betting_insights': {
                'value_bets': [
                    {
                        'game': 'Cowboys @ Eagles',
                        'recommendation': 'Cowboys +7.5',
                        'odds': '-110',
                        'bookmaker': 'DraftKings',
                        'reason': 'Better odds than market average'
                    }
                ],
                'featured_games': [
                    {'matchup': 'Cowboys @ Eagles', 'spread': '+7.5 (-110)', 'total': '47.5 (-110)'},
                    {'matchup': 'Chiefs @ Broncos', 'spread': '-3.5 (-115)', 'total': '44.5 (-105)'},
                ]
            },
            'must_watch': [
                {
                    'game': 'Dallas Cowboys @ Philadelphia Eagles',
                    'date': '2025-11-10T20:20:00Z',
                    'reasons': ['Division game', 'Playoff implications', 'Rivalry game']
                },
                {
                    'game': 'Kansas City Chiefs @ Denver Broncos',
                    'date': '2025-11-10T13:00:00Z',
                    'reasons': ['Division game']
                }
            ]
        },
        'nba': {
            'enabled': True,
            'trends': [
                {'type': 'hot_streak', 'team': 'Boston Celtics', 'description': '7-game win streak'},
                {'type': 'cold_streak', 'team': 'Detroit Pistons', 'description': '5-game losing streak'},
            ],
            'recent_games': [
                {
                    'home_team': 'Los Angeles Lakers',
                    'away_team': 'Boston Celtics',
                    'home_score': 112,
                    'away_score': 118,
                    'winner': 'Boston Celtics',
                    'loser': 'Los Angeles Lakers',
                    'winner_score': 118,
                    'loser_score': 112,
                    'is_close': True,
                    'is_upset': False,
                    'is_blowout': False,
                    'leaders': {
                        'Points': {'name': 'Jayson Tatum', 'value': '35 PTS'},
                        'Rebounds': {'name': 'Anthony Davis', 'value': '14 REB'}
                    }
                }
            ],
            'standout_players': [
                {'player': 'Jayson Tatum', 'team': 'Boston Celtics', 'stat_category': 'points', 'value': '35 PTS'},
                {'player': 'Luka Dončić', 'team': 'Dallas Mavericks', 'stat_category': 'points', 'value': '42 PTS, 10 AST, 8 REB'},
                {'player': 'Nikola Jokić', 'team': 'Denver Nuggets', 'stat_category': 'points', 'value': 'Triple-double: 28 PTS, 13 REB, 11 AST'},
            ],
            'injuries': [
                {'headline': 'Stephen Curry day-to-day with shoulder soreness'},
                {'headline': 'Kawhi Leonard to miss 2-3 weeks with knee injury'},
            ],
            'roster_changes': [],
            'betting_insights': {
                'value_bets': [],
                'featured_games': [
                    {'matchup': 'Lakers @ Warriors', 'spread': '+2.5 (-110)', 'total': '229.5 (-110)'},
                ]
            },
            'must_watch': [
                {
                    'game': 'Los Angeles Lakers @ Golden State Warriors',
                    'date': '2025-11-09T22:00:00Z',
                    'reasons': ['Western Conference showdown', 'LeBron vs Curry']
                }
            ]
        }
    }

    # Generate the report
    report = formatter.format_full_report(demo_data)
    return report


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DEMO SPORTS REPORT")
    print("="*80 + "\n")

    report = generate_demo_report()
    print(report)

    print("\n" + "="*80)
    print("This is a DEMO report with sample data to showcase the format.")
    print("Run 'python cli.py --all' to generate a real report with live data.")
    print("="*80 + "\n")

    # Save to file
    with open('reports/demo_report.md', 'w') as f:
        f.write(report)
    print("Demo report saved to: reports/demo_report.md\n")
