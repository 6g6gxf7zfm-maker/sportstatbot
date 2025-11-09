"""
Tree Map Visualizations
Feature #33: Tree map of lineup usage share
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class LineupTreeMap(BaseVisualization):
    """
    Feature #33: Tree map of lineup usage share

    Visualizes player lineup combinations and usage percentages.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create lineup usage tree map

        Args:
            data: Dictionary containing:
                - lineups: List of {
                    players: [list of player names],
                    minutes: float,
                    plus_minus: float,
                    games: int
                  }
                - team_name: Team name

        Returns:
            Plotly Figure
        """
        lineups = data.get('lineups', [])
        team_name = data.get('team_name', 'Team')

        if not lineups:
            lineups = self._generate_sample_lineups()

        self.title = f"{team_name} Lineup Usage"

        # Prepare data for treemap
        labels = []
        parents = []
        values = []
        colors = []
        hover_text = []

        # Root
        total_minutes = sum(l['minutes'] for l in lineups)
        labels.append(team_name)
        parents.append("")
        values.append(total_minutes)
        colors.append(0)
        hover_text.append(f"Total: {total_minutes:.0f} min")

        # Group by position or lineup size
        for i, lineup in enumerate(sorted(lineups, key=lambda x: x['minutes'], reverse=True)[:20]):
            lineup_name = f"Lineup {i+1}"
            player_str = ", ".join(lineup['players'][:3])  # Show first 3 players

            if len(lineup['players']) > 3:
                player_str += f" +{len(lineup['players']) - 3} more"

            labels.append(lineup_name)
            parents.append(team_name)
            values.append(lineup['minutes'])

            # Color based on plus/minus
            colors.append(lineup['plus_minus'])

            # Hover text
            usage_pct = (lineup['minutes'] / total_minutes) * 100
            hover_text.append(
                f"<b>{player_str}</b><br>"
                f"Minutes: {lineup['minutes']:.1f}<br>"
                f"Usage: {usage_pct:.1f}%<br>"
                f"Plus/Minus: {lineup['plus_minus']:+.1f}<br>"
                f"Games: {lineup['games']}"
            )

        # Create treemap
        self.fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(
                colorscale='RdYlGn',
                cmid=0,
                colorbar=dict(title="Plus/Minus"),
                line=dict(width=2, color='white')
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            textposition='middle center',
            marker_colors=colors
        ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'height': 600
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_lineups(self) -> List[Dict]:
        """Generate sample lineup data"""
        np.random.seed(42)

        players_pool = [
            'Curry', 'Thompson', 'Green', 'Wiggins', 'Looney',
            'Payton', 'Poole', 'Kuminga', 'Moody', 'DiVincenzo'
        ]

        lineups = []

        # Generate various lineup combinations
        for _ in range(30):
            n_players = np.random.choice([3, 4, 5], p=[0.2, 0.3, 0.5])
            players = list(np.random.choice(players_pool, size=n_players, replace=False))

            minutes = np.random.uniform(5, 120)
            plus_minus = np.random.normal(0, 10)
            games = np.random.randint(1, 30)

            lineups.append({
                'players': players,
                'minutes': minutes,
                'plus_minus': plus_minus,
                'games': games
            })

        return lineups
