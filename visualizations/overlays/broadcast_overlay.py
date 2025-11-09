"""
Broadcast Overlay Graphics
Feature #37: Customizable broadcast overlay pack
"""

import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime

from ..core.base_viz import BaseVisualization


class BroadcastOverlay(BaseVisualization):
    """
    Feature #37: Customizable broadcast overlay pack

    Creates broadcast-style overlays for live visualization displays.
    """

    def create_scoreboard(
        self,
        data: Dict[str, Any],
        **kwargs
    ) -> go.Figure:
        """
        Create broadcast-style scoreboard overlay

        Args:
            data: Dictionary containing:
                - team_a: {name, score, record, logo_url}
                - team_b: {name, score, record, logo_url}
                - quarter: Current quarter/period
                - time_remaining: Time remaining in period
                - possession: Which team has possession

        Returns:
            Plotly Figure
        """
        team_a = data.get('team_a', {})
        team_b = data.get('team_b', {})
        quarter = data.get('quarter', 1)
        time_remaining = data.get('time_remaining', '15:00')
        possession = data.get('possession', 'A')

        self.title = ""  # No title for overlay

        # Create figure
        self.fig = go.Figure()

        # Create scoreboard as annotations
        scoreboard_y = 0.95

        # Team A
        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.2, y=scoreboard_y,
            text=f"<b>{team_a.get('name', 'Team A')}</b>",
            showarrow=False,
            font=dict(size=20, color='white', family='Arial Black'),
            bgcolor=self.colors.get_team_color(team_a.get('name', 'A')[:3]),
            bordercolor='white',
            borderwidth=3 if possession == 'A' else 1,
            borderpad=10
        )

        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.3, y=scoreboard_y,
            text=f"<b>{team_a.get('score', 0)}</b>",
            showarrow=False,
            font=dict(size=32, color='white', family='Arial Black'),
            bgcolor='rgba(0, 0, 0, 0.8)',
            bordercolor='white',
            borderwidth=2,
            borderpad=10
        )

        # VS
        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.5, y=scoreboard_y,
            text="VS",
            showarrow=False,
            font=dict(size=16, color='white', family='Arial Black')
        )

        # Team B
        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.7, y=scoreboard_y,
            text=f"<b>{team_b.get('score', 0)}</b>",
            showarrow=False,
            font=dict(size=32, color='white', family='Arial Black'),
            bgcolor='rgba(0, 0, 0, 0.8)',
            bordercolor='white',
            borderwidth=2,
            borderpad=10
        )

        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.8, y=scoreboard_y,
            text=f"<b>{team_b.get('name', 'Team B')}</b>",
            showarrow=False,
            font=dict(size=20, color='white', family='Arial Black'),
            bgcolor=self.colors.get_team_color(team_b.get('name', 'B')[:3]),
            bordercolor='white',
            borderwidth=3 if possession == 'B' else 1,
            borderpad=10
        )

        # Quarter and time
        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.5, y=scoreboard_y - 0.06,
            text=f"Q{quarter} | {time_remaining}",
            showarrow=False,
            font=dict(size=16, color='white', family='Arial Black'),
            bgcolor='rgba(0, 0, 0, 0.8)',
            bordercolor='white',
            borderwidth=2,
            borderpad=8
        )

        # Team records
        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.2, y=scoreboard_y - 0.06,
            text=team_a.get('record', '0-0'),
            showarrow=False,
            font=dict(size=12, color='white'),
            bgcolor='rgba(0, 0, 0, 0.6)'
        )

        self.fig.add_annotation(
            xref='paper', yref='paper',
            x=0.8, y=scoreboard_y - 0.06,
            text=team_b.get('record', '0-0'),
            showarrow=False,
            font=dict(size=12, color='white'),
            bgcolor='rgba(0, 0, 0, 0.6)'
        )

        # Update layout for transparent overlay
        self.fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            width=self.width,
            height=200,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        return self.fig

    def create_stat_ticker(
        self,
        data: Dict[str, Any],
        **kwargs
    ) -> go.Figure:
        """
        Create scrolling stat ticker overlay

        Args:
            data: Dictionary containing:
                - stats: List of {label, team_a_value, team_b_value}

        Returns:
            Plotly Figure
        """
        stats = data.get('stats', [])

        if not stats:
            stats = [
                {'label': 'Total Yards', 'team_a_value': 345, 'team_b_value': 289},
                {'label': 'Passing Yards', 'team_a_value': 245, 'team_b_value': 198},
                {'label': 'Rushing Yards', 'team_a_value': 100, 'team_b_value': 91},
                {'label': 'Turnovers', 'team_a_value': 1, 'team_b_value': 2}
            ]

        self.fig = go.Figure()

        # Create stat comparison bars
        for idx, stat in enumerate(stats):
            y_pos = 0.9 - (idx * 0.2)

            # Label
            self.fig.add_annotation(
                xref='paper', yref='paper',
                x=0.5, y=y_pos + 0.05,
                text=f"<b>{stat['label']}</b>",
                showarrow=False,
                font=dict(size=14, color='white', family='Arial Black'),
                bgcolor='rgba(0, 0, 0, 0.8)'
            )

            # Team A value
            self.fig.add_annotation(
                xref='paper', yref='paper',
                x=0.3, y=y_pos,
                text=str(stat['team_a_value']),
                showarrow=False,
                font=dict(size=18, color='white', family='Arial Black'),
                bgcolor=self.colors.WIN if stat['team_a_value'] > stat['team_b_value'] else self.colors.NEUTRAL
            )

            # Team B value
            self.fig.add_annotation(
                xref='paper', yref='paper',
                x=0.7, y=y_pos,
                text=str(stat['team_b_value']),
                showarrow=False,
                font=dict(size=18, color='white', family='Arial Black'),
                bgcolor=self.colors.WIN if stat['team_b_value'] > stat['team_a_value'] else self.colors.NEUTRAL
            )

        # Update layout
        self.fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            width=400,
            height=max(300, len(stats) * 80),
            margin=dict(l=0, r=0, t=0, b=0)
        )

        return self.fig
