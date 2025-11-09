"""
Expected Goals (xG) Visualizations
Feature #35: Multi-layer xG difference field
Feature #39: Expected run/goal density heat surface
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization
from ..field_graphics.soccer_pitch import SoccerPitch


class XGDifferenceField(BaseVisualization):
    """
    Feature #35: Multi-layer xG difference field

    Shows expected goals overlaid on soccer pitch with multiple layers.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create xG difference field visualization

        Args:
            data: Dictionary containing:
                - team_a_shots: List of {x, y, xg}
                - team_b_shots: List of {x, y, xg}
                - team_a_name: Team A name
                - team_b_name: Team B name

        Returns:
            Plotly Figure
        """
        team_a_shots = data.get('team_a_shots', [])
        team_b_shots = data.get('team_b_shots', [])
        team_a = data.get('team_a_name', 'Team A')
        team_b = data.get('team_b_name', 'Team B')

        if not team_a_shots:
            team_a_shots, team_b_shots = self._generate_sample_shots()

        self.title = f"{team_a} vs {team_b} - xG Map"

        # Create pitch
        pitch = SoccerPitch()

        # Create figure
        self.fig = go.Figure()

        # Add pitch
        pitch.add_to_figure(self.fig)

        # Add Team A shots (attacking left to right)
        df_a = pd.DataFrame(team_a_shots)
        if not df_a.empty:
            self.fig.add_trace(go.Scatter(
                x=df_a['x'],
                y=df_a['y'],
                mode='markers',
                marker=dict(
                    size=df_a['xg'] * 100,  # Size based on xG
                    color=df_a['xg'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="xG", x=1.1),
                    line=dict(width=2, color='darkred'),
                    opacity=0.7
                ),
                name=team_a,
                hovertemplate=(
                    f"<b>{team_a}</b><br>"
                    "xG: %{marker.color:.2f}<br>"
                    "Position: (%{x:.1f}, %{y:.1f})<br>"
                    "<extra></extra>"
                )
            ))

        # Add Team B shots (attacking right to left)
        df_b = pd.DataFrame(team_b_shots)
        if not df_b.empty:
            self.fig.add_trace(go.Scatter(
                x=df_b['x'],
                y=df_b['y'],
                mode='markers',
                marker=dict(
                    size=df_b['xg'] * 100,
                    color=df_b['xg'],
                    colorscale='Blues',
                    showscale=False,
                    line=dict(width=2, color='darkblue'),
                    opacity=0.7
                ),
                name=team_b,
                hovertemplate=(
                    f"<b>{team_b}</b><br>"
                    "xG: %{marker.color:.2f}<br>"
                    "Position: (%{x:.1f}, %{y:.1f})<br>"
                    "<extra></extra>"
                )
            ))

        # Add xG totals as annotations
        total_xg_a = sum(s['xg'] for s in team_a_shots)
        total_xg_b = sum(s['xg'] for s in team_b_shots)

        self.fig.add_annotation(
            x=20,
            y=60,
            text=f"<b>{team_a}</b><br>xG: {total_xg_a:.2f}",
            showarrow=False,
            font=dict(size=16, color='darkred'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='darkred',
            borderwidth=2
        )

        self.fig.add_annotation(
            x=85,
            y=60,
            text=f"<b>{team_b}</b><br>xG: {total_xg_b:.2f}",
            showarrow=False,
            font=dict(size=16, color='darkblue'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='darkblue',
            borderwidth=2
        )

        # Update layout
        layout = self._get_layout_template()
        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_shots(self) -> tuple:
        """Generate sample shot data"""
        np.random.seed(42)

        pitch = SoccerPitch()

        # Team A shots (left half)
        team_a_shots = []
        for _ in range(15):
            x = np.random.uniform(pitch.PITCH_LENGTH / 2, pitch.PITCH_LENGTH - 5)
            y = np.random.uniform(10, pitch.PITCH_WIDTH - 10)

            # xG based on distance to goal
            dist_to_goal = np.sqrt((pitch.PITCH_LENGTH - x)**2 + (pitch.PITCH_WIDTH/2 - y)**2)
            xg = max(0.05, min(0.95, 1 / (1 + dist_to_goal / 10)))

            team_a_shots.append({'x': x, 'y': y, 'xg': xg})

        # Team B shots (right half)
        team_b_shots = []
        for _ in range(12):
            x = np.random.uniform(5, pitch.PITCH_LENGTH / 2)
            y = np.random.uniform(10, pitch.PITCH_WIDTH - 10)

            dist_to_goal = np.sqrt(x**2 + (pitch.PITCH_WIDTH/2 - y)**2)
            xg = max(0.05, min(0.95, 1 / (1 + dist_to_goal / 10)))

            team_b_shots.append({'x': x, 'y': y, 'xg': xg})

        return team_a_shots, team_b_shots


class ExpectedGoalDensity(BaseVisualization):
    """
    Feature #39: Expected run/goal density heat surface

    3D surface plot showing goal/run density across the field.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create expected goal density surface

        Args:
            data: Dictionary containing:
                - shots: List of {x, y, xg}
                - team_name: Team name

        Returns:
            Plotly Figure
        """
        shots = data.get('shots', [])
        team_name = data.get('team_name', 'Team')

        if not shots:
            shots = self._generate_sample_density_data()

        self.title = f"{team_name} Goal Density Surface"

        df = pd.DataFrame(shots)

        # Create 2D density grid
        x_bins = np.linspace(0, 105, 30)
        y_bins = np.linspace(0, 68, 20)

        # Weighted 2D histogram (weighted by xG)
        H, x_edges, y_edges = np.histogram2d(
            df['x'],
            df['y'],
            bins=[x_bins, y_bins],
            weights=df['xg']
        )

        # Create 3D surface
        self.fig = go.Figure(data=[go.Surface(
            z=H.T,
            x=x_edges,
            y=y_edges,
            colorscale='Hot',
            colorbar=dict(title="xG Density"),
            hovertemplate=(
                'X: %{x:.1f}<br>'
                'Y: %{y:.1f}<br>'
                'Density: %{z:.2f}<br>'
                '<extra></extra>'
            )
        )])

        # Update layout for 3D
        layout = self._get_layout_template()
        layout.update({
            'scene': {
                'xaxis': {'title': 'Field Length (m)'},
                'yaxis': {'title': 'Field Width (m)'},
                'zaxis': {'title': 'xG Density'},
                'camera': {
                    'eye': {'x': 1.5, 'y': 1.5, 'z': 1.2}
                }
            },
            'height': 700
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_density_data(self) -> List[Dict]:
        """Generate sample density data"""
        np.random.seed(42)

        shots = []

        # Concentrate shots around penalty area
        for _ in range(100):
            # Bias towards penalty area
            if np.random.random() < 0.7:
                x = np.random.normal(95, 10)
                y = np.random.normal(34, 8)
            else:
                x = np.random.uniform(70, 105)
                y = np.random.uniform(10, 58)

            x = np.clip(x, 0, 105)
            y = np.clip(y, 0, 68)

            # xG based on distance
            dist_to_goal = np.sqrt((105 - x)**2 + (34 - y)**2)
            xg = max(0.05, min(0.95, 1 / (1 + dist_to_goal / 15)))

            shots.append({'x': x, 'y': y, 'xg': xg})

        return shots
