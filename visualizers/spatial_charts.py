"""
Spatial Chart Generator
========================
Charts for heatmaps, shot charts, and cluster maps.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from .base_chart import BaseChartGenerator
from .chart_utils import create_gradient_colormap


class SpatialChartGenerator(BaseChartGenerator):
    """Generator for spatial visualization charts."""

    def generate_shot_heatmap(self, shot_data, court_type='basketball', filename=None):
        """
        Generate a shot heatmap on a court/field diagram.

        Args:
            shot_data: List of dicts with 'x', 'y', 'made' keys
                      Example: [{'x': 10, 'y': 20, 'made': True}, ...]
            court_type: Type of court ('basketball', 'hockey', 'soccer')
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 11))

        # Draw court/field
        if court_type == 'basketball':
            self._draw_basketball_court(ax)
            x_lim, y_lim = (0, 50), (0, 47)
        elif court_type == 'hockey':
            self._draw_hockey_rink(ax)
            x_lim, y_lim = (0, 200), (0, 85)
        elif court_type == 'soccer':
            self._draw_soccer_field(ax)
            x_lim, y_lim = (0, 120), (0, 80)
        else:
            x_lim, y_lim = (0, 100), (0, 100)

        # Extract coordinates
        x_coords = [shot['x'] for shot in shot_data]
        y_coords = [shot['y'] for shot in shot_data]
        made_shots = [shot.get('made', False) for shot in shot_data]

        # Create hexbin heatmap
        hexbin = ax.hexbin(x_coords, y_coords, C=[1 if made else 0 for made in made_shots],
                          gridsize=20, cmap='YlOrRd', alpha=0.7, edgecolors='black',
                          linewidths=0.2, mincnt=1, reduce_C_function=np.mean)

        # Add colorbar
        cbar = plt.colorbar(hexbin, ax=ax, label='Shot Success Rate')
        cbar.set_label('Success Rate', fontsize=11, fontweight='bold')

        # Overlay individual shots
        made_x = [shot['x'] for shot in shot_data if shot.get('made', False)]
        made_y = [shot['y'] for shot in shot_data if shot.get('made', False)]
        miss_x = [shot['x'] for shot in shot_data if not shot.get('made', False)]
        miss_y = [shot['y'] for shot in shot_data if not shot.get('made', False)]

        ax.scatter(made_x, made_y, c='green', s=30, alpha=0.6, edgecolors='darkgreen',
                  linewidths=0.5, marker='o', label='Made')
        ax.scatter(miss_x, miss_y, c='red', s=30, alpha=0.6, edgecolors='darkred',
                  linewidths=0.5, marker='x', label='Missed')

        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        ax.set_aspect('equal')
        ax.axis('off')
        self.add_legend(ax, location='upper right', framealpha=0.9)

        title = f'Shot Heatmap - {court_type.title()}'
        subtitle = f'Total Shots: {len(shot_data)} | Made: {sum(made_shots)} | Success Rate: {sum(made_shots)/len(shot_data)*100:.1f}%'
        if filename is None:
            filename = f'shot_heatmap_{court_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        self.add_title(ax, title, subtitle)
        from .chart_utils import add_watermark
        add_watermark(ax)
        self.add_timestamp(ax)

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def _draw_basketball_court(self, ax):
        """Draw basketball court lines."""
        # Court outline
        ax.plot([0, 0, 50, 50, 0], [0, 47, 47, 0, 0], 'black', linewidth=2)

        # Half court line
        ax.plot([25, 25], [0, 47], 'black', linewidth=2)

        # Three-point arc (simplified)
        theta = np.linspace(0, np.pi, 100)
        r = 23.75
        x_arc = 5 + r * np.cos(theta)
        y_arc = 25 + r * np.sin(theta)
        ax.plot(x_arc, y_arc, 'black', linewidth=2)

        # Paint/Key
        ax.add_patch(patches.Rectangle((0, 17), 19, 13, fill=False, edgecolor='black', linewidth=2))

        # Hoop
        hoop = patches.Circle((5.25, 25), 0.75, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(hoop)

    def _draw_hockey_rink(self, ax):
        """Draw hockey rink lines."""
        # Rink outline (simplified rectangle with rounded corners)
        ax.plot([0, 0, 200, 200, 0], [0, 85, 85, 0, 0], 'black', linewidth=2)

        # Blue lines
        ax.plot([75, 75], [0, 85], 'blue', linewidth=2)
        ax.plot([125, 125], [0, 85], 'blue', linewidth=2)

        # Red center line
        ax.plot([100, 100], [0, 85], 'red', linewidth=2)

        # Goal creases
        ax.add_patch(patches.Circle((11, 42.5), 6, fill=False, edgecolor='blue', linewidth=2))
        ax.add_patch(patches.Circle((189, 42.5), 6, fill=False, edgecolor='blue', linewidth=2))

    def _draw_soccer_field(self, ax):
        """Draw soccer field lines."""
        # Field outline
        ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], 'white', linewidth=2)

        # Halfway line
        ax.plot([60, 60], [0, 80], 'white', linewidth=2)

        # Center circle
        circle = patches.Circle((60, 40), 9.15, fill=False, edgecolor='white', linewidth=2)
        ax.add_patch(circle)

        # Penalty boxes
        ax.add_patch(patches.Rectangle((0, 22.3), 16.5, 35.4, fill=False, edgecolor='white', linewidth=2))
        ax.add_patch(patches.Rectangle((103.5, 22.3), 16.5, 35.4, fill=False, edgecolor='white', linewidth=2))

        # Goal areas
        ax.add_patch(patches.Rectangle((0, 32.3), 5.5, 15.4, fill=False, edgecolor='white', linewidth=2))
        ax.add_patch(patches.Rectangle((114.5, 32.3), 5.5, 15.4, fill=False, edgecolor='white', linewidth=2))

        # Set green background
        ax.set_facecolor('#2d6e2d')

    def generate_injury_cluster_map(self, injury_data, filename=None):
        """
        Generate a cluster map showing injuries per team.

        Args:
            injury_data: Dict of team names to injury counts or list of injuries
                        Example: {'Lakers': 5, 'Warriors': 3, ...}
                        Or: {'Lakers': ['Player1', 'Player2'], ...}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 10))

        # Convert to counts if needed
        if isinstance(list(injury_data.values())[0], list):
            injury_counts = {team: len(injuries) for team, injuries in injury_data.items()}
        else:
            injury_counts = injury_data

        # Sort by injury count
        sorted_teams = sorted(injury_counts.items(), key=lambda x: x[1], reverse=True)
        teams = [t[0] for t in sorted_teams]
        counts = [t[1] for t in sorted_teams]

        # Create color map based on severity
        colors = []
        for count in counts:
            if count == 0:
                colors.append('#5CB85C')  # Green - healthy
            elif count <= 2:
                colors.append('#FDB927')  # Yellow - minor concerns
            elif count <= 4:
                colors.append('#FF8C00')  # Orange - moderate concerns
            else:
                colors.append('#BF0D3E')  # Red - major concerns

        # Create bubble chart
        y_pos = np.arange(len(teams))
        bubble_sizes = [count * 200 + 100 for count in counts]  # Scale for visibility

        scatter = ax.scatter(counts, y_pos, s=bubble_sizes, c=colors, alpha=0.6,
                           edgecolors='black', linewidths=2)

        # Add count labels inside bubbles
        for i, (count, y) in enumerate(zip(counts, y_pos)):
            ax.text(count, y, str(count), ha='center', va='center',
                   fontweight='bold', fontsize=12, color='white')

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(teams, fontsize=11)
        ax.invert_yaxis()
        self.add_labels(ax, xlabel='Number of Injuries', ylabel='Team')
        self.add_grid(ax, axis='x', alpha=0.3)

        # Add severity zones
        ax.axvspan(0, 2, alpha=0.1, color='green', label='Healthy (0-2)')
        ax.axvspan(2, 4, alpha=0.1, color='yellow', label='Moderate (2-4)')
        ax.axvspan(4, max(counts) + 1, alpha=0.1, color='red', label='Severe (4+)')

        self.add_legend(ax, location='lower right')

        title = 'Team Injury Cluster Map'
        subtitle = f'Total Injuries: {sum(counts)} | Most Affected: {teams[0]} ({counts[0]} injuries)'
        if filename is None:
            filename = f'injury_cluster_map_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        self.add_title(ax, title, subtitle)
        from .chart_utils import add_watermark
        add_watermark(ax)
        self.add_timestamp(ax)

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def generate_zone_efficiency_map(self, zone_data, court_type='basketball', filename=None):
        """
        Generate a zone efficiency map showing performance by court/field area.

        Args:
            zone_data: Dict mapping zone names to efficiency percentages
                      Example: {'Paint': 0.65, 'Mid-Range': 0.42, 'Three-Point': 0.38, ...}
            court_type: Type of court/field
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        from datetime import datetime

        fig, ax = self.create_figure(figsize=(12, 10))

        # Define zones for basketball (simplified)
        if court_type == 'basketball':
            zones = {
                'Paint': {'coords': [(0, 17), (19, 13)], 'pos': (9.5, 25)},
                'Mid-Range Left': {'coords': [(0, 0), (25, 17)], 'pos': (12, 8)},
                'Mid-Range Right': {'coords': [(0, 30), (25, 17)], 'pos': (12, 39)},
                'Three-Point Left': {'coords': [(19, 0), (31, 17)], 'pos': (25, 8)},
                'Three-Point Right': {'coords': [(19, 30), (31, 17)], 'pos': (25, 39)},
                'Corner Three Left': {'coords': [(0, 0), (5, 6)], 'pos': (2.5, 3)},
                'Corner Three Right': {'coords': [(0, 41), (5, 6)], 'pos': (2.5, 44)},
            }

            self._draw_basketball_court(ax)

            # Color zones based on efficiency
            for zone_name, efficiency in zone_data.items():
                if zone_name in zones:
                    zone_info = zones[zone_name]
                    # Color based on efficiency (green = good, red = bad)
                    if efficiency >= 0.50:
                        color = '#5CB85C'
                        alpha = 0.6
                    elif efficiency >= 0.40:
                        color = '#FDB927'
                        alpha = 0.5
                    else:
                        color = '#BF0D3E'
                        alpha = 0.4

                    # Draw zone rectangle/patch
                    rect = patches.Rectangle(
                        zone_info['coords'][0],
                        zone_info['coords'][1][0],
                        zone_info['coords'][1][1],
                        fill=True,
                        facecolor=color,
                        alpha=alpha,
                        edgecolor='black',
                        linewidth=2
                    )
                    ax.add_patch(rect)

                    # Add efficiency label
                    ax.text(zone_info['pos'][0], zone_info['pos'][1],
                           f'{efficiency*100:.1f}%',
                           ha='center', va='center', fontweight='bold',
                           fontsize=11, color='white',
                           bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        ax.set_xlim(0, 50)
        ax.set_ylim(0, 47)
        ax.set_aspect('equal')
        ax.axis('off')

        title = f'Zone Efficiency Map - {court_type.title()}'
        if filename is None:
            filename = f'zone_efficiency_{court_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        self.add_title(ax, title)
        from .chart_utils import add_watermark
        add_watermark(ax)
        self.add_timestamp(ax)

        plt.tight_layout()
        return self.save_and_close(fig, filename)
