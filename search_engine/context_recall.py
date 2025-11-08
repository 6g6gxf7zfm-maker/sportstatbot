"""Context recall and comparative search functionality."""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re


class ContextRecall:
    """
    Context recall system for finding historical events and patterns.
    Enables queries like "Show me last time Celtics lost 3 straight".
    """

    def __init__(self, search_engine):
        """
        Initialize context recall.

        Args:
            search_engine: SemanticSearchEngine instance
        """
        self.search_engine = search_engine

    def find_last_occurrence(self, event_description: str, team: Optional[str] = None,
                            player: Optional[str] = None) -> Optional[Dict]:
        """
        Find the last time a specific event occurred.

        Args:
            event_description: Description of the event (e.g., "lost 3 straight")
            team: Team name (optional)
            player: Player name (optional)

        Returns:
            Most recent matching event or None
        """
        # Build search query
        query_parts = [event_description]

        if team:
            query_parts.append(team)
        if player:
            query_parts.append(player)

        query = ' '.join(query_parts)

        # Search with semantic search
        results = self.search_engine.search(query, top_k=20)

        if not results:
            return None

        # Return most recent result
        # Sort by date if available
        dated_results = [
            r for r in results
            if r.get('metadata', {}).get('date')
        ]

        if dated_results:
            dated_results.sort(
                key=lambda x: x['metadata']['date'],
                reverse=True
            )
            return dated_results[0]

        return results[0]

    def find_streak_history(self, team: str, streak_type: str,
                           streak_length: int) -> List[Dict]:
        """
        Find historical streaks for a team.

        Args:
            team: Team name
            streak_type: 'win' or 'loss'
            streak_length: Minimum streak length

        Returns:
            List of streak occurrences
        """
        query = f"{team} {streak_length} game {streak_type}ing streak"

        results = self.search_engine.search(query, top_k=10)

        # Filter to only results mentioning streaks
        streak_results = []

        for result in results:
            content = result.get('content', '').lower()

            # Look for streak mentions
            if 'streak' in content and streak_type in content:
                streak_results.append(result)

        return streak_results

    def find_similar_games(self, game_description: str, top_k: int = 5) -> List[Dict]:
        """
        Find games similar to a description.

        Args:
            game_description: Description of game scenario
            top_k: Number of similar games to find

        Returns:
            List of similar games
        """
        query = f"game {game_description}"
        return self.search_engine.search(query, top_k=top_k)

    def find_player_milestones(self, player: str, milestone_type: str) -> List[Dict]:
        """
        Find player milestones and achievements.

        Args:
            player: Player name
            milestone_type: Type of milestone (e.g., "career high", "record", "first")

        Returns:
            List of milestone occurrences
        """
        query = f"{player} {milestone_type}"
        return self.search_engine.search(query, top_k=10)

    def find_head_to_head_history(self, team1: str, team2: str,
                                   limit: int = 10) -> List[Dict]:
        """
        Find head-to-head matchup history between two teams.

        Args:
            team1: First team
            team2: Second team
            limit: Number of historical matchups

        Returns:
            List of past matchups
        """
        query = f"{team1} vs {team2}"
        results = self.search_engine.search(query, top_k=limit * 2)

        # Filter to results mentioning both teams
        h2h_results = []

        for result in results:
            content = result.get('content', '').lower()

            if team1.lower() in content and team2.lower() in content:
                h2h_results.append(result)

        return h2h_results[:limit]


class ComparativeSearch:
    """
    Comparative search for comparing teams, players, or time periods.
    Enables queries like "Compare Ravens Week 3 vs Week 10 defense".
    """

    def __init__(self, data_fetcher, search_engine):
        """
        Initialize comparative search.

        Args:
            data_fetcher: Data fetcher for current stats
            search_engine: Semantic search engine for historical data
        """
        self.data_fetcher = data_fetcher
        self.search_engine = search_engine

    def compare_team_periods(self, team: str, period1: str,
                            period2: str, aspect: Optional[str] = None) -> Dict:
        """
        Compare a team's performance across two time periods.

        Args:
            team: Team name
            period1: First time period (e.g., "Week 3", "March")
            period2: Second time period
            aspect: Specific aspect to compare (e.g., "defense", "offense")

        Returns:
            Comparison dictionary
        """
        # Search for data from each period
        query1 = f"{team} {period1}"
        if aspect:
            query1 += f" {aspect}"

        query2 = f"{team} {period2}"
        if aspect:
            query2 += f" {aspect}"

        results1 = self.search_engine.search(query1, top_k=5)
        results2 = self.search_engine.search(query2, top_k=5)

        # Extract key stats from each period
        stats1 = self._extract_stats_from_results(results1)
        stats2 = self._extract_stats_from_results(results2)

        return {
            'team': team,
            'period1': {
                'name': period1,
                'stats': stats1,
                'sources': results1
            },
            'period2': {
                'name': period2,
                'stats': stats2,
                'sources': results2
            },
            'comparison': self._compare_stats(stats1, stats2)
        }

    def compare_players(self, player1: str, player2: str,
                       stat_categories: Optional[List[str]] = None,
                       time_period: Optional[str] = None) -> Dict:
        """
        Compare two players' performance.

        Args:
            player1: First player name
            player2: Second player name
            stat_categories: Specific stats to compare (optional)
            time_period: Time period for comparison (optional)

        Returns:
            Comparison dictionary
        """
        # Build queries
        query1 = player1
        query2 = player2

        if time_period:
            query1 += f" {time_period}"
            query2 += f" {time_period}"

        if stat_categories:
            stats_str = ' '.join(stat_categories)
            query1 += f" {stats_str}"
            query2 += f" {stats_str}"

        # Search for player data
        results1 = self.search_engine.search(query1, top_k=10)
        results2 = self.search_engine.search(query2, top_k=10)

        stats1 = self._extract_stats_from_results(results1)
        stats2 = self._extract_stats_from_results(results2)

        return {
            'player1': {
                'name': player1,
                'stats': stats1,
                'sources': results1
            },
            'player2': {
                'name': player2,
                'stats': stats2,
                'sources': results2
            },
            'comparison': self._compare_stats(stats1, stats2),
            'winner': self._determine_winner(stats1, stats2)
        }

    def compare_teams(self, team1: str, team2: str,
                     aspects: Optional[List[str]] = None) -> Dict:
        """
        Compare two teams across various aspects.

        Args:
            team1: First team
            team2: Second team
            aspects: Specific aspects to compare (e.g., ['offense', 'defense'])

        Returns:
            Comparison dictionary
        """
        if not aspects:
            aspects = ['offense', 'defense', 'overall']

        comparisons = {}

        for aspect in aspects:
            query1 = f"{team1} {aspect}"
            query2 = f"{team2} {aspect}"

            results1 = self.search_engine.search(query1, top_k=5)
            results2 = self.search_engine.search(query2, top_k=5)

            stats1 = self._extract_stats_from_results(results1)
            stats2 = self._extract_stats_from_results(results2)

            comparisons[aspect] = {
                'team1': stats1,
                'team2': stats2,
                'advantage': self._determine_winner(stats1, stats2)
            }

        return {
            'team1': team1,
            'team2': team2,
            'comparisons': comparisons,
            'overall_advantage': self._calculate_overall_advantage(comparisons)
        }

    def compare_seasons(self, team: str, season1: str, season2: str) -> Dict:
        """
        Compare a team's performance across different seasons.

        Args:
            team: Team name
            season1: First season (e.g., "2023")
            season2: Second season

        Returns:
            Comparison dictionary
        """
        query1 = f"{team} {season1} season"
        query2 = f"{team} {season2} season"

        results1 = self.search_engine.search(query1, top_k=20)
        results2 = self.search_engine.search(query2, top_k=20)

        return {
            'team': team,
            'season1': {
                'name': season1,
                'performance': self._extract_stats_from_results(results1),
                'highlights': self._extract_highlights(results1)
            },
            'season2': {
                'name': season2,
                'performance': self._extract_stats_from_results(results2),
                'highlights': self._extract_highlights(results2)
            }
        }

    def _extract_stats_from_results(self, results: List[Dict]) -> Dict:
        """Extract statistics from search results."""
        all_stats = {}

        for result in results:
            metadata = result.get('metadata', {})
            stats = metadata.get('stats', {})

            # Merge stats, preferring more recent values
            for stat_name, stat_value in stats.items():
                if stat_name not in all_stats:
                    all_stats[stat_name] = stat_value

        # Also try to extract from content
        for result in results:
            content = result.get('content', '')
            extracted = self._extract_stats_from_text(content)
            for stat_name, stat_value in extracted.items():
                if stat_name not in all_stats:
                    all_stats[stat_name] = stat_value

        return all_stats

    def _extract_stats_from_text(self, text: str) -> Dict:
        """Extract statistics from text content using patterns."""
        stats = {}

        # Pattern for "X points", "Y yards", etc.
        number_stat_pattern = r'(\d+\.?\d*)\s+(points|yards|rebounds|assists|goals|touchdowns?|interceptions?)'
        matches = re.finditer(number_stat_pattern, text, re.IGNORECASE)

        for match in matches:
            value = float(match.group(1))
            stat_name = match.group(2).lower()
            stats[stat_name] = value

        # Pattern for percentages
        pct_pattern = r'(\d+\.?\d*)%\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)'
        matches = re.finditer(pct_pattern, text)

        for match in matches:
            value = float(match.group(1))
            stat_name = match.group(2).lower().strip()
            stats[f"{stat_name}_pct"] = value

        return stats

    def _compare_stats(self, stats1: Dict, stats2: Dict) -> Dict:
        """
        Compare two stat dictionaries.

        Returns:
            Dictionary with differences and percentages
        """
        comparison = {}

        all_stat_names = set(stats1.keys()) | set(stats2.keys())

        for stat_name in all_stat_names:
            val1 = stats1.get(stat_name)
            val2 = stats2.get(stat_name)

            if val1 is not None and val2 is not None:
                try:
                    val1 = float(val1)
                    val2 = float(val2)

                    diff = val2 - val1
                    pct_change = (diff / val1 * 100) if val1 != 0 else 0

                    comparison[stat_name] = {
                        'value1': val1,
                        'value2': val2,
                        'difference': diff,
                        'percent_change': pct_change,
                        'better': 'period2' if diff > 0 else 'period1'
                    }
                except (ValueError, TypeError):
                    pass

        return comparison

    def _determine_winner(self, stats1: Dict, stats2: Dict) -> Optional[str]:
        """Determine which set of stats is better overall."""
        if not stats1 or not stats2:
            return None

        score1 = 0
        score2 = 0

        positive_stats = ['points', 'yards', 'goals', 'assists', 'rebounds', 'wins']
        negative_stats = ['turnovers', 'interceptions', 'losses', 'errors']

        all_stats = set(stats1.keys()) | set(stats2.keys())

        for stat in all_stats:
            val1 = stats1.get(stat)
            val2 = stats2.get(stat)

            if val1 is None or val2 is None:
                continue

            try:
                val1 = float(val1)
                val2 = float(val2)

                # Determine if higher is better
                higher_is_better = any(pos in stat.lower() for pos in positive_stats)
                lower_is_better = any(neg in stat.lower() for neg in negative_stats)

                if higher_is_better:
                    if val1 > val2:
                        score1 += 1
                    elif val2 > val1:
                        score2 += 1
                elif lower_is_better:
                    if val1 < val2:
                        score1 += 1
                    elif val2 < val1:
                        score2 += 1

            except (ValueError, TypeError):
                continue

        if score1 > score2:
            return 'entity1'
        elif score2 > score1:
            return 'entity2'
        else:
            return 'tie'

    def _extract_highlights(self, results: List[Dict]) -> List[str]:
        """Extract highlight moments from results."""
        highlights = []

        for result in results:
            content = result.get('content', '')

            # Look for exciting moments
            excitement_keywords = [
                'career high', 'record', 'milestone', 'comeback', 'clutch',
                'game-winner', 'overtime', 'championship', 'playoff'
            ]

            for keyword in excitement_keywords:
                if keyword in content.lower():
                    # Extract sentence containing the keyword
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            highlights.append(sentence.strip())
                            break

        return list(set(highlights))[:10]  # Unique, max 10

    def _calculate_overall_advantage(self, comparisons: Dict) -> str:
        """Calculate overall advantage from aspect comparisons."""
        team1_wins = 0
        team2_wins = 0

        for aspect, data in comparisons.items():
            advantage = data.get('advantage')
            if advantage == 'entity1':
                team1_wins += 1
            elif advantage == 'entity2':
                team2_wins += 1

        if team1_wins > team2_wins:
            return 'team1'
        elif team2_wins > team1_wins:
            return 'team2'
        else:
            return 'even'
