"""
Comparison Chart Generator
===========================
Charts for comparing expected vs actual metrics, spreads, and deltas.
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from .base_chart import BaseChartGenerator
from .chart_utils import format_percentage, create_annotation


class ComparisonChartGenerator(BaseChartGenerator):
    """Generator for comparison charts."""

    def generate_expected_vs_actual(self, team_data, metric='goals', filename=None):
        """
        Generate expected vs actual comparison chart.

        Args:
            team_data: Dict with team names and their expected/actual values
                      Example: {'Lakers': {'expected': [25, 28, 22], 'actual': [27, 26, 24]}}
            metric: Metric name (e.g., 'goals', 'points', 'runs')
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 8))

        teams = list(team_data.keys())
        n_teams = len(teams)
        x = np.arange(n_teams)
        width = 0.35

        # Calculate totals
        expected_totals = [sum(data['expected']) for data in team_data.values()]
        actual_totals = [sum(data['actual']) for data in team_data.values()]

        # Create bars
        bars1 = ax.bar(x - width/2, expected_totals, width, label=f'Expected {metric.title()}',
                      color=self.colors['primary'], alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x + width/2, actual_totals, width, label=f'Actual {metric.title()}',
                      color=self.colors['secondary'], alpha=0.8, edgecolor='black', linewidth=0.5)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold', fontsize=9)

        # Calculate and show difference
        for i, (exp, act) in enumerate(zip(expected_totals, actual_totals)):
            diff = act - exp
            y_pos = max(exp, act) + 2
            color = '#5CB85C' if diff > 0 else '#BF0D3E' if diff < 0 else 'gray'
            symbol = '+' if diff > 0 else ''
            ax.text(i, y_pos, f'{symbol}{diff:.0f}',
                   ha='center', va='bottom', color=color,
                   fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=color))

        # Styling
        ax.set_xticks(x)
        ax.set_xticklabels(teams, rotation=45, ha='right')
        self.add_labels(ax, xlabel='Team', ylabel=metric.title())
        self.add_grid(ax, axis='y', alpha=0.3)
        self.add_legend(ax, location='upper left')

        # Add diagonal reference line
        max_val = max(max(expected_totals), max(actual_totals))
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, linewidth=1,
               label='Perfect Match')

        title = f'Expected vs Actual {metric.title()}'
        subtitle = f'Overperformers in green, Underperformers in red'
        if filename is None:
            filename = f'expected_vs_actual_{metric}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_spread_delta(self, game_data, filename=None):
        """
        Generate spread vs fair line delta chart.

        Args:
            game_data: List of dicts with game info
                      Example: [{'game': 'LAL vs GSW', 'spread': -5.5, 'fair_line': -4.0}, ...]
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 8))

        games = [g['game'] for g in game_data]
        spreads = [g['spread'] for g in game_data]
        fair_lines = [g['fair_line'] for g in game_data]
        deltas = [spread - fair for spread, fair in zip(spreads, fair_lines)]

        x = np.arange(len(games))
        width = 0.25

        # Create bars
        bars1 = ax.bar(x - width, spreads, width, label='Actual Spread',
                      color=self.colors['primary'], alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x, fair_lines, width, label='Fair Line',
                      color=self.colors['secondary'], alpha=0.8, edgecolor='black', linewidth=0.5)
        bars3 = ax.bar(x + width, deltas, width, label='Delta (Value)',
                      color=['#5CB85C' if d > 0 else '#BF0D3E' if d < 0 else 'gray' for d in deltas],
                      alpha=0.8, edgecolor='black', linewidth=0.5)

        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                y_pos = height if height > 0 else height - 0.5
                va = 'bottom' if height > 0 else 'top'
                ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                       f'{height:.1f}',
                       ha='center', va=va, fontweight='bold', fontsize=8)

        # Highlight high-value games
        for i, delta in enumerate(deltas):
            if abs(delta) >= 2.0:  # Threshold for "edge"
                create_annotation(ax, f'Edge: {abs(delta):.1f}', xy=(x[i] + width, delta),
                                xytext=(20, 20 if delta > 0 else -20),
                                style='success' if delta > 0 else 'danger')

        # Styling
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(games, rotation=45, ha='right', fontsize=9)
        self.add_labels(ax, xlabel='Game', ylabel='Line Value')
        self.add_grid(ax, axis='y', alpha=0.3)
        self.add_legend(ax, location='upper left')

        title = 'Spread vs Fair Line Delta (Betting Value)'
        subtitle = 'Green = Potential value on underdog | Red = Potential value on favorite'
        if filename is None:
            filename = f'spread_delta_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_scatter_comparison(self, x_data, y_data, team_names, x_label, y_label,
                                   highlight_teams=None, filename=None):
        """
        Generate a scatter plot comparing two metrics.

        Args:
            x_data: List of x-axis values
            y_data: List of y-axis values
            team_names: List of team names
            x_label: Label for x-axis
            y_label: Label for y-axis
            highlight_teams: List of team names to highlight (optional)
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 10))

        # Create colors for highlighting
        colors = []
        sizes = []
        for team in team_names:
            if highlight_teams and team in highlight_teams:
                colors.append(self.colors['accent'])
                sizes.append(300)
            else:
                colors.append(self.colors['primary'])
                sizes.append(150)

        # Scatter plot
        scatter = ax.scatter(x_data, y_data, c=colors, s=sizes, alpha=0.6,
                           edgecolors='black', linewidths=1.5)

        # Add team labels
        for i, team in enumerate(team_names):
            ax.annotate(team, (x_data[i], y_data[i]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray'))

        # Add quadrant lines at means
        mean_x = np.mean(x_data)
        mean_y = np.mean(y_data)
        ax.axvline(x=mean_x, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
        ax.axhline(y=mean_y, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)

        # Add quadrant labels
        x_range = max(x_data) - min(x_data)
        y_range = max(y_data) - min(y_data)
        ax.text(mean_x + x_range*0.4, mean_y + y_range*0.4, 'Elite',
               fontsize=12, fontweight='bold', color='green', alpha=0.5,
               ha='center', va='center')
        ax.text(mean_x - x_range*0.4, mean_y + y_range*0.4, 'Good Defense',
               fontsize=12, fontweight='bold', color='blue', alpha=0.5,
               ha='center', va='center')
        ax.text(mean_x + x_range*0.4, mean_y - y_range*0.4, 'Good Offense',
               fontsize=12, fontweight='bold', color='orange', alpha=0.5,
               ha='center', va='center')
        ax.text(mean_x - x_range*0.4, mean_y - y_range*0.4, 'Struggling',
               fontsize=12, fontweight='bold', color='red', alpha=0.5,
               ha='center', va='center')

        # Styling
        self.add_labels(ax, xlabel=x_label, ylabel=y_label)
        self.add_grid(ax, alpha=0.3)

        title = f'{x_label} vs {y_label}'
        if filename is None:
            filename = f'scatter_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_performance_matrix(self, team_metrics, filename=None):
        """
        Generate a performance matrix heatmap.

        Args:
            team_metrics: Dict of teams to dict of metrics
                         Example: {'Lakers': {'Points': 115, 'Rebounds': 45, ...}, ...}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        import seaborn as sns
        import pandas as pd

        fig, ax = self.create_figure(figsize=(14, 10))

        # Convert to DataFrame
        df = pd.DataFrame(team_metrics).T

        # Normalize each column (metric) to 0-100 scale for comparison
        df_normalized = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()) * 100, axis=0)

        # Create heatmap
        sns.heatmap(df_normalized, annot=df, fmt='.1f', cmap='RdYlGn',
                   center=50, ax=ax, cbar_kws={'label': 'Percentile'},
                   linewidths=0.5, linecolor='black')

        ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
        ax.set_ylabel('Team', fontsize=12, fontweight='bold')

        title = 'Team Performance Matrix'
        subtitle = 'Higher values (green) are better'
        if filename is None:
            filename = f'performance_matrix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)
