"""
Score Worm Graph
Feature #32: Dynamic score worm graph across concurrent games
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Any

from ..core.base_viz import BaseVisualization


class ScoreWormGraph(BaseVisualization):
    """
    Feature #32: Dynamic score worm graph across concurrent games

    Shows score progression for multiple games simultaneously.
    """

    def create(self, data: Dict[str, Any], **kwargs) -> go.Figure:
        """
        Create score worm graph

        Args:
            data: Dictionary containing:
                - games: List of {
                    game_id, team_a, team_b,
                    scoring_plays: [{time, score_a, score_b, description}]
                  }

        Returns:
            Plotly Figure
        """
        games = data.get('games', [])

        if not games:
            games = self._generate_sample_games()

        self.title = "Live Score Tracker"

        # Create figure with subplots for each game
        n_games = len(games)
        self.fig = make_subplots(
            rows=n_games,
            cols=1,
            subplot_titles=[f"{g['team_a']} vs {g['team_b']}" for g in games],
            vertical_spacing=0.1
        )

        # Add worm for each game
        for idx, game in enumerate(games, 1):
            df = pd.DataFrame(game['scoring_plays'])

            # Team A score line
            self.fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['score_a'],
                    mode='lines+markers',
                    line=dict(color=self.colors.get_team_color(game['team_a'][:3]), width=3),
                    marker=dict(size=8),
                    name=game['team_a'],
                    legendgroup=f"game{idx}",
                    hovertemplate=(
                        f"<b>{game['team_a']}</b><br>"
                        "Time: %{x}<br>"
                        "Score: %{y}<br>"
                        "%{customdata}<br>"
                        "<extra></extra>"
                    ),
                    customdata=df['description'].values
                ),
                row=idx,
                col=1
            )

            # Team B score line
            self.fig.add_trace(
                go.Scatter(
                    x=df['time'],
                    y=df['score_b'],
                    mode='lines+markers',
                    line=dict(color=self.colors.get_team_color(game['team_b'][:3]), width=3),
                    marker=dict(size=8),
                    name=game['team_b'],
                    legendgroup=f"game{idx}",
                    hovertemplate=(
                        f"<b>{game['team_b']}</b><br>"
                        "Time: %{x}<br>"
                        "Score: %{y}<br>"
                        "%{customdata}<br>"
                        "<extra></extra>"
                    ),
                    customdata=df['description'].values
                ),
                row=idx,
                col=1
            )

            # Update axes for this subplot
            self.fig.update_xaxes(
                title_text="Game Time (min)" if idx == n_games else "",
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                row=idx,
                col=1
            )

            self.fig.update_yaxes(
                title_text="Score",
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                row=idx,
                col=1
            )

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'height': 300 * n_games,
            'hovermode': 'x unified',
            'showlegend': True
        })

        self.fig.update_layout(**layout)

        return self.fig

    def _generate_sample_games(self) -> List[Dict]:
        """Generate sample concurrent games"""
        np.random.seed(42)

        games = [
            {
                'game_id': 1,
                'team_a': 'Chiefs',
                'team_b': 'Bills',
                'scoring_plays': self._generate_scoring_plays()
            },
            {
                'game_id': 2,
                'team_a': '49ers',
                'team_b': 'Eagles',
                'scoring_plays': self._generate_scoring_plays()
            },
            {
                'game_id': 3,
                'team_a': 'Cowboys',
                'team_b': 'Ravens',
                'scoring_plays': self._generate_scoring_plays()
            }
        ]

        return games

    def _generate_scoring_plays(self) -> List[Dict]:
        """Generate scoring plays for a game"""
        plays = []

        time = 0
        score_a = 0
        score_b = 0

        play_types = ['TD', 'FG', 'Safety']
        descriptions = {
            'TD': 'Touchdown',
            'FG': 'Field Goal',
            'Safety': 'Safety'
        }
        points = {
            'TD': 7,
            'FG': 3,
            'Safety': 2
        }

        # Start with 0-0
        plays.append({
            'time': 0,
            'score_a': 0,
            'score_b': 0,
            'description': 'Kickoff'
        })

        for _ in range(15):
            time += np.random.uniform(3, 12)

            # Random team scores
            if np.random.random() < 0.5:
                play_type = np.random.choice(play_types, p=[0.6, 0.35, 0.05])
                score_a += points[play_type]
                desc = f"Team A - {descriptions[play_type]}"
            else:
                play_type = np.random.choice(play_types, p=[0.6, 0.35, 0.05])
                score_b += points[play_type]
                desc = f"Team B - {descriptions[play_type]}"

            plays.append({
                'time': time,
                'score_a': score_a,
                'score_b': score_b,
                'description': desc
            })

        return plays
