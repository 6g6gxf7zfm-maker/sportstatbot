"""
Chart Generation System for SportStatBot
Creates statistical visualizations for reports
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime


class ChartGenerator:
    """Generate charts and graphs for sports statistics"""

    def __init__(self, output_dir: str = "reports/charts"):
        """Initialize chart generator with output directory"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')

    def generate_streak_chart(
        self,
        team_name: str,
        wins: int,
        losses: int,
        sport: str = "NBA"
    ) -> str:
        """Generate a streak visualization chart"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data
        categories = ['Wins', 'Losses']
        values = [wins, losses]
        colors = ['#2ecc71', '#e74c3c']  # Green for wins, red for losses

        # Create bar chart
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Styling
        ax.set_ylabel('Games', fontsize=12, fontweight='bold')
        ax.set_title(f'{team_name} Recent Streak', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(values) + 2)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')

        # Grid
        ax.grid(axis='y', alpha=0.3)

        # Save
        filename = f"{sport}_{team_name.replace(' ', '_')}_streak_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_standings_chart(
        self,
        standings_data: List[Dict],
        sport: str = "NBA",
        division: str = "Conference"
    ) -> str:
        """Generate a standings visualization"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Extract data (top 10 teams)
        teams = [team['team'][:15] for team in standings_data[:10]]  # Truncate long names
        wins = [team['wins'] for team in standings_data[:10]]
        losses = [team['losses'] for team in standings_data[:10]]

        # Calculate win percentage
        win_pcts = [w / (w + l) * 100 if (w + l) > 0 else 0 for w, l in zip(wins, losses)]

        # Create horizontal bar chart
        y_pos = range(len(teams))
        colors = ['#2ecc71' if pct > 50 else '#e74c3c' for pct in win_pcts]

        bars = ax.barh(y_pos, win_pcts, color=colors, alpha=0.7, edgecolor='black')

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(teams)
        ax.set_xlabel('Win Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{sport} {division} Standings', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 100)

        # Add percentage labels
        for i, (bar, pct) in enumerate(zip(bars, win_pcts)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                   f'{pct:.1f}%',
                   ha='left', va='center', fontweight='bold')

        # Grid
        ax.grid(axis='x', alpha=0.3)

        # Save
        filename = f"{sport}_standings_{division.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_player_performance_chart(
        self,
        player_name: str,
        stats: Dict[str, float],
        sport: str = "NBA"
    ) -> str:
        """Generate a player performance visualization"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract stats
        stat_names = list(stats.keys())[:6]  # Top 6 stats
        stat_values = [stats[name] for name in stat_names]

        # Create bar chart
        bars = ax.bar(stat_names, stat_values, color='#3498db', alpha=0.7, edgecolor='black')

        # Styling
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title(f'{player_name} Performance', fontsize=14, fontweight='bold')
        ax.set_xticklabels(stat_names, rotation=45, ha='right')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontweight='bold')

        # Grid
        ax.grid(axis='y', alpha=0.3)

        # Save
        filename = f"{sport}_{player_name.replace(' ', '_')}_performance_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_score_progression_chart(
        self,
        game_data: Dict,
        sport: str = "NBA"
    ) -> str:
        """Generate a score progression chart for a game"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Mock quarter-by-quarter scoring (in real implementation, this would come from API)
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        home_team = game_data.get('home_team', 'Home')
        away_team = game_data.get('away_team', 'Away')

        # Generate sample quarter scores (would be real data)
        home_scores = [25, 28, 22, 30]  # Example
        away_scores = [22, 30, 28, 24]  # Example

        # Cumulative scores
        home_cumulative = [sum(home_scores[:i+1]) for i in range(len(home_scores))]
        away_cumulative = [sum(away_scores[:i+1]) for i in range(len(away_scores))]

        # Plot lines
        ax.plot(quarters, home_cumulative, marker='o', linewidth=2,
               label=home_team, color='#2ecc71')
        ax.plot(quarters, away_cumulative, marker='s', linewidth=2,
               label=away_team, color='#e74c3c')

        # Styling
        ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Score', fontsize=12, fontweight='bold')
        ax.set_title(f'{away_team} vs {home_team} - Score Progression',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        # Save
        filename = f"{sport}_game_progression_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_team_comparison_chart(
        self,
        team1: str,
        team2: str,
        stats1: Dict[str, float],
        stats2: Dict[str, float],
        sport: str = "NBA"
    ) -> str:
        """Generate a team comparison chart"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Get common stats
        stat_names = list(set(stats1.keys()) & set(stats2.keys()))[:5]
        team1_values = [stats1[stat] for stat in stat_names]
        team2_values = [stats2[stat] for stat in stat_names]

        # Bar positions
        x = range(len(stat_names))
        width = 0.35

        # Create grouped bars
        bars1 = ax.bar([i - width/2 for i in x], team1_values, width,
                       label=team1, color='#3498db', alpha=0.7, edgecolor='black')
        bars2 = ax.bar([i + width/2 for i in x], team2_values, width,
                       label=team2, color='#e74c3c', alpha=0.7, edgecolor='black')

        # Styling
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title(f'{team1} vs {team2} Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(stat_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Save
        filename = f"{sport}_comparison_{team1.replace(' ', '_')}_vs_{team2.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_betting_odds_chart(
        self,
        games: List[Dict],
        sport: str = "NBA"
    ) -> str:
        """Generate betting odds comparison chart"""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Extract data (top 5 games)
        matchups = []
        spreads = []
        totals = []

        for game in games[:5]:
            home = game.get('home_team', 'Home')
            away = game.get('away_team', 'Away')
            matchups.append(f"{away[:10]}\n@\n{home[:10]}")
            spreads.append(game.get('spread', 0))
            totals.append(game.get('total', 0))

        # Create subplot for spreads
        y_pos = range(len(matchups))
        colors = ['#2ecc71' if s > 0 else '#e74c3c' for s in spreads]

        bars = ax.barh(y_pos, spreads, color=colors, alpha=0.7, edgecolor='black')

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(matchups, fontsize=9)
        ax.set_xlabel('Spread', fontsize=12, fontweight='bold')
        ax.set_title(f'{sport} Betting Lines', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linewidth=1, linestyle='--')
        ax.grid(axis='x', alpha=0.3)

        # Add spread labels
        for i, (bar, spread) in enumerate(zip(bars, spreads)):
            width = bar.get_width()
            x_pos = width + (0.5 if width >= 0 else -0.5)
            ax.text(x_pos, bar.get_y() + bar.get_height()/2.,
                   f'{spread:+.1f}',
                   ha='left' if width >= 0 else 'right',
                   va='center', fontweight='bold')

        # Save
        filename = f"{sport}_betting_odds_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        return filepath

    def embed_chart_in_markdown(self, chart_path: str, caption: str = "") -> str:
        """Generate markdown to embed a chart"""
        if not os.path.exists(chart_path):
            return ""

        md = f"\n![{caption}]({chart_path})\n"
        if caption:
            md += f"*{caption}*\n"
        return md

    def generate_all_charts_for_report(self, data: Dict, sport: str) -> List[str]:
        """Generate all relevant charts for a sport report"""
        charts = []

        # Standings chart
        if data.get('standings'):
            try:
                chart_path = self.generate_standings_chart(data['standings'], sport)
                charts.append(chart_path)
            except Exception as e:
                print(f"Error generating standings chart: {e}")

        # Player performance charts (top 3 players)
        if data.get('standout_players'):
            for player in data['standout_players'][:3]:
                try:
                    # Mock stats for demonstration
                    stats = {'PTS': 30, 'REB': 10, 'AST': 8, 'STL': 2, 'BLK': 1}
                    chart_path = self.generate_player_performance_chart(
                        player.get('name', 'Player'),
                        stats,
                        sport
                    )
                    charts.append(chart_path)
                except Exception as e:
                    print(f"Error generating player chart: {e}")

        # Betting odds chart
        if data.get('must_watch'):
            try:
                chart_path = self.generate_betting_odds_chart(data['must_watch'], sport)
                charts.append(chart_path)
            except Exception as e:
                print(f"Error generating betting chart: {e}")

        return charts
