"""
Base Chart Generator
====================
Base class for all chart generators with common functionality.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from .chart_utils import setup_chart_style, save_chart, add_watermark, get_sport_colors


class BaseChartGenerator:
    """
    Base class for all chart generators.
    Provides common functionality for creating and saving charts.
    """

    def __init__(self, sport='default', style='sports', output_dir='charts'):
        """
        Initialize the base chart generator.

        Args:
            sport: Sport identifier for color schemes
            style: Chart style ('dark', 'light', 'sports')
            output_dir: Directory to save charts
        """
        self.sport = sport
        self.style = style
        self.output_dir = output_dir
        self.colors = get_sport_colors(sport)
        setup_chart_style(style, sport)

    def create_figure(self, figsize=(12, 6), **kwargs):
        """
        Create a new figure with consistent styling.

        Args:
            figsize: Figure size as (width, height) tuple
            **kwargs: Additional arguments for plt.figure()

        Returns:
            tuple: (fig, ax) - Figure and axes objects
        """
        fig, ax = plt.subplots(figsize=figsize, **kwargs)
        return fig, ax

    def save_and_close(self, fig, filename, dpi=300):
        """
        Save a chart and close the figure.

        Args:
            fig: Matplotlib figure object
            filename: Output filename
            dpi: Resolution in dots per inch

        Returns:
            str: Path to saved file
        """
        return save_chart(fig, filename, self.output_dir, dpi)

    def add_title(self, ax, title, subtitle=None, **kwargs):
        """
        Add a title to a chart with optional subtitle.

        Args:
            ax: Matplotlib axes object
            title: Main title text
            subtitle: Subtitle text (optional)
            **kwargs: Additional arguments for ax.set_title()
        """
        if subtitle:
            full_title = f"{title}\n{subtitle}"
            fontsize = kwargs.pop('fontsize', 14)
            ax.set_title(full_title, fontsize=fontsize, fontweight='bold', pad=20, **kwargs)
        else:
            fontsize = kwargs.pop('fontsize', 16)
            ax.set_title(title, fontsize=fontsize, fontweight='bold', pad=15, **kwargs)

    def add_labels(self, ax, xlabel=None, ylabel=None, **kwargs):
        """
        Add axis labels to a chart.

        Args:
            ax: Matplotlib axes object
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional arguments for label styling
        """
        fontsize = kwargs.pop('fontsize', 12)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=fontsize, fontweight='bold', **kwargs)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=fontsize, fontweight='bold', **kwargs)

    def add_grid(self, ax, axis='both', alpha=0.3, linestyle='--', **kwargs):
        """
        Add a grid to a chart.

        Args:
            ax: Matplotlib axes object
            axis: Grid axis ('both', 'x', 'y')
            alpha: Grid transparency
            linestyle: Grid line style
            **kwargs: Additional arguments for ax.grid()
        """
        ax.grid(True, axis=axis, alpha=alpha, linestyle=linestyle, **kwargs)

    def add_legend(self, ax, location='best', frameon=True, **kwargs):
        """
        Add a legend to a chart.

        Args:
            ax: Matplotlib axes object
            location: Legend location
            frameon: Whether to draw a frame around the legend
            **kwargs: Additional arguments for ax.legend()
        """
        ax.legend(loc=location, frameon=frameon, **kwargs)

    def format_x_axis_dates(self, ax, date_format='%b %d', rotation=45, **kwargs):
        """
        Format x-axis for date display.

        Args:
            ax: Matplotlib axes object
            date_format: Date format string
            rotation: Label rotation angle
            **kwargs: Additional formatting arguments
        """
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=rotation, ha='right')

    def add_timestamp(self, ax, position='bottom_left'):
        """
        Add a timestamp to the chart.

        Args:
            ax: Matplotlib axes object
            position: Position of timestamp
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        positions = {
            'bottom_left': (0.02, 0.02),
            'bottom_right': (0.98, 0.02),
            'top_left': (0.02, 0.98),
            'top_right': (0.98, 0.98)
        }

        ha_map = {
            'bottom_left': 'left',
            'top_left': 'left',
            'bottom_right': 'right',
            'top_right': 'right'
        }

        va_map = {
            'bottom_left': 'bottom',
            'bottom_right': 'bottom',
            'top_left': 'top',
            'top_right': 'top'
        }

        pos = positions.get(position, positions['bottom_left'])
        ax.text(
            pos[0], pos[1], f'Generated: {timestamp}',
            transform=ax.transAxes,
            fontsize=8,
            color='gray',
            alpha=0.7,
            ha=ha_map.get(position, 'left'),
            va=va_map.get(position, 'bottom')
        )

    def finalize_chart(self, fig, ax, title, filename, xlabel=None, ylabel=None,
                       add_watermark_flag=True, add_timestamp_flag=True, **kwargs):
        """
        Finalize a chart with all common elements and save it.

        Args:
            fig: Matplotlib figure object
            ax: Matplotlib axes object
            title: Chart title
            filename: Output filename
            xlabel: X-axis label (optional)
            ylabel: Y-axis label (optional)
            add_watermark_flag: Whether to add watermark
            add_timestamp_flag: Whether to add timestamp
            **kwargs: Additional arguments

        Returns:
            str: Path to saved file
        """
        self.add_title(ax, title)

        if xlabel or ylabel:
            self.add_labels(ax, xlabel, ylabel)

        if add_watermark_flag:
            add_watermark(ax)

        if add_timestamp_flag:
            self.add_timestamp(ax)

        plt.tight_layout()
        return self.save_and_close(fig, filename, kwargs.get('dpi', 300))
