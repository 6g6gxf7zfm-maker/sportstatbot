"""
Scatter Plot Visualizations
Feature #29: Dual-axis "luck vs skill" scatter dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class LuckVsSkillScatter(BaseVisualization):
    """
    Feature #29: Dual-axis "luck vs skill" scatter dashboard

    Visualizes teams/players on luck vs skill axes with quadrant analysis.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create luck vs skill scatter plot

        Args:
            data: Dictionary containing:
                - teams: List of {name, luck_score, skill_score, wins, losses, expected_wins}

        Returns:
            Plotly Figure
        """
        teams = data.get('teams', [])

        if not teams:
            teams = self._generate_sample_teams()

        self.title = "Luck vs Skill Analysis"

        df = pd.DataFrame(teams)

        # Create scatter plot
        self.fig = go.Figure()

        # Add scatter points
        self.fig.add_trace(go.Scatter(
            x=df['skill_score'],
            y=df['luck_score'],
            mode='markers+text',
            marker=dict(
                size=df['wins'] * 2,  # Size based on wins
                color=df['wins'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Wins"),
                line=dict(width=2, color='white')
            ),
            text=df['name'],
            textposition='top center',
            textfont=dict(size=10),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Skill Score: %{x:.2f}<br>"
                "Luck Score: %{y:.2f}<br>"
                "Record: %{customdata[0]}-%{customdata[1]}<br>"
                "Expected Wins: %{customdata[2]:.1f}<br>"
                "Luck Factor: %{customdata[3]:.1f}<br>"
                "<extra></extra>"
            ),
            customdata=df[['wins', 'losses', 'expected_wins', 'luck_factor']].values
        ))

        # Add quadrant lines
        skill_median = df['skill_score'].median()
        luck_median = df['luck_score'].median()

        # Vertical line (skill median)
        self.fig.add_vline(
            x=skill_median,
            line_dash="dash",
            line_color="gray",
            line_width=2
        )

        # Horizontal line (luck median)
        self.fig.add_hline(
            y=luck_median,
            line_dash="dash",
            line_color="gray",
            line_width=2
        )

        # Add quadrant labels
        quadrants = [
            {'x': 0.25, 'y': 0.75, 'text': 'Lucky & Good', 'color': self.colors.WIN},
            {'x': 0.75, 'y': 0.75, 'text': 'Skilled & Lucky', 'color': self.colors.WIN},
            {'x': 0.25, 'y': 0.25, 'text': 'Unlucky & Poor', 'color': self.colors.LOSS},
            {'x': 0.75, 'y': 0.25, 'text': 'Skilled but Unlucky', 'color': self.colors.TIE}
        ]

        for quad in quadrants:
            self.fig.add_annotation(
                xref='paper',
                yref='paper',
                x=quad['x'],
                y=quad['y'],
                text=quad['text'],
                showarrow=False,
                font=dict(size=14, color=quad['color']),
                bgcolor='rgba(255, 255, 255, 0.7)',
                bordercolor=quad['color'],
                borderwidth=2
            )

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'title': 'Skill Score (Expected Performance) →',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)',
                'zeroline': False
            },
            'yaxis': {
                'title': 'Luck Score (Actual vs Expected) →',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)',
                'zeroline': False
            },
            'hovermode': 'closest'
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_teams(self) -> List[Dict]:
        """Generate sample team data"""
        np.random.seed(42)

        team_names = [
            'Chiefs', 'Bills', '49ers', 'Eagles', 'Cowboys',
            'Ravens', 'Bengals', 'Dolphins', 'Packers', 'Vikings',
            'Lions', 'Giants', 'Patriots', 'Rams', 'Seahawks', 'Cardinals'
        ]

        teams = []
        for name in team_names:
            skill_score = np.random.uniform(30, 95)
            expected_wins = skill_score / 100 * 17  # 17 game season

            # Luck factor: how much actual wins differ from expected
            luck_factor = np.random.normal(0, 2)
            actual_wins = int(np.clip(expected_wins + luck_factor, 0, 17))

            # Luck score based on wins above/below expected
            luck_score = (actual_wins - expected_wins) * 10 + 50

            teams.append({
                'name': name,
                'skill_score': skill_score,
                'luck_score': luck_score,
                'wins': actual_wins,
                'losses': 17 - actual_wins,
                'expected_wins': expected_wins,
                'luck_factor': luck_factor
            })

        return teams
