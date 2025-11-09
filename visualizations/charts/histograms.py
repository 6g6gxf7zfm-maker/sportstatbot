"""
Histogram Visualizations
Feature #48: Histogram of shot distances per player
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class ShotDistanceHistogram(BaseVisualization):
    """
    Feature #48: Histogram of shot distances per player

    Shows distribution of shot distances with success rates.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create shot distance histogram

        Args:
            data: Dictionary containing:
                - shots: List of {player, distance, made}
                - player_name: Optional specific player (default: all players)

        Returns:
            Plotly Figure
        """
        shots = data.get('shots', [])
        player_name = data.get('player_name', None)

        if not shots:
            shots = self._generate_sample_shots()

        df = pd.DataFrame(shots)

        if player_name:
            df = df[df['player'] == player_name]
            self.title = f"{player_name} Shot Distance Distribution"
        else:
            self.title = "Team Shot Distance Distribution"

        # Create figure with subplots
        self.fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=('Shot Attempt Distribution', 'Success Rate by Distance'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )

        # Histogram of all shots
        made_shots = df[df['made'] == True]
        missed_shots = df[df['made'] == False]

        self.fig.add_trace(
            go.Histogram(
                x=made_shots['distance'],
                name='Made',
                marker_color=self.colors.WIN,
                opacity=0.7,
                nbinsx=20,
                hovertemplate='Distance: %{x:.0f} ft<br>Count: %{y}<extra></extra>'
            ),
            row=1,
            col=1
        )

        self.fig.add_trace(
            go.Histogram(
                x=missed_shots['distance'],
                name='Missed',
                marker_color=self.colors.LOSS,
                opacity=0.7,
                nbinsx=20,
                hovertemplate='Distance: %{x:.0f} ft<br>Count: %{y}<extra></extra>'
            ),
            row=1,
            col=1
        )

        # Success rate by distance (binned)
        bins = np.arange(0, df['distance'].max() + 5, 5)
        df['distance_bin'] = pd.cut(df['distance'], bins=bins)

        success_rate = df.groupby('distance_bin').apply(
            lambda x: (x['made'].sum() / len(x) * 100) if len(x) > 0 else 0
        ).reset_index()

        success_rate['bin_center'] = success_rate['distance_bin'].apply(
            lambda x: x.mid if pd.notna(x) else 0
        )

        self.fig.add_trace(
            go.Bar(
                x=success_rate['bin_center'],
                y=success_rate[0],
                marker=dict(
                    color=success_rate[0],
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=100,
                    colorbar=dict(title="Success %", y=0.2, len=0.3)
                ),
                name='Success Rate',
                hovertemplate='Distance: %{x:.0f} ft<br>Success Rate: %{y:.1f}%<extra></extra>',
                showlegend=False
            ),
            row=2,
            col=1
        )

        # Add league average line
        overall_success = (df['made'].sum() / len(df)) * 100
        self.fig.add_hline(
            y=overall_success,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Avg: {overall_success:.1f}%",
            annotation_position="right",
            row=2,
            col=1
        )

        # Update axes
        self.fig.update_xaxes(title_text="Distance (feet)", row=1, col=1)
        self.fig.update_yaxes(title_text="Number of Shots", row=1, col=1)

        self.fig.update_xaxes(title_text="Distance Range (feet)", row=2, col=1)
        self.fig.update_yaxes(title_text="Success Rate (%)", row=2, col=1, range=[0, 100])

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'height': 700,
            'barmode': 'overlay',
            'hovermode': 'x unified'
        })

        self.fig.update_layout(**layout)

        # Add summary statistics
        self._add_summary_stats(df)

        return self.fig

    def _add_summary_stats(self, df: pd.DataFrame):
        """Add summary statistics annotation"""

        total_shots = len(df)
        made_shots = df['made'].sum()
        success_rate = (made_shots / total_shots) * 100
        avg_distance = df['distance'].mean()
        median_distance = df['distance'].median()

        stats_text = (
            f"Total Shots: {total_shots} | "
            f"Made: {made_shots} ({success_rate:.1f}%) | "
            f"Avg Distance: {avg_distance:.1f} ft | "
            f"Median: {median_distance:.1f} ft"
        )

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.08,
            text=stats_text,
            showarrow=False,
            font=dict(size=12, family='Arial'),
            xanchor='center'
        )

    def _generate_sample_shots(self) -> List[Dict]:
        """Generate sample shot data"""
        np.random.seed(42)

        players = ['Curry', 'Thompson', 'Poole', 'Wiggins', 'Green']

        shots = []

        for _ in range(300):
            player = np.random.choice(players)

            # Distance distribution (more shots closer)
            if np.random.random() < 0.4:
                distance = np.random.uniform(0, 10)  # Close range
                success_prob = 0.7
            elif np.random.random() < 0.7:
                distance = np.random.uniform(10, 20)  # Mid range
                success_prob = 0.45
            else:
                distance = np.random.uniform(20, 35)  # Three point
                success_prob = 0.38

            made = np.random.random() < success_prob

            shots.append({
                'player': player,
                'distance': distance,
                'made': made
            })

        return shots
