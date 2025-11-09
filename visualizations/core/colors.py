"""
Color schemes and themes for sports visualizations
"""

from typing import Dict, List, Tuple
import plotly.express as px


class ColorScheme:
    """Centralized color scheme management for all visualizations"""

    # Primary action colors
    WIN = '#00C853'           # Green
    LOSS = '#D32F2F'          # Red
    NEUTRAL = '#607D8B'       # Blue Gray
    TIE = '#FFA726'           # Orange

    # Heat intensity gradient
    HEAT_LOW = '#FFF9C4'      # Light Yellow
    HEAT_MEDIUM = '#FF9800'   # Orange
    HEAT_HIGH = '#D32F2F'     # Red

    # Confidence levels (with opacity)
    CONFIDENCE_VERY_LOW = 'rgba(255, 205, 210, 0.2)'    # Light Red
    CONFIDENCE_LOW = 'rgba(255, 224, 130, 0.4)'         # Light Orange
    CONFIDENCE_MEDIUM = 'rgba(255, 245, 157, 0.6)'      # Light Yellow
    CONFIDENCE_HIGH = 'rgba(174, 213, 129, 0.8)'        # Light Green
    CONFIDENCE_VERY_HIGH = 'rgba(102, 187, 106, 1.0)'   # Green

    # Sport-specific colors
    NFL = '#013369'           # NFL Blue
    NBA = '#C8102E'           # NBA Red
    MLB = '#041E42'           # MLB Navy
    NHL = '#000000'           # NHL Black
    MLS = '#000000'           # MLS Black
    SOCCER = '#00A651'        # Soccer Green

    # Chart backgrounds
    BG_DARK = '#1E1E1E'       # Dark background
    BG_LIGHT = '#FFFFFF'      # Light background
    BG_TRANSPARENT = 'rgba(0,0,0,0)'  # Transparent

    # Text colors
    TEXT_DARK = '#212121'     # Dark text
    TEXT_LIGHT = '#FFFFFF'    # Light text
    TEXT_MUTED = '#757575'    # Muted text

    # Team color mapping (common teams)
    TEAM_COLORS = {
        # NFL
        'KC': '#E31837',  # Chiefs Red
        'BUF': '#00338D', # Bills Blue
        'SF': '#AA0000',  # 49ers Red
        'PHI': '#004C54', # Eagles Green
        'DAL': '#041E42', # Cowboys Navy
        'NE': '#002244',  # Patriots Navy

        # NBA
        'LAL': '#552583', # Lakers Purple
        'BOS': '#007A33', # Celtics Green
        'GSW': '#1D428A', # Warriors Blue
        'MIA': '#98002E', # Heat Red

        # MLB
        'NYY': '#003087', # Yankees Navy
        'LAD': '#005A9C', # Dodgers Blue
        'BOS': '#BD3039', # Red Sox Red

        # NHL
        'TOR': '#003E7E', # Maple Leafs Blue
        'MTL': '#AF1E2D', # Canadiens Red
        'NYR': '#0038A8', # Rangers Blue
    }

    @classmethod
    def get_team_color(cls, team_abbr: str, fallback: str = None) -> str:
        """Get color for a specific team"""
        return cls.TEAM_COLORS.get(team_abbr.upper(), fallback or cls.NEUTRAL)

    @classmethod
    def get_heat_gradient(cls, n_colors: int = 10) -> List[str]:
        """Get gradient for heatmaps"""
        return px.colors.sequential.Reds

    @classmethod
    def get_diverging_scale(cls) -> List[str]:
        """Get red-to-green diverging scale"""
        return ['#D32F2F', '#FFEB3B', '#00C853']

    @classmethod
    def get_confidence_color(cls, confidence: float) -> str:
        """
        Get color based on confidence level (0-1)

        Args:
            confidence: Float between 0 and 1

        Returns:
            RGBA color string
        """
        if confidence < 0.2:
            return cls.CONFIDENCE_VERY_LOW
        elif confidence < 0.4:
            return cls.CONFIDENCE_LOW
        elif confidence < 0.6:
            return cls.CONFIDENCE_MEDIUM
        elif confidence < 0.8:
            return cls.CONFIDENCE_HIGH
        else:
            return cls.CONFIDENCE_VERY_HIGH

    @classmethod
    def get_probability_gradient(cls, probability: float) -> str:
        """
        Get color for probability visualization (0-1)

        Args:
            probability: Float between 0 and 1

        Returns:
            Hex color string
        """
        # Red (0%) -> Yellow (50%) -> Green (100%)
        if probability < 0.5:
            # Red to Yellow
            ratio = probability * 2
            return f'rgb({255}, {int(255 * ratio)}, 0)'
        else:
            # Yellow to Green
            ratio = (probability - 0.5) * 2
            return f'rgb({int(255 * (1 - ratio))}, 255, {int(200 * ratio)})'

    @classmethod
    def get_sport_color(cls, sport: str) -> str:
        """Get primary color for sport"""
        sport_map = {
            'nfl': cls.NFL,
            'nba': cls.NBA,
            'mlb': cls.MLB,
            'nhl': cls.NHL,
            'mls': cls.MLS,
            'soccer': cls.SOCCER,
        }
        return sport_map.get(sport.lower(), cls.NEUTRAL)

    @classmethod
    def get_plotly_template(cls, dark_mode: bool = False) -> str:
        """Get Plotly template based on theme"""
        return 'plotly_dark' if dark_mode else 'plotly_white'
