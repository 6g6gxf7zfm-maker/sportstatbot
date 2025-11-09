"""
Heatmap Visualizations
Feature #26: EPA heatmaps synchronized to clock
Feature #42: Calendar heatmap of team form
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from ..core.base_viz import BaseVisualization
from ..field_graphics.football_field import FootballField


class EPAHeatmap(BaseVisualization):
    """
    Feature #26: Animated EPA heatmaps synchronized to game clock

    Shows Expected Points Added across the field, updating in real-time
    with game clock.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field = FootballField()

    def create(
        self,
        data: Dict[str, Any],
        animate: bool = True,
        frame_duration: int = 500
    ) -> go.Figure:
        """
        Create EPA heatmap

        Args:
            data: Dictionary containing:
                - plays: List of plays with {x, y, epa, quarter, time_remaining}
                - team_name: Team name
            animate: Whether to animate with clock
            frame_duration: Animation frame duration in ms

        Returns:
            Plotly Figure
        """
        plays = pd.DataFrame(data.get('plays', []))
        team_name = data.get('team_name', 'Team')

        if plays.empty:
            # Generate sample data
            plays = self._generate_sample_data()

        self.title = f"{team_name} EPA Heatmap"

        # Create base figure with field
        self.fig = go.Figure()

        if animate:
            self.fig = self._create_animated_heatmap(plays, frame_duration)
        else:
            self.fig = self._create_static_heatmap(plays)

        # Add field overlay
        shapes, annotations = self.field.create_field()
        self.fig.update_layout(
            **self._get_layout_template(),
            shapes=shapes
        )

        self.fig.update_xaxes(range=[0, FootballField.FIELD_LENGTH])
        self.fig.update_yaxes(range=[0, FootballField.FIELD_WIDTH])

        return self.fig

    def _create_animated_heatmap(self, plays: pd.DataFrame, frame_duration: int) -> go.Figure:
        """Create animated heatmap synchronized to game clock"""

        # Sort plays by time
        plays = plays.sort_values('game_seconds')

        # Create frames for animation
        frames = []
        quarters = plays['quarter'].unique()

        for quarter in sorted(quarters):
            quarter_plays = plays[plays['quarter'] == quarter]
            time_points = sorted(quarter_plays['game_seconds'].unique())

            for time_point in time_points:
                # Get all plays up to this point
                current_plays = plays[plays['game_seconds'] <= time_point]

                # Create 2D histogram for heatmap
                heatmap_data, x_edges, y_edges = self._create_heatmap_grid(current_plays)

                # Format time
                minutes = int(time_point // 60)
                seconds = int(time_point % 60)
                time_label = f"Q{int(quarter)} {minutes:02d}:{seconds:02d}"

                frame = go.Frame(
                    data=[go.Heatmap(
                        z=heatmap_data,
                        x=x_edges,
                        y=y_edges,
                        colorscale='RdYlGn',
                        zmid=0,
                        colorbar=dict(title="EPA"),
                        hovertemplate='Yard: %{x}<br>Width: %{y}<br>EPA: %{z:.2f}<extra></extra>'
                    )],
                    name=time_label,
                    layout=go.Layout(
                        title=dict(text=f"{self.title} - {time_label}")
                    )
                )
                frames.append(frame)

        # Add initial frame
        initial_data = plays.head(1)
        heatmap_data, x_edges, y_edges = self._create_heatmap_grid(initial_data)

        self.fig = go.Figure(
            data=[go.Heatmap(
                z=heatmap_data,
                x=x_edges,
                y=y_edges,
                colorscale='RdYlGn',
                zmid=0,
                colorbar=dict(title="EPA")
            )],
            frames=frames
        )

        # Add play button
        self.fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶ Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': frame_duration, 'redraw': True},
                            'fromcurrent': True,
                            'mode': 'immediate'
                        }]
                    },
                    {
                        'label': '⏸ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate'
                        }]
                    }
                ],
                'x': 0.1,
                'y': 1.15
            }],
            sliders=[{
                'active': 0,
                'steps': [
                    {
                        'args': [[f.name], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate'
                        }],
                        'label': f.name,
                        'method': 'animate'
                    }
                    for f in frames
                ],
                'x': 0.1,
                'len': 0.85,
                'y': 0
            }]
        )

        return self.fig

    def _create_static_heatmap(self, plays: pd.DataFrame) -> go.Figure:
        """Create static cumulative heatmap"""

        heatmap_data, x_edges, y_edges = self._create_heatmap_grid(plays)

        self.fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=x_edges,
            y=y_edges,
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="EPA"),
            hovertemplate='Yard: %{x}<br>Width: %{y}<br>EPA: %{z:.2f}<extra></extra>'
        ))

        return self.fig

    def _create_heatmap_grid(self, plays: pd.DataFrame) -> tuple:
        """Create 2D heatmap grid from plays"""

        if plays.empty:
            x_bins = np.linspace(0, FootballField.FIELD_LENGTH, 25)
            y_bins = np.linspace(0, FootballField.FIELD_WIDTH, 15)
            return np.zeros((14, 24)), x_bins, y_bins

        # Create 2D histogram
        H, x_edges, y_edges = np.histogram2d(
            plays['x'],
            plays['y'],
            bins=[25, 15],
            range=[[0, FootballField.FIELD_LENGTH], [0, FootballField.FIELD_WIDTH]],
            weights=plays['epa']
        )

        return H.T, x_edges, y_edges

    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample EPA data"""
        np.random.seed(42)
        n_plays = 100

        return pd.DataFrame({
            'x': np.random.uniform(10, 110, n_plays),
            'y': np.random.uniform(0, FootballField.FIELD_WIDTH, n_plays),
            'epa': np.random.normal(0, 0.5, n_plays),
            'quarter': np.random.randint(1, 5, n_plays),
            'game_seconds': np.sort(np.random.uniform(0, 3600, n_plays))
        })


class CalendarHeatmap(BaseVisualization):
    """
    Feature #42: Calendar heatmap of team form by day

    Shows team performance over a calendar with color-coded results.
    """

    def create(
        self,
        data: Dict[str, Any],
        **kwargs
    ) -> go.Figure:
        """
        Create calendar heatmap

        Args:
            data: Dictionary containing:
                - games: List of {date, result, score_diff}
                - team_name: Team name
                - start_date: Season start date
                - end_date: Season end date

        Returns:
            Plotly Figure
        """
        games = data.get('games', [])
        team_name = data.get('team_name', 'Team')
        start_date = data.get('start_date', datetime.now() - timedelta(days=180))
        end_date = data.get('end_date', datetime.now())

        if not games:
            games = self._generate_sample_games()

        self.title = f"{team_name} Season Calendar"

        # Convert to DataFrame
        df = pd.DataFrame(games)
        df['date'] = pd.to_datetime(df['date'])

        # Create calendar grid
        calendar_data = self._create_calendar_grid(df, start_date, end_date)

        # Create heatmap
        self.fig = go.Figure(data=go.Heatmap(
            z=calendar_data['z'],
            x=calendar_data['x'],
            y=calendar_data['y'],
            colorscale=[
                [0, self.colors.LOSS],      # Losses
                [0.5, self.colors.NEUTRAL],  # No game
                [1, self.colors.WIN]         # Wins
            ],
            zmid=0,
            text=calendar_data['text'],
            hovertemplate='%{text}<extra></extra>',
            showscale=False
        ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {'title': 'Week', 'tickmode': 'linear'},
            'yaxis': {
                'title': '',
                'tickmode': 'array',
                'tickvals': list(range(7)),
                'ticktext': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            'height': 400
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _create_calendar_grid(
        self,
        df: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List]:
        """Create calendar grid data"""

        # Create date range
        date_range = pd.date_range(start_date, end_date, freq='D')

        # Map games to dates
        game_map = {row['date'].date(): row for _, row in df.iterrows()}

        # Create grid (weeks x days)
        calendar_data = {
            'x': [],  # Week number
            'y': [],  # Day of week (0=Mon, 6=Sun)
            'z': [],  # Value (1=win, -1=loss, 0=no game)
            'text': []  # Hover text
        }

        week = 0
        for date in date_range:
            day_of_week = date.weekday()

            # New week on Monday
            if day_of_week == 0:
                week += 1

            calendar_data['x'].append(week)
            calendar_data['y'].append(day_of_week)

            # Check if game on this date
            if date.date() in game_map:
                game = game_map[date.date()]
                result = game['result']
                score_diff = game.get('score_diff', 0)

                if result == 'W':
                    calendar_data['z'].append(1)
                    calendar_data['text'].append(f"{date.strftime('%b %d')}<br>Win (+{score_diff})")
                elif result == 'L':
                    calendar_data['z'].append(-1)
                    calendar_data['text'].append(f"{date.strftime('%b %d')}<br>Loss ({score_diff})")
                else:
                    calendar_data['z'].append(0)
                    calendar_data['text'].append(f"{date.strftime('%b %d')}<br>Tie")
            else:
                calendar_data['z'].append(0)
                calendar_data['text'].append(f"{date.strftime('%b %d')}<br>No game")

        return calendar_data

    def _generate_sample_games(self) -> List[Dict]:
        """Generate sample game data"""
        np.random.seed(42)
        games = []

        start_date = datetime.now() - timedelta(days=120)

        for i in range(30):
            date = start_date + timedelta(days=i * 4)
            result = np.random.choice(['W', 'L'], p=[0.6, 0.4])
            score_diff = np.random.randint(1, 25) if result == 'W' else -np.random.randint(1, 25)

            games.append({
                'date': date,
                'result': result,
                'score_diff': score_diff
            })

        return games
