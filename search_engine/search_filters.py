"""Search filter system for refining queries."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class SearchFilter:
    """Base class for search filters."""

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Apply filter to data."""
        raise NotImplementedError


class PlayerFilter(SearchFilter):
    """Filter by player name(s)."""

    def __init__(self, players: List[str]):
        self.players = [p.lower() for p in players]

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only specified players."""
        filtered = []

        for item in data:
            # Check if any of the filter players are mentioned
            content = str(item.get('content', '')).lower()
            metadata = item.get('metadata', {})
            player_list = [p.lower() for p in metadata.get('players', [])]

            for player in self.players:
                if player in content or player in player_list:
                    filtered.append(item)
                    break

        return filtered


class TeamFilter(SearchFilter):
    """Filter by team name(s)."""

    def __init__(self, teams: List[str]):
        self.teams = [t.lower() for t in teams]

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only specified teams."""
        filtered = []

        for item in data:
            content = str(item.get('content', '')).lower()
            metadata = item.get('metadata', {})
            team_list = [t.lower() for t in metadata.get('teams', [])]

            for team in self.teams:
                if team in content or team in team_list:
                    filtered.append(item)
                    break

        return filtered


class SportFilter(SearchFilter):
    """Filter by sport."""

    def __init__(self, sport: str):
        self.sport = sport.lower()

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only specified sport."""
        return [
            item for item in data
            if item.get('metadata', {}).get('sport', '').lower() == self.sport
        ]


class DateRangeFilter(SearchFilter):
    """Filter by date range."""

    def __init__(self, start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None):
        self.start_date = start_date
        self.end_date = end_date

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only items within date range."""
        filtered = []

        for item in data:
            metadata = item.get('metadata', {})
            date_str = metadata.get('date') or metadata.get('timestamp')

            if not date_str:
                continue

            try:
                item_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

                # Check if within range
                if self.start_date and item_date < self.start_date:
                    continue
                if self.end_date and item_date > self.end_date:
                    continue

                filtered.append(item)

            except (ValueError, AttributeError):
                # Skip items with invalid dates
                continue

        return filtered


class TimeWindowFilter(SearchFilter):
    """Filter by relative time window (e.g., last 7 days)."""

    def __init__(self, days: Optional[int] = None, weeks: Optional[int] = None,
                 months: Optional[int] = None):
        now = datetime.now()

        if days:
            self.start_date = now - timedelta(days=days)
        elif weeks:
            self.start_date = now - timedelta(weeks=weeks)
        elif months:
            self.start_date = now - timedelta(days=months * 30)  # Approximate
        else:
            self.start_date = None

        self.end_date = now

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only items within time window."""
        if not self.start_date:
            return data

        date_filter = DateRangeFilter(self.start_date, self.end_date)
        return date_filter.apply(data)


class StoryTypeFilter(SearchFilter):
    """Filter by story/content type."""

    def __init__(self, story_types: List[str]):
        """
        Initialize with story types.

        Args:
            story_types: List of types like 'injury', 'trade', 'game', 'analysis', etc.
        """
        self.story_types = [t.lower() for t in story_types]

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only specified story types."""
        filtered = []

        for item in data:
            metadata = item.get('metadata', {})
            item_type = metadata.get('type', '').lower()
            tags = [t.lower() for t in metadata.get('tags', [])]

            for story_type in self.story_types:
                if story_type == item_type or story_type in tags:
                    filtered.append(item)
                    break

        return filtered


class GameResultFilter(SearchFilter):
    """Filter by game result (win/loss)."""

    def __init__(self, result: str):
        """
        Initialize with result type.

        Args:
            result: 'win', 'loss', or 'tie'
        """
        self.result = result.lower()

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data to include only specified game results."""
        return [
            item for item in data
            if item.get('metadata', {}).get('result', '').lower() == self.result
        ]


class StatThresholdFilter(SearchFilter):
    """Filter by statistical threshold."""

    def __init__(self, stat_name: str, operator: str, value: float):
        """
        Initialize with stat criteria.

        Args:
            stat_name: Name of the stat
            operator: Comparison operator ('>', '<', '>=', '<=', '==')
            value: Threshold value
        """
        self.stat_name = stat_name.lower()
        self.operator = operator
        self.value = value

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Filter data based on stat threshold."""
        filtered = []

        for item in data:
            stats = item.get('metadata', {}).get('stats', {})
            stat_value = stats.get(self.stat_name)

            if stat_value is None:
                continue

            try:
                stat_value = float(stat_value)

                if self._compare(stat_value, self.value):
                    filtered.append(item)

            except (ValueError, TypeError):
                continue

        return filtered

    def _compare(self, value: float, threshold: float) -> bool:
        """Compare value against threshold using operator."""
        if self.operator == '>':
            return value > threshold
        elif self.operator == '<':
            return value < threshold
        elif self.operator == '>=':
            return value >= threshold
        elif self.operator == '<=':
            return value <= threshold
        elif self.operator == '==':
            return value == threshold
        return False


class FilterPipeline:
    """Pipeline for applying multiple filters in sequence."""

    def __init__(self):
        self.filters: List[SearchFilter] = []

    def add_filter(self, filter_obj: SearchFilter):
        """Add a filter to the pipeline."""
        self.filters.append(filter_obj)
        return self  # Allow chaining

    def apply(self, data: List[Dict]) -> List[Dict]:
        """Apply all filters in sequence."""
        result = data

        for filter_obj in self.filters:
            result = filter_obj.apply(result)

        return result

    def clear(self):
        """Clear all filters."""
        self.filters = []


class FilterBuilder:
    """Builder for creating filter pipelines from parsed queries."""

    @staticmethod
    def build_from_parsed_query(parsed_query: Dict) -> FilterPipeline:
        """
        Build filter pipeline from parsed query.

        Args:
            parsed_query: Parsed query dictionary from QueryParser

        Returns:
            FilterPipeline with appropriate filters
        """
        pipeline = FilterPipeline()

        # Sport filter
        if parsed_query.get('sport'):
            pipeline.add_filter(SportFilter(parsed_query['sport']))

        # Team filter
        if parsed_query.get('teams'):
            pipeline.add_filter(TeamFilter(parsed_query['teams']))

        # Player filter
        if parsed_query.get('players'):
            pipeline.add_filter(PlayerFilter(parsed_query['players']))

        # Time filter
        time_filter = parsed_query.get('time_filter')
        if time_filter:
            if time_filter['type'] == 'since':
                pipeline.add_filter(DateRangeFilter(
                    start_date=time_filter['date']
                ))
            elif time_filter['type'] == 'last_n':
                count = time_filter['count']
                period = time_filter['period']

                if period in ['day', 'days']:
                    pipeline.add_filter(TimeWindowFilter(days=count))
                elif period in ['week', 'weeks']:
                    pipeline.add_filter(TimeWindowFilter(weeks=count))
                elif period in ['month', 'months']:
                    pipeline.add_filter(TimeWindowFilter(months=count))

        # Additional filters from query
        filters = parsed_query.get('filters', {})

        if filters.get('result'):
            pipeline.add_filter(GameResultFilter(filters['result']))

        return pipeline

    @staticmethod
    def build_custom(sport: Optional[str] = None,
                    teams: Optional[List[str]] = None,
                    players: Optional[List[str]] = None,
                    date_range: Optional[Tuple[datetime, datetime]] = None,
                    last_n_days: Optional[int] = None) -> FilterPipeline:
        """
        Build custom filter pipeline.

        Args:
            sport: Sport to filter by
            teams: List of teams
            players: List of players
            date_range: Tuple of (start_date, end_date)
            last_n_days: Filter to last N days

        Returns:
            FilterPipeline with specified filters
        """
        pipeline = FilterPipeline()

        if sport:
            pipeline.add_filter(SportFilter(sport))

        if teams:
            pipeline.add_filter(TeamFilter(teams))

        if players:
            pipeline.add_filter(PlayerFilter(players))

        if date_range:
            pipeline.add_filter(DateRangeFilter(date_range[0], date_range[1]))

        if last_n_days:
            pipeline.add_filter(TimeWindowFilter(days=last_n_days))

        return pipeline


def create_quick_filter(filter_type: str, value: Any) -> SearchFilter:
    """
    Create a quick filter of a specific type.

    Args:
        filter_type: Type of filter ('sport', 'team', 'player', 'date', etc.)
        value: Filter value

    Returns:
        SearchFilter instance
    """
    filter_type = filter_type.lower()

    if filter_type == 'sport':
        return SportFilter(value)
    elif filter_type == 'team':
        return TeamFilter([value] if isinstance(value, str) else value)
    elif filter_type == 'player':
        return PlayerFilter([value] if isinstance(value, str) else value)
    elif filter_type == 'last_days':
        return TimeWindowFilter(days=value)
    elif filter_type == 'last_weeks':
        return TimeWindowFilter(weeks=value)
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")
