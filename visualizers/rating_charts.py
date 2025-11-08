"""
Rating Chart Generator
======================
Charts for offensive/defensive ratings and performance metrics.
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from .base_chart import BaseChartGenerator
from .chart_utils import calculate_rolling_average, generate_date_range, format_rating


class RatingChartGenerator(BaseChartGenerator):
    """Generator for rating-based charts (OffRtg, DefRtg, etc.)."""

    def generate_rolling_ratings(self, team_data, metric='offensive_rating', window=5, filename=None):
        """
        Generate a rolling rating chart for one or more teams.

        Args:
            team_data: Dict with team names as keys and rating lists as values
                      Example: {'Lakers': [110, 112, 108, ...], 'Warriors': [115, 113, ...]}
            metric: Metric name for chart title
            window: Rolling average window size
            filename: Output filename (auto-generated if None)

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 7))

        # Generate x-axis (dates or game numbers)
        max_games = max(len(ratings) for ratings in team_data.values())
        x_values = list(range(1, max_games + 1))

        # Plot each team's rolling average
        for team_name, ratings in team_data.items():
            if len(ratings) >= window:
                rolling_avg = calculate_rolling_average(ratings, window)
                # Adjust x values for rolling average
                x_rolling = x_values[window-1:len(rolling_avg)+window-1]

                # Plot line
                ax.plot(x_rolling, rolling_avg, marker='o', linewidth=2.5,
                       label=team_name, markersize=4, alpha=0.9)

                # Add trend arrow at the end
                if len(rolling_avg) >= 2:
                    trend = rolling_avg[-1] - rolling_avg[-2]
                    arrow_color = '#5CB85C' if trend > 0 else '#BF0D3E'
                    ax.annotate('', xy=(x_rolling[-1], rolling_avg[-1]),
                              xytext=(x_rolling[-2], rolling_avg[-2]),
                              arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))

        # Styling
        self.add_grid(ax, alpha=0.3)
        self.add_labels(ax, xlabel='Game Number', ylabel=f'{metric.replace("_", " ").title()}')
        self.add_legend(ax, location='best', framealpha=0.9)

        # Add league average line if applicable
        all_ratings = [r for ratings in team_data.values() for r in ratings]
        if all_ratings:
            league_avg = np.mean(all_ratings)
            ax.axhline(y=league_avg, color='gray', linestyle='--', linewidth=1.5,
                      alpha=0.5, label=f'League Avg: {format_rating(league_avg)}')

        title = f'Rolling {metric.replace("_", " ").title()} ({window}-Game Average)'
        if filename is None:
            filename = f'rolling_{metric}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_off_def_comparison(self, team_name, offensive_ratings, defensive_ratings, filename=None):
        """
        Generate a dual-axis chart comparing offensive and defensive ratings.

        Args:
            team_name: Team name
            offensive_ratings: List of offensive rating values
            defensive_ratings: List of defensive rating values (lower is better)
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax1 = self.create_figure(figsize=(14, 7))

        games = list(range(1, len(offensive_ratings) + 1))

        # Offensive rating on left axis
        color_off = self.colors['secondary']
        ax1.set_xlabel('Game Number', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Offensive Rating', color=color_off, fontsize=12, fontweight='bold')
        line1 = ax1.plot(games, offensive_ratings, color=color_off, marker='o',
                        linewidth=2.5, label='Offensive Rating', markersize=5)
        ax1.tick_params(axis='y', labelcolor=color_off)
        ax1.fill_between(games, offensive_ratings, alpha=0.2, color=color_off)

        # Defensive rating on right axis
        ax2 = ax1.twinx()
        color_def = self.colors['primary']
        ax2.set_ylabel('Defensive Rating (Lower is Better)', color=color_def,
                      fontsize=12, fontweight='bold')
        line2 = ax2.plot(games, defensive_ratings, color=color_def, marker='s',
                        linewidth=2.5, label='Defensive Rating', markersize=5)
        ax2.tick_params(axis='y', labelcolor=color_def)
        ax2.fill_between(games, defensive_ratings, alpha=0.2, color=color_def)
        ax2.invert_yaxis()  # Invert so lower is visually better

        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.9)

        self.add_grid(ax1, alpha=0.3)

        title = f'{team_name} - Offensive vs Defensive Rating'
        if filename is None:
            filename = f'{team_name.lower().replace(" ", "_")}_off_def_rating_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        # Add watermark and timestamp manually
        from .chart_utils import add_watermark
        add_watermark(ax1)
        self.add_timestamp(ax1)

        ax1.set_title(title, fontsize=16, fontweight='bold', pad=15)
        plt.tight_layout()
        return self.save_and_close(fig, filename)

    def generate_rating_distribution(self, league_ratings, team_highlight=None, filename=None):
        """
        Generate a distribution chart showing where teams rank.

        Args:
            league_ratings: Dict of team names to ratings
            team_highlight: Team name to highlight (optional)
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 8))

        # Sort teams by rating
        sorted_teams = sorted(league_ratings.items(), key=lambda x: x[1], reverse=True)
        teams = [t[0] for t in sorted_teams]
        ratings = [t[1] for t in sorted_teams]

        # Create color list (highlight specific team)
        colors = []
        for team in teams:
            if team_highlight and team == team_highlight:
                colors.append(self.colors['accent'])
            else:
                colors.append(self.colors['primary'])

        # Horizontal bar chart
        y_pos = np.arange(len(teams))
        bars = ax.barh(y_pos, ratings, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Add value labels
        for i, (bar, rating) in enumerate(zip(bars, ratings)):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{format_rating(rating)}',
                   ha='left', va='center', fontweight='bold', fontsize=9)

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(teams, fontsize=10)
        ax.invert_yaxis()  # Highest rating at top
        self.add_labels(ax, xlabel='Rating', ylabel='Team')
        self.add_grid(ax, axis='x', alpha=0.3)

        # Add league average line
        league_avg = np.mean(ratings)
        ax.axvline(x=league_avg, color='red', linestyle='--', linewidth=2,
                  alpha=0.7, label=f'League Avg: {format_rating(league_avg)}')
        self.add_legend(ax, location='lower right')

        title = 'League Rating Distribution'
        if filename is None:
            filename = f'league_rating_distribution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_rating_heatmap(self, team_ratings_over_time, filename=None):
        """
        Generate a heatmap showing team ratings over time.

        Args:
            team_ratings_over_time: 2D array or dict of dicts
                                   Example: {team: {date: rating, ...}, ...}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        import seaborn as sns

        fig, ax = self.create_figure(figsize=(16, 10))

        # Convert dict to 2D array if needed
        if isinstance(team_ratings_over_time, dict):
            teams = list(team_ratings_over_time.keys())
            dates = sorted(set(date for team_data in team_ratings_over_time.values()
                             for date in team_data.keys()))
            data = []
            for team in teams:
                team_data = team_ratings_over_time[team]
                row = [team_data.get(date, np.nan) for date in dates]
                data.append(row)

            # Create heatmap
            sns.heatmap(data, annot=True, fmt='.1f', cmap='RdYlGn', center=100,
                       xticklabels=[d.strftime('%m/%d') if isinstance(d, datetime) else d for d in dates],
                       yticklabels=teams, ax=ax, cbar_kws={'label': 'Rating'}, linewidths=0.5)
        else:
            # Assume it's already a 2D array
            sns.heatmap(team_ratings_over_time, annot=True, fmt='.1f', cmap='RdYlGn',
                       center=100, ax=ax, cbar_kws={'label': 'Rating'}, linewidths=0.5)

        title = 'Team Ratings Over Time'
        if filename is None:
            filename = f'rating_heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)
