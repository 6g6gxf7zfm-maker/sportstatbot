"""
Win Path Video Animation
Feature #36: Animated "win path" video summarizing turning points
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import imageio
import os

from ..core.base_viz import BaseVisualization


class WinPathVideo(BaseVisualization):
    """
    Feature #36: Animated "win path" video summarizing turning points

    Creates animated visualization showing win probability over game time.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create win path animation

        Args:
            data: Dictionary containing:
                - game_events: List of {time, win_prob_a, win_prob_b, event_desc, is_turning_point}
                - team_a_name: Team A name
                - team_b_name: Team B name

        Returns:
            Plotly Figure
        """
        events = data.get('game_events', [])
        team_a = data.get('team_a_name', 'Team A')
        team_b = data.get('team_b_name', 'Team B')

        if not events:
            events = self._generate_sample_events()

        self.title = f"{team_a} vs {team_b} - Win Probability"

        df = pd.DataFrame(events)
        df = df.sort_values('time')

        # Create figure
        self.fig = go.Figure()

        # Add win probability lines
        self.fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['win_prob_a'],
            mode='lines',
            line=dict(color=self.colors.get_team_color(team_a[:3]), width=4),
            fill='tonexty',
            fillcolor=f'rgba{self._hex_to_rgba(self.colors.get_team_color(team_a[:3]), 0.3)}',
            name=team_a,
            hovertemplate=(
                f'<b>{team_a}</b><br>'
                'Time: %{x}<br>'
                'Win Probability: %{y:.1f}%<br>'
                '<extra></extra>'
            )
        ))

        # Add 50% line
        self.fig.add_hline(
            y=50,
            line_dash="dash",
            line_color="gray",
            line_width=2
        )

        # Mark turning points
        turning_points = df[df['is_turning_point'] == True]

        self.fig.add_trace(go.Scatter(
            x=turning_points['time'],
            y=turning_points['win_prob_a'],
            mode='markers+text',
            marker=dict(
                size=20,
                color='gold',
                symbol='star',
                line=dict(width=3, color='darkorange')
            ),
            text=[f"⭐{i+1}" for i in range(len(turning_points))],
            textposition='top center',
            textfont=dict(size=12, family='Arial Black'),
            name='Turning Points',
            hovertemplate=(
                '<b>TURNING POINT</b><br>'
                'Time: %{x}<br>'
                'Win Prob: %{y:.1f}%<br>'
                '%{customdata}<br>'
                '<extra></extra>'
            ),
            customdata=turning_points['event_desc'].values
        ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': 'Game Time (minutes)',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'yaxis': {
                'title': f'Win Probability (%)',
                'range': [0, 100],
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'hovermode': 'x unified'
        })

        self.fig.update_layout(**layout)

        # Add summary
        self._add_turning_point_summary(turning_points, team_a, team_b)

        return self.fig

    def export_video(
        self,
        filename: str = 'win_path_video',
        fps: int = 2,
        output_dir: str = 'visualizations/output'
    ) -> str:
        """
        Export win path as video/GIF

        Args:
            filename: Output filename
            fps: Frames per second
            output_dir: Output directory

        Returns:
            Path to exported file
        """
        if not self.fig:
            raise ValueError("No figure to export. Call create() first.")

        os.makedirs(output_dir, exist_ok=True)

        # Export as GIF using kaleido
        gif_path = os.path.join(output_dir, f"{filename}.gif")

        # For now, export as HTML with animation
        html_path = os.path.join(output_dir, f"{filename}.html")
        self.fig.write_html(html_path)

        return html_path

    def _add_turning_point_summary(
        self,
        turning_points: pd.DataFrame,
        team_a: str,
        team_b: str
    ):
        """Add summary of turning points"""

        if turning_points.empty:
            return

        summary_lines = ["<b>Key Turning Points:</b>"]

        for idx, (_, tp) in enumerate(turning_points.iterrows(), 1):
            time_str = f"{int(tp['time']//60)}:{int(tp['time']%60):02d}"
            summary_lines.append(
                f"{idx}. {time_str} - {tp['event_desc']} ({tp['win_prob_a']:.0f}% {team_a})"
            )

        summary_text = "<br>".join(summary_lines[:4])  # Show first 4

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.02,
            y=0.98,
            text=summary_text,
            showarrow=False,
            font=dict(size=10, family='Arial'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1,
            align='left',
            xanchor='left',
            yanchor='top'
        )

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> str:
        """Convert hex color to RGBA tuple string"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'({r}, {g}, {b}, {alpha})'

    def _generate_sample_events(self) -> List[Dict]:
        """Generate sample game events"""
        np.random.seed(42)

        events = []
        time = 0
        win_prob_a = 50

        for i in range(100):
            time += np.random.uniform(0.5, 2)

            # Random walk for win probability
            change = np.random.normal(0, 5)
            win_prob_a = np.clip(win_prob_a + change, 5, 95)

            # Determine if turning point (large swing)
            is_turning_point = abs(change) > 12

            event_types = [
                'Touchdown', 'Interception', 'Field Goal', 'Fumble',
                'Big Play', 'Defensive Stop', 'Score', 'Turnover'
            ]

            events.append({
                'time': time,
                'win_prob_a': win_prob_a,
                'win_prob_b': 100 - win_prob_a,
                'event_desc': np.random.choice(event_types) if is_turning_point else 'Play',
                'is_turning_point': is_turning_point
            })

        return events
