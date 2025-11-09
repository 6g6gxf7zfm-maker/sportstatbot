"""
Flow Diagram Visualizations
Feature #34: Turnover flow diagram showing possession chains
Feature #40: Ball-movement chord diagrams
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class TurnoverFlowDiagram(BaseVisualization):
    """
    Feature #34: Turnover flow diagram showing possession chains

    Sankey diagram showing how possessions flow between teams and result in turnovers.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create turnover flow diagram

        Args:
            data: Dictionary containing:
                - turnovers: List of {from_team, to_team, turnover_type, count}
                - team_a_name: Team A name
                - team_b_name: Team B name

        Returns:
            Plotly Figure
        """
        turnovers = data.get('turnovers', [])
        team_a = data.get('team_a_name', 'Team A')
        team_b = data.get('team_b_name', 'Team B')

        if not turnovers:
            turnovers = self._generate_sample_turnovers(team_a, team_b)

        self.title = f"{team_a} vs {team_b} - Turnover Flow"

        # Build Sankey diagram data
        df = pd.DataFrame(turnovers)

        # Create node labels
        node_labels = [
            f"{team_a} Possession",
            f"{team_b} Possession",
            "Interception",
            "Fumble",
            "Turnover on Downs",
            "Punt",
            f"{team_a} Score",
            f"{team_b} Score"
        ]

        # Map to node indices
        node_map = {label: idx for idx, label in enumerate(node_labels)}

        # Build links
        sources = []
        targets = []
        values = []
        labels = []

        for _, row in df.iterrows():
            source = node_map.get(row['source'], 0)
            target = node_map.get(row['target'], 1)

            sources.append(source)
            targets.append(target)
            values.append(row['count'])
            labels.append(f"{row['count']} {row.get('label', '')}")

        # Create Sankey
        self.fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=node_labels,
                color=[
                    self.colors.get_team_color(team_a[:3]),
                    self.colors.get_team_color(team_b[:3]),
                    self.colors.LOSS,
                    self.colors.LOSS,
                    self.colors.TIE,
                    self.colors.NEUTRAL,
                    self.colors.WIN,
                    self.colors.WIN
                ]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                label=labels,
                color='rgba(150, 150, 150, 0.3)',
                hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>'
            )
        )])

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'height': 600
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_turnovers(self, team_a: str, team_b: str) -> List[Dict]:
        """Generate sample turnover data"""
        np.random.seed(42)

        turnovers = [
            # Team A possessions
            {'source': f'{team_a} Possession', 'target': 'Interception', 'count': 2, 'label': 'INTs'},
            {'source': f'{team_a} Possession', 'target': 'Fumble', 'count': 1, 'label': 'Fumbles'},
            {'source': f'{team_a} Possession', 'target': 'Punt', 'count': 5, 'label': 'Punts'},
            {'source': f'{team_a} Possession', 'target': f'{team_a} Score', 'count': 4, 'label': 'TDs/FGs'},

            # Team B possessions
            {'source': f'{team_b} Possession', 'target': 'Interception', 'count': 1, 'label': 'INTs'},
            {'source': f'{team_b} Possession', 'target': 'Fumble', 'count': 2, 'label': 'Fumbles'},
            {'source': f'{team_b} Possession', 'target': 'Punt', 'count': 6, 'label': 'Punts'},
            {'source': f'{team_b} Possession', 'target': f'{team_b} Score', 'count': 3, 'label': 'TDs/FGs'},

            # Turnovers lead to possessions
            {'source': 'Interception', 'target': f'{team_b} Possession', 'count': 2, 'label': 'to B'},
            {'source': 'Interception', 'target': f'{team_a} Possession', 'count': 1, 'label': 'to A'},
            {'source': 'Fumble', 'target': f'{team_a} Possession', 'count': 2, 'label': 'recovered'},
            {'source': 'Fumble', 'target': f'{team_b} Possession', 'count': 1, 'label': 'recovered'},
            {'source': 'Punt', 'target': f'{team_b} Possession', 'count': 5, 'label': ''},
            {'source': 'Punt', 'target': f'{team_a} Possession', 'count': 6, 'label': ''}
        ]

        return turnovers


class BallMovementChord(BaseVisualization):
    """
    Feature #40: Ball-movement chord diagrams

    Shows passing/ball movement patterns between players.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create ball movement chord diagram

        Args:
            data: Dictionary containing:
                - passes: List of {from_player, to_player, count, success_rate}
                - team_name: Team name

        Returns:
            Plotly Figure
        """
        passes = data.get('passes', [])
        team_name = data.get('team_name', 'Team')

        if not passes:
            passes = self._generate_sample_passes()

        self.title = f"{team_name} Ball Movement Network"

        df = pd.DataFrame(passes)

        # Get unique players
        players = list(set(df['from_player'].unique()) | set(df['to_player'].unique()))
        player_map = {player: idx for idx, player in enumerate(players)}

        # Build chord data
        sources = [player_map[p] for p in df['from_player']]
        targets = [player_map[p] for p in df['to_player']]
        values = df['count'].values

        # Create Sankey (chord-like visualization)
        self.fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=players,
                color=[self.colors.get_probability_gradient(np.random.random())
                       for _ in players]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(100, 149, 237, 0.3)',
                hovertemplate=(
                    '%{source.label} → %{target.label}<br>'
                    'Passes: %{value}<br>'
                    '<extra></extra>'
                )
            )
        )])

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'height': 700
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_passes(self) -> List[Dict]:
        """Generate sample passing data"""
        np.random.seed(42)

        players = ['Curry', 'Thompson', 'Green', 'Wiggins', 'Looney']

        passes = []
        for from_player in players:
            for to_player in players:
                if from_player != to_player:
                    count = np.random.randint(5, 30)
                    success_rate = np.random.uniform(0.7, 0.95)

                    passes.append({
                        'from_player': from_player,
                        'to_player': to_player,
                        'count': count,
                        'success_rate': success_rate
                    })

        return passes
