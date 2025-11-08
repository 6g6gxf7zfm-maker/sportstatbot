"""Drill-down agent for exploring detailed data behind summaries."""
from typing import Dict, List, Optional, Any
import re


class DrillDownAgent:
    """
    Drill-down agent that provides detailed data behind summary points.
    Click on a bullet point in a report to see the full underlying data.
    """

    def __init__(self, data_fetcher, search_engine):
        """
        Initialize drill-down agent.

        Args:
            data_fetcher: Data fetcher for live stats
            search_engine: Search engine for historical context
        """
        self.data_fetcher = data_fetcher
        self.search_engine = search_engine

    def drill_down(self, bullet_point: str, context: Optional[Dict] = None) -> Dict:
        """
        Get detailed data behind a summary bullet point.

        Args:
            bullet_point: The bullet point text to expand
            context: Optional context (sport, date, team, etc.)

        Returns:
            Dictionary with detailed information
        """
        # Parse the bullet point to understand what it's about
        parsed = self._parse_bullet_point(bullet_point)

        # Determine drill-down type
        drill_type = parsed['type']

        if drill_type == 'player_stat':
            return self._drill_player_stat(parsed, context)

        elif drill_type == 'team_performance':
            return self._drill_team_performance(parsed, context)

        elif drill_type == 'streak':
            return self._drill_streak(parsed, context)

        elif drill_type == 'injury':
            return self._drill_injury(parsed, context)

        elif drill_type == 'game_result':
            return self._drill_game_result(parsed, context)

        elif drill_type == 'trend':
            return self._drill_trend(parsed, context)

        else:
            return self._drill_generic(bullet_point, context)

    def _parse_bullet_point(self, text: str) -> Dict:
        """
        Parse a bullet point to understand its type and content.

        Returns:
            Dictionary with parsed information
        """
        parsed = {
            'type': 'generic',
            'entities': {},
            'stats': {},
            'keywords': []
        }

        text_lower = text.lower()

        # Detect type based on keywords
        if 'streak' in text_lower:
            parsed['type'] = 'streak'
        elif any(word in text_lower for word in ['injury', 'injured', 'out', 'questionable']):
            parsed['type'] = 'injury'
        elif any(word in text_lower for word in ['won', 'lost', 'defeated', 'beat']):
            parsed['type'] = 'game_result'
        elif any(word in text_lower for word in ['trend', 'trending', 'momentum']):
            parsed['type'] = 'trend'

        # Extract player names (capitalized words)
        player_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        players = re.findall(player_pattern, text)
        if players:
            parsed['entities']['players'] = players

            # If has stats, it's a player stat bullet
            if self._has_stats(text):
                parsed['type'] = 'player_stat'

        # Extract team names
        team_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b(?=\s+(?:won|lost|are|is|have))'
        teams = re.findall(team_pattern, text)
        if teams:
            parsed['entities']['teams'] = teams

            if parsed['type'] == 'generic' and self._has_performance_indicators(text):
                parsed['type'] = 'team_performance'

        # Extract statistics
        stat_pattern = r'(\d+\.?\d*)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)'
        stats = re.findall(stat_pattern, text)
        for value, name in stats:
            parsed['stats'][name.lower()] = float(value)

        return parsed

    def _has_stats(self, text: str) -> bool:
        """Check if text contains statistical information."""
        stat_keywords = ['points', 'yards', 'rebounds', 'assists', 'goals', 'saves']
        return any(keyword in text.lower() for keyword in stat_keywords)

    def _has_performance_indicators(self, text: str) -> bool:
        """Check if text contains performance indicators."""
        perf_keywords = ['record', 'rank', 'place', 'standing', 'position']
        return any(keyword in text.lower() for keyword in perf_keywords)

    def _drill_player_stat(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed data about a player's statistical performance."""
        players = parsed['entities'].get('players', [])
        if not players:
            return {'error': 'No player identified'}

        player = players[0]

        # Get player's full game log
        game_log = self._get_player_game_log(player, context)

        # Get season stats
        season_stats = self._get_player_season_stats(player, context)

        # Get similar performances
        similar = self.search_engine.search(
            f"{player} similar performance",
            top_k=5
        )

        return {
            'type': 'player_stat_detail',
            'player': player,
            'game_log': game_log,
            'season_stats': season_stats,
            'season_rank': self._get_player_rank(player, parsed['stats'], context),
            'career_context': self._get_career_context(player, parsed['stats']),
            'similar_performances': similar
        }

    def _drill_team_performance(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed data about a team's performance."""
        teams = parsed['entities'].get('teams', [])
        if not teams:
            return {'error': 'No team identified'}

        team = teams[0]

        # Get recent games
        recent_games = self._get_team_recent_games(team, context)

        # Get season stats
        season_stats = self._get_team_season_stats(team, context)

        # Get advanced metrics
        advanced_metrics = self._get_team_advanced_metrics(team, context)

        return {
            'type': 'team_performance_detail',
            'team': team,
            'recent_games': recent_games,
            'season_stats': season_stats,
            'advanced_metrics': advanced_metrics,
            'league_rank': self._get_team_rank(team, context),
            'trends': self._analyze_team_trends(recent_games)
        }

    def _drill_streak(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed data about a streak."""
        teams = parsed['entities'].get('teams', [])
        if not teams:
            return {'error': 'No team identified'}

        team = teams[0]

        # Get games in streak
        streak_games = self._get_streak_games(team, context)

        # Get historical context
        historical_streaks = self.search_engine.search(
            f"{team} streak history",
            top_k=10
        )

        return {
            'type': 'streak_detail',
            'team': team,
            'streak_games': streak_games,
            'streak_stats': self._calculate_streak_stats(streak_games),
            'historical_context': historical_streaks,
            'comparison_to_history': self._compare_to_historical_streaks(
                len(streak_games),
                historical_streaks
            )
        }

    def _drill_injury(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed injury information."""
        players = parsed['entities'].get('players', [])
        if not players:
            return {'error': 'No player identified'}

        player = players[0]

        # Get injury details
        injury_report = self._get_injury_details(player, context)

        # Get team impact
        team_impact = self._analyze_injury_impact(player, context)

        return {
            'type': 'injury_detail',
            'player': player,
            'injury_report': injury_report,
            'timeline': injury_report.get('timeline'),
            'replacement_performance': self._get_replacement_stats(player, context),
            'team_impact': team_impact,
            'historical_injuries': self._get_player_injury_history(player)
        }

    def _drill_game_result(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed game result information."""
        teams = parsed['entities'].get('teams', [])

        # Get full box score
        box_score = self._get_game_box_score(teams, context)

        # Get play-by-play highlights
        highlights = self._get_game_highlights(teams, context)

        return {
            'type': 'game_result_detail',
            'box_score': box_score,
            'highlights': highlights,
            'key_moments': self._extract_key_moments(highlights),
            'player_performances': self._extract_top_performances(box_score),
            'game_flow': self._analyze_game_flow(highlights)
        }

    def _drill_trend(self, parsed: Dict, context: Optional[Dict]) -> Dict:
        """Get detailed trend information."""
        # Get trend data over time
        trend_data = self._get_trend_data(parsed, context)

        # Get contributing factors
        factors = self._analyze_trend_factors(trend_data)

        return {
            'type': 'trend_detail',
            'trend_data': trend_data,
            'contributing_factors': factors,
            'projection': self._project_trend(trend_data),
            'comparison_to_league': self._compare_trend_to_league(trend_data, context)
        }

    def _drill_generic(self, text: str, context: Optional[Dict]) -> Dict:
        """Generic drill-down using search."""
        # Use semantic search to find related content
        results = self.search_engine.search(text, top_k=10)

        return {
            'type': 'generic_detail',
            'summary': text,
            'related_content': results,
            'key_facts': self._extract_key_facts(results)
        }

    # Helper methods (placeholders for actual data fetching)

    def _get_player_game_log(self, player: str, context: Optional[Dict]) -> List[Dict]:
        """Get player's recent game log."""
        # This would fetch actual game log data
        return []

    def _get_player_season_stats(self, player: str, context: Optional[Dict]) -> Dict:
        """Get player's season statistics."""
        return {}

    def _get_player_rank(self, player: str, stats: Dict, context: Optional[Dict]) -> Dict:
        """Get player's league ranking in stats."""
        return {}

    def _get_career_context(self, player: str, stats: Dict) -> str:
        """Get career context for player's performance."""
        return "Career context not available"

    def _get_team_recent_games(self, team: str, context: Optional[Dict]) -> List[Dict]:
        """Get team's recent games."""
        return []

    def _get_team_season_stats(self, team: str, context: Optional[Dict]) -> Dict:
        """Get team's season statistics."""
        return {}

    def _get_team_advanced_metrics(self, team: str, context: Optional[Dict]) -> Dict:
        """Get team's advanced metrics."""
        return {}

    def _get_team_rank(self, team: str, context: Optional[Dict]) -> Dict:
        """Get team's league rankings."""
        return {}

    def _analyze_team_trends(self, games: List[Dict]) -> Dict:
        """Analyze trends from recent games."""
        return {}

    def _get_streak_games(self, team: str, context: Optional[Dict]) -> List[Dict]:
        """Get games in current streak."""
        return []

    def _calculate_streak_stats(self, games: List[Dict]) -> Dict:
        """Calculate statistics during streak."""
        return {}

    def _compare_to_historical_streaks(self, length: int, historical: List[Dict]) -> str:
        """Compare current streak to historical ones."""
        return f"This is a {length}-game streak"

    def _get_injury_details(self, player: str, context: Optional[Dict]) -> Dict:
        """Get detailed injury information."""
        return {}

    def _analyze_injury_impact(self, player: str, context: Optional[Dict]) -> Dict:
        """Analyze impact of injury on team."""
        return {}

    def _get_replacement_stats(self, player: str, context: Optional[Dict]) -> Dict:
        """Get stats of player's replacement."""
        return {}

    def _get_player_injury_history(self, player: str) -> List[Dict]:
        """Get player's injury history."""
        return []

    def _get_game_box_score(self, teams: List[str], context: Optional[Dict]) -> Dict:
        """Get full game box score."""
        return {}

    def _get_game_highlights(self, teams: List[str], context: Optional[Dict]) -> List[Dict]:
        """Get game highlights."""
        return []

    def _extract_key_moments(self, highlights: List[Dict]) -> List[str]:
        """Extract key moments from highlights."""
        return []

    def _extract_top_performances(self, box_score: Dict) -> List[Dict]:
        """Extract top performances from box score."""
        return []

    def _analyze_game_flow(self, highlights: List[Dict]) -> Dict:
        """Analyze how the game flowed."""
        return {}

    def _get_trend_data(self, parsed: Dict, context: Optional[Dict]) -> List[Dict]:
        """Get trend data over time."""
        return []

    def _analyze_trend_factors(self, trend_data: List[Dict]) -> List[str]:
        """Analyze factors contributing to trend."""
        return []

    def _project_trend(self, trend_data: List[Dict]) -> str:
        """Project where trend is heading."""
        return "Trend projection not available"

    def _compare_trend_to_league(self, trend_data: List[Dict],
                                context: Optional[Dict]) -> str:
        """Compare trend to league average."""
        return "League comparison not available"

    def _extract_key_facts(self, results: List[Dict]) -> List[str]:
        """Extract key facts from search results."""
        facts = []

        for result in results[:5]:
            content = result.get('content', '')

            # Extract sentences with numbers (likely facts)
            sentences = content.split('.')
            for sentence in sentences:
                if re.search(r'\d+', sentence):
                    facts.append(sentence.strip())

        return facts[:10]
