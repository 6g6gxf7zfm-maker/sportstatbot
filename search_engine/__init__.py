"""
SportStatBot Search & Query Engine

Natural language search and query system for sports statistics and reports.
"""

from typing import Dict, List, Optional, Any

from .query_parser import QueryParser
from .semantic_search import SemanticSearchEngine
from .stats_glossary import StatsGlossary
from .search_filters import (
    SearchFilter, FilterPipeline, FilterBuilder,
    PlayerFilter, TeamFilter, SportFilter, DateRangeFilter
)
from .context_recall import ContextRecall, ComparativeSearch
from .story_generator import StoryGenerator, SmartPromptCompletion
from .drill_down import DrillDownAgent
from .cross_check import CrossCheckVerifier
from .report_storage import ReportStorage

__all__ = [
    'SportStatSearchEngine',
    'QueryParser',
    'SemanticSearchEngine',
    'StatsGlossary',
    'SearchFilter',
    'FilterPipeline',
    'FilterBuilder',
    'ContextRecall',
    'ComparativeSearch',
    'StoryGenerator',
    'DrillDownAgent',
    'CrossCheckVerifier',
    'ReportStorage'
]


class SportStatSearchEngine:
    """
    Main search engine interface that orchestrates all search functionality.
    Provides a unified API for natural language queries, semantic search,
    context recall, comparisons, and more.
    """

    def __init__(self, data_fetcher=None, storage_path: str = './search_data'):
        """
        Initialize the search engine.

        Args:
            data_fetcher: Data fetcher for live stats (optional)
            storage_path: Path for storing search indices and reports
        """
        # Initialize components
        self.query_parser = QueryParser()
        self.semantic_search = SemanticSearchEngine(storage_path)
        self.stats_glossary = StatsGlossary()
        self.story_generator = StoryGenerator()
        self.report_storage = ReportStorage(storage_path)
        self.cross_check = CrossCheckVerifier()

        # Initialize context-dependent components
        self.data_fetcher = data_fetcher
        self.context_recall = ContextRecall(self.semantic_search)
        self.comparative_search = ComparativeSearch(data_fetcher, self.semantic_search)
        self.drill_down = DrillDownAgent(data_fetcher, self.semantic_search)

        # Smart completion
        self.smart_completion = SmartPromptCompletion(self.story_generator)

    def query(self, natural_language_query: str, **kwargs) -> Dict:
        """
        Main query interface - handles any natural language question.

        Args:
            natural_language_query: Natural language question
            **kwargs: Additional options (top_k, filters, etc.)

        Returns:
            Query results with answer and supporting data

        Examples:
            >>> engine.query("Which teams have the best net rating since March?")
            >>> engine.query("Show me last time Celtics lost 3 straight")
            >>> engine.query("Compare Ravens Week 3 vs Week 10 defense")
            >>> engine.query("What is EPA?")
        """
        # Parse the query
        parsed = self.query_parser.parse(natural_language_query)

        # Check if it's a stat explanation query
        stat_abbr = self.query_parser.is_stat_explanation_query(natural_language_query)
        if stat_abbr:
            return self._handle_stat_explanation(stat_abbr)

        # Route to appropriate handler based on query type
        query_type = parsed['query_type']

        if query_type == 'comparison':
            return self._handle_comparison(parsed, **kwargs)

        elif query_type == 'history':
            return self._handle_history(parsed, **kwargs)

        elif query_type == 'explain':
            return self._handle_explanation(parsed, **kwargs)

        elif query_type in ['best', 'worst']:
            return self._handle_ranking(parsed, **kwargs)

        else:
            return self._handle_general_query(parsed, **kwargs)

    def ask_the_story(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        "Ask the Story" - semantic search through past reports and digests.

        Args:
            query: Natural language search query
            top_k: Number of results to return

        Returns:
            List of relevant story segments
        """
        # Parse query for better filtering
        parsed = self.query_parser.parse(query)

        # Build filters
        filter_pipeline = FilterBuilder.build_from_parsed_query(parsed)

        # Perform semantic search
        results = self.semantic_search.search(query, top_k=top_k * 2)

        # Apply filters
        if filter_pipeline.filters:
            results = filter_pipeline.apply(results)

        return results[:top_k]

    def explain_stat(self, stat_abbr: str) -> str:
        """
        Get explanation of a statistical term.

        Args:
            stat_abbr: Stat abbreviation (e.g., 'EPA', 'TS%', 'wRC+')

        Returns:
            Formatted explanation
        """
        return self.stats_glossary.format_stat_explanation(stat_abbr)

    def search_stats_glossary(self, query: str, sport: Optional[str] = None) -> List[Dict]:
        """
        Search the stats glossary.

        Args:
            query: Search query
            sport: Optional sport filter

        Returns:
            Matching stats
        """
        return self.stats_glossary.search_stats(query, sport)

    def find_last_occurrence(self, event: str, team: Optional[str] = None,
                            player: Optional[str] = None) -> Optional[Dict]:
        """
        Context recall: Find last time an event occurred.

        Args:
            event: Event description (e.g., "lost 3 straight")
            team: Team name (optional)
            player: Player name (optional)

        Returns:
            Most recent occurrence
        """
        return self.context_recall.find_last_occurrence(event, team, player)

    def compare(self, entity1: str, entity2: str, aspect: Optional[str] = None,
               time_period: Optional[str] = None) -> Dict:
        """
        Compare two entities (players, teams, time periods).

        Args:
            entity1: First entity
            entity2: Second entity
            aspect: What to compare (optional)
            time_period: Time period for comparison (optional)

        Returns:
            Comparison results
        """
        # Determine if comparing players or teams
        # Simple heuristic: check if names have spaces (players) or not (teams)
        if ' ' in entity1 and ' ' in entity2:
            # Likely players
            return self.comparative_search.compare_players(
                entity1, entity2,
                stat_categories=[aspect] if aspect else None,
                time_period=time_period
            )
        else:
            # Likely teams
            return self.comparative_search.compare_teams(
                entity1, entity2,
                aspects=[aspect] if aspect else None
            )

    def stats_to_story(self, data: Dict, story_type: str = 'auto') -> str:
        """
        Generate narrative from statistical data.

        Args:
            data: Statistical data dictionary
            story_type: Type of story ('auto' to detect)

        Returns:
            Generated story text
        """
        return self.story_generator.generate_data_story(data, story_type)

    def drill_down_bullet(self, bullet_point: str,
                         context: Optional[Dict] = None) -> Dict:
        """
        Drill down into a bullet point to see underlying data.

        Args:
            bullet_point: Bullet point text
            context: Optional context

        Returns:
            Detailed data
        """
        return self.drill_down.drill_down(bullet_point, context)

    def cross_check_stat(self, stat_name: str, value: Any,
                        entity: str, context: Optional[Dict] = None) -> Dict:
        """
        Verify a statistic across multiple sources.

        Args:
            stat_name: Name of stat
            value: Value to verify
            entity: Entity (player/team)
            context: Optional context

        Returns:
            Verification result
        """
        return self.cross_check.verify_stat(stat_name, value, entity, context)

    def index_report(self, report: Dict):
        """
        Index a report for searchability.

        Args:
            report: Report data dictionary
        """
        # Store in database
        report_id = self.report_storage.store_report(report)

        # Index in semantic search
        content = report.get('content', '')
        metadata = {
            'sport': report.get('sport'),
            'date': report.get('date') or report.get('timestamp'),
            'teams': report.get('teams', []),
            'players': report.get('players', [])
        }

        self.semantic_search.index_report(report_id, content, metadata)

        # Index sections if present
        if 'sections' in report:
            sections = []
            for i, section in enumerate(report['sections']):
                sections.append({
                    'title': section.get('title', f'Section {i+1}'),
                    'content': section.get('content', ''),
                    'metadata': {
                        **metadata,
                        'section_type': section.get('type')
                    }
                })

            self.semantic_search.index_report_sections(report_id, sections)

    def complete_prompt(self, partial_text: str,
                       context: Optional[Dict] = None) -> List[str]:
        """
        Smart prompt completion for writing.

        Args:
            partial_text: Incomplete text
            context: Optional context

        Returns:
            List of completion suggestions
        """
        return self.smart_completion.complete_prompt(partial_text, context)

    # Private handler methods

    def _handle_stat_explanation(self, stat_abbr: str) -> Dict:
        """Handle stat explanation queries."""
        explanation = self.explain_stat(stat_abbr)

        return {
            'query_type': 'stat_explanation',
            'stat': stat_abbr,
            'answer': explanation,
            'source': 'stats_glossary'
        }

    def _handle_comparison(self, parsed: Dict, **kwargs) -> Dict:
        """Handle comparison queries."""
        entities = parsed.get('entities', [])

        # Extract the two entities to compare
        teams = [e['value'] for e in entities if e['type'] == 'team']
        players = [e['value'] for e in entities if e['type'] == 'player']

        if len(teams) >= 2:
            comparison = self.compare(teams[0], teams[1])
        elif len(players) >= 2:
            comparison = self.compare(players[0], players[1])
        else:
            return {
                'query_type': 'comparison',
                'error': 'Could not identify two entities to compare',
                'parsed': parsed
            }

        return {
            'query_type': 'comparison',
            'answer': comparison,
            'source': 'comparative_search'
        }

    def _handle_history(self, parsed: Dict, **kwargs) -> Dict:
        """Handle historical/context recall queries."""
        teams = parsed.get('teams', [])
        event = parsed['original_query']

        result = self.find_last_occurrence(
            event,
            team=teams[0] if teams else None
        )

        return {
            'query_type': 'history',
            'answer': result,
            'source': 'context_recall'
        }

    def _handle_explanation(self, parsed: Dict, **kwargs) -> Dict:
        """Handle explanation queries."""
        # Try to find what they want explained
        stats = parsed.get('stats', [])

        if stats:
            explanation = self.explain_stat(stats[0])
            return {
                'query_type': 'explanation',
                'answer': explanation,
                'source': 'stats_glossary'
            }

        # General explanation - use semantic search
        results = self.semantic_search.search(
            parsed['original_query'],
            top_k=3
        )

        return {
            'query_type': 'explanation',
            'answer': results,
            'source': 'semantic_search'
        }

    def _handle_ranking(self, parsed: Dict, **kwargs) -> Dict:
        """Handle best/worst ranking queries."""
        # Use semantic search to find relevant information
        results = self.semantic_search.search(
            parsed['original_query'],
            top_k=kwargs.get('top_k', 10)
        )

        return {
            'query_type': parsed['query_type'],
            'answer': results,
            'source': 'semantic_search',
            'parsed': parsed
        }

    def _handle_general_query(self, parsed: Dict, **kwargs) -> Dict:
        """Handle general queries."""
        # Build filters from parsed query
        filter_pipeline = FilterBuilder.build_from_parsed_query(parsed)

        # Perform semantic search
        results = self.semantic_search.search(
            parsed['original_query'],
            top_k=kwargs.get('top_k', 5)
        )

        # Apply filters
        if filter_pipeline.filters:
            results = filter_pipeline.apply(results)

        return {
            'query_type': 'general',
            'answer': results,
            'source': 'semantic_search',
            'parsed': parsed
        }

    def get_stats(self) -> Dict:
        """Get search engine statistics."""
        return {
            'semantic_search': self.semantic_search.get_stats(),
            'storage': self.report_storage.get_stats(),
            'glossary_stats': len(self.stats_glossary.get_all_stats_list())
        }
