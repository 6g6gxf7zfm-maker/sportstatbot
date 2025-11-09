"""
Radar Chart Visualizations
Feature #31: Radar comparison cards for any two players
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class PlayerRadarComparison(BaseVisualization):
    """
    Feature #31: Radar comparison cards for any two players

    Interactive radar charts comparing player statistics.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create player comparison radar chart

        Args:
            data: Dictionary containing:
                - player1: {name, stats: {category: value}}
                - player2: {name, stats: {category: value}}
                - categories: List of stat categories

        Returns:
            Plotly Figure
        """
        player1 = data.get('player1', {})
        player2 = data.get('player2', {})
        categories = data.get('categories', [])

        if not player1 or not player2:
            player1, player2, categories = self._generate_sample_players()

        self.title = f"{player1['name']} vs {player2['name']}"

        # Extract stats
        stats1 = [player1['stats'].get(cat, 0) for cat in categories]
        stats2 = [player2['stats'].get(cat, 0) for cat in categories]

        # Create figure
        self.fig = go.Figure()

        # Add Player 1
        self.fig.add_trace(go.Scatterpolar(
            r=stats1 + [stats1[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0, 200, 83, 0.3)',
            line=dict(color=self.colors.WIN, width=3),
            name=player1['name'],
            hovertemplate=(
                f"<b>{player1['name']}</b><br>"
                "%{theta}: %{r:.1f}<br>"
                "<extra></extra>"
            )
        ))

        # Add Player 2
        self.fig.add_trace(go.Scatterpolar(
            r=stats2 + [stats2[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(33, 150, 243, 0.3)',
            line=dict(color='#2196F3', width=3),
            name=player2['name'],
            hovertemplate=(
                f"<b>{player2['name']}</b><br>"
                "%{theta}: %{r:.1f}<br>"
                "<extra></extra>"
            )
        ))

        # Update layout for radar
        layout = self._get_layout_template()
        layout.update({
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, 100],
                    'showticklabels': True,
                    'tickfont': {'size': 12}
                },
                'angularaxis': {
                    'tickfont': {'size': 14, 'family': 'Arial Black'}
                },
                'bgcolor': self.colors.BG_DARK if self.dark_mode else 'rgba(240, 240, 240, 0.3)'
            },
            'showlegend': True,
            'legend': {
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.2,
                'xanchor': 'center',
                'x': 0.5,
                'font': {'size': 14, 'family': 'Arial Black'}
            }
        })

        self.fig.update_layout(**layout)

        # Add stat comparison table below
        self._add_comparison_annotations(player1, player2, categories, stats1, stats2)

        return self.fig

    def _add_comparison_annotations(
        self,
        player1: Dict,
        player2: Dict,
        categories: List[str],
        stats1: List[float],
        stats2: List[float]
    ):
        """Add comparison annotations showing who leads in each category"""

        # Create summary text
        p1_leads = sum(1 for s1, s2 in zip(stats1, stats2) if s1 > s2)
        p2_leads = sum(1 for s1, s2 in zip(stats1, stats2) if s2 > s1)

        summary = f"{player1['name']}: {p1_leads} categories | {player2['name']}: {p2_leads} categories"

        self.fig.add_annotation(
            text=summary,
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.15,
            showarrow=False,
            font=dict(size=14, family='Arial Black'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=2
        )

    def _generate_sample_players(self) -> tuple:
        """Generate sample player data"""
        np.random.seed(42)

        categories = [
            'Passing Yards',
            'Touchdowns',
            'Completion %',
            'QB Rating',
            'Yards/Attempt',
            'Big Plays'
        ]

        player1 = {
            'name': 'Patrick Mahomes',
            'stats': {
                'Passing Yards': 85,
                'Touchdowns': 92,
                'Completion %': 78,
                'QB Rating': 90,
                'Yards/Attempt': 82,
                'Big Plays': 88
            }
        }

        player2 = {
            'name': 'Josh Allen',
            'stats': {
                'Passing Yards': 82,
                'Touchdowns': 88,
                'Completion %': 75,
                'QB Rating': 85,
                'Yards/Attempt': 85,
                'Big Plays': 90
            }
        }

        return player1, player2, categories
