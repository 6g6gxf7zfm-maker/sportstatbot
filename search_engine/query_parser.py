"""Natural language query parser for sports questions."""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser


class QueryParser:
    """
    Parses natural language queries into structured search parameters.
    Handles questions like "Which teams have the best net rating since March?"
    """

    def __init__(self):
        # Team name patterns
        self.team_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b(?=\s+(?:have|has|is|are|was|were|lost|won|played))',
            r'(?:team|teams)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        # Player name patterns
        self.player_patterns = [
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b(?=\s+(?:scored|threw|rushed|passed|had|made))',
            r'(?:player|players)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        # Sport keywords
        self.sport_keywords = {
            'nfl': ['nfl', 'football', 'quarterback', 'touchdown', 'passing', 'rushing'],
            'nba': ['nba', 'basketball', 'points', 'rebounds', 'assists', 'three-pointer'],
            'mlb': ['mlb', 'baseball', 'pitcher', 'batting', 'home run', 'strikeout', 'rbi'],
            'nhl': ['nhl', 'hockey', 'goal', 'goalie', 'puck', 'ice'],
            'soccer': ['soccer', 'football', 'premier league', 'mls', 'goal', 'match'],
            'golf': ['golf', 'pga', 'tournament', 'birdie', 'par', 'stroke']
        }

        # Query type patterns
        self.query_types = {
            'comparison': r'(?:compare|versus|vs|difference between)',
            'trend': r'(?:trend|trending|streak|hot|cold|momentum)',
            'best': r'(?:best|top|leading|highest|most)',
            'worst': r'(?:worst|bottom|lowest|least|fewest)',
            'recent': r'(?:recent|latest|last|yesterday|today)',
            'stats': r'(?:stats|statistics|numbers|data)',
            'explain': r'(?:explain|what is|what does|define|meaning of)',
            'history': r'(?:last time|history|historical|when did|when was)',
            'prediction': r'(?:predict|forecast|expect|likely|odds)',
        }

        # Time expressions
        self.time_patterns = {
            'since_date': r'since\s+([A-Z][a-z]+(?:\s+\d{1,2}(?:st|nd|rd|th)?)?(?:\s+\d{4})?)',
            'last_n': r'(?:last|past)\s+(\d+)\s+(day|week|month|year|game)s?',
            'this_period': r'this\s+(week|month|season|year)',
            'specific_date': r'on\s+([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
        }

        # Stat keywords
        self.stat_keywords = {
            'nfl': ['yards', 'touchdowns', 'interceptions', 'epa', 'qbr', 'completion', 'rating'],
            'nba': ['points', 'rebounds', 'assists', 'ts%', 'per', 'usage', 'plus-minus', 'efficiency'],
            'mlb': ['avg', 'era', 'war', 'ops', 'wrc+', 'fip', 'babip', 'whip'],
            'nhl': ['goals', 'assists', 'save%', 'corsi', 'fenwick', 'xgf%', 'pdo'],
            'soccer': ['goals', 'assists', 'xg', 'xa', 'passes', 'tackles', 'ppda']
        }

    def parse(self, query: str) -> Dict:
        """
        Parse a natural language query into structured parameters.

        Args:
            query: Natural language query string

        Returns:
            Dictionary with parsed query components
        """
        query_lower = query.lower()

        parsed = {
            'original_query': query,
            'query_type': self._detect_query_type(query_lower),
            'sport': self._detect_sport(query_lower),
            'teams': self._extract_teams(query),
            'players': self._extract_players(query),
            'stats': self._extract_stats(query_lower),
            'time_filter': self._extract_time_filter(query_lower),
            'filters': self._extract_filters(query_lower),
            'entities': self._extract_entities(query),
        }

        return parsed

    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query being asked."""
        for query_type, pattern in self.query_types.items():
            if re.search(pattern, query, re.IGNORECASE):
                return query_type

        # Default to general stats query
        return 'general'

    def _detect_sport(self, query: str) -> Optional[str]:
        """
        Detect which sport the query is about.

        Args:
            query: Query string (lowercase)

        Returns:
            Sport key or None
        """
        sport_scores = {}

        for sport, keywords in self.sport_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                sport_scores[sport] = score

        if sport_scores:
            return max(sport_scores, key=sport_scores.get)

        return None

    def _extract_teams(self, query: str) -> List[str]:
        """Extract team names from query."""
        teams = []

        for pattern in self.team_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                team = match.group(1).strip()
                if team and len(team) > 2:  # Avoid short words
                    teams.append(team)

        return list(set(teams))  # Remove duplicates

    def _extract_players(self, query: str) -> List[str]:
        """Extract player names from query."""
        players = []

        for pattern in self.player_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                player = match.group(1).strip()
                if player and len(player.split()) >= 2:  # Must be full name
                    players.append(player)

        return list(set(players))

    def _extract_stats(self, query: str) -> List[str]:
        """Extract stat types mentioned in query."""
        stats = []

        # Check all sport stat keywords
        for sport_stats in self.stat_keywords.values():
            for stat in sport_stats:
                if stat in query:
                    stats.append(stat)

        # Look for common stat abbreviations
        stat_pattern = r'\b([A-Z]{2,6}%?)\b'
        matches = re.finditer(stat_pattern, query)
        for match in matches:
            stat = match.group(1)
            if len(stat) <= 6:  # Reasonable stat abbreviation length
                stats.append(stat)

        return list(set(stats))

    def _extract_time_filter(self, query: str) -> Optional[Dict]:
        """
        Extract time-based filters from query.

        Returns:
            Dictionary with time filter parameters or None
        """
        # Try "since date" pattern
        match = re.search(self.time_patterns['since_date'], query, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                parsed_date = self._parse_date_string(date_str)
                return {
                    'type': 'since',
                    'date': parsed_date,
                    'original': date_str
                }
            except:
                pass

        # Try "last N period" pattern
        match = re.search(self.time_patterns['last_n'], query, re.IGNORECASE)
        if match:
            count = int(match.group(1))
            period = match.group(2)
            return {
                'type': 'last_n',
                'count': count,
                'period': period,
                'original': f'last {count} {period}s'
            }

        # Try "this period" pattern
        match = re.search(self.time_patterns['this_period'], query, re.IGNORECASE)
        if match:
            period = match.group(1)
            return {
                'type': 'this',
                'period': period,
                'original': f'this {period}'
            }

        # Try specific date pattern
        match = re.search(self.time_patterns['specific_date'], query, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                parsed_date = self._parse_date_string(date_str)
                return {
                    'type': 'on',
                    'date': parsed_date,
                    'original': date_str
                }
            except:
                pass

        return None

    def _parse_date_string(self, date_str: str) -> datetime:
        """
        Parse a date string into datetime object.

        Args:
            date_str: Date string like "March", "March 15", "March 15, 2024"

        Returns:
            datetime object
        """
        current_year = datetime.now().year

        # Add year if not present
        if not re.search(r'\d{4}', date_str):
            date_str = f"{date_str} {current_year}"

        # Parse the date
        parsed = date_parser.parse(date_str, fuzzy=True)

        # If parsed date is in future, use previous year
        if parsed > datetime.now():
            parsed = parsed.replace(year=current_year - 1)

        return parsed

    def _extract_filters(self, query: str) -> Dict:
        """
        Extract various filters from query.

        Returns:
            Dictionary of filter parameters
        """
        filters = {}

        # Position filter
        positions = ['quarterback', 'qb', 'running back', 'rb', 'wide receiver', 'wr',
                    'center', 'guard', 'forward', 'pitcher', 'goalie', 'defender']
        for pos in positions:
            if pos in query:
                filters['position'] = pos
                break

        # Home/Away filter
        if 'home' in query and 'games' in query:
            filters['location'] = 'home'
        elif 'away' in query and 'games' in query:
            filters['location'] = 'away'

        # Win/Loss filter
        if 'wins' in query or 'winning' in query:
            filters['result'] = 'win'
        elif 'losses' in query or 'losing' in query:
            filters['result'] = 'loss'

        # Playoff filter
        if 'playoff' in query:
            filters['playoff'] = True

        # Streak filter
        if 'streak' in query:
            if 'winning' in query or 'win' in query:
                filters['streak_type'] = 'win'
            elif 'losing' in query or 'loss' in query:
                filters['streak_type'] = 'loss'

        return filters

    def _extract_entities(self, query: str) -> List[Dict]:
        """
        Extract all entities (teams, players, stats, etc.) with context.

        Returns:
            List of entity dictionaries
        """
        entities = []

        # Teams
        for team in self._extract_teams(query):
            entities.append({
                'type': 'team',
                'value': team
            })

        # Players
        for player in self._extract_players(query):
            entities.append({
                'type': 'player',
                'value': player
            })

        # Stats
        for stat in self._extract_stats(query.lower()):
            entities.append({
                'type': 'stat',
                'value': stat
            })

        return entities

    def format_parsed_query(self, parsed: Dict) -> str:
        """
        Format parsed query into human-readable string.

        Args:
            parsed: Parsed query dictionary

        Returns:
            Formatted string
        """
        lines = [
            f"Query Type: {parsed['query_type'].title()}",
            f"Sport: {parsed['sport'].upper() if parsed['sport'] else 'Unknown'}",
        ]

        if parsed['teams']:
            lines.append(f"Teams: {', '.join(parsed['teams'])}")

        if parsed['players']:
            lines.append(f"Players: {', '.join(parsed['players'])}")

        if parsed['stats']:
            lines.append(f"Stats: {', '.join(parsed['stats'])}")

        if parsed['time_filter']:
            tf = parsed['time_filter']
            lines.append(f"Time Filter: {tf['original']}")

        if parsed['filters']:
            filter_str = ', '.join(f"{k}={v}" for k, v in parsed['filters'].items())
            lines.append(f"Filters: {filter_str}")

        return '\n'.join(lines)

    def is_stat_explanation_query(self, query: str) -> Optional[str]:
        """
        Check if query is asking for stat explanation.

        Args:
            query: Query string

        Returns:
            Stat abbreviation if asking for explanation, None otherwise
        """
        query_lower = query.lower()

        # Check for explanation patterns
        explain_patterns = [
            r'what (?:is|does) ([A-Z]{2,6}%?)(?: mean| measure)?',
            r'explain ([A-Z]{2,6}%?)',
            r'define ([A-Z]{2,6}%?)',
            r'([A-Z]{2,6}%?) (?:meaning|definition|explanation)',
        ]

        for pattern in explain_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).upper()

        return None
