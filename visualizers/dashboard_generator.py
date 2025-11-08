"""
Dashboard Generator
===================
Generate HTML dashboards with embedded charts and interactive elements.
"""

import os
import base64
from datetime import datetime
from jinja2 import Template
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class DashboardGenerator:
    """Generator for HTML dashboards with visualizations."""

    def __init__(self, output_dir='dashboards'):
        """
        Initialize dashboard generator.

        Args:
            output_dir: Directory to save dashboard files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_full_dashboard(self, dashboard_data, filename=None):
        """
        Generate a complete HTML dashboard with all charts.

        Args:
            dashboard_data: Dict with all dashboard sections and data
                           {
                               'title': 'SportStatBot Dashboard',
                               'subtitle': 'Daily Sports Analysis',
                               'charts': [list of chart file paths],
                               'tables': [list of data tables],
                               'metrics': {dict of key metrics}
                           }
            filename: Output HTML filename

        Returns:
            str: Path to saved dashboard
        """
        if filename is None:
            filename = f'dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

        filepath = os.path.join(self.output_dir, filename)

        # Create HTML content
        html_content = self._create_html_template(dashboard_data)

        # Write to file
        with open(filepath, 'w') as f:
            f.write(html_content)

        return filepath

    def _create_html_template(self, data):
        """Create HTML template for dashboard."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', 'Helvetica', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            color: #1e3c72;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.2em;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 10px;
        }

        .metric-label {
            font-size: 1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .chart-container img {
            width: 100%;
            height: auto;
            border-radius: 5px;
        }

        .chart-container h3 {
            color: #1e3c72;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #2a5298;
        }

        .table-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: #2a5298;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }

        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        tr:hover {
            background: #f5f5f5;
        }

        .footer {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            color: #666;
            margin-top: 30px;
        }

        .timestamp {
            font-size: 0.9em;
            color: #999;
        }

        .interactive-chart {
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="header">
            <h1>{{ title }}</h1>
            <p>{{ subtitle }}</p>
            <p class="timestamp">Generated: {{ timestamp }}</p>
        </div>

        <!-- Key Metrics -->
        {% if metrics %}
        <div class="metrics-grid">
            {% for metric_name, metric_value in metrics.items() %}
            <div class="metric-card">
                <div class="metric-value">{{ metric_value }}</div>
                <div class="metric-label">{{ metric_name }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Interactive Charts -->
        {% if interactive_charts %}
        <div class="interactive-chart">
            {% for chart_html in interactive_charts %}
            {{ chart_html | safe }}
            {% endfor %}
        </div>
        {% endif %}

        <!-- Static Charts Grid -->
        {% if charts %}
        <div class="chart-grid">
            {% for chart in charts %}
            <div class="chart-container">
                <h3>{{ chart.title }}</h3>
                <img src="{{ chart.path }}" alt="{{ chart.title }}">
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Data Tables -->
        {% if tables %}
        {% for table in tables %}
        <div class="table-container">
            <h3>{{ table.title }}</h3>
            <table>
                <thead>
                    <tr>
                        {% for header in table.headers %}
                        <th>{{ header }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in table.rows %}
                    <tr>
                        {% for cell in row %}
                        <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endfor %}
        {% endif %}

        <!-- Footer -->
        <div class="footer">
            <p><strong>SportStatBot</strong> - Expert Sports Analysis & Visualization</p>
            <p class="timestamp">Dashboard auto-updates daily</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)

        # Prepare data for template
        template_data = {
            'title': data.get('title', 'SportStatBot Dashboard'),
            'subtitle': data.get('subtitle', 'Comprehensive Sports Analytics'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': data.get('metrics', {}),
            'charts': data.get('charts', []),
            'tables': data.get('tables', []),
            'interactive_charts': data.get('interactive_charts', [])
        }

        return template.render(**template_data)

    def create_interactive_line_chart(self, x_data, y_data, title, x_label, y_label):
        """
        Create an interactive Plotly line chart.

        Args:
            x_data: X-axis data
            y_data: Y-axis data (can be dict for multiple lines)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            str: HTML string for the chart
        """
        fig = go.Figure()

        if isinstance(y_data, dict):
            for name, values in y_data.items():
                fig.add_trace(go.Scatter(x=x_data, y=values, mode='lines+markers',
                                       name=name, line=dict(width=3)))
        else:
            fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines+markers',
                                   line=dict(width=3)))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            hovermode='x unified',
            template='plotly_white',
            height=500
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def create_interactive_bar_chart(self, categories, values, title, x_label, y_label):
        """
        Create an interactive Plotly bar chart.

        Args:
            categories: Category labels
            values: Bar values (can be dict for grouped bars)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            str: HTML string for the chart
        """
        fig = go.Figure()

        if isinstance(values, dict):
            for name, vals in values.items():
                fig.add_trace(go.Bar(x=categories, y=vals, name=name))
        else:
            fig.add_trace(go.Bar(x=categories, y=values))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template='plotly_white',
            height=500,
            barmode='group'
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def create_interactive_heatmap(self, z_data, x_labels, y_labels, title):
        """
        Create an interactive Plotly heatmap.

        Args:
            z_data: 2D array of values
            x_labels: X-axis labels
            y_labels: Y-axis labels
            title: Chart title

        Returns:
            str: HTML string for the chart
        """
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale='RdYlGn',
            text=z_data,
            texttemplate='%{text:.1f}',
            textfont={"size": 10},
        ))

        fig.update_layout(
            title=title,
            template='plotly_white',
            height=600
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def create_interactive_radar(self, categories, values, title, team_names=None):
        """
        Create an interactive Plotly radar chart.

        Args:
            categories: Radar axis categories
            values: Values for each category (dict for multiple teams)
            title: Chart title
            team_names: Team names (if values is a list of lists)

        Returns:
            str: HTML string for the chart
        """
        fig = go.Figure()

        if isinstance(values, dict):
            for name, vals in values.items():
                fig.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=categories,
                    fill='toself',
                    name=name
                ))
        else:
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself'
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=title,
            template='plotly_white',
            height=600
        )

        return fig.to_html(full_html=False, include_plotlyjs=False)

    def create_multi_section_dashboard(self, sections, filename=None):
        """
        Create a dashboard with multiple sections.

        Args:
            sections: List of section dicts
                     [{'title': 'Section 1', 'charts': [...], 'metrics': {...}}, ...]
            filename: Output filename

        Returns:
            str: Path to saved dashboard
        """
        dashboard_data = {
            'title': 'SportStatBot - Comprehensive Analysis',
            'subtitle': 'Multi-Sport Dashboard',
            'sections': sections
        }

        # Flatten all charts and metrics
        all_charts = []
        all_metrics = {}

        for section in sections:
            all_charts.extend(section.get('charts', []))
            all_metrics.update(section.get('metrics', {}))

        dashboard_data['charts'] = all_charts
        dashboard_data['metrics'] = all_metrics

        return self.generate_full_dashboard(dashboard_data, filename)

    def embed_image_as_base64(self, image_path):
        """
        Embed an image as base64 for self-contained HTML.

        Args:
            image_path: Path to image file

        Returns:
            str: Base64 encoded image data URI
        """
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Detect image format
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }.get(ext, 'image/png')

        return f'data:{mime_type};base64,{image_data}'

    def generate_notion_compatible_export(self, dashboard_data, filename=None):
        """
        Generate a Notion-compatible HTML export.

        Args:
            dashboard_data: Dashboard data dict
            filename: Output filename

        Returns:
            str: Path to saved file
        """
        # Notion-friendly simplified template
        template_str = """
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
        h1 { color: #37352F; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #F7F6F3; border-radius: 5px; }
        .chart { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #E3E2E0; padding: 8px; text-align: left; }
        th { background: #F7F6F3; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>{{ subtitle }}</p>

    {% if metrics %}
    <div class="metrics">
        {% for metric_name, metric_value in metrics.items() %}
        <div class="metric">
            <strong>{{ metric_name }}:</strong> {{ metric_value }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if charts %}
    {% for chart in charts %}
    <div class="chart">
        <h3>{{ chart.title }}</h3>
        <img src="{{ chart.embedded_path }}" alt="{{ chart.title }}" style="max-width: 100%;">
    </div>
    {% endfor %}
    {% endif %}

    {% if tables %}
    {% for table in tables %}
    <h3>{{ table.title }}</h3>
    <table>
        <thead>
            <tr>
                {% for header in table.headers %}
                <th>{{ header }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table.rows %}
            <tr>
                {% for cell in row %}
                <td>{{ cell }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endfor %}
    {% endif %}

    <p><em>Generated: {{ timestamp }}</em></p>
</body>
</html>
        """

        if filename is None:
            filename = f'notion_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

        # Embed images as base64 for Notion compatibility
        charts_with_embedded = []
        for chart in dashboard_data.get('charts', []):
            chart_copy = chart.copy()
            if os.path.exists(chart['path']):
                chart_copy['embedded_path'] = self.embed_image_as_base64(chart['path'])
            charts_with_embedded.append(chart_copy)

        template = Template(template_str)
        html_content = template.render(
            title=dashboard_data.get('title', 'SportStatBot Export'),
            subtitle=dashboard_data.get('subtitle', ''),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            metrics=dashboard_data.get('metrics', {}),
            charts=charts_with_embedded,
            tables=dashboard_data.get('tables', [])
        )

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(html_content)

        return filepath
