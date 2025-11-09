"""
Progress Bar Visualization
Feature #41: Season progress bar with milestones
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class SeasonProgressBar(BaseVisualization):
    """
    Feature #41: Season progress bar with milestones

    Shows season progression with key milestones and achievements.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create season progress bar

        Args:
            data: Dictionary containing:
                - team_name: Team name
                - current_week: Current week number
                - total_weeks: Total weeks in season
                - milestones: List of {week, title, description, achieved}
                - record: Team record {wins, losses, ties}

        Returns:
            Plotly Figure
        """
        team_name = data.get('team_name', 'Team')
        current_week = data.get('current_week', 10)
        total_weeks = data.get('total_weeks', 18)
        milestones = data.get('milestones', [])
        record = data.get('record', {'wins': 7, 'losses': 3, 'ties': 0})

        if not milestones:
            milestones = self._generate_sample_milestones(total_weeks)

        self.title = f"{team_name} Season Progress"

        progress_pct = (current_week / total_weeks) * 100

        # Create figure
        self.fig = go.Figure()

        # Main progress bar
        self.fig.add_trace(go.Bar(
            x=[progress_pct],
            y=['Season'],
            orientation='h',
            marker=dict(
                color=self.colors.WIN,
                line=dict(color=self.colors.WIN, width=2)
            ),
            text=f"Week {current_week}/{total_weeks}",
            textposition='inside',
            textfont=dict(size=16, color='white', family='Arial Black'),
            hovertemplate=(
                f'<b>Week {current_week} of {total_weeks}</b><br>'
                f'{progress_pct:.1f}% Complete<br>'
                f'Record: {record["wins"]}-{record["losses"]}'
                f'{"-" + str(record["ties"]) if record["ties"] > 0 else ""}<br>'
                '<extra></extra>'
            ),
            showlegend=False
        ))

        # Remaining season (gray)
        self.fig.add_trace(go.Bar(
            x=[100 - progress_pct],
            y=['Season'],
            orientation='h',
            marker=dict(
                color='rgba(200, 200, 200, 0.3)',
                line=dict(color='gray', width=2)
            ),
            text=f"{total_weeks - current_week} weeks left",
            textposition='inside',
            textfont=dict(size=12, color='gray'),
            hoverinfo='skip',
            showlegend=False
        ))

        # Add milestone markers
        for milestone in milestones:
            week = milestone['week']
            milestone_pct = (week / total_weeks) * 100

            # Marker position
            marker_color = self.colors.WIN if milestone.get('achieved') else self.colors.TIE
            marker_symbol = 'star' if milestone.get('achieved') else 'circle'

            self.fig.add_trace(go.Scatter(
                x=[milestone_pct],
                y=['Season'],
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=marker_color,
                    symbol=marker_symbol,
                    line=dict(width=2, color='white')
                ),
                text=f"Wk{week}",
                textposition='top center',
                textfont=dict(size=10),
                name=milestone['title'],
                hovertemplate=(
                    f"<b>{milestone['title']}</b><br>"
                    f"Week {week}<br>"
                    f"{milestone['description']}<br>"
                    f"Status: {'✓ Achieved' if milestone.get('achieved') else 'Upcoming'}<br>"
                    '<extra></extra>'
                ),
                showlegend=False
            ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': 'Season Progress (%)',
                'range': [0, 100],
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)',
                'ticksuffix': '%'
            },
            'yaxis': {
                'showticklabels': False,
                'showgrid': False
            },
            'barmode': 'stack',
            'height': 400,
            'hovermode': 'closest'
        })

        self.fig.update_layout(**layout)

        # Add record summary
        record_text = (
            f"Record: {record['wins']}-{record['losses']}"
            f"{'-' + str(record['ties']) if record['ties'] > 0 else ''}"
        )

        win_pct = record['wins'] / (record['wins'] + record['losses'] + record['ties'])

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.15,
            text=f"{record_text} ({win_pct:.3f})",
            showarrow=False,
            font=dict(size=18, family='Arial Black'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor=self.colors.WIN if win_pct > 0.5 else self.colors.LOSS,
            borderwidth=2
        )

        # Add milestone legend
        self._add_milestone_list(milestones, current_week)

        return self.fig

    def _add_milestone_list(self, milestones: List[Dict], current_week: int):
        """Add list of milestones below the progress bar"""

        upcoming = [m for m in milestones if m['week'] >= current_week and not m.get('achieved')]
        achieved = [m for m in milestones if m.get('achieved')]

        milestone_text = "<b>Milestones:</b><br>"

        if achieved:
            milestone_text += "✓ Achieved: " + ", ".join(f"{m['title']} (Wk{m['week']})" for m in achieved[:3]) + "<br>"

        if upcoming:
            milestone_text += "◯ Upcoming: " + ", ".join(f"{m['title']} (Wk{m['week']})" for m in upcoming[:3])

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.25,
            text=milestone_text,
            showarrow=False,
            font=dict(size=12),
            xanchor='center',
            align='center'
        )

    def _generate_sample_milestones(self, total_weeks: int) -> List[Dict]:
        """Generate sample milestones"""
        np.random.seed(42)

        milestones = [
            {'week': 4, 'title': 'First Quarter', 'description': '25% of season', 'achieved': True},
            {'week': 6, 'title': '.500 Record', 'description': 'Break even', 'achieved': True},
            {'week': 9, 'title': 'Midseason', 'description': '50% of season', 'achieved': True},
            {'week': 12, 'title': 'Playoff Push', 'description': 'Must-win games', 'achieved': False},
            {'week': 14, 'title': 'Clinch Spot', 'description': 'Playoff berth', 'achieved': False},
            {'week': 17, 'title': 'Regular Season End', 'description': 'Final standings', 'achieved': False}
        ]

        return milestones
