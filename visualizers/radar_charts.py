"""
Radar Chart Generator
=====================
Charts for team radar plots across multiple metrics.
"""

import matplotlib.pyplot as plt
import numpy as np
from math import pi
from datetime import datetime
from .base_chart import BaseChartGenerator


class RadarChartGenerator(BaseChartGenerator):
    """Generator for radar/spider charts."""

    def generate_team_radar(self, team_name, metrics_data, filename=None):
        """
        Generate a radar chart for a team across multiple metrics.

        Args:
            team_name: Team name
            metrics_data: Dict of metric names to values (0-100 scale)
                         Example: {'Offense': 85, 'Defense': 72, 'Rebounding': 78, ...}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Prepare data
        categories = list(metrics_data.keys())
        values = list(metrics_data.values())

        # Number of variables
        N = len(categories)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * pi for n in range(N)]
        values += values[:1]  # Complete the circle
        angles += angles[:1]

        # Plot
        ax.plot(angles, values, 'o-', linewidth=2.5, color=self.colors['primary'],
               label=team_name, markersize=8)
        ax.fill(angles, values, alpha=0.25, color=self.colors['primary'])

        # Fix axis to go in the right order
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=11, fontweight='bold')

        # Set y-axis limits
        ax.set_ylim(0, 100)

        # Add value labels
        for angle, value, category in zip(angles[:-1], values[:-1], categories):
            ax.text(angle, value + 5, f'{value:.0f}', ha='center', va='center',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))

        # Add grid circles
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color='gray')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Add legend
        self.add_legend(ax, location='upper right', framealpha=0.9)

        title = f'{team_name} - Performance Radar'
        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_radar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        ax.set_title(title, size=16, fontweight='bold', pad=30)

        from .chart_utils import add_watermark
        add_watermark(ax, position='center', alpha=0.1)
        self.add_timestamp(ax, position='bottom_right')

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def generate_comparison_radar(self, teams_data, filename=None):
        """
        Generate a radar chart comparing multiple teams.

        Args:
            teams_data: Dict of team names to metrics dicts
                       Example: {'Lakers': {'Off': 85, 'Def': 72, ...}, 'Warriors': {...}}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 12), subplot_kw=dict(projection='polar'))

        # Get categories from first team
        first_team = list(teams_data.keys())[0]
        categories = list(teams_data[first_team].keys())
        N = len(categories)

        # Compute angles
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Color palette for teams
        colors_palette = [
            self.colors['primary'],
            self.colors['secondary'],
            self.colors['accent'],
            '#5CB85C',
            '#BF0D3E',
            '#FDB927',
            '#17408B',
            '#88C0D0'
        ]

        # Plot each team
        for i, (team_name, metrics) in enumerate(teams_data.items()):
            values = list(metrics.values())
            values += values[:1]

            color = colors_palette[i % len(colors_palette)]
            ax.plot(angles, values, 'o-', linewidth=2.5, label=team_name,
                   color=color, markersize=6)
            ax.fill(angles, values, alpha=0.15, color=color)

        # Styling
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color='gray')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Legend
        self.add_legend(ax, location='upper right', framealpha=0.9, fontsize=10)

        title = 'Team Comparison Radar'
        if filename is None:
            filename = f'team_comparison_radar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        ax.set_title(title, size=16, fontweight='bold', pad=30)

        from .chart_utils import add_watermark
        add_watermark(ax, position='center', alpha=0.1)
        self.add_timestamp(ax, position='bottom_right')

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def generate_stacked_radar(self, team_name, offense_metrics, defense_metrics, filename=None):
        """
        Generate a stacked radar chart showing offense and defense separately.

        Args:
            team_name: Team name
            offense_metrics: Dict of offensive metric names to values
            defense_metrics: Dict of defensive metric names to values
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8),
                                       subplot_kw=dict(projection='polar'))

        # Offensive radar
        categories_off = list(offense_metrics.keys())
        values_off = list(offense_metrics.values())
        N_off = len(categories_off)
        angles_off = [n / float(N_off) * 2 * pi for n in range(N_off)]
        values_off += values_off[:1]
        angles_off += angles_off[:1]

        ax1.plot(angles_off, values_off, 'o-', linewidth=2.5,
                color=self.colors['secondary'], markersize=8)
        ax1.fill(angles_off, values_off, alpha=0.25, color=self.colors['secondary'])
        ax1.set_xticks(angles_off[:-1])
        ax1.set_xticklabels(categories_off, size=10, fontweight='bold')
        ax1.set_ylim(0, 100)
        ax1.set_yticks([20, 40, 60, 80, 100])
        ax1.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color='gray')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.set_title('Offensive Metrics', size=14, fontweight='bold', pad=20)

        # Defensive radar
        categories_def = list(defense_metrics.keys())
        values_def = list(defense_metrics.values())
        N_def = len(categories_def)
        angles_def = [n / float(N_def) * 2 * pi for n in range(N_def)]
        values_def += values_def[:1]
        angles_def += angles_def[:1]

        ax2.plot(angles_def, values_def, 'o-', linewidth=2.5,
                color=self.colors['primary'], markersize=8)
        ax2.fill(angles_def, values_def, alpha=0.25, color=self.colors['primary'])
        ax2.set_xticks(angles_def[:-1])
        ax2.set_xticklabels(categories_def, size=10, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.set_yticks([20, 40, 60, 80, 100])
        ax2.set_yticklabels(['20', '40', '60', '80', '100'], size=8, color='gray')
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.set_title('Defensive Metrics', size=14, fontweight='bold', pad=20)

        # Main title
        fig.suptitle(f'{team_name} - Offensive & Defensive Radar',
                    fontsize=18, fontweight='bold', y=0.98)

        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_stacked_radar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        from .chart_utils import add_watermark
        add_watermark(ax1, position='center', alpha=0.1)

        plt.tight_layout()
        return self.save_and_close(fig, filename)
