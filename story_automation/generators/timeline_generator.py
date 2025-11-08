"""
Timeline Generator - Event chronology builder
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class TimelineGenerator:
    """Generate chronological timelines of events"""

    def __init__(self):
        pass

    def generate_timeline(
        self,
        context: Dict[str, Any],
        sport: str,
        format_type: str = 'vertical'
    ) -> Dict[str, Any]:
        """
        Generate event timeline

        Args:
            context: Story context with events
            sport: Sport name
            format_type: Timeline format (vertical, horizontal, compact)

        Returns:
            Timeline data structure
        """
        # Extract events from context
        events = self._extract_events(context, sport)

        # Sort events chronologically
        events.sort(key=lambda x: x['timestamp'])

        # Format timeline
        timeline = {
            'sport': sport,
            'format': format_type,
            'event_count': len(events),
            'events': events,
            'formatted': self._format_timeline(events, format_type)
        }

        return timeline

    def _extract_events(
        self,
        context: Dict[str, Any],
        sport: str
    ) -> List[Dict[str, Any]]:
        """Extract events from context"""
        events = []

        # Recent games as events
        games = context.get('recent_games', [])
        for game in games:
            events.append({
                'type': 'game',
                'timestamp': datetime.now() - timedelta(hours=len(events)),  # Approximate
                'description': f"{game.get('away_team', 'Away')} @ {game.get('home_team', 'Home')}",
                'details': f"Score: {game.get('away_score', 0)}-{game.get('home_score', 0)}",
                'significance': 'high' if game.get('classification') == 'upset' else 'medium'
            })

        # Injuries as events
        injuries = context.get('injuries', [])
        for injury in injuries[:5]:
            events.append({
                'type': 'injury',
                'timestamp': datetime.now() - timedelta(hours=len(events) * 2),
                'description': injury.get('headline', ''),
                'details': injury.get('description', ''),
                'significance': 'high'
            })

        # Roster changes as events
        roster_changes = context.get('roster_changes', [])
        for change in roster_changes[:5]:
            events.append({
                'type': 'roster',
                'timestamp': datetime.now() - timedelta(hours=len(events) * 2),
                'description': change.get('headline', ''),
                'details': change.get('description', ''),
                'significance': 'medium'
            })

        # Trends as milestone events
        trends = context.get('trends', [])
        for trend in trends:
            if 'streak' in trend.get('type', ''):
                events.append({
                    'type': 'milestone',
                    'timestamp': datetime.now() - timedelta(days=3),
                    'description': trend.get('description', ''),
                    'details': f"Team: {trend.get('team', '')}",
                    'significance': 'high'
                })

        return events

    def _format_timeline(
        self,
        events: List[Dict[str, Any]],
        format_type: str
    ) -> str:
        """Format timeline for display"""
        if format_type == 'vertical':
            return self._format_vertical(events)
        elif format_type == 'horizontal':
            return self._format_horizontal(events)
        elif format_type == 'compact':
            return self._format_compact(events)
        else:
            return self._format_vertical(events)

    def _format_vertical(self, events: List[Dict[str, Any]]) -> str:
        """Format as vertical timeline"""
        output = "## Event Timeline\n\n"

        for i, event in enumerate(events):
            # Event marker
            icon = self._get_event_icon(event['type'])
            timestamp = event['timestamp'].strftime('%B %d, %I:%M %p')

            output += f"### {icon} {timestamp}\n"
            output += f"**{event['description']}**\n\n"

            if event.get('details'):
                output += f"_{event['details']}_\n\n"

            # Add connector if not last event
            if i < len(events) - 1:
                output += "|\n"

        return output

    def _format_horizontal(self, events: List[Dict[str, Any]]) -> str:
        """Format as horizontal timeline"""
        output = "## Event Timeline\n\n"
        output += "|"

        for event in events:
            icon = self._get_event_icon(event['type'])
            output += f" {icon} |"

        output += "\n|"
        for event in events:
            timestamp = event['timestamp'].strftime('%m/%d')
            output += f" {timestamp} |"

        output += "\n\n"

        # Details below
        for event in events:
            output += f"**{event['description']}** • "

        return output.rstrip(' • ')

    def _format_compact(self, events: List[Dict[str, Any]]) -> str:
        """Format as compact list"""
        output = "## Recent Events\n\n"

        for event in events:
            icon = self._get_event_icon(event['type'])
            time_ago = self._get_time_ago(event['timestamp'])

            output += f"• {icon} **{event['description']}** _{time_ago}_\n"

        return output

    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event type"""
        icons = {
            'game': '🏆',
            'injury': '🏥',
            'roster': '📝',
            'milestone': '⭐',
            'trade': '🔄',
            'signing': '✍️'
        }
        return icons.get(event_type, '📌')

    def _get_time_ago(self, timestamp: datetime) -> str:
        """Get human-readable time ago"""
        delta = datetime.now() - timestamp

        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"

    def group_events_by_date(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by date"""
        grouped = defaultdict(list)

        for event in events:
            date_key = event['timestamp'].strftime('%Y-%m-%d')
            grouped[date_key].append(event)

        return dict(grouped)

    def filter_events_by_type(
        self,
        events: List[Dict[str, Any]],
        event_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter events by type"""
        return [e for e in events if e['type'] in event_types]

    def get_significant_events(
        self,
        events: List[Dict[str, Any]],
        min_significance: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """Get only significant events"""
        significance_order = {'low': 0, 'medium': 1, 'high': 2}
        min_level = significance_order.get(min_significance, 1)

        return [
            e for e in events
            if significance_order.get(e.get('significance', 'low'), 0) >= min_level
        ]
