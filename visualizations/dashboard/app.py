"""
Main Dashboard Application
Features #44 & #45: Dynamic font scaling and side-by-side compare mode
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ..charts.heatmaps import EPAHeatmap
from ..charts.worm_graphs import ScoreWormGraph
from ..charts.radar_charts import PlayerRadarComparison
from ..core.colors import ColorScheme


def create_dashboard(port: int = 8050, debug: bool = False) -> dash.Dash:
    """
    Create Dash dashboard application

    Args:
        port: Port number for dashboard
        debug: Enable debug mode

    Returns:
        Dash app instance
    """

    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    colors = ColorScheme()

    # App layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(
                    "🏆 Sports Analytics Dashboard",
                    id='main-title',
                    className='text-center mb-4',
                    style={'font-size': '2.5rem'}
                )
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("Single View", id='single-view-btn', color='primary', active=True),
                    dbc.Button("Side-by-Side Compare", id='compare-view-btn', color='secondary'),
                    dbc.Button("Studio Mode", id='studio-view-btn', color='info')
                ], className='mb-3')
            ])
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("Font Size:"),
                dcc.Slider(
                    id='font-size-slider',
                    min=0.5,
                    max=2.0,
                    step=0.1,
                    value=1.0,
                    marks={
                        0.5: '50%',
                        1.0: '100%',
                        1.5: '150%',
                        2.0: '200%'
                    }
                )
            ], width=6),
            dbc.Col([
                html.Label("Theme:"),
                dbc.RadioItems(
                    id='theme-selector',
                    options=[
                        {'label': 'Light', 'value': 'light'},
                        {'label': 'Dark', 'value': 'dark'}
                    ],
                    value='light',
                    inline=True
                )
            ], width=6)
        ], className='mb-4'),

        html.Div(id='dashboard-content'),

        dbc.Row([
            dbc.Col([
                html.Footer(
                    "SportStatBot © 2025 | Interactive Sports Analytics",
                    className='text-center mt-5 text-muted'
                )
            ])
        ])

    ], fluid=True, id='main-container')

    # Callbacks
    @app.callback(
        Output('main-container', 'style'),
        Input('font-size-slider', 'value'),
        Input('theme-selector', 'value')
    )
    def update_global_style(font_scale, theme):
        """Update global font size and theme"""

        bg_color = colors.BG_DARK if theme == 'dark' else colors.BG_LIGHT
        text_color = colors.TEXT_LIGHT if theme == 'dark' else colors.TEXT_DARK

        return {
            'font-size': f'{font_scale}rem',
            'background-color': bg_color,
            'color': text_color,
            'min-height': '100vh',
            'padding': '20px'
        }

    @app.callback(
        Output('dashboard-content', 'children'),
        [Input('single-view-btn', 'n_clicks'),
         Input('compare-view-btn', 'n_clicks'),
         Input('studio-view-btn', 'n_clicks'),
         Input('theme-selector', 'value')]
    )
    def update_view(single_clicks, compare_clicks, studio_clicks, theme):
        """Update dashboard view based on selected mode"""

        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'single-view-btn'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        dark_mode = (theme == 'dark')

        if button_id == 'compare-view-btn':
            return create_compare_view(dark_mode)
        elif button_id == 'studio-view-btn':
            return create_studio_view(dark_mode)
        else:
            return create_single_view(dark_mode)

    return app


def create_single_view(dark_mode: bool = False):
    """Create single visualization view"""

    # Create sample visualizations
    radar = PlayerRadarComparison(dark_mode=dark_mode)
    radar_fig = radar.create({})

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=radar_fig)
            ])
        ])
    ])


def create_compare_view(dark_mode: bool = False):
    """
    Feature #45: Side-by-side compare mode

    Show two visualizations side by side for comparison.
    """

    radar1 = PlayerRadarComparison(dark_mode=dark_mode)
    fig1 = radar1.create({
        'player1': {
            'name': 'Patrick Mahomes',
            'stats': {
                'Passing': 92,
                'Rushing': 65,
                'Decision Making': 90,
                'Accuracy': 88,
                'Arm Strength': 95,
                'Mobility': 70
            }
        },
        'player2': {
            'name': 'Josh Allen',
            'stats': {
                'Passing': 88,
                'Rushing': 85,
                'Decision Making': 82,
                'Accuracy': 80,
                'Arm Strength': 98,
                'Mobility': 90
            }
        },
        'categories': ['Passing', 'Rushing', 'Decision Making', 'Accuracy', 'Arm Strength', 'Mobility']
    })

    worm = ScoreWormGraph(dark_mode=dark_mode)
    fig2 = worm.create({})

    return dbc.Container([
        html.H2("Side-by-Side Comparison", className='text-center mb-4'),
        dbc.Row([
            dbc.Col([
                html.H4("Player Comparison"),
                dcc.Graph(figure=fig1)
            ], width=6),
            dbc.Col([
                html.H4("Score Tracker"),
                dcc.Graph(figure=fig2)
            ], width=6)
        ])
    ])


def create_studio_view(dark_mode: bool = False):
    """
    Feature #44: Dynamic font scaling for large-screen studio view

    Optimized layout for large displays with scaled fonts.
    """

    from .studio_view import StudioView

    studio = StudioView(dark_mode=dark_mode)
    layout = studio.create_layout()

    return layout


def run_dashboard(port: int = 8050, debug: bool = True):
    """Run the dashboard server"""
    app = create_dashboard(port=port, debug=debug)
    app.run_server(debug=debug, port=port)


if __name__ == '__main__':
    run_dashboard()
