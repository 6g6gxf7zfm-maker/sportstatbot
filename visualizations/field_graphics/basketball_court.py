"""
NBA Basketball Court Graphics
"""

import plotly.graph_objects as go
from typing import List
import numpy as np


class BasketballCourt:
    """Generate NBA basketball court overlay"""

    # Court dimensions in feet
    COURT_LENGTH = 94
    COURT_WIDTH = 50

    def __init__(self, half_court: bool = False):
        """
        Initialize basketball court

        Args:
            half_court: Only show half court
        """
        self.half_court = half_court

    def create_court(self) -> List[dict]:
        """
        Create basketball court shapes

        Returns:
            List of Plotly shapes
        """
        shapes = []

        # Court outline
        max_x = self.COURT_LENGTH / 2 if self.half_court else self.COURT_LENGTH
        shapes.append({
            'type': 'rect',
            'x0': 0, 'y0': 0,
            'x1': max_x,
            'y1': self.COURT_WIDTH,
            'line': {'color': 'black', 'width': 2},
            'fillcolor': 'rgba(210, 180, 140, 0.3)'  # Wood color
        })

        # Add court elements for each side
        sides = [0] if self.half_court else [0, self.COURT_LENGTH]

        for side_x in sides:
            direction = 1 if side_x == 0 else -1

            # Paint / Key
            shapes.append({
                'type': 'rect',
                'x0': side_x,
                'y0': (self.COURT_WIDTH - 16) / 2,
                'x1': side_x + direction * 19,
                'y1': (self.COURT_WIDTH + 16) / 2,
                'line': {'color': 'black', 'width': 2},
                'fillcolor': 'rgba(0, 0, 255, 0.1)'
            })

            # Free throw circle
            shapes.append({
                'type': 'circle',
                'x0': side_x + direction * 13,
                'y0': self.COURT_WIDTH / 2 - 6,
                'x1': side_x + direction * 19,
                'y1': self.COURT_WIDTH / 2 + 6,
                'line': {'color': 'black', 'width': 2}
            })

            # Three-point arc (simplified as arc-like path)
            theta = np.linspace(-np.pi/2 + 0.4, np.pi/2 - 0.4, 50)
            radius = 23.75
            center_x = side_x + direction * 5.25

            x_arc = center_x + direction * radius * np.cos(theta)
            y_arc = self.COURT_WIDTH / 2 + radius * np.sin(theta)

            shapes.append({
                'type': 'path',
                'path': ' L '.join([f'M {x_arc[0]} {y_arc[0]}'] +
                                  [f'{x} {y}' for x, y in zip(x_arc, y_arc)]),
                'line': {'color': 'black', 'width': 2}
            })

            # Basket
            shapes.append({
                'type': 'circle',
                'x0': side_x + direction * 4.5,
                'y0': self.COURT_WIDTH / 2 - 0.75,
                'x1': side_x + direction * 5.75,
                'y1': self.COURT_WIDTH / 2 + 0.75,
                'line': {'color': 'orange', 'width': 3}
            })

        # Center circle
        if not self.half_court:
            shapes.append({
                'type': 'circle',
                'x0': self.COURT_LENGTH / 2 - 6,
                'y0': self.COURT_WIDTH / 2 - 6,
                'x1': self.COURT_LENGTH / 2 + 6,
                'y1': self.COURT_WIDTH / 2 + 6,
                'line': {'color': 'black', 'width': 2}
            })

        return shapes

    def add_to_figure(self, fig: go.Figure):
        """Add court to existing figure"""
        shapes = self.create_court()
        fig.update_layout(shapes=shapes)

        max_x = self.COURT_LENGTH / 2 if self.half_court else self.COURT_LENGTH

        fig.update_xaxes(
            range=[0, max_x],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )

        fig.update_yaxes(
            range=[0, self.COURT_WIDTH],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor='x',
            scaleratio=1
        )

        return fig
