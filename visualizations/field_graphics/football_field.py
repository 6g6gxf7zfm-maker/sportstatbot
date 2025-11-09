"""
NFL Football Field Graphics
"""

import plotly.graph_objects as go
from typing import List, Tuple


class FootballField:
    """Generate NFL football field overlay"""

    # Field dimensions in yards
    FIELD_LENGTH = 120  # Including end zones
    FIELD_WIDTH = 53.3

    def __init__(self, include_numbers: bool = True):
        """
        Initialize football field

        Args:
            include_numbers: Include yard line numbers
        """
        self.include_numbers = include_numbers

    def create_field(self) -> List[dict]:
        """
        Create football field shapes and annotations

        Returns:
            List of Plotly shapes and annotations
        """
        shapes = []
        annotations = []

        # Field outline
        shapes.append({
            'type': 'rect',
            'x0': 0, 'y0': 0,
            'x1': self.FIELD_LENGTH,
            'y1': self.FIELD_WIDTH,
            'line': {'color': 'white', 'width': 2},
            'fillcolor': 'rgba(0, 100, 0, 0.3)'
        })

        # End zones
        for x in [0, 110]:
            shapes.append({
                'type': 'rect',
                'x0': x, 'y0': 0,
                'x1': x + 10,
                'y1': self.FIELD_WIDTH,
                'line': {'color': 'white', 'width': 2},
                'fillcolor': 'rgba(0, 50, 0, 0.5)'
            })

        # Yard lines (every 5 yards)
        for yard in range(10, 110, 5):
            width = 2 if yard % 10 == 0 else 1
            shapes.append({
                'type': 'line',
                'x0': yard, 'y0': 0,
                'x1': yard, 'y1': self.FIELD_WIDTH,
                'line': {'color': 'white', 'width': width}
            })

            # Add numbers
            if self.include_numbers and yard % 10 == 0:
                # Display yard number (flip at midfield)
                yard_num = yard - 10 if yard <= 50 else 110 - yard

                if 10 <= yard <= 100:
                    annotations.append({
                        'x': yard,
                        'y': self.FIELD_WIDTH / 2,
                        'text': str(yard_num),
                        'showarrow': False,
                        'font': {'size': 20, 'color': 'white'},
                        'xanchor': 'center',
                        'yanchor': 'middle'
                    })

        # Hash marks
        for yard in range(10, 110):
            # Top hash marks
            shapes.append({
                'type': 'line',
                'x0': yard, 'y0': self.FIELD_WIDTH * 0.4,
                'x1': yard, 'y1': self.FIELD_WIDTH * 0.4 + 0.5,
                'line': {'color': 'white', 'width': 1}
            })
            # Bottom hash marks
            shapes.append({
                'type': 'line',
                'x0': yard, 'y0': self.FIELD_WIDTH * 0.6,
                'x1': yard, 'y1': self.FIELD_WIDTH * 0.6 - 0.5,
                'line': {'color': 'white', 'width': 1}
            })

        return shapes, annotations

    def add_to_figure(self, fig: go.Figure):
        """Add field to existing figure"""
        shapes, annotations = self.create_field()

        fig.update_layout(
            shapes=shapes,
            annotations=annotations
        )

        # Set axis properties
        fig.update_xaxes(
            range=[0, self.FIELD_LENGTH],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )

        fig.update_yaxes(
            range=[0, self.FIELD_WIDTH],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )

        return fig
