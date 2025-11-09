"""
Studio View Layout
Feature #44: Dynamic font scaling for large-screen studio view
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go

from ..charts.probability_charts import ProbabilityTicker
from ..overlays.broadcast_overlay import BroadcastOverlay
from ..core.colors import ColorScheme


class StudioView:
    """
    Feature #44: Dynamic font scaling for large-screen studio view

    Optimized dashboard layout for studio/large screen displays.
    """

    def __init__(self, dark_mode: bool = False):
        self.dark_mode = dark_mode
        self.colors = ColorScheme()

    def create_layout(self):
        """Create studio view layout"""

        # Create overlay components
        overlay = BroadcastOverlay(dark_mode=self.dark_mode)
        scoreboard = overlay.create_scoreboard({
            'team_a': {'name': 'Chiefs', 'score': 28, 'record': '10-3'},
            'team_b': {'name': 'Bills', 'score': 24, 'record': '9-4'},
            'quarter': 4,
            'time_remaining': '5:23',
            'possession': 'A'
        })

        ticker = ProbabilityTicker(dark_mode=self.dark_mode)
        ticker_fig = ticker.create({})

        return dbc.Container([
            # Top: Scoreboard Overlay
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=scoreboard,
                        config={'displayModeBar': False},
                        style={'height': '200px'}
                    )
                ])
            ], className='mb-3'),

            # Middle: Main Content Area (3 columns)
            dbc.Row([
                # Left: Stats
                dbc.Col([
                    html.Div([
                        html.H3("Team Stats", className='text-center studio-heading'),
                        html.Div([
                            self._create_stat_item("Total Yards", "345", "289"),
                            self._create_stat_item("Passing", "245", "198"),
                            self._create_stat_item("Rushing", "100", "91"),
                            self._create_stat_item("Turnovers", "1", "2"),
                            self._create_stat_item("3rd Down", "6/12", "4/11"),
                        ], className='stat-container')
                    ], className='studio-panel')
                ], width=3),

                # Center: Main Visualization
                dbc.Col([
                    html.Div([
                        html.H2("Win Probability", className='text-center studio-heading-large'),
                        # Placeholder for main viz
                        html.Div([
                            html.H1("65%", className='text-center studio-metric', style={'font-size': '120px'}),
                            html.P("Chiefs Win Probability", className='text-center', style={'font-size': '24px'})
                        ])
                    ], className='studio-panel-center')
                ], width=6),

                # Right: Probability Ticker
                dbc.Col([
                    html.Div([
                        html.H3("Live Probabilities", className='text-center studio-heading'),
                        dcc.Graph(
                            figure=ticker_fig,
                            config={'displayModeBar': False},
                            style={'height': '500px'}
                        )
                    ], className='studio-panel')
                ], width=3)
            ]),

            # Bottom: Info Bar
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🔴 LIVE", className='live-indicator'),
                        html.Span(" | ", style={'margin': '0 20px'}),
                        html.Span("SportStatBot Analytics Dashboard", className='info-text'),
                        html.Span(" | ", style={'margin': '0 20px'}),
                        html.Span("Real-time Updates", className='info-text')
                    ], className='info-bar')
                ])
            ], className='mt-3')

        ], fluid=True, className='studio-container', style=self._get_studio_styles())

    def _create_stat_item(self, label: str, team_a_val: str, team_b_val: str):
        """Create stat comparison item"""

        try:
            a_numeric = float(team_a_val)
            b_numeric = float(team_b_val)
            a_winning = a_numeric > b_numeric
        except:
            # Handle non-numeric (like "6/12")
            a_winning = True

        return html.Div([
            html.Div(label, className='stat-label', style={'font-size': '18px', 'font-weight': 'bold'}),
            html.Div([
                html.Span(
                    team_a_val,
                    className='stat-value',
                    style={
                        'font-size': '28px',
                        'color': self.colors.WIN if a_winning else self.colors.TEXT_MUTED,
                        'font-weight': 'bold',
                        'margin-right': '20px'
                    }
                ),
                html.Span('-', style={'margin': '0 10px', 'font-size': '20px'}),
                html.Span(
                    team_b_val,
                    className='stat-value',
                    style={
                        'font-size': '28px',
                        'color': self.colors.WIN if not a_winning else self.colors.TEXT_MUTED,
                        'font-weight': 'bold',
                        'margin-left': '20px'
                    }
                )
            ], className='stat-values')
        ], className='stat-row', style={'margin': '20px 0', 'padding': '15px', 'border-bottom': '1px solid #ddd'})

    def _get_studio_styles(self):
        """Get CSS styles for studio view"""

        bg_color = self.colors.BG_DARK if self.dark_mode else self.colors.BG_LIGHT
        text_color = self.colors.TEXT_LIGHT if self.dark_mode else self.colors.TEXT_DARK

        return {
            'background-color': bg_color,
            'color': text_color,
            'min-height': '100vh',
            'padding': '30px',
            'font-family': 'Arial, sans-serif'
        }
