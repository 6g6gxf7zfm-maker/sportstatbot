"""
Timeline Visualization
Feature #28: Timeline ribbon of momentum swings with hover stats
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class MomentumTimeline(BaseVisualization):
    """
    Feature #28: Timeline ribbon of momentum swings with hover stats

    Shows game momentum over time with interactive hover statistics.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create momentum timeline

        Args:
            data: Dictionary containing:
                - events: List of {time, momentum, team_a, team_b, event_desc, score_a, score_b}
                - team_a_name: Team A name
                - team_b_name: Team B name

        Returns:
            Plotly Figure
        """
        events = data.get('events', [])
        team_a_name = data.get('team_a_name', 'Team A')
        team_b_name = data.get('team_b_name', 'Team B')

        if not events:
            events = self._generate_sample_events()

        self.title = f"{team_a_name} vs {team_b_name} - Momentum Timeline"

        df = pd.DataFrame(events)
        df = df.sort_values('time')

        # Create figure
        self.fig = go.Figure()

        # Add momentum area chart
        self.fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['momentum'],
            fill='tozeroy',
            fillcolor='rgba(0, 200, 83, 0.3)',
            line=dict(color=self.colors.WIN, width=3),
            mode='lines',
            name=team_a_name,
            hovertemplate=(
                f"<b>{team_a_name}</b><br>"
                "Time: %{x}<br>"
                "Momentum: %{y:.1f}<br>"
                "Score: %{customdata[0]}<br>"
                "Event: %{customdata[1]}<br>"
                "<extra></extra>"
            ),
            customdata=df[['score_a', 'event_desc']].values
        ))

        # Add negative momentum for Team B
        self.fig.add_trace(go.Scatter(
            x=df['time'],
            y=-df['momentum'],
            fill='tozeroy',
            fillcolor='rgba(211, 47, 47, 0.3)',
            line=dict(color=self.colors.LOSS, width=3),
            mode='lines',
            name=team_b_name,
            hovertemplate=(
                f"<b>{team_b_name}</b><br>"
                "Time: %{x}<br>"
                "Momentum: %{y:.1f}<br>"
                "Score: %{customdata[0]}<br>"
                "Event: %{customdata[1]}<br>"
                "<extra></extra>"
            ),
            customdata=df[['score_b', 'event_desc']].values
        ))

        # Add zero line
        self.fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            line_width=2
        )

        # Mark key momentum swings
        momentum_changes = df[abs(df['momentum'].diff()) > 15].copy()

        self.fig.add_trace(go.Scatter(
            x=momentum_changes['time'],
            y=momentum_changes['momentum'],
            mode='markers',
            marker=dict(
                size=15,
                color='gold',
                symbol='star',
                line=dict(width=2, color='darkorange')
            ),
            name='Key Moments',
            hovertemplate=(
                "<b>KEY MOMENT</b><br>"
                "Time: %{x}<br>"
                "%{customdata}<br>"
                "<extra></extra>"
            ),
            customdata=momentum_changes['event_desc'].values
        ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': 'Game Time (minutes)',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'yaxis': {
                'title': f'Momentum ({team_a_name} ← → {team_b_name})',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)',
                'zeroline': True
            },
            'hovermode': 'x unified'
        })

        self.fig.update_layout(**layout)

        # Add quarter markers for football/basketball
        if 'quarter' in df.columns:
            for quarter in df['quarter'].unique():
                quarter_start = df[df['quarter'] == quarter]['time'].min()
                self.fig.add_vline(
                    x=quarter_start,
                    line_dash="dot",
                    line_color="gray",
                    annotation_text=f"Q{int(quarter)}",
                    annotation_position="top"
                )

        return self.fig

    def _generate_sample_events(self) -> List[Dict]:
        """Generate sample momentum events"""
        np.random.seed(42)

        events = []
        time = 0
        momentum = 0
        score_a = 0
        score_b = 0

        event_types = [
            'Touchdown', 'Field Goal', 'Interception', 'Fumble Recovery',
            'Sack', 'Big Play', 'Turnover', 'Score'
        ]

        for i in range(60):
            time += np.random.uniform(0.5, 3)

            # Random momentum change
            momentum_change = np.random.normal(0, 8)
            momentum = np.clip(momentum + momentum_change, -50, 50)

            # Occasional scoring
            if np.random.random() < 0.15:
                if momentum > 0:
                    score_a += np.random.choice([3, 6, 7])
                else:
                    score_b += np.random.choice([3, 6, 7])

            event_desc = np.random.choice(event_types)

            events.append({
                'time': time,
                'momentum': momentum,
                'score_a': score_a,
                'score_b': score_b,
                'event_desc': event_desc,
                'quarter': int(time // 15) + 1
            })

        return events
