"""
Chart Utilities
===============
Helper functions and utilities for chart generation.
"""

import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np

# Color schemes for different sports
SPORT_COLORS = {
    'nfl': {'primary': '#013369', 'secondary': '#D50A0A', 'accent': '#FFB612'},
    'nba': {'primary': '#17408B', 'secondary': '#C9082A', 'accent': '#FDB927'},
    'mlb': {'primary': '#041E42', 'secondary': '#BF0D3E', 'accent': '#FFFFFF'},
    'nhl': {'primary': '#000000', 'secondary': '#C8102E', 'accent': '#FCB514'},
    'mls': {'primary': '#000000', 'secondary': '#C4122E', 'accent': '#EBEBEB'},
    'soccer': {'primary': '#37003C', 'secondary': '#00FF85', 'accent': '#FFFFFF'},
    'default': {'primary': '#2E3440', 'secondary': '#88C0D0', 'accent': '#EBCB8B'}
}

# Chart style configurations
CHART_STYLES = {
    'dark': {
        'bg_color': '#1e1e1e',
        'text_color': '#ffffff',
        'grid_color': '#3e3e3e',
        'accent_color': '#88C0D0'
    },
    'light': {
        'bg_color': '#ffffff',
        'text_color': '#000000',
        'grid_color': '#e0e0e0',
        'accent_color': '#17408B'
    },
    'sports': {
        'bg_color': '#f5f5f5',
        'text_color': '#2e3440',
        'grid_color': '#d8dee9',
        'accent_color': '#88C0D0'
    }
}


def setup_chart_style(style='sports', sport=None):
    """
    Set up matplotlib style for consistent chart appearance.

    Args:
        style: Style preset ('dark', 'light', 'sports')
        sport: Sport key for sport-specific colors
    """
    sns.set_theme()
    plt.rcParams['figure.facecolor'] = CHART_STYLES[style]['bg_color']
    plt.rcParams['axes.facecolor'] = CHART_STYLES[style]['bg_color']
    plt.rcParams['text.color'] = CHART_STYLES[style]['text_color']
    plt.rcParams['axes.labelcolor'] = CHART_STYLES[style]['text_color']
    plt.rcParams['xtick.color'] = CHART_STYLES[style]['text_color']
    plt.rcParams['ytick.color'] = CHART_STYLES[style]['text_color']
    plt.rcParams['grid.color'] = CHART_STYLES[style]['grid_color']
    plt.rcParams['axes.edgecolor'] = CHART_STYLES[style]['grid_color']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['font.size'] = 10


def get_sport_colors(sport):
    """Get color scheme for a specific sport."""
    return SPORT_COLORS.get(sport.lower(), SPORT_COLORS['default'])


def create_gradient_colormap(colors, name='custom'):
    """Create a custom gradient colormap."""
    return mcolors.LinearSegmentedColormap.from_list(name, colors)


def save_chart(fig, filename, output_dir='charts', dpi=300):
    """
    Save a chart to file.

    Args:
        fig: Matplotlib figure object
        filename: Output filename
        output_dir: Output directory
        dpi: Resolution in dots per inch

    Returns:
        str: Path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath


def format_percentage(value, decimal_places=1):
    """Format a decimal as percentage."""
    return f"{value * 100:.{decimal_places}f}%"


def format_rating(value, decimal_places=1):
    """Format a rating value."""
    return f"{value:.{decimal_places}f}"


def calculate_rolling_average(data, window=5):
    """Calculate rolling average for a data series."""
    if len(data) < window:
        return data
    return np.convolve(data, np.ones(window)/window, mode='valid')


def generate_date_range(days=30, end_date=None):
    """Generate a range of dates."""
    if end_date is None:
        end_date = datetime.now()
    return [end_date - timedelta(days=i) for i in range(days, 0, -1)]


def normalize_data(data, min_val=0, max_val=100):
    """Normalize data to a specific range."""
    data_array = np.array(data)
    data_min, data_max = data_array.min(), data_array.max()
    if data_max == data_min:
        return np.full_like(data_array, (min_val + max_val) / 2)
    normalized = (data_array - data_min) / (data_max - data_min)
    return normalized * (max_val - min_val) + min_val


def get_trend_color(value, threshold_positive=0, threshold_negative=0, reverse=False):
    """
    Get color based on trend value.

    Args:
        value: The value to evaluate
        threshold_positive: Threshold for positive (green) color
        threshold_negative: Threshold for negative (red) color
        reverse: If True, reverse the color scheme (red for positive, green for negative)

    Returns:
        str: Hex color code
    """
    if reverse:
        if value > threshold_positive:
            return '#BF0D3E'  # Red
        elif value < threshold_negative:
            return '#5CB85C'  # Green
    else:
        if value > threshold_positive:
            return '#5CB85C'  # Green
        elif value < threshold_negative:
            return '#BF0D3E'  # Red
    return '#FDB927'  # Yellow/Neutral


def abbreviate_team_name(team_name, max_length=10):
    """Abbreviate team name for display."""
    if len(team_name) <= max_length:
        return team_name

    # Common abbreviations
    abbrev_map = {
        'Lakers': 'LAL',
        'Warriors': 'GSW',
        'Celtics': 'BOS',
        'Heat': 'MIA',
        'Bucks': 'MIL',
        'Nets': 'BKN',
        'Clippers': 'LAC',
        'Patriots': 'NE',
        'Cowboys': 'DAL',
        'Packers': 'GB',
        '49ers': 'SF',
        'Chiefs': 'KC',
        'Yankees': 'NYY',
        'Red Sox': 'BOS',
        'Dodgers': 'LAD',
        'Cubs': 'CHC',
    }

    for full, abbrev in abbrev_map.items():
        if full in team_name:
            return abbrev

    # Default: take first letters of each word
    words = team_name.split()
    if len(words) > 1:
        return ''.join(w[0] for w in words[:3]).upper()
    return team_name[:max_length]


def create_annotation(ax, text, xy, xytext=None, style='info'):
    """
    Add an annotation to a chart.

    Args:
        ax: Matplotlib axes object
        text: Annotation text
        xy: Point to annotate
        xytext: Position of annotation text (optional)
        style: Annotation style ('info', 'warning', 'success', 'danger')
    """
    style_colors = {
        'info': '#17408B',
        'warning': '#FDB927',
        'success': '#5CB85C',
        'danger': '#BF0D3E'
    }

    if xytext is None:
        xytext = (10, 10)

    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        textcoords='offset points',
        bbox=dict(boxstyle='round,pad=0.5', fc=style_colors.get(style, '#17408B'), alpha=0.7),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color=style_colors.get(style, '#17408B')),
        color='white',
        fontsize=9,
        fontweight='bold'
    )


def add_watermark(ax, text='SportStatBot', position='bottom_right', alpha=0.3):
    """Add a watermark to a chart."""
    positions = {
        'bottom_right': (0.95, 0.05),
        'bottom_left': (0.05, 0.05),
        'top_right': (0.95, 0.95),
        'top_left': (0.05, 0.95),
        'center': (0.5, 0.5)
    }

    ha_map = {
        'bottom_right': 'right',
        'top_right': 'right',
        'bottom_left': 'left',
        'top_left': 'left',
        'center': 'center'
    }

    va_map = {
        'bottom_right': 'bottom',
        'bottom_left': 'bottom',
        'top_right': 'top',
        'top_left': 'top',
        'center': 'center'
    }

    pos = positions.get(position, positions['bottom_right'])
    ha = ha_map.get(position, 'right')
    va = va_map.get(position, 'bottom')

    ax.text(
        pos[0], pos[1], text,
        transform=ax.transAxes,
        fontsize=12,
        color='gray',
        alpha=alpha,
        ha=ha,
        va=va,
        fontweight='bold'
    )
