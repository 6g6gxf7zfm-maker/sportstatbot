"""
Player Card Generator
=====================
Generate visual player cards with headshots, form charts, and bio information.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw
import io
from .base_chart import BaseChartGenerator
from .chart_utils import format_percentage


class PlayerCardGenerator(BaseChartGenerator):
    """Generator for player card visualizations."""

    def generate_player_card(self, player_data, filename=None):
        """
        Generate a comprehensive player card with stats and form.

        Args:
            player_data: Dict with player information
                        {
                            'name': 'LeBron James',
                            'team': 'Lakers',
                            'position': 'SF',
                            'number': 23,
                            'stats': {'PPG': 27.5, 'RPG': 8.2, 'APG': 7.1},
                            'recent_form': [25, 32, 28, 30, 27],  # Last 5 games
                            'season_avg': 27.5,
                            'headshot_url': None  # Optional image URL or path
                        }
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig = plt.figure(figsize=(10, 14))

        # Create grid for layout
        gs = fig.add_gridspec(5, 2, height_ratios=[1.5, 1, 1, 1, 0.8], hspace=0.3, wspace=0.3)

        # Header section with player name and number
        ax_header = fig.add_subplot(gs[0, :])
        self._create_header(ax_header, player_data)

        # Headshot section (placeholder or actual image)
        ax_headshot = fig.add_subplot(gs[1, 0])
        self._create_headshot(ax_headshot, player_data.get('headshot_url'))

        # Bio info section
        ax_bio = fig.add_subplot(gs[1, 1])
        self._create_bio(ax_bio, player_data)

        # Stats section
        ax_stats = fig.add_subplot(gs[2, :])
        self._create_stats_display(ax_stats, player_data.get('stats', {}))

        # Recent form chart
        ax_form = fig.add_subplot(gs[3, :])
        self._create_form_chart(ax_form, player_data)

        # Footer with team info
        ax_footer = fig.add_subplot(gs[4, :])
        self._create_footer(ax_footer, player_data)

        if filename is None:
            player_name_safe = player_data['name'].lower().replace(' ', '_')
            filename = f'player_card_{player_name_safe}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        from .chart_utils import add_watermark
        add_watermark(ax_footer, position='bottom_right', alpha=0.3)

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def _create_header(self, ax, player_data):
        """Create header with player name and number."""
        ax.axis('off')

        # Background
        header_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                   facecolor=self.colors['primary'], edgecolor='black',
                                   linewidth=3, transform=ax.transAxes)
        ax.add_patch(header_box)

        # Player name
        ax.text(0.05, 0.5, player_data['name'], transform=ax.transAxes,
               fontsize=32, fontweight='bold', color='white', va='center')

        # Jersey number (large)
        if 'number' in player_data:
            ax.text(0.95, 0.5, f"#{player_data['number']}", transform=ax.transAxes,
                   fontsize=48, fontweight='bold', color='white', va='center', ha='right',
                   alpha=0.7)

    def _create_headshot(self, ax, headshot_url):
        """Create headshot section (placeholder or actual image)."""
        ax.axis('off')

        if headshot_url:
            try:
                # Load and display actual image
                # In a real implementation, you'd load from URL or file
                # img = Image.open(headshot_url)
                # ax.imshow(img)
                pass
            except:
                pass

        # Create placeholder silhouette
        circle = patches.Circle((0.5, 0.5), 0.35, transform=ax.transAxes,
                              facecolor=self.colors['primary'], edgecolor='black',
                              linewidth=3, alpha=0.3)
        ax.add_patch(circle)

        # Add player icon/text
        ax.text(0.5, 0.5, '👤', transform=ax.transAxes,
               fontsize=80, ha='center', va='center', alpha=0.5)

    def _create_bio(self, ax, player_data):
        """Create bio information section."""
        ax.axis('off')

        bio_info = [
            ('Team', player_data.get('team', 'N/A')),
            ('Position', player_data.get('position', 'N/A')),
            ('Height', player_data.get('height', 'N/A')),
            ('Weight', player_data.get('weight', 'N/A')),
        ]

        y_pos = 0.9
        for label, value in bio_info:
            ax.text(0.1, y_pos, f'{label}:', transform=ax.transAxes,
                   fontsize=11, fontweight='bold', color=self.colors['primary'])
            ax.text(0.5, y_pos, str(value), transform=ax.transAxes,
                   fontsize=11, color='black')
            y_pos -= 0.2

        # Add border
        border = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                          fill=False, edgecolor=self.colors['primary'], linewidth=2)
        ax.add_patch(border)

    def _create_stats_display(self, ax, stats):
        """Create stats display section."""
        ax.axis('off')

        if not stats:
            return

        stat_names = list(stats.keys())
        stat_values = list(stats.values())
        n_stats = len(stat_names)

        # Create stat boxes
        box_width = 0.9 / n_stats
        for i, (name, value) in enumerate(zip(stat_names, stat_values)):
            x_pos = 0.05 + i * (0.9 / n_stats)

            # Stat box
            stat_box = FancyBboxPatch((x_pos, 0.2), box_width * 0.9, 0.6,
                                     boxstyle="round,pad=0.02", transform=ax.transAxes,
                                     facecolor=self.colors['secondary'], edgecolor='black',
                                     linewidth=2, alpha=0.8)
            ax.add_patch(stat_box)

            # Stat value (large)
            ax.text(x_pos + box_width * 0.45, 0.6, f'{value:.1f}' if isinstance(value, float) else str(value),
                   transform=ax.transAxes, fontsize=20, fontweight='bold',
                   color='white', ha='center', va='center')

            # Stat name (small)
            ax.text(x_pos + box_width * 0.45, 0.3, name, transform=ax.transAxes,
                   fontsize=10, fontweight='bold', color='white', ha='center', va='center')

    def _create_form_chart(self, ax, player_data):
        """Create recent form chart."""
        recent_form = player_data.get('recent_form', [])
        season_avg = player_data.get('season_avg', 0)

        if not recent_form:
            ax.axis('off')
            return

        games = list(range(1, len(recent_form) + 1))

        # Bar chart
        colors = ['#5CB85C' if val >= season_avg else '#BF0D3E' for val in recent_form]
        bars = ax.bar(games, recent_form, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, val in zip(bars, recent_form):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.0f}' if isinstance(val, float) else str(val),
                   ha='center', va='bottom', fontweight='bold', fontsize=10)

        # Season average line
        if season_avg > 0:
            ax.axhline(y=season_avg, color='blue', linestyle='--', linewidth=2,
                      alpha=0.7, label=f'Season Avg: {season_avg:.1f}')

        # Styling
        ax.set_xlabel('Last 5 Games', fontsize=11, fontweight='bold')
        ax.set_ylabel('Points', fontsize=11, fontweight='bold')
        ax.set_title('Recent Form', fontsize=13, fontweight='bold', pad=10)
        ax.grid(True, axis='y', alpha=0.3)
        ax.legend(loc='upper left')

    def _create_footer(self, ax, player_data):
        """Create footer with team branding."""
        ax.axis('off')

        # Team banner
        banner = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                          facecolor=self.colors['accent'], edgecolor='black',
                          linewidth=2, alpha=0.6)
        ax.add_patch(banner)

        # Team name
        team_name = player_data.get('team', '')
        ax.text(0.5, 0.5, team_name.upper(), transform=ax.transAxes,
               fontsize=18, fontweight='bold', color='black', ha='center', va='center')

    def generate_comparison_card(self, player1_data, player2_data, filename=None):
        """
        Generate a comparison card for two players.

        Args:
            player1_data: First player's data
            player2_data: Second player's data
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

        # Create mini player cards for each
        self._create_mini_card(ax1, player1_data)
        self._create_mini_card(ax2, player2_data)

        # Main title
        fig.suptitle(f"{player1_data['name']} vs {player2_data['name']}",
                    fontsize=20, fontweight='bold', y=0.98)

        if filename is None:
            p1_name = player1_data['name'].lower().replace(' ', '_')
            p2_name = player2_data['name'].lower().replace(' ', '_')
            filename = f'comparison_{p1_name}_vs_{p2_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def _create_mini_card(self, ax, player_data):
        """Create a mini player card for comparison."""
        ax.axis('off')

        # Player name header
        header = FancyBboxPatch((0.05, 0.85), 0.9, 0.12, boxstyle="round,pad=0.01",
                               facecolor=self.colors['primary'], edgecolor='black',
                               linewidth=2, transform=ax.transAxes)
        ax.add_patch(header)

        ax.text(0.5, 0.91, player_data['name'], transform=ax.transAxes,
               fontsize=16, fontweight='bold', color='white', ha='center', va='center')

        # Stats
        stats = player_data.get('stats', {})
        y_pos = 0.75
        for stat_name, stat_value in stats.items():
            # Stat box
            stat_box = FancyBboxPatch((0.1, y_pos - 0.08), 0.8, 0.08,
                                     boxstyle="round,pad=0.01", transform=ax.transAxes,
                                     facecolor=self.colors['secondary'], edgecolor='black',
                                     linewidth=1, alpha=0.7)
            ax.add_patch(stat_box)

            # Stat label and value
            ax.text(0.15, y_pos - 0.04, stat_name, transform=ax.transAxes,
                   fontsize=11, fontweight='bold', color='white', va='center')
            ax.text(0.85, y_pos - 0.04, f'{stat_value:.1f}' if isinstance(stat_value, float) else str(stat_value),
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   color='white', va='center', ha='right')

            y_pos -= 0.12

        # Border
        border = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                          fill=False, edgecolor='black', linewidth=3)
        ax.add_patch(border)

    def generate_team_roster_cards(self, team_name, players_data, filename=None):
        """
        Generate a grid of player cards for a team roster.

        Args:
            team_name: Team name
            players_data: List of player data dicts
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        n_players = len(players_data)
        n_cols = 3
        n_rows = (n_players + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))

        if n_rows == 1:
            axes = [axes]
        if n_cols == 1:
            axes = [[ax] for ax in axes]

        for i, player_data in enumerate(players_data):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row][col] if n_rows > 1 else axes[col]
            self._create_mini_card(ax, player_data)

        # Hide unused subplots
        for i in range(n_players, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row][col] if n_rows > 1 else axes[col]
            ax.axis('off')

        fig.suptitle(f'{team_name} - Roster Cards', fontsize=22, fontweight='bold', y=0.995)

        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_roster_cards_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        plt.tight_layout()
        return self.save_and_close(fig, filename)
