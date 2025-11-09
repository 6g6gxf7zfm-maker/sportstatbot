"""
GIF Exporter for Play Sequences
Feature #49: Play-sequence animation export to GIF
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Any
import imageio
import os

from ..core.colors import ColorScheme


class PlaySequenceGIF:
    """
    Feature #49: Play-sequence animation export to GIF

    Exports play-by-play sequences as animated GIFs.
    """

    def __init__(self):
        self.colors = ColorScheme()

    def create_gif(
        self,
        data: Dict[str, Any],
        filename: str = 'play_sequence',
        fps: int = 2,
        output_dir: str = 'visualizations/output'
    ) -> str:
        """
        Create GIF from play sequence

        Args:
            data: Dictionary containing:
                - plays: List of {frame_num, player_positions: [{x, y, team, player_id}], event_desc}
                - field_type: 'football', 'basketball', 'soccer'
                - team_a_name: Team A name
                - team_b_name: Team B name
            filename: Output filename
            fps: Frames per second
            output_dir: Output directory

        Returns:
            Path to GIF file
        """
        plays = data.get('plays', [])
        field_type = data.get('field_type', 'football')
        team_a = data.get('team_a_name', 'Team A')
        team_b = data.get('team_b_name', 'Team B')

        if not plays:
            plays = self._generate_sample_plays(field_type)

        os.makedirs(output_dir, exist_ok=True)
        gif_path = os.path.join(output_dir, f"{filename}.gif")

        # Generate frames
        frames = []

        for play in plays:
            frame = self._create_frame(
                play,
                field_type,
                team_a,
                team_b
            )
            frames.append(frame)

        # Save as GIF
        imageio.mimsave(
            gif_path,
            frames,
            fps=fps,
            loop=0
        )

        return gif_path

    def _create_frame(
        self,
        play: Dict,
        field_type: str,
        team_a: str,
        team_b: str
    ) -> np.ndarray:
        """Create single frame for the GIF"""

        fig, ax = plt.subplots(figsize=(12, 6))

        # Draw field
        if field_type == 'football':
            self._draw_football_field(ax)
            field_length, field_width = 120, 53.3
        elif field_type == 'basketball':
            self._draw_basketball_court(ax)
            field_length, field_width = 94, 50
        else:  # soccer
            self._draw_soccer_pitch(ax)
            field_length, field_width = 105, 68

        # Draw player positions
        positions = play.get('player_positions', [])

        for pos in positions:
            x, y = pos['x'], pos['y']
            team = pos['team']
            player_id = pos.get('player_id', '')

            color = self.colors.get_team_color(
                team_a[:3] if team == 'A' else team_b[:3]
            )

            # Draw player circle
            circle = mpatches.Circle(
                (x, y),
                radius=2,
                facecolor=color,
                edgecolor='white',
                linewidth=2,
                zorder=10
            )
            ax.add_patch(circle)

            # Add player ID
            ax.text(
                x, y,
                str(player_id),
                color='white',
                fontsize=10,
                fontweight='bold',
                ha='center',
                va='center',
                zorder=11
            )

        # Add event description
        event_desc = play.get('event_desc', '')
        ax.text(
            field_length / 2,
            field_width + 3,
            event_desc,
            fontsize=14,
            fontweight='bold',
            ha='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        # Set limits
        ax.set_xlim(-5, field_length + 5)
        ax.set_ylim(-5, field_width + 5)
        ax.set_aspect('equal')
        ax.axis('off')

        # Convert to image
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)

        return frame

    def _draw_football_field(self, ax):
        """Draw simplified football field"""
        # Field outline
        field = mpatches.Rectangle(
            (0, 0), 120, 53.3,
            linewidth=2,
            edgecolor='white',
            facecolor='green',
            alpha=0.3
        )
        ax.add_patch(field)

        # Yard lines
        for yard in range(10, 110, 10):
            ax.plot([yard, yard], [0, 53.3], 'w-', linewidth=1)

    def _draw_basketball_court(self, ax):
        """Draw simplified basketball court"""
        court = mpatches.Rectangle(
            (0, 0), 94, 50,
            linewidth=2,
            edgecolor='black',
            facecolor='tan',
            alpha=0.3
        )
        ax.add_patch(court)

        # Center line
        ax.plot([47, 47], [0, 50], 'k-', linewidth=2)

    def _draw_soccer_pitch(self, ax):
        """Draw simplified soccer pitch"""
        pitch = mpatches.Rectangle(
            (0, 0), 105, 68,
            linewidth=2,
            edgecolor='white',
            facecolor='green',
            alpha=0.3
        )
        ax.add_patch(pitch)

        # Center line
        ax.plot([52.5, 52.5], [0, 68], 'w-', linewidth=2)

    def _generate_sample_plays(self, field_type: str) -> List[Dict]:
        """Generate sample play sequence"""
        np.random.seed(42)

        if field_type == 'football':
            field_length, field_width = 120, 53.3
        elif field_type == 'basketball':
            field_length, field_width = 94, 50
        else:
            field_length, field_width = 105, 68

        plays = []

        # Generate 10 frames
        for frame in range(10):
            positions = []

            # Team A players
            for i in range(5):
                positions.append({
                    'x': np.random.uniform(10, field_length - 10),
                    'y': np.random.uniform(10, field_width - 10),
                    'team': 'A',
                    'player_id': i + 1
                })

            # Team B players
            for i in range(5):
                positions.append({
                    'x': np.random.uniform(10, field_length - 10),
                    'y': np.random.uniform(10, field_width - 10),
                    'team': 'B',
                    'player_id': i + 1
                })

            plays.append({
                'frame_num': frame,
                'player_positions': positions,
                'event_desc': f'Frame {frame + 1}/10'
            })

        return plays
