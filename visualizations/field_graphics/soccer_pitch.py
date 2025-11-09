"""
Soccer Pitch Graphics
"""

import plotly.graph_objects as go
from typing import List
import numpy as np


class SoccerPitch:
    """Generate soccer pitch overlay"""

    # Pitch dimensions in meters (standard)
    PITCH_LENGTH = 105
    PITCH_WIDTH = 68

    def __init__(self, half_pitch: bool = False):
        """
        Initialize soccer pitch

        Args:
            half_pitch: Only show half pitch
        """
        self.half_pitch = half_pitch

    def create_pitch(self) -> List[dict]:
        """
        Create soccer pitch shapes

        Returns:
            List of Plotly shapes
        """
        shapes = []

        # Pitch outline
        max_x = self.PITCH_LENGTH / 2 if self.half_pitch else self.PITCH_LENGTH
        shapes.append({
            'type': 'rect',
            'x0': 0, 'y0': 0,
            'x1': max_x,
            'y1': self.PITCH_WIDTH,
            'line': {'color': 'white', 'width': 2},
            'fillcolor': 'rgba(0, 128, 0, 0.3)'  # Grass green
        })

        # Add pitch elements for each side
        sides = [0] if self.half_pitch else [0, self.PITCH_LENGTH]

        for side_x in sides:
            direction = 1 if side_x == 0 else -1

            # Penalty box
            shapes.append({
                'type': 'rect',
                'x0': side_x,
                'y0': (self.PITCH_WIDTH - 40.3) / 2,
                'x1': side_x + direction * 16.5,
                'y1': (self.PITCH_WIDTH + 40.3) / 2,
                'line': {'color': 'white', 'width': 2}
            })

            # Goal box (6-yard box)
            shapes.append({
                'type': 'rect',
                'x0': side_x,
                'y0': (self.PITCH_WIDTH - 18.3) / 2,
                'x1': side_x + direction * 5.5,
                'y1': (self.PITCH_WIDTH + 18.3) / 2,
                'line': {'color': 'white', 'width': 2}
            })

            # Penalty arc
            theta = np.linspace(0, np.pi, 50) if direction == 1 else np.linspace(np.pi, 2*np.pi, 50)
            radius = 9.15
            center_x = side_x + direction * 11

            x_arc = center_x + radius * np.cos(theta)
            y_arc = self.PITCH_WIDTH / 2 + radius * np.sin(theta)

            shapes.append({
                'type': 'path',
                'path': ' L '.join([f'M {x_arc[0]} {y_arc[0]}'] +
                                  [f'{x} {y}' for x, y in zip(x_arc, y_arc)]),
                'line': {'color': 'white', 'width': 2}
            })

            # Penalty spot
            shapes.append({
                'type': 'circle',
                'x0': side_x + direction * 10.5,
                'y0': self.PITCH_WIDTH / 2 - 0.3,
                'x1': side_x + direction * 11.5,
                'y1': self.PITCH_WIDTH / 2 + 0.3,
                'line': {'color': 'white', 'width': 2},
                'fillcolor': 'white'
            })

            # Goal
            shapes.append({
                'type': 'rect',
                'x0': side_x - direction * 0.5,
                'y0': (self.PITCH_WIDTH - 7.3) / 2,
                'x1': side_x,
                'y1': (self.PITCH_WIDTH + 7.3) / 2,
                'line': {'color': 'white', 'width': 3}
            })

        # Center circle
        if not self.half_pitch:
            shapes.append({
                'type': 'circle',
                'x0': self.PITCH_LENGTH / 2 - 9.15,
                'y0': self.PITCH_WIDTH / 2 - 9.15,
                'x1': self.PITCH_LENGTH / 2 + 9.15,
                'y1': self.PITCH_WIDTH / 2 + 9.15,
                'line': {'color': 'white', 'width': 2}
            })

            # Center spot
            shapes.append({
                'type': 'circle',
                'x0': self.PITCH_LENGTH / 2 - 0.3,
                'y0': self.PITCH_WIDTH / 2 - 0.3,
                'x1': self.PITCH_LENGTH / 2 + 0.3,
                'y1': self.PITCH_WIDTH / 2 + 0.3,
                'line': {'color': 'white', 'width': 2},
                'fillcolor': 'white'
            })

            # Halfway line
            shapes.append({
                'type': 'line',
                'x0': self.PITCH_LENGTH / 2,
                'y0': 0,
                'x1': self.PITCH_LENGTH / 2,
                'y1': self.PITCH_WIDTH,
                'line': {'color': 'white', 'width': 2}
            })

        return shapes

    def add_to_figure(self, fig: go.Figure):
        """Add pitch to existing figure"""
        shapes = self.create_pitch()
        fig.update_layout(shapes=shapes)

        max_x = self.PITCH_LENGTH / 2 if self.half_pitch else self.PITCH_LENGTH

        fig.update_xaxes(
            range=[0, max_x],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )

        fig.update_yaxes(
            range=[0, self.PITCH_WIDTH],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor='x',
            scaleratio=1
        )

        return fig
