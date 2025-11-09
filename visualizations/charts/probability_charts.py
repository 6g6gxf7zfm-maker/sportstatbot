"""
Probability Visualization Charts
Feature #30: Probability fan chart of playoff odds
Feature #43: Rolling probability ticker across bottom of dashboard
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class PlayoffProbabilityFan(BaseVisualization):
    """
    Feature #30: Probability fan chart of playoff odds

    Fan chart showing playoff probability projections with uncertainty bands.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create playoff probability fan chart

        Args:
            data: Dictionary containing:
                - team_name: Team name
                - current_prob: Current playoff probability
                - projections: List of {week, prob_10, prob_25, prob_50, prob_75, prob_90}

        Returns:
            Plotly Figure
        """
        team_name = data.get('team_name', 'Team')
        projections = data.get('projections', [])

        if not projections:
            projections = self._generate_sample_projections()

        self.title = f"{team_name} Playoff Probability Fan Chart"

        df = pd.DataFrame(projections)

        # Create figure
        self.fig = go.Figure()

        # Add confidence bands (widest to narrowest)
        # 10th to 90th percentile
        self.fig.add_trace(go.Scatter(
            x=df['week'],
            y=df['prob_90'],
            fill=None,
            mode='lines',
            line=dict(color=self.colors.NEUTRAL, width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        self.fig.add_trace(go.Scatter(
            x=df['week'],
            y=df['prob_10'],
            fill='tonexty',
            mode='lines',
            line=dict(color=self.colors.NEUTRAL, width=0),
            fillcolor='rgba(96, 125, 139, 0.15)',
            name='80% Confidence',
            hovertemplate='Week %{x}<br>10th-90th percentile<extra></extra>'
        ))

        # 25th to 75th percentile
        self.fig.add_trace(go.Scatter(
            x=df['week'],
            y=df['prob_75'],
            fill=None,
            mode='lines',
            line=dict(color=self.colors.NEUTRAL, width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        self.fig.add_trace(go.Scatter(
            x=df['week'],
            y=df['prob_25'],
            fill='tonexty',
            mode='lines',
            line=dict(color=self.colors.NEUTRAL, width=0),
            fillcolor='rgba(96, 125, 139, 0.3)',
            name='50% Confidence',
            hovertemplate='Week %{x}<br>25th-75th percentile<extra></extra>'
        ))

        # Median line
        self.fig.add_trace(go.Scatter(
            x=df['week'],
            y=df['prob_50'],
            mode='lines+markers',
            line=dict(color=self.colors.WIN, width=4),
            marker=dict(size=8, color=self.colors.WIN),
            name='Median Projection',
            hovertemplate=(
                '<b>Week %{x}</b><br>'
                'Playoff Odds: %{y:.1f}%<br>'
                '<extra></extra>'
            )
        ))

        # Add 50% reference line
        self.fig.add_hline(
            y=50,
            line_dash="dash",
            line_color="gray",
            annotation_text="50% Threshold",
            annotation_position="right"
        )

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': 'Week',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'yaxis': {
                'title': 'Playoff Probability (%)',
                'range': [0, 100],
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'hovermode': 'x unified'
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_projections(self) -> List[Dict]:
        """Generate sample projection data"""
        np.random.seed(42)

        projections = []
        base_prob = 50

        for week in range(1, 19):
            # Add some trend
            trend = (week - 9) * 2  # Increase over season

            # Random walk
            change = np.random.normal(0, 5)
            base_prob = np.clip(base_prob + change + trend / 5, 5, 95)

            # Generate percentiles with uncertainty
            uncertainty = max(20, 40 - week * 2)  # Decrease uncertainty over time

            projections.append({
                'week': week,
                'prob_10': max(0, base_prob - uncertainty),
                'prob_25': max(0, base_prob - uncertainty / 2),
                'prob_50': base_prob,
                'prob_75': min(100, base_prob + uncertainty / 2),
                'prob_90': min(100, base_prob + uncertainty)
            })

        return projections


class ProbabilityTicker(BaseVisualization):
    """
    Feature #43: Rolling probability ticker across bottom of dashboard

    Real-time updating probability ticker for multiple events.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create probability ticker

        Args:
            data: Dictionary containing:
                - events: List of {name, probability, change}

        Returns:
            Plotly Figure
        """
        events = data.get('events', [])

        if not events:
            events = self._generate_sample_events()

        self.title = "Live Probability Ticker"

        df = pd.DataFrame(events)

        # Create horizontal bar chart
        self.fig = go.Figure()

        # Sort by probability
        df = df.sort_values('probability', ascending=True)

        # Color based on probability
        colors = [self.colors.get_probability_gradient(p/100) for p in df['probability']]

        self.fig.add_trace(go.Bar(
            y=df['name'],
            x=df['probability'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=2)
            ),
            text=[f"{p:.1f}%" for p in df['probability']],
            textposition='inside',
            textfont=dict(size=14, color='white', family='Arial Black'),
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Probability: %{x:.1f}%<br>'
                'Change: %{customdata:+.1f}%<br>'
                '<extra></extra>'
            ),
            customdata=df['change'].values
        ))

        # Add change indicators
        for idx, row in df.iterrows():
            if abs(row['change']) > 0.1:
                arrow = '▲' if row['change'] > 0 else '▼'
                color = self.colors.WIN if row['change'] > 0 else self.colors.LOSS

                self.fig.add_annotation(
                    y=row['name'],
                    x=row['probability'] + 2,
                    text=f"{arrow} {abs(row['change']):.1f}%",
                    showarrow=False,
                    font=dict(size=12, color=color, family='Arial Black'),
                    xanchor='left'
                )

        # Update layout for ticker style
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': '',
                'range': [0, 105],
                'showgrid': False,
                'showticklabels': False
            },
            'yaxis': {
                'title': '',
                'showgrid': False,
                'tickfont': {'size': 14, 'family': 'Arial Black'}
            },
            'height': max(300, len(events) * 50),
            'margin': {'l': 150, 'r': 100, 't': 50, 'b': 20},
            'showlegend': False
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_events(self) -> List[Dict]:
        """Generate sample ticker events"""
        np.random.seed(42)

        event_names = [
            'Chiefs Win Super Bowl',
            'Bills Make Playoffs',
            '49ers Win Division',
            'Eagles Get #1 Seed',
            'Cowboys Wild Card',
            'Ravens 12+ Wins'
        ]

        events = []
        for name in event_names:
            prob = np.random.uniform(20, 90)
            change = np.random.normal(0, 5)

            events.append({
                'name': name,
                'probability': prob,
                'change': change
            })

        return events
