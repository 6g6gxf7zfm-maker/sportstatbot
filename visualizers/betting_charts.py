"""
Betting Chart Generator
========================
Charts for line movement, win probability, and betting edges.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from datetime import datetime, timedelta
from .base_chart import BaseChartGenerator
from .chart_utils import format_percentage, create_annotation


class BettingChartGenerator(BaseChartGenerator):
    """Generator for betting-related charts."""

    def generate_line_movement(self, game_name, timestamps, opening_lines, current_lines,
                              line_type='spread', filename=None):
        """
        Generate a line movement chart showing opening vs current lines.

        Args:
            game_name: Game identifier (e.g., "LAL vs GSW")
            timestamps: List of datetime objects for line updates
            opening_lines: List of opening line values
            current_lines: List of current line values at each timestamp
            line_type: Type of line ('spread', 'total', 'moneyline')
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 7))

        # Plot line movement
        ax.plot(timestamps, current_lines, marker='o', linewidth=2.5,
               color=self.colors['primary'], label=f'Current {line_type.title()}',
               markersize=6)

        # Plot opening line as horizontal reference
        if opening_lines:
            opening_avg = np.mean(opening_lines) if isinstance(opening_lines, list) else opening_lines
            ax.axhline(y=opening_avg, color=self.colors['secondary'], linestyle='--',
                      linewidth=2, alpha=0.7, label=f'Opening {line_type.title()}: {opening_avg}')

        # Highlight significant movements
        if len(current_lines) >= 2:
            for i in range(1, len(current_lines)):
                movement = current_lines[i] - current_lines[i-1]
                if abs(movement) >= 1.0:  # Significant move threshold
                    color = '#5CB85C' if movement > 0 else '#BF0D3E'
                    ax.annotate(f'{movement:+.1f}',
                              xy=(timestamps[i], current_lines[i]),
                              xytext=(10, 10 if movement > 0 else -10),
                              textcoords='offset points',
                              fontsize=9, fontweight='bold', color=color,
                              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=color),
                              arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

        # Fill area between opening and current
        if opening_lines:
            opening_line = [opening_avg] * len(timestamps)
            ax.fill_between(timestamps, opening_line, current_lines,
                           where=[c > opening_avg for c in current_lines],
                           alpha=0.2, color='#5CB85C', label='Line increased')
            ax.fill_between(timestamps, opening_line, current_lines,
                           where=[c <= opening_avg for c in current_lines],
                           alpha=0.2, color='#BF0D3E', label='Line decreased')

        # Styling
        self.format_x_axis_dates(ax, date_format='%m/%d %H:%M', rotation=45)
        self.add_labels(ax, xlabel='Time', ylabel=f'{line_type.title()} Value')
        self.add_grid(ax, alpha=0.3)
        self.add_legend(ax, location='best')

        # Movement summary
        if current_lines:
            total_movement = current_lines[-1] - (opening_avg if opening_lines else current_lines[0])
            movement_pct = (total_movement / opening_avg * 100) if opening_lines and opening_avg != 0 else 0
            movement_color = '#5CB85C' if total_movement > 0 else '#BF0D3E' if total_movement < 0 else 'gray'

            ax.text(0.02, 0.98, f'Total Movement: {total_movement:+.1f} ({movement_pct:+.1f}%)',
                   transform=ax.transAxes, ha='left', va='top',
                   fontsize=12, fontweight='bold', color='white',
                   bbox=dict(boxstyle='round', facecolor=movement_color, alpha=0.9, pad=0.8))

        title = f'{game_name} - {line_type.title()} Line Movement'
        if filename is None:
            filename = f'line_movement_{game_name.lower().replace(" ", "_")}_{line_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_win_probability_timeline(self, game_name, timeline_data, filename=None):
        """
        Generate a win probability timeline/animation for a game.

        Args:
            game_name: Game identifier
            timeline_data: List of dicts with 'time', 'team1_prob', 'team2_prob'
                          Example: [{'time': '1Q 5:30', 'team1_prob': 0.55, 'team2_prob': 0.45}, ...]
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 7))

        times = [d['time'] for d in timeline_data]
        team1_probs = [d['team1_prob'] * 100 for d in timeline_data]
        team2_probs = [d['team2_prob'] * 100 for d in timeline_data]

        x = np.arange(len(times))

        # Create stacked area chart
        ax.fill_between(x, 0, team1_probs, alpha=0.6, color=self.colors['primary'],
                       label=timeline_data[0].get('team1', 'Team 1'))
        ax.fill_between(x, team1_probs, 100, alpha=0.6, color=self.colors['secondary'],
                       label=timeline_data[0].get('team2', 'Team 2'))

        # Add 50% reference line
        ax.axhline(y=50, color='white', linestyle='--', linewidth=2, alpha=0.8, label='Even (50%)')

        # Highlight key moments (big swings)
        for i in range(1, len(team1_probs)):
            swing = abs(team1_probs[i] - team1_probs[i-1])
            if swing >= 15:  # Threshold for "key moment"
                ax.axvline(x=i, color='yellow', linestyle=':', linewidth=2, alpha=0.5)
                ax.text(i, 50, 'Key Moment', rotation=90, va='center', ha='right',
                       fontsize=9, fontweight='bold', color='yellow',
                       bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        # Add probability labels at key points
        for i in [0, len(x)//2, len(x)-1]:
            if i < len(team1_probs):
                ax.text(i, team1_probs[i]/2, f'{team1_probs[i]:.0f}%',
                       ha='center', va='center', fontsize=11, fontweight='bold',
                       color='white')
                ax.text(i, team1_probs[i] + (100-team1_probs[i])/2, f'{team2_probs[i]:.0f}%',
                       ha='center', va='center', fontsize=11, fontweight='bold',
                       color='white')

        # Styling
        ax.set_xticks(x[::max(1, len(x)//10)])  # Show ~10 labels
        ax.set_xticklabels([times[i] for i in range(0, len(times), max(1, len(times)//10))],
                          rotation=45, ha='right')
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
        self.add_labels(ax, xlabel='Game Time', ylabel='Win Probability')
        self.add_grid(ax, alpha=0.3)
        self.add_legend(ax, location='upper left')

        title = f'{game_name} - Win Probability Timeline'
        if filename is None:
            filename = f'win_probability_{game_name.lower().replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_top_edges(self, edges_data, filename=None):
        """
        Generate a "Top Edges of the Day" chart for betting insights.

        Args:
            edges_data: List of dicts with edge information
                       Example: [{'game': 'LAL vs GSW', 'bet_type': 'Spread', 'edge': 3.5,
                                 'recommended': 'LAL +5.5', 'confidence': 0.75}, ...]
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(14, 10))

        # Sort by edge value
        sorted_edges = sorted(edges_data, key=lambda x: abs(x['edge']), reverse=True)

        games = [e['game'] for e in sorted_edges]
        edges = [e['edge'] for e in sorted_edges]
        confidences = [e.get('confidence', 0.5) for e in sorted_edges]

        y_pos = np.arange(len(games))

        # Create horizontal bars
        colors = []
        for edge, conf in zip(edges, confidences):
            # Color based on confidence and edge size
            if conf >= 0.7 and abs(edge) >= 3:
                colors.append('#5CB85C')  # High confidence, big edge
            elif conf >= 0.6 and abs(edge) >= 2:
                colors.append('#90EE90')  # Good edge
            elif abs(edge) >= 1.5:
                colors.append('#FDB927')  # Moderate edge
            else:
                colors.append('#FFD700')  # Small edge

        bars = ax.barh(y_pos, edges, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Add edge value labels
        for i, (bar, edge, conf, data) in enumerate(zip(bars, edges, confidences, sorted_edges)):
            width = bar.get_width()
            x_pos = width + (0.2 if width > 0 else -0.2)
            ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                   f'{abs(edge):.1f}% edge',
                   ha='left' if width > 0 else 'right', va='center',
                   fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

            # Add recommended bet
            rec_x = -max(abs(e) for e in edges) * 0.3
            ax.text(rec_x, bar.get_y() + bar.get_height()/2,
                   data.get('recommended', ''),
                   ha='right', va='center', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor=colors[i], alpha=0.7, edgecolor='black'))

            # Add confidence indicator
            conf_text = f"{conf*100:.0f}%"
            ax.text(width + (0.8 if width > 0 else -0.8), bar.get_y() + bar.get_height()/2,
                   f'🎯 {conf_text}',
                   ha='left' if width > 0 else 'right', va='center',
                   fontsize=8, color='gray', fontweight='bold')

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(games, fontsize=10, fontweight='bold')
        ax.invert_yaxis()
        ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
        self.add_labels(ax, xlabel='Edge (%)', ylabel='Game')
        self.add_grid(ax, axis='x', alpha=0.3)

        # Add edge thresholds
        ax.axvspan(3, max(edges) + 1, alpha=0.1, color='green', label='Strong Edge (3%+)')
        ax.axvspan(2, 3, alpha=0.1, color='yellow', label='Good Edge (2-3%)')
        ax.axvspan(min(edges) - 1, -3, alpha=0.1, color='green')
        ax.axvspan(-3, -2, alpha=0.1, color='yellow')

        self.add_legend(ax, location='lower right')

        title = 'Top Betting Edges of the Day'
        subtitle = f'{len(edges_data)} opportunities identified | 🎯 = Confidence level'
        if filename is None:
            filename = f'top_edges_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)

    def generate_odds_comparison(self, game_name, bookmaker_odds, filename=None):
        """
        Generate an odds comparison chart across bookmakers.

        Args:
            game_name: Game identifier
            bookmaker_odds: Dict of bookmaker names to odds
                           Example: {'DraftKings': -110, 'FanDuel': -115, 'BetMGM': -108, ...}
            filename: Output filename

        Returns:
            str: Path to saved chart
        """
        fig, ax = self.create_figure(figsize=(12, 7))

        bookmakers = list(bookmaker_odds.keys())
        odds = list(bookmaker_odds.values())

        x_pos = np.arange(len(bookmakers))

        # Create bars
        colors = []
        for odd in odds:
            if odd == max(odds):
                colors.append('#5CB85C')  # Best odds
            elif odd == min(odds):
                colors.append('#BF0D3E')  # Worst odds
            else:
                colors.append(self.colors['primary'])

        bars = ax.bar(x_pos, odds, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, odd in zip(bars, odds):
            height = bar.get_height()
            y_pos = height if height > 0 else height - 5
            va = 'bottom' if height > 0 else 'top'
            label_color = '#5CB85C' if odd == max(odds) else '#BF0D3E' if odd == min(odds) else 'black'
            ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                   f'{odd:+d}',
                   ha='center', va=va, fontweight='bold', fontsize=11, color=label_color)

        # Add average line
        avg_odds = np.mean(odds)
        ax.axhline(y=avg_odds, color='blue', linestyle='--', linewidth=2,
                  alpha=0.7, label=f'Average: {avg_odds:+.0f}')

        # Highlight best value
        best_idx = odds.index(max(odds))
        ax.annotate('BEST VALUE',
                   xy=(best_idx, odds[best_idx]),
                   xytext=(0, 20),
                   textcoords='offset points',
                   ha='center',
                   fontsize=11,
                   fontweight='bold',
                   color='white',
                   bbox=dict(boxstyle='round', facecolor='#5CB85C', alpha=0.9, edgecolor='black', linewidth=2),
                   arrowprops=dict(arrowstyle='->', color='#5CB85C', lw=2))

        # Styling
        ax.set_xticks(x_pos)
        ax.set_xticklabels(bookmakers, rotation=45, ha='right', fontsize=10)
        self.add_labels(ax, xlabel='Bookmaker', ylabel='Odds')
        self.add_grid(ax, axis='y', alpha=0.3)
        self.add_legend(ax, location='upper right')

        title = f'{game_name} - Odds Comparison'
        subtitle = f'Best: {bookmakers[best_idx]} ({odds[best_idx]:+d}) | Worst: {bookmakers[odds.index(min(odds))]} ({min(odds):+d})'
        if filename is None:
            filename = f'odds_comparison_{game_name.lower().replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        return self.finalize_chart(fig, ax, title, filename)
