"""Generate data freshness heatmap visualizations."""
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.health_monitor import HealthMonitor
from pipeline.cache_manager import CacheManager
import config


class FreshnessHeatmap:
    """
    Generates data freshness heatmaps.
    Color coding: 🟢 Green = Fresh, 🟡 Yellow = Stale, 🔴 Red = Critical
    """

    def __init__(self):
        """Initialize heatmap generator."""
        self.health_monitor = HealthMonitor()
        self.cache_manager = CacheManager()
        self.sports_config = config.SPORTS_CONFIG

    def generate_heatmap(self, include_inactive: bool = False) -> Dict:
        """
        Generate freshness heatmap for all sports.

        Args:
            include_inactive: Include inactive sports

        Returns:
            Heatmap data structure
        """
        heatmap = {
            'timestamp': datetime.now().isoformat(),
            'sports': {}
        }

        # Get all beat statuses
        all_beats = self.health_monitor.get_all_beats_status()

        # Organize by sport
        for beat_key, status in all_beats.items():
            sport = beat_key.split('_')[0]

            # Check if sport is active
            sport_config = self.sports_config.get(sport, {})
            if not include_inactive and not sport_config.get('season_active', True):
                continue

            if sport not in heatmap['sports']:
                heatmap['sports'][sport] = {
                    'display_name': sport_config.get('display_name', sport.upper()),
                    'emoji': sport_config.get('emoji', '🏆'),
                    'data_sources': {}
                }

            data_type = '_'.join(beat_key.split('_')[1:])

            heatmap['sports'][sport]['data_sources'][data_type] = {
                'status': status['status'],
                'color': status['color'],
                'hours_stale': status['hours_stale'],
                'success_rate': status['success_rate'],
                'last_success': status['last_success']
            }

        return heatmap

    def render_text_heatmap(self, heatmap: Optional[Dict] = None) -> str:
        """
        Render heatmap as text with color indicators.

        Args:
            heatmap: Heatmap data (generates new if None)

        Returns:
            Formatted text heatmap
        """
        if heatmap is None:
            heatmap = self.generate_heatmap()

        output = []

        output.append("=" * 70)
        output.append("📊 DATA FRESHNESS HEATMAP")
        output.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 70)
        output.append("")

        output.append("Legend: 🟢 Fresh (<1h) | 🟡 Stale (1-24h) | 🔴 Critical (>24h) | ⚪ No Data")
        output.append("")

        # Sort sports alphabetically
        for sport_key in sorted(heatmap['sports'].keys()):
            sport_data = heatmap['sports'][sport_key]

            output.append(f"\n{sport_data['emoji']} {sport_data['display_name']}")
            output.append("-" * 70)

            # Get all data sources for this sport
            sources = sport_data['data_sources']

            if not sources:
                output.append("  ⚪ No data available")
                continue

            # Display each data source with color indicator
            for data_type, source_data in sorted(sources.items()):
                color_emoji = {
                    'green': '🟢',
                    'yellow': '🟡',
                    'red': '🔴',
                    'gray': '⚪'
                }
                emoji = color_emoji.get(source_data['color'], '⚪')

                # Format data type nicely
                formatted_type = data_type.replace('_', ' ').title()

                # Build status line
                status_parts = [formatted_type]

                if source_data['hours_stale'] is not None:
                    hours = source_data['hours_stale']
                    if hours < 1:
                        age_str = f"{hours * 60:.0f}m old"
                    else:
                        age_str = f"{hours:.1f}h old"
                    status_parts.append(age_str)

                if source_data['success_rate'] is not None:
                    status_parts.append(f"{source_data['success_rate']:.0f}% success")

                status_line = " • ".join(status_parts)
                output.append(f"  {emoji} {status_line}")

        output.append("")
        output.append("=" * 70)

        return "\n".join(output)

    def render_html_heatmap(self, heatmap: Optional[Dict] = None) -> str:
        """
        Render heatmap as HTML (for web viewing).

        Args:
            heatmap: Heatmap data (generates new if None)

        Returns:
            HTML string
        """
        if heatmap is None:
            heatmap = self.generate_heatmap()

        html = []

        html.append("<!DOCTYPE html>")
        html.append("<html><head>")
        html.append("<title>SportStatBot - Data Freshness Heatmap</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }")
        html.append("h1 { color: #333; }")
        html.append(".sport-section { background: white; margin: 15px 0; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html.append(".sport-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; }")
        html.append(".data-source { padding: 8px; margin: 5px 0; border-radius: 4px; }")
        html.append(".status-green { background: #d4edda; border-left: 4px solid #28a745; }")
        html.append(".status-yellow { background: #fff3cd; border-left: 4px solid #ffc107; }")
        html.append(".status-red { background: #f8d7da; border-left: 4px solid #dc3545; }")
        html.append(".status-gray { background: #e2e3e5; border-left: 4px solid #6c757d; }")
        html.append(".timestamp { color: #666; font-size: 14px; }")
        html.append(".legend { background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }")
        html.append("</style>")
        html.append("</head><body>")

        html.append("<h1>📊 Data Freshness Heatmap</h1>")
        html.append(f"<p class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

        html.append("<div class='legend'>")
        html.append("<strong>Legend:</strong> ")
        html.append("<span style='color: #28a745;'>● Fresh (&lt;1h)</span> | ")
        html.append("<span style='color: #ffc107;'>● Stale (1-24h)</span> | ")
        html.append("<span style='color: #dc3545;'>● Critical (&gt;24h)</span> | ")
        html.append("<span style='color: #6c757d;'>● No Data</span>")
        html.append("</div>")

        # Render each sport
        for sport_key in sorted(heatmap['sports'].keys()):
            sport_data = heatmap['sports'][sport_key]

            html.append("<div class='sport-section'>")
            html.append(f"<div class='sport-title'>{sport_data['emoji']} {sport_data['display_name']}</div>")

            sources = sport_data['data_sources']

            if not sources:
                html.append("<div class='data-source status-gray'>No data available</div>")
            else:
                for data_type, source_data in sorted(sources.items()):
                    color_class = f"status-{source_data['color']}"
                    formatted_type = data_type.replace('_', ' ').title()

                    status_info = []
                    if source_data['hours_stale'] is not None:
                        hours = source_data['hours_stale']
                        age_str = f"{hours:.1f}h old" if hours >= 1 else f"{hours * 60:.0f}m old"
                        status_info.append(age_str)

                    if source_data['success_rate'] is not None:
                        status_info.append(f"{source_data['success_rate']:.0f}% success")

                    info_str = " • ".join(status_info) if status_info else "No recent data"

                    html.append(
                        f"<div class='data-source {color_class}'>"
                        f"<strong>{formatted_type}</strong>: {info_str}"
                        f"</div>"
                    )

            html.append("</div>")

        html.append("</body></html>")

        return "\n".join(html)

    def save_heatmap(self, format: str = "text", filepath: Optional[str] = None) -> str:
        """
        Save heatmap to file.

        Args:
            format: Output format ('text', 'html', or 'json')
            filepath: Optional filepath (auto-generated if None)

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == "text":
            content = self.render_text_heatmap()
            default_path = f"reports/monitoring/heatmap_{timestamp}.txt"
            filepath = filepath or default_path

        elif format == "html":
            content = self.render_html_heatmap()
            default_path = f"reports/monitoring/heatmap_{timestamp}.html"
            filepath = filepath or default_path

        elif format == "json":
            heatmap = self.generate_heatmap()
            content = json.dumps(heatmap, indent=2)
            default_path = f"reports/monitoring/heatmap_{timestamp}.json"
            filepath = filepath or default_path

        else:
            raise ValueError(f"Unsupported format: {format}")

        try:
            filepath_obj = Path(filepath)
            filepath_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                f.write(content)

            return str(filepath)

        except Exception as e:
            print(f"Error saving heatmap: {e}")
            return ""

    def get_critical_items(self) -> List[Dict]:
        """
        Get list of critical (red) items that need attention.

        Returns:
            List of critical items with details
        """
        heatmap = self.generate_heatmap()
        critical_items = []

        for sport_key, sport_data in heatmap['sports'].items():
            for data_type, source_data in sport_data['data_sources'].items():
                if source_data['color'] == 'red' or source_data['status'] == 'critical':
                    critical_items.append({
                        'sport': sport_data['display_name'],
                        'data_type': data_type,
                        'hours_stale': source_data['hours_stale'],
                        'success_rate': source_data['success_rate'],
                        'last_success': source_data['last_success']
                    })

        return critical_items
