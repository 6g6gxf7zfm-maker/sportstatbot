"""
Confidence Glow Visualization
Feature #46: Real-time confidence glow (color intensity = certainty)
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any

from ..core.base_viz import BaseVisualization


class ConfidenceGlow(BaseVisualization):
    """
    Feature #46: Real-time confidence glow (color intensity = certainty)

    Visualizes prediction confidence using color intensity and glow effects.
    """

    def create(
        self,
        data: Dict[str, Any],
        **kwargs
    ) -> go.Figure:
        """
        Create confidence glow visualization

        Args:
            data: Dictionary containing:
                - predictions: List of {name, value, confidence}

        Returns:
            Plotly Figure
        """
        predictions = data.get('predictions', [])

        if not predictions:
            predictions = self._generate_sample_predictions()

        self.title = "Prediction Confidence"

        # Create figure
        self.fig = go.Figure()

        # Sort by confidence
        predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)

        for idx, pred in enumerate(predictions):
            confidence = pred['confidence']
            value = pred['value']
            name = pred['name']

            # Color based on confidence
            color = self.colors.get_confidence_color(confidence)

            # Size based on confidence
            marker_size = 30 + (confidence * 50)

            # Glow effect using multiple overlapping markers
            for glow_layer in range(3):
                glow_size = marker_size + (glow_layer * 15)
                glow_opacity = (confidence / 3) * (1 - glow_layer * 0.3)

                self.fig.add_trace(go.Scatter(
                    x=[idx],
                    y=[value],
                    mode='markers',
                    marker=dict(
                        size=glow_size,
                        color=color,
                        opacity=glow_opacity
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Main marker with text
            self.fig.add_trace(go.Scatter(
                x=[idx],
                y=[value],
                mode='markers+text',
                marker=dict(
                    size=marker_size,
                    color=color,
                    line=dict(width=3, color='white')
                ),
                text=name,
                textposition='bottom center',
                textfont=dict(
                    size=12,
                    color='white',
                    family='Arial Black'
                ),
                name=name,
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    f"Value: {value:.1f}<br>"
                    f"Confidence: {confidence*100:.0f}%<br>"
                    "<extra></extra>"
                ),
                showlegend=False
            ))

        # Update layout
        layout = self._get_layout_template()
        layout.update({
            'xaxis': {
                'showgrid': False,
                'showticklabels': False,
                'zeroline': False
            },
            'yaxis': {
                'title': 'Prediction Value',
                'showgrid': True,
                'gridcolor': 'rgba(128, 128, 128, 0.2)'
            },
            'hovermode': 'closest',
            'plot_bgcolor': self.colors.BG_DARK if self.dark_mode else 'rgba(240, 240, 240, 0.5)'
        })

        self.fig.update_layout(**layout)

        # Add confidence legend
        self._add_confidence_legend()

        return self.fig

    def _add_confidence_legend(self):
        """Add legend explaining confidence levels"""

        legend_items = [
            "Very High (80-100%): Bright glow",
            "High (60-80%): Strong glow",
            "Medium (40-60%): Moderate glow",
            "Low (20-40%): Faint glow",
            "Very Low (0-20%): Minimal glow"
        ]

        legend_text = "<b>Confidence Levels:</b><br>" + "<br>".join(legend_items)

        self.fig.add_annotation(
            xref='paper',
            yref='paper',
            x=1.02,
            y=0.5,
            text=legend_text,
            showarrow=False,
            font=dict(size=10),
            align='left',
            xanchor='left',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1
        )

    def _generate_sample_predictions(self) -> list:
        """Generate sample prediction data"""
        np.random.seed(42)

        predictions = []

        for i in range(8):
            predictions.append({
                'name': f'Prediction {i+1}',
                'value': np.random.uniform(40, 90),
                'confidence': np.random.random()
            })

        return predictions
