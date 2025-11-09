"""
Shot Trajectory Visualization
Feature #27: Interactive shot-trajectory replay over field graphic
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization
from ..field_graphics.basketball_court import BasketballCourt
from ..field_graphics.soccer_pitch import SoccerPitch


class ShotTrajectory(BaseVisualization):
    """
    Feature #27: Interactive shot-trajectory replay over field graphic

    Shows shot trajectories with arc visualization and interactive replay.
    """

    def create(
        self,
        data: Dict[str, Any],
        animate: bool = True
    ) -> go.Figure:
        """
        Create shot trajectory visualization

        Args:
            data: Dictionary containing:
                - shots: List of {x_start, y_start, x_end, y_end, made, player, distance}
                - sport: 'basketball' or 'soccer'
                - team_name: Team name

        Returns:
            Plotly Figure
        """
        shots = data.get('shots', [])
        sport = data.get('sport', 'basketball')
        team_name = data.get('team_name', 'Team')

        if not shots:
            shots = self._generate_sample_shots(sport)

        self.title = f"{team_name} Shot Trajectories"

        # Create field/court overlay
        if sport == 'basketball':
            field = BasketballCourt(half_court=True)
        else:
            field = SoccerPitch(half_pitch=True)

        # Create base figure
        self.fig = go.Figure()

        # Add field shapes first
        field.add_to_figure(self.fig)

        if animate:
            self._add_animated_trajectories(shots)
        else:
            self._add_static_trajectories(shots)

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'showlegend': True,
            'hovermode': 'closest'
        })
        self.fig.update_layout(**layout)

        return self.fig

    def _add_static_trajectories(self, shots: List[Dict]):
        """Add all shot trajectories to figure"""

        for i, shot in enumerate(shots):
            # Calculate arc trajectory
            arc_x, arc_y = self._calculate_arc(
                shot['x_start'],
                shot['y_start'],
                shot['x_end'],
                shot['y_end'],
                height_factor=0.3
            )

            # Color based on make/miss
            color = self.colors.WIN if shot['made'] else self.colors.LOSS
            opacity = 0.7 if shot['made'] else 0.3

            # Add trajectory line
            self.fig.add_trace(go.Scatter(
                x=arc_x,
                y=arc_y,
                mode='lines',
                line=dict(color=color, width=2),
                opacity=opacity,
                name=f"{shot['player']} - {'Made' if shot['made'] else 'Miss'}",
                hovertemplate=(
                    f"<b>{shot['player']}</b><br>"
                    f"Distance: {shot['distance']:.1f}ft<br>"
                    f"Result: {'Made' if shot['made'] else 'Miss'}<br>"
                    "<extra></extra>"
                ),
                showlegend=(i < 10)  # Only show first 10 in legend
            ))

            # Add end point marker
            marker_symbol = 'circle' if shot['made'] else 'x'
            self.fig.add_trace(go.Scatter(
                x=[shot['x_end']],
                y=[shot['y_end']],
                mode='markers',
                marker=dict(
                    symbol=marker_symbol,
                    size=10,
                    color=color,
                    line=dict(width=2, color='white')
                ),
                showlegend=False,
                hoverinfo='skip'
            ))

    def _add_animated_trajectories(self, shots: List[Dict]):
        """Add animated shot trajectories"""

        frames = []

        # Create frames for each shot
        for shot_idx, shot in enumerate(shots):
            frame_data = []

            # Add all previous complete trajectories
            for prev_shot in shots[:shot_idx]:
                arc_x, arc_y = self._calculate_arc(
                    prev_shot['x_start'],
                    prev_shot['y_start'],
                    prev_shot['x_end'],
                    prev_shot['y_end']
                )
                color = self.colors.WIN if prev_shot['made'] else self.colors.LOSS

                frame_data.append(go.Scatter(
                    x=arc_x,
                    y=arc_y,
                    mode='lines+markers',
                    line=dict(color=color, width=2),
                    marker=dict(size=8, color=color),
                    opacity=0.3
                ))

            # Add current shot trajectory
            arc_x, arc_y = self._calculate_arc(
                shot['x_start'],
                shot['y_start'],
                shot['x_end'],
                shot['y_end']
            )
            color = self.colors.WIN if shot['made'] else self.colors.LOSS

            frame_data.append(go.Scatter(
                x=arc_x,
                y=arc_y,
                mode='lines+markers',
                line=dict(color=color, width=4),
                marker=dict(size=12, color=color),
                opacity=1.0,
                name=f"{shot['player']}"
            ))

            frames.append(go.Frame(
                data=frame_data,
                name=f"Shot {shot_idx + 1}",
                layout=go.Layout(
                    title=dict(text=f"{self.title} - {shot['player']} ({shot['distance']:.1f}ft)")
                )
            ))

        # Set initial frame
        self.fig.update(frames=frames)

        # Add animation controls
        self.fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶ Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 1000, 'redraw': True},
                            'fromcurrent': True
                        }]
                    },
                    {
                        'label': '⏸ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate'
                        }]
                    }
                ]
            }],
            sliders=[{
                'active': 0,
                'steps': [
                    {
                        'args': [[f.name], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate'
                        }],
                        'label': f.name,
                        'method': 'animate'
                    }
                    for f in frames
                ]
            }]
        )

    def _calculate_arc(
        self,
        x_start: float,
        y_start: float,
        x_end: float,
        y_end: float,
        height_factor: float = 0.3,
        n_points: int = 20
    ) -> tuple:
        """Calculate parabolic arc for shot trajectory"""

        # Linear interpolation for x and y
        t = np.linspace(0, 1, n_points)
        x = x_start + (x_end - x_start) * t
        y = y_start + (y_end - y_start) * t

        # Add parabolic height
        distance = np.sqrt((x_end - x_start)**2 + (y_end - y_start)**2)
        height = distance * height_factor * (1 - (2*t - 1)**2)  # Parabolic curve

        # Adjust y to account for height (simplified 2D projection)
        y = y + height * 0.3

        return x, y

    def _generate_sample_shots(self, sport: str) -> List[Dict]:
        """Generate sample shot data"""
        np.random.seed(42)

        if sport == 'basketball':
            court = BasketballCourt(half_court=True)
            shots = []

            for i in range(15):
                # Random shot location
                x_start = np.random.uniform(5, court.COURT_LENGTH / 2 - 10)
                y_start = np.random.uniform(5, court.COURT_WIDTH - 5)

                # Basket location
                x_end = 5.25
                y_end = court.COURT_WIDTH / 2

                distance = np.sqrt((x_end - x_start)**2 + (y_end - y_start)**2)
                made = np.random.random() < (0.7 if distance < 15 else 0.4)

                shots.append({
                    'x_start': x_start,
                    'y_start': y_start,
                    'x_end': x_end,
                    'y_end': y_end,
                    'distance': distance,
                    'made': made,
                    'player': f'Player {i+1}'
                })

            return shots
        else:
            # Soccer shots
            pitch = SoccerPitch(half_pitch=True)
            shots = []

            for i in range(15):
                x_start = np.random.uniform(10, pitch.PITCH_LENGTH / 2 - 5)
                y_start = np.random.uniform(10, pitch.PITCH_WIDTH - 10)

                x_end = 0
                y_end = pitch.PITCH_WIDTH / 2 + np.random.normal(0, 2)

                distance = np.sqrt((x_end - x_start)**2 + (y_end - y_start)**2)
                made = np.random.random() < 0.3

                shots.append({
                    'x_start': x_start,
                    'y_start': y_start,
                    'x_end': x_end,
                    'y_end': y_end,
                    'distance': distance,
                    'made': made,
                    'player': f'Player {i+1}'
                })

            return shots
