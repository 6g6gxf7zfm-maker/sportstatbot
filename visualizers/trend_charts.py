"""
Trend Chart Generator
=====================
Charts for form pulse, season progress, and momentum gauges.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime, timedelta
from .base_chart import BaseChartGenerator
from .chart_utils import get_trend_color, format_percentage


class TrendChartGenerator(BaseChartGenerator):
    """Generator for trend-based charts."""

    def generate_form_pulse(self, team_name, results, filename=None):
        """
        Generate a form pulse graph with green/red trend lights.

        Args:
            team_name: Team name
            results: List of game results ('W' or 'L') in chronological order
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 6))

        games = list(range(1, len(results) + 1))
        form_values = []
        current_form = 0

        # Calculate form momentum
        for result in results:
            if result == 'W':
                current_form = min(current_form + 1, 5)  # Cap at +5
            else:
                current_form = max(current_form - 1, -5)  # Cap at -5
            form_values.append(current_form)

        # Create line plot
        colors = ['#5CB85C' if v > 0 else '#BF0D3E' if v < 0 else 'gray' for v in form_values]
        ax.plot(games, form_values, linewidth=3, color=self.colors['primary'], marker='o', markersize=8)

        # Fill areas
        ax.fill_between(games, 0, form_values,
                       where=[v > 0 for v in form_values],
                       alpha=0.3, color='#5CB85C', label='Positive Form')
        ax.fill_between(games, 0, form_values,
                       where=[v < 0 for v in form_values],
                       alpha=0.3, color='#BF0D3E', label='Negative Form')

        # Add result markers
        for i, (game, result, form) in enumerate(zip(games, results, form_values)):
            marker_color = '#5CB85C' if result == 'W' else '#BF0D3E'
            marker = 'o' if result == 'W' else 'x'
            ax.scatter(game, form, s=200, c=marker_color, marker=marker,
                      edgecolors='black', linewidths=2, zorder=5)

            # Add W/L label
            ax.text(game, form + 0.3, result, ha='center', va='bottom',
                   fontweight='bold', fontsize=10, color='white',
                   bbox=dict(boxstyle='round', facecolor=marker_color, alpha=0.8))

        # Add horizontal zones
        ax.axhspan(3, 5, alpha=0.1, color='green', label='Hot Streak')
        ax.axhspan(-5, -3, alpha=0.1, color='red', label='Cold Streak')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.5)

        # Styling
        ax.set_ylim(-6, 6)
        ax.set_yticks(range(-5, 6, 1))
        self.add_labels(ax, xlabel='Game Number', ylabel='Form Momentum')
        self.add_grid(ax, alpha=0.3)
        self.add_legend(ax, location='upper left')

        # Current form indicator
        current_form_val = form_values[-1] if form_values else 0
        form_text = 'HOT' if current_form_val >= 3 else 'COLD' if current_form_val <= -3 else 'NEUTRAL'
        form_color = '#5CB85C' if current_form_val >= 3 else '#BF0D3E' if current_form_val <= -3 else '#FDB927'

        ax.text(0.98, 0.95, f'Current Form: {form_text}',
               transform=ax.transAxes, ha='right', va='top',
               fontsize=14, fontweight='bold', color='white',
               bbox=dict(boxstyle='round', facecolor=form_color, alpha=0.9, pad=1))

        title = f'{team_name} - Form Pulse'
        subtitle = f'Recent {len(results)} games | {results.count("W")}W - {results.count("L")}L'
        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_form_pulse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_season_progress(self, team_name, current_wins, current_losses,
                                target_wins=None, playoff_threshold=None, filename=None):
        """
        Generate season progress bars toward playoffs or targets.

        Args:
            team_name: Team name
            current_wins: Current number of wins
            current_losses: Current number of losses
            target_wins: Target win total (optional)
            playoff_threshold: Estimated wins needed for playoffs (optional)
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 8))

        total_games = current_wins + current_losses
        win_pct = current_wins / total_games if total_games > 0 else 0

        # Calculate projected season totals (assuming 82-game season)
        season_length = 82
        projected_wins = int(win_pct * season_length)

        # Set defaults
        if target_wins is None:
            target_wins = 50  # Typical playoff threshold
        if playoff_threshold is None:
            playoff_threshold = 45

        # Create progress bars
        bar_height = 0.6
        y_positions = [3, 2, 1]

        # Games played bar
        games_pct = total_games / season_length
        ax.barh(y_positions[0], total_games, bar_height,
               color=self.colors['primary'], alpha=0.7, edgecolor='black', linewidth=2)
        ax.barh(y_positions[0], season_length - total_games, bar_height,
               left=total_games, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
        ax.text(total_games / 2, y_positions[0], f'{total_games}/{season_length} Games',
               ha='center', va='center', fontweight='bold', fontsize=12, color='white')

        # Wins progress bar
        ax.barh(y_positions[1], current_wins, bar_height,
               color='#5CB85C', alpha=0.7, edgecolor='black', linewidth=2)
        ax.barh(y_positions[1], projected_wins - current_wins, bar_height,
               left=current_wins, color='#90EE90', alpha=0.5, edgecolor='black', linewidth=2)
        if projected_wins < season_length:
            ax.barh(y_positions[1], season_length - projected_wins, bar_height,
                   left=projected_wins, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
        ax.text(current_wins / 2, y_positions[1], f'{current_wins} Wins',
               ha='center', va='center', fontweight='bold', fontsize=12, color='white')

        # Target progress bar
        target_pct = current_wins / target_wins if target_wins > 0 else 0
        target_color = '#5CB85C' if current_wins >= target_wins else '#FDB927'
        ax.barh(y_positions[2], min(current_wins, target_wins), bar_height,
               color=target_color, alpha=0.7, edgecolor='black', linewidth=2)
        if current_wins < target_wins:
            ax.barh(y_positions[2], target_wins - current_wins, bar_height,
                   left=current_wins, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
        ax.text(target_wins / 2, y_positions[2],
               f'Target: {current_wins}/{target_wins} ({format_percentage(target_pct, 0)})',
               ha='center', va='center', fontweight='bold', fontsize=12,
               color='white' if current_wins < target_wins else 'black')

        # Add playoff threshold line
        ax.axvline(x=playoff_threshold, color='red', linestyle='--', linewidth=2.5,
                  alpha=0.7, label=f'Playoff Threshold (~{playoff_threshold} wins)')

        # Add projected wins line
        ax.axvline(x=projected_wins, color='blue', linestyle='--', linewidth=2.5,
                  alpha=0.7, label=f'Projected: {projected_wins} wins')

        # Styling
        ax.set_yticks(y_positions)
        ax.set_yticklabels(['Season Progress', 'Win Progress', 'Target Progress'], fontsize=12, fontweight='bold')
        ax.set_xlim(0, season_length)
        ax.set_xlabel('Wins', fontsize=12, fontweight='bold')
        self.add_grid(ax, axis='x', alpha=0.3)
        self.add_legend(ax, location='lower right')

        # Status indicator
        if projected_wins >= playoff_threshold:
            status = 'ON TRACK'
            status_color = '#5CB85C'
        elif projected_wins >= playoff_threshold - 5:
            status = 'BUBBLE'
            status_color = '#FDB927'
        else:
            status = 'BELOW PACE'
            status_color = '#BF0D3E'

        ax.text(0.98, 0.95, f'Playoff Status: {status}',
               transform=ax.transAxes, ha='right', va='top',
               fontsize=14, fontweight='bold', color='white',
               bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.9, pad=1))

        title = f'{team_name} - Season Progress'
        subtitle = f'Record: {current_wins}-{current_losses} | Win %: {format_percentage(win_pct)} | Projected: {projected_wins}-{season_length - projected_wins}'
        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_season_progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_momentum_gauge(self, team1, team2, momentum_score, filename=None):
        """
        Generate a momentum gauge dial for upcoming matchup.

        Args:
            team1: First team name
            team2: Second team name
            momentum_score: Momentum score (-100 to 100, negative favors team1, positive favors team2)
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 8))

        # Create gauge background
        theta = np.linspace(np.pi, 0, 100)
        r = 1

        # Color zones
        colors_gauge = ['#BF0D3E', '#FF6B6B', '#FDB927', '#90EE90', '#5CB85C']
        segments = 5
        segment_size = len(theta) // segments

        for i in range(segments):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < segments - 1 else len(theta)
            ax.fill_between(theta[start_idx:end_idx],
                           0, [r] * (end_idx - start_idx),
                           color=colors_gauge[i], alpha=0.6)

        # Draw gauge outline
        ax.plot(theta, [r] * len(theta), 'black', linewidth=3)
        ax.plot([np.pi, np.pi], [0, r], 'black', linewidth=3)
        ax.plot([0, 0], [0, r], 'black', linewidth=3)

        # Calculate needle angle
        # momentum_score ranges from -100 to 100
        # Map to angle from π (left) to 0 (right)
        normalized_score = (momentum_score + 100) / 200  # 0 to 1
        needle_angle = np.pi - (normalized_score * np.pi)

        # Draw needle
        needle_length = 0.9
        ax.plot([needle_angle, needle_angle], [0, needle_length],
               color='black', linewidth=4, zorder=10)
        ax.scatter([needle_angle], [needle_length], s=300, c='red',
                  edgecolors='black', linewidths=2, zorder=11)

        # Center circle
        center = patches.Circle((np.pi/2, 0), 0.05, color='black', zorder=12)
        ax.add_patch(center)

        # Add labels
        ax.text(np.pi, -0.3, team1, ha='left', va='top',
               fontsize=16, fontweight='bold', color=self.colors['primary'])
        ax.text(0, -0.3, team2, ha='right', va='top',
               fontsize=16, fontweight='bold', color=self.colors['secondary'])

        # Add score indicator
        ax.text(np.pi/2, -0.5, f'Momentum: {abs(momentum_score):.0f}%',
               ha='center', va='top', fontsize=14, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black', linewidth=2))

        # Determine favored team
        if momentum_score < -20:
            favored = f'{team1} has strong momentum'
            favor_color = '#BF0D3E'
        elif momentum_score < -5:
            favored = f'{team1} has slight edge'
            favor_color = '#FDB927'
        elif momentum_score > 20:
            favored = f'{team2} has strong momentum'
            favor_color = '#5CB85C'
        elif momentum_score > 5:
            favored = f'{team2} has slight edge'
            favor_color = '#FDB927'
        else:
            favored = 'Even momentum'
            favor_color = 'gray'

        ax.text(np.pi/2, 0.5, favored, ha='center', va='bottom',
               fontsize=13, fontweight='bold', color='white',
               bbox=dict(boxstyle='round', facecolor=favor_color, alpha=0.9, pad=0.8))

        # Styling
        ax.set_xlim(np.pi + 0.2, -0.2)
        ax.set_ylim(-0.6, 1.2)
        ax.axis('off')

        title = f'Momentum Gauge: {team1} vs {team2}'
        if filename is None:
            filename = f'momentum_gauge_{team1.lower().replace(" ", "_")}_vs_{team2.lower().replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        ax.set_title(title, fontsize=18, fontweight='bold', pad=20)

        from .chart_utils import add_watermark
        add_watermark(ax)
        self.add_timestamp(ax)

        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def generate_league_parity_chart(self, team_strengths, filename=None):
        """
        Generate a league parity chart showing standard deviation of team strength.

        Args:
            team_strengths: Dict of team names to strength ratings
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 8))

        teams = list(team_strengths.keys())
        strengths = list(team_strengths.values())

        # Calculate statistics
        mean_strength = np.mean(strengths)
        std_dev = np.std(strengths)

        # Sort by strength
        sorted_data = sorted(zip(teams, strengths), key=lambda x: x[1], reverse=True)
        sorted_teams = [x[0] for x in sorted_data]
        sorted_strengths = [x[1] for x in sorted_data]

        # Create bars
        colors = []
        for strength in sorted_strengths:
            if strength > mean_strength + std_dev:
                colors.append('#5CB85C')  # Elite
            elif strength > mean_strength:
                colors.append('#90EE90')  # Above average
            elif strength > mean_strength - std_dev:
                colors.append('#FFD700')  # Below average
            else:
                colors.append('#BF0D3E')  # Struggling

        x_pos = np.arange(len(sorted_teams))
        bars = ax.bar(x_pos, sorted_strengths, color=colors, alpha=0.8,
                     edgecolor='black', linewidth=1)

        # Add value labels
        for bar, strength in zip(bars, sorted_strengths):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{strength:.1f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        # Add statistical lines
        ax.axhline(y=mean_strength, color='blue', linestyle='--', linewidth=2,
                  alpha=0.7, label=f'Mean: {mean_strength:.1f}')
        ax.axhline(y=mean_strength + std_dev, color='green', linestyle='--', linewidth=1.5,
                  alpha=0.5, label=f'+1 SD: {mean_strength + std_dev:.1f}')
        ax.axhline(y=mean_strength - std_dev, color='red', linestyle='--', linewidth=1.5,
                  alpha=0.5, label=f'-1 SD: {mean_strength - std_dev:.1f}')

        # Styling
        ax.set_xticks(x_pos)
        ax.set_xticklabels(sorted_teams, rotation=45, ha='right', fontsize=9)
        self.add_labels(ax, xlabel='Team', ylabel='Strength Rating')
        self.add_grid(ax, axis='y', alpha=0.3)
        self.add_legend(ax, location='upper right')

        # Parity assessment
        if std_dev < 5:
            parity_status = 'HIGH PARITY'
            parity_color = '#5CB85C'
            parity_desc = 'League is highly competitive'
        elif std_dev < 10:
            parity_status = 'MODERATE PARITY'
            parity_color = '#FDB927'
            parity_desc = 'Some separation between teams'
        else:
            parity_status = 'LOW PARITY'
            parity_color = '#BF0D3E'
            parity_desc = 'Clear tiers of teams'

        ax.text(0.98, 0.95, f'{parity_status}\n{parity_desc}',
               transform=ax.transAxes, ha='right', va='top',
               fontsize=12, fontweight='bold', color='white',
               bbox=dict(boxstyle='round', facecolor=parity_color, alpha=0.9, pad=0.8))

        title = 'League Parity Chart'
        subtitle = f'Standard Deviation: {std_dev:.2f} | Range: {min(strengths):.1f} - {max(strengths):.1f}'
        if filename is None:
            filename = f'league_parity_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)
