"""
Sports Analytics Visualization Package

Provides comprehensive visualization capabilities for sports analytics including:
- Interactive charts and graphs
- Field/court overlays
- Real-time animations
- Broadcast-quality overlays
- Advanced analytics visualizations
"""

__version__ = "1.0.0"
__author__ = "SportStatBot"

from .core.base_viz import BaseVisualization
from .core.colors import ColorScheme
from .core.utils import export_chart, cache_visualization

__all__ = [
    'BaseVisualization',
    'ColorScheme',
    'export_chart',
    'cache_visualization'
]
