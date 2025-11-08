"""
Visualization Manager
=====================
Central manager for coordinating all visualization generation.
"""

import os
from datetime import datetime
from .rating_charts import RatingChartGenerator
from .spatial_charts import SpatialChartGenerator
from .comparison_charts import ComparisonChartGenerator
from .radar_charts import RadarChartGenerator
from .trend_charts import TrendChartGenerator
from .betting_charts import BettingChartGenerator
from .player_cards import PlayerCardGenerator
from .dashboard_generator import DashboardGenerator


class VisualizationManager:
    """
    Central manager for all visualization operations.
    Provides a unified interface for generating charts and dashboards.
    """

    def __init__(self, sport='default', output_dir='visualizations'):
        """
        Initialize visualization manager.

        Args:
            sport: Sport identifier for styling
            output_dir: Base directory for all outputs
        """
        self.sport = sport
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize chart generators
        chart_dir = os.path.join(output_dir, 'charts')
        self.rating_charts = RatingChartGenerator(sport=sport, output_dir=chart_dir)
        self.spatial_charts = SpatialChartGenerator(sport=sport, output_dir=chart_dir)
        self.comparison_charts = ComparisonChartGenerator(sport=sport, output_dir=chart_dir)
        self.radar_charts = RadarChartGenerator(sport=sport, output_dir=chart_dir)
        self.trend_charts = TrendChartGenerator(sport=sport, output_dir=chart_dir)
        self.betting_charts = BettingChartGenerator(sport=sport, output_dir=chart_dir)
        self.player_cards = PlayerCardGenerator(sport=sport, output_dir=chart_dir)

        # Initialize dashboard generator
        dashboard_dir = os.path.join(output_dir, 'dashboards')
        self.dashboard = DashboardGenerator(output_dir=dashboard_dir)

        self.generated_charts = []

    def generate_team_analysis_suite(self, team_name, team_data):
        """
        Generate a complete suite of charts for team analysis.

        Args:
            team_name: Team name
            team_data: Dict with team data (ratings, stats, form, etc.)

        Returns:
            list: Paths to all generated charts
        """
        charts = []

        # Rolling ratings if available
        if 'offensive_ratings' in team_data and 'defensive_ratings' in team_data:
            chart = self.rating_charts.generate_off_def_comparison(
                team_name,
                team_data['offensive_ratings'],
                team_data['defensive_ratings']
            )
            charts.append(chart)

        # Team radar
        if 'metrics' in team_data:
            chart = self.radar_charts.generate_team_radar(team_name, team_data['metrics'])
            charts.append(chart)

        # Form pulse
        if 'recent_results' in team_data:
            chart = self.trend_charts.generate_form_pulse(team_name, team_data['recent_results'])
            charts.append(chart)

        # Season progress
        if 'wins' in team_data and 'losses' in team_data:
            chart = self.trend_charts.generate_season_progress(
                team_name,
                team_data['wins'],
                team_data['losses'],
                team_data.get('target_wins'),
                team_data.get('playoff_threshold')
            )
            charts.append(chart)

        self.generated_charts.extend(charts)
        return charts

    def generate_matchup_analysis(self, team1, team2, matchup_data):
        """
        Generate charts for matchup analysis.

        Args:
            team1: First team name
            team2: Second team name
            matchup_data: Dict with matchup data

        Returns:
            list: Paths to generated charts
        """
        charts = []

        # Momentum gauge
        if 'momentum_score' in matchup_data:
            chart = self.trend_charts.generate_momentum_gauge(
                team1, team2, matchup_data['momentum_score']
            )
            charts.append(chart)

        # Team comparison radar
        if 'team_metrics' in matchup_data:
            chart = self.radar_charts.generate_comparison_radar(matchup_data['team_metrics'])
            charts.append(chart)

        # Scatter comparison
        if 'offensive_ratings' in matchup_data and 'defensive_ratings' in matchup_data:
            chart = self.comparison_charts.generate_scatter_comparison(
                matchup_data['offensive_ratings'],
                matchup_data['defensive_ratings'],
                [team1, team2],
                'Offensive Rating',
                'Defensive Rating',
                highlight_teams=[team1, team2]
            )
            charts.append(chart)

        self.generated_charts.extend(charts)
        return charts

    def generate_betting_analysis(self, betting_data):
        """
        Generate betting analysis charts.

        Args:
            betting_data: Dict with betting data

        Returns:
            list: Paths to generated charts
        """
        charts = []

        # Top edges
        if 'edges' in betting_data:
            chart = self.betting_charts.generate_top_edges(betting_data['edges'])
            charts.append(chart)

        # Line movement
        if 'line_movement' in betting_data:
            for game_data in betting_data['line_movement']:
                chart = self.betting_charts.generate_line_movement(
                    game_data['game'],
                    game_data['timestamps'],
                    game_data['opening_lines'],
                    game_data['current_lines'],
                    game_data.get('line_type', 'spread')
                )
                charts.append(chart)

        # Spread delta
        if 'spreads' in betting_data:
            chart = self.comparison_charts.generate_spread_delta(betting_data['spreads'])
            charts.append(chart)

        self.generated_charts.extend(charts)
        return charts

    def generate_league_overview(self, league_data):
        """
        Generate league-wide overview charts.

        Args:
            league_data: Dict with league-wide data

        Returns:
            list: Paths to generated charts
        """
        charts = []

        # League parity
        if 'team_strengths' in league_data:
            chart = self.trend_charts.generate_league_parity_chart(league_data['team_strengths'])
            charts.append(chart)

        # Injury cluster map
        if 'injuries' in league_data:
            chart = self.spatial_charts.generate_injury_cluster_map(league_data['injuries'])
            charts.append(chart)

        # Rating distribution
        if 'team_ratings' in league_data:
            chart = self.rating_charts.generate_rating_distribution(
                league_data['team_ratings'],
                league_data.get('highlight_team')
            )
            charts.append(chart)

        # Performance matrix
        if 'team_metrics' in league_data:
            chart = self.comparison_charts.generate_performance_matrix(league_data['team_metrics'])
            charts.append(chart)

        self.generated_charts.extend(charts)
        return charts

    def generate_player_analysis(self, player_data):
        """
        Generate player analysis visualizations.

        Args:
            player_data: Dict or list of player data

        Returns:
            list: Paths to generated charts
        """
        charts = []

        if isinstance(player_data, list):
            # Multiple players - roster cards
            team_name = player_data[0].get('team', 'Team')
            chart = self.player_cards.generate_team_roster_cards(team_name, player_data)
            charts.append(chart)
        elif 'comparison' in player_data:
            # Player comparison
            chart = self.player_cards.generate_comparison_card(
                player_data['player1'],
                player_data['player2']
            )
            charts.append(chart)
        else:
            # Single player card
            chart = self.player_cards.generate_player_card(player_data)
            charts.append(chart)

        self.generated_charts.extend(charts)
        return charts

    def generate_comprehensive_dashboard(self, dashboard_config):
        """
        Generate a comprehensive HTML dashboard.

        Args:
            dashboard_config: Dict with dashboard configuration
                             {
                                 'title': 'Dashboard Title',
                                 'metrics': {...},
                                 'charts': [...],
                                 'tables': [...],
                                 'export_type': 'full' or 'notion'
                             }

        Returns:
            str: Path to generated dashboard
        """
        export_type = dashboard_config.get('export_type', 'full')

        if export_type == 'notion':
            return self.dashboard.generate_notion_compatible_export(dashboard_config)
        else:
            return self.dashboard.generate_full_dashboard(dashboard_config)

    def generate_daily_report_visualizations(self, report_data):
        """
        Generate all visualizations for a daily report.

        Args:
            report_data: Dict with daily report data from SportsReportGenerator

        Returns:
            dict: Organized chart paths by category
        """
        all_charts = {
            'team_analysis': [],
            'betting': [],
            'league_overview': [],
            'player_highlights': []
        }

        # Generate team analysis charts for each sport
        for sport, data in report_data.items():
            if not isinstance(data, dict):
                continue

            # Team trends and form
            if 'trends' in data:
                for trend in data['trends'][:3]:  # Top 3 teams
                    team_charts = self.generate_team_analysis_suite(
                        trend.get('team', ''),
                        {
                            'recent_results': ['W'] * trend.get('wins', 0),
                            'wins': trend.get('wins', 0),
                            'losses': trend.get('losses', 0)
                        }
                    )
                    all_charts['team_analysis'].extend(team_charts)

            # Betting insights
            if 'betting_insights' in data and data['betting_insights']:
                betting_charts = self.generate_betting_analysis({
                    'edges': data['betting_insights'].get('value_bets', [])
                })
                all_charts['betting'].extend(betting_charts)

        return all_charts

    def create_summary_report(self, title='SportStatBot Visualization Report'):
        """
        Create a summary report of all generated visualizations.

        Args:
            title: Report title

        Returns:
            str: Path to summary dashboard
        """
        dashboard_data = {
            'title': title,
            'subtitle': f'Generated {len(self.generated_charts)} visualizations',
            'charts': [
                {
                    'title': os.path.basename(chart).replace('_', ' ').replace('.png', '').title(),
                    'path': chart
                }
                for chart in self.generated_charts
            ],
            'metrics': {
                'Total Charts': len(self.generated_charts),
                'Generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'Sport': self.sport.upper()
            }
        }

        return self.dashboard.generate_full_dashboard(dashboard_data)

    def clear_generated_charts(self):
        """Clear the list of generated charts."""
        self.generated_charts = []

    def get_generated_charts(self):
        """Get list of all generated chart paths."""
        return self.generated_charts.copy()
