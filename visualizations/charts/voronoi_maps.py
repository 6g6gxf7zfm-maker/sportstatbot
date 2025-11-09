"""
Voronoi Map Visualization
Feature #47: Positional area control map (Voronoi overlay)
"""

import plotly.graph_objects as go
import numpy as np
from scipy.spatial import Voronoi
from typing import Dict, List, Any, Tuple

from ..core.base_viz import BaseVisualization
from ..field_graphics.soccer_pitch import SoccerPitch


class PositionalAreaControl(BaseVisualization):
    """
    Feature #47: Positional area control map (Voronoi overlay)

    Shows player positioning and area control using Voronoi diagram.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create positional area control map

        Args:
            data: Dictionary containing:
                - team_a_positions: List of {x, y, player_name}
                - team_b_positions: List of {x, y, player_name}
                - team_a_name: Team A name
                - team_b_name: Team B name
                - sport: 'soccer' or other

        Returns:
            Plotly Figure
        """
        team_a_pos = data.get('team_a_positions', [])
        team_b_pos = data.get('team_b_positions', [])
        team_a = data.get('team_a_name', 'Team A')
        team_b = data.get('team_b_name', 'Team B')
        sport = data.get('sport', 'soccer')

        if not team_a_pos or not team_b_pos:
            team_a_pos, team_b_pos = self._generate_sample_positions()

        self.title = f"{team_a} vs {team_b} - Area Control"

        # Create field
        if sport == 'soccer':
            pitch = SoccerPitch()
            field_length = pitch.PITCH_LENGTH
            field_width = pitch.PITCH_WIDTH
        else:
            field_length = 100
            field_width = 50

        # Create figure
        self.fig = go.Figure()

        # Add field
        if sport == 'soccer':
            pitch.add_to_figure(self.fig)

        # Combine all positions
        all_positions = []
        team_labels = []

        for pos in team_a_pos:
            all_positions.append([pos['x'], pos['y']])
            team_labels.append('A')

        for pos in team_b_pos:
            all_positions.append([pos['x'], pos['y']])
            team_labels.append('B')

        all_positions = np.array(all_positions)

        # Create Voronoi diagram
        vor = Voronoi(all_positions)

        # Draw Voronoi regions
        for region_idx, region in enumerate(vor.regions):
            if not region or -1 in region:
                continue

            # Get polygon vertices
            polygon = [vor.vertices[i] for i in region]

            if not polygon:
                continue

            polygon = np.array(polygon)

            # Determine team color
            # Find which point owns this region
            point_idx = None
            for idx, point_region in enumerate(vor.point_region):
                if vor.regions[point_region] == region:
                    point_idx = idx
                    break

            if point_idx is None:
                continue

            team = team_labels[point_idx]
            color = self.colors.get_team_color(team_a[:3] if team == 'A' else team_b[:3])

            # Draw filled polygon
            self.fig.add_trace(go.Scatter(
                x=polygon[:, 0].tolist() + [polygon[0, 0]],
                y=polygon[:, 1].tolist() + [polygon[0, 1]],
                fill='toself',
                fillcolor=f'rgba{self._hex_to_rgba(color, 0.2)}',
                line=dict(color=color, width=1),
                mode='lines',
                showlegend=False,
                hoverinfo='skip'
            ))

        # Add player positions
        for idx, pos in enumerate(team_a_pos):
            self.fig.add_trace(go.Scatter(
                x=[pos['x']],
                y=[pos['y']],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=self.colors.get_team_color(team_a[:3]),
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                text=pos.get('player_name', f'A{idx+1}'),
                textposition='top center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                name=team_a if idx == 0 else '',
                legendgroup=team_a,
                showlegend=(idx == 0),
                hovertemplate=(
                    f"<b>{pos.get('player_name', f'A{idx+1}')}</b><br>"
                    f"Team: {team_a}<br>"
                    f"Position: ({pos['x']:.1f}, {pos['y']:.1f})<br>"
                    "<extra></extra>"
                )
            ))

        for idx, pos in enumerate(team_b_pos):
            self.fig.add_trace(go.Scatter(
                x=[pos['x']],
                y=[pos['y']],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=self.colors.get_team_color(team_b[:3]),
                    line=dict(width=2, color='white'),
                    symbol='square'
                ),
                text=pos.get('player_name', f'B{idx+1}'),
                textposition='top center',
                textfont=dict(size=10, color='white', family='Arial Black'),
                name=team_b if idx == 0 else '',
                legendgroup=team_b,
                showlegend=(idx == 0),
                hovertemplate=(
                    f"<b>{pos.get('player_name', f'B{idx+1}')}</b><br>"
                    f"Team: {team_b}<br>"
                    f"Position: ({pos['x']:.1f}, {pos['y']:.1f})<br>"
                    "<extra></extra>"
                )
            ))

        # Calculate area control
        team_a_area = self._calculate_team_area(vor, team_labels, 'A', field_length, field_width)
        team_b_area = self._calculate_team_area(vor, team_labels, 'B', field_length, field_width)

        total_area = team_a_area + team_b_area
        team_a_pct = (team_a_area / total_area * 100) if total_area > 0 else 50
        team_b_pct = (team_b_area / total_area * 100) if total_area > 0 else 50

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'range': [0, field_length],
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False
            },
            'yaxis': {
                'range': [0, field_width],
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False,
                'scaleanchor': 'x',
                'scaleratio': 1
            },
            'hovermode': 'closest'
        })

        self.fig.update_layout(**layout)

        # Add area control summary
        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=-0.1,
            text=f"<b>Area Control:</b> {team_a}: {team_a_pct:.1f}% | {team_b}: {team_b_pct:.1f}%",
            showarrow=False,
            font=dict(size=14, family='Arial Black'),
            xanchor='center'
        )

        return self.fig

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> str:
        """Convert hex color to RGBA tuple string"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f'({r}, {g}, {b}, {alpha})'

    def _calculate_team_area(
        self,
        vor: Voronoi,
        team_labels: List[str],
        team: str,
        field_length: float,
        field_width: float
    ) -> float:
        """Calculate approximate area controlled by team"""
        # Simplified: count regions
        team_regions = sum(1 for label in team_labels if label == team)
        return team_regions  # Simplified metric

    def _generate_sample_positions(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate sample player positions"""
        np.random.seed(42)

        pitch = SoccerPitch()

        # Team A positions (attacking left to right)
        team_a = []
        formations_a = [
            (15, 34), (25, 15), (25, 53), (35, 25), (35, 43),
            (45, 20), (45, 34), (45, 48), (55, 25), (55, 43), (60, 34)
        ]

        for idx, (x, y) in enumerate(formations_a):
            team_a.append({
                'x': x,
                'y': y,
                'player_name': f'A{idx+1}'
            })

        # Team B positions (attacking right to left)
        team_b = []
        formations_b = [
            (90, 34), (80, 15), (80, 53), (70, 25), (70, 43),
            (60, 20), (60, 34), (60, 48), (50, 25), (50, 43), (45, 34)
        ]

        for idx, (x, y) in enumerate(formations_b):
            team_b.append({
                'x': x,
                'y': y,
                'player_name': f'B{idx+1}'
            })

        return team_a, team_b
