"""
Base visualization class for all chart types
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import plotly.graph_objects as go
from datetime import datetime
import os

from .colors import ColorScheme


class BaseVisualization(ABC):
    """Base class for all visualizations"""

    def __init__(
        self,
        title: str = "",
        dark_mode: bool = False,
        width: int = 1200,
        height: int = 600,
        sport: str = "nfl"
    ):
        """
        Initialize base visualization

        Args:
            title: Chart title
            dark_mode: Use dark theme
            width: Chart width in pixels
            height: Chart height in pixels
            sport: Sport type (nfl, nba, mlb, etc.)
        """
        self.title = title
        self.dark_mode = dark_mode
        self.width = width
        self.height = height
        self.sport = sport.lower()
        self.colors = ColorScheme()
        self.fig = None

    def _get_layout_template(self) -> Dict[str, Any]:
        """Get base layout configuration"""
        bg_color = self.colors.BG_DARK if self.dark_mode else self.colors.BG_LIGHT
        text_color = self.colors.TEXT_LIGHT if self.dark_mode else self.colors.TEXT_DARK

        return {
            'title': {
                'text': self.title,
                'font': {'size': 24, 'color': text_color, 'family': 'Arial Black'},
                'x': 0.5,
                'xanchor': 'center'
            },
            'paper_bgcolor': bg_color,
            'plot_bgcolor': bg_color,
            'font': {'color': text_color, 'family': 'Arial'},
            'width': self.width,
            'height': self.height,
            'hovermode': 'closest',
            'hoverlabel': {
                'bgcolor': 'rgba(0,0,0,0.8)',
                'font': {'color': 'white', 'size': 12}
            }
        }

    @abstractmethod
    def create(self, data: Any, **kwargs) -> go.Figure:
        """
        Create the visualization

        Args:
            data: Input data for the visualization
            **kwargs: Additional parameters

        Returns:
            Plotly Figure object
        """
        pass

    def update_layout(self, **kwargs):
        """Update figure layout with custom parameters"""
        if self.fig:
            self.fig.update_layout(**kwargs)

    def show(self):
        """Display the visualization"""
        if self.fig:
            self.fig.show()

    def save(
        self,
        filename: str,
        format: str = 'html',
        output_dir: str = 'visualizations/output'
    ) -> str:
        """
        Save visualization to file

        Args:
            filename: Output filename (without extension)
            format: Output format ('html', 'png', 'jpg', 'svg', 'pdf')
            output_dir: Output directory

        Returns:
            Full path to saved file
        """
        if not self.fig:
            raise ValueError("No figure to save. Call create() first.")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Build full path
        filepath = os.path.join(output_dir, f"{filename}.{format}")

        # Save based on format
        if format == 'html':
            self.fig.write_html(
                filepath,
                include_plotlyjs='cdn',
                config={'displayModeBar': True, 'responsive': True}
            )
        elif format in ['png', 'jpg', 'jpeg', 'svg', 'pdf']:
            self.fig.write_image(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def to_dict(self) -> Dict:
        """Convert figure to dictionary"""
        if self.fig:
            return self.fig.to_dict()
        return {}

    def to_json(self) -> str:
        """Convert figure to JSON"""
        if self.fig:
            return self.fig.to_json()
        return "{}"

    def add_timestamp(self, position: str = 'bottom_right'):
        """Add timestamp to visualization"""
        if not self.fig:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Position mapping
        positions = {
            'bottom_right': {'x': 0.99, 'y': 0.01, 'xanchor': 'right', 'yanchor': 'bottom'},
            'bottom_left': {'x': 0.01, 'y': 0.01, 'xanchor': 'left', 'yanchor': 'bottom'},
            'top_right': {'x': 0.99, 'y': 0.99, 'xanchor': 'right', 'yanchor': 'top'},
            'top_left': {'x': 0.01, 'y': 0.99, 'xanchor': 'left', 'yanchor': 'top'},
        }

        pos = positions.get(position, positions['bottom_right'])

        self.fig.add_annotation(
            text=f"Generated: {timestamp}",
            font={'size': 10, 'color': self.colors.TEXT_MUTED},
            showarrow=False,
            **pos
        )

    def add_watermark(self, text: str = "SportStatBot"):
        """Add watermark to visualization"""
        if not self.fig:
            return

        self.fig.add_annotation(
            text=text,
            font={'size': 40, 'color': 'rgba(128,128,128,0.1)'},
            showarrow=False,
            x=0.5,
            y=0.5,
            xanchor='center',
            yanchor='middle',
            textangle=-30
        )
