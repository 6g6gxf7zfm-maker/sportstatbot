"""
Depth Chart Visualization
Feature #38: Depth-chart visualization that updates with injuries
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class DepthChartVisualization(BaseVisualization):
    """
    Feature #38: Depth-chart visualization that updates with injuries

    Interactive depth chart showing player positions and injury status.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create depth chart visualization

        Args:
            data: Dictionary containing:
                - positions: Dict of {position: [list of players with depth, status]}
                - team_name: Team name

        Returns:
            Plotly Figure
        """
        positions = data.get('positions', {})
        team_name = data.get('team_name', 'Team')

        if not positions:
            positions = self._generate_sample_depth_chart()

        self.title = f"{team_name} Depth Chart"

        # Create figure
        self.fig = go.Figure()

        # Colors for player status
        status_colors = {
            'healthy': self.colors.WIN,
            'questionable': self.colors.TIE,
            'out': self.colors.LOSS,
            'ir': '#666666'
        }

        # Layout positions
        position_order = list(positions.keys())
        n_positions = len(position_order)

        for pos_idx, position in enumerate(position_order):
            players = positions[position]

            for depth, player in enumerate(players):
                status = player.get('status', 'healthy')
                name = player['name']
                stats = player.get('stats', '')

                # Calculate position
                x = pos_idx
                y = -depth  # Depth 0 at top

                # Add player box
                color = status_colors.get(status, self.colors.NEUTRAL)

                # Marker style based on status
                if status == 'out' or status == 'ir':
                    opacity = 0.4
                    line_style = 'dash'
                else:
                    opacity = 1.0
                    line_style = 'solid'

                self.fig.add_trace(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    marker=dict(
                        size=80,
                        color=color,
                        opacity=opacity,
                        line=dict(width=3, color='white'),
                        symbol='square'
                    ),
                    text=name,
                    textposition='middle center',
                    textfont=dict(size=10, color='white', family='Arial Black'),
                    name=position if depth == 0 else '',
                    showlegend=False,
                    hovertemplate=(
                        f'<b>{name}</b><br>'
                        f'Position: {position}<br>'
                        f'Depth: {depth + 1}<br>'
                        f'Status: {status.upper()}<br>'
                        f'{stats}<br>'
                        '<extra></extra>'
                    )
                ))

                # Add status indicator
                status_text = ''
                if status == 'questionable':
                    status_text = '⚠️'
                elif status == 'out':
                    status_text = '❌'
                elif status == 'ir':
                    status_text = '🏥'

                if status_text:
                    self.fig.add_annotation(
                        x=x + 0.35,
                        y=y + 0.35,
                        text=status_text,
                        showarrow=False,
                        font=dict(size=16)
                    )

        # Add position labels
        for pos_idx, position in enumerate(position_order):
            self.fig.add_annotation(
                x=pos_idx,
                y=0.5,
                text=f'<b>{position}</b>',
                showarrow=False,
                font=dict(size=14, family='Arial Black'),
                yanchor='bottom'
            )

        # Add depth level labels
        max_depth = max(len(players) for players in positions.values())
        for depth in range(max_depth):
            self.fig.add_annotation(
                x=-0.8,
                y=-depth,
                text=f'{depth + 1}',
                showarrow=False,
                font=dict(size=12, color=self.colors.TEXT_MUTED)
            )

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'showgrid': False,
                'showticklabels': False,
                'zeroline': False,
                'range': [-1, n_positions]
            },
            'yaxis': {
                'showgrid': False,
                'showticklabels': False,
                'zeroline': False,
                'range': [-max_depth, 1],
                'scaleanchor': 'x'
            },
            'height': max(400, max_depth * 100 + 100),
            'hovermode': 'closest'
        })

        self.fig.update_layout(**layout)

        # Add legend for status
        self._add_status_legend()

        return self.fig

    def _add_status_legend(self):
        """Add legend explaining status indicators"""
        legend_text = (
            "Status: ✓ Healthy | ⚠️ Questionable | ❌ Out | 🏥 IR"
        )

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.1,
            text=legend_text,
            showarrow=False,
            font=dict(size=12),
            xanchor='center'
        )

    def _generate_sample_depth_chart(self) -> Dict:
        """Generate sample depth chart data"""
        np.random.seed(42)

        positions = {
            'QB': [
                {'name': 'Mahomes', 'status': 'healthy', 'stats': '300 YPG, 30 TD'},
                {'name': 'Backup QB', 'status': 'healthy', 'stats': ''}
            ],
            'RB': [
                {'name': 'RB1', 'status': 'healthy', 'stats': '1200 YDS, 12 TD'},
                {'name': 'RB2', 'status': 'questionable', 'stats': '600 YDS, 4 TD'},
                {'name': 'RB3', 'status': 'healthy', 'stats': '200 YDS'}
            ],
            'WR1': [
                {'name': 'WR1', 'status': 'healthy', 'stats': '1400 YDS, 14 TD'},
                {'name': 'WR4', 'status': 'healthy', 'stats': '400 YDS, 2 TD'}
            ],
            'WR2': [
                {'name': 'WR2', 'status': 'out', 'stats': '800 YDS, 6 TD'},
                {'name': 'WR5', 'status': 'healthy', 'stats': '300 YDS, 1 TD'}
            ],
            'TE': [
                {'name': 'Kelce', 'status': 'healthy', 'stats': '1100 YDS, 11 TD'},
                {'name': 'TE2', 'status': 'healthy', 'stats': '200 YDS, 2 TD'}
            ],
            'LT': [
                {'name': 'LT1', 'status': 'healthy', 'stats': 'Pro Bowl'},
                {'name': 'LT2', 'status': 'ir', 'stats': 'Injured Reserve'}
            ],
            'LG': [
                {'name': 'LG1', 'status': 'healthy', 'stats': ''},
                {'name': 'LG2', 'status': 'healthy', 'stats': ''}
            ],
            'C': [
                {'name': 'C1', 'status': 'questionable', 'stats': 'Ankle'},
                {'name': 'C2', 'status': 'healthy', 'stats': ''}
            ],
            'RG': [
                {'name': 'RG1', 'status': 'healthy', 'stats': ''},
                {'name': 'RG2', 'status': 'healthy', 'stats': ''}
            ],
            'RT': [
                {'name': 'RT1', 'status': 'healthy', 'stats': ''},
                {'name': 'RT2', 'status': 'healthy', 'stats': ''}
            ]
        }

        return positions
