"""
Search Engine - Advanced search capabilities including stat-based queries
"""

from typing import List, Dict, Optional, Set
from datetime import datetime

from .database_handler import DatabaseHandler
from .models import League, DocumentType


class SearchEngine:
    """Advanced search engine for sports content"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def search(
        self,
        query: str,
        league: Optional[League] = None,
        folder: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        doc_type: Optional[DocumentType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """Comprehensive search across all documents"""
        results = self.db.search_documents(
            query,
            league=league.value if league else None,
            folder=folder
        )

        # Apply additional filters
        if tags:
            results = [doc for doc in results
                      if any(tag in doc.get('metadata', {}).get('tags', [])
                            for tag in tags)]

        if doc_type:
            results = [doc for doc in results
                      if doc.get('metadata', {}).get('document_type') == doc_type.value]

        if date_from or date_to:
            filtered = []
            for doc in results:
                doc_date_str = doc.get('metadata', {}).get('date')
                if doc_date_str:
                    doc_date = datetime.fromisoformat(doc_date_str)
                    if date_from and doc_date < date_from:
                        continue
                    if date_to and doc_date > date_to:
                        continue
                    filtered.append(doc)
            results = filtered

        return results

    def search_by_stat(
        self,
        stat_name: str,
        operator: str = ">",
        value: float = 0,
        league: Optional[League] = None
    ) -> List[Dict]:
        """
        Search for stories mentioning specific statistical thresholds
        Examples:
        - Find all stories with xG > 2
        - Find all stories with EPA/play > 0.25
        """
        results = self.db.search_by_stat(stat_name, operator, value)

        if league:
            results = [doc for doc in results
                      if doc.get('metadata', {}).get('league') == league.value]

        return results

    def search_by_player(self, player_name: str, limit: int = 50) -> List[Dict]:
        """Find all stories mentioning a specific player"""
        mentions = self.db.find_mentions(player_name, limit=limit)

        # Get full documents
        doc_ids = list(set(m['doc_id'] for m in mentions))
        results = []
        for doc_id in doc_ids:
            doc = self.db.get_document(doc_id)
            if doc:
                # Add mention context
                doc['mention_context'] = [
                    m for m in mentions if m['doc_id'] == doc_id
                ]
                results.append(doc)

        return results

    def search_by_team(self, team_name: str, limit: int = 50) -> List[Dict]:
        """Find all stories mentioning a specific team"""
        mentions = self.db.find_mentions(team_name, limit=limit)

        doc_ids = list(set(m['doc_id'] for m in mentions))
        results = []
        for doc_id in doc_ids:
            doc = self.db.get_document(doc_id)
            if doc:
                doc['mention_context'] = [
                    m for m in mentions if m['doc_id'] == doc_id
                ]
                results.append(doc)

        return results

    def search_by_matchup(self, team1: str, team2: str) -> List[Dict]:
        """Find stories about a specific matchup"""
        # Find documents mentioning both teams
        team1_docs = {m['doc_id'] for m in self.db.find_mentions(team1, limit=100)}
        team2_docs = {m['doc_id'] for m in self.db.find_mentions(team2, limit=100)}

        # Intersection - documents mentioning both teams
        common_doc_ids = team1_docs.intersection(team2_docs)

        results = []
        for doc_id in common_doc_ids:
            doc = self.db.get_document(doc_id)
            if doc:
                results.append(doc)

        # Sort by date descending
        results.sort(
            key=lambda d: d.get('metadata', {}).get('date', ''),
            reverse=True
        )

        return results

    def advanced_search(self, filters: Dict) -> List[Dict]:
        """
        Advanced search with complex filters

        Filters:
        - text: text search query
        - league: League enum
        - tags: Set of tags (match any)
        - teams: List of teams (match any)
        - players: List of players (match any)
        - stats: Dict of {stat_name: (operator, value)}
        - date_range: (start_date, end_date)
        - version: Document version
        """
        # Start with text search or all documents
        if filters.get('text'):
            results = self.db.search_documents(
                filters['text'],
                league=filters.get('league').value if filters.get('league') else None
            )
        else:
            # Get all documents (would need optimization for large datasets)
            results = []

        # Apply team filter
        if filters.get('teams'):
            team_doc_ids = set()
            for team in filters['teams']:
                mentions = self.db.find_mentions(team, limit=1000)
                team_doc_ids.update(m['doc_id'] for m in mentions)

            if not results:
                results = [self.db.get_document(doc_id) for doc_id in team_doc_ids]
            else:
                results = [doc for doc in results if doc['doc_id'] in team_doc_ids]

        # Apply player filter
        if filters.get('players'):
            player_doc_ids = set()
            for player in filters['players']:
                mentions = self.db.find_mentions(player, limit=1000)
                player_doc_ids.update(m['doc_id'] for m in mentions)

            if not results:
                results = [self.db.get_document(doc_id) for doc_id in player_doc_ids]
            else:
                results = [doc for doc in results if doc['doc_id'] in player_doc_ids]

        # Apply stat filters
        if filters.get('stats'):
            for stat_name, (operator, value) in filters['stats'].items():
                stat_results = self.db.search_by_stat(stat_name, operator, value)
                stat_doc_ids = {doc['doc_id'] for doc in stat_results}

                if not results:
                    results = stat_results
                else:
                    results = [doc for doc in results if doc['doc_id'] in stat_doc_ids]

        # Apply tag filter
        if filters.get('tags'):
            results = [doc for doc in results
                      if any(tag in doc.get('metadata', {}).get('tags', [])
                            for tag in filters['tags'])]

        # Apply date range filter
        if filters.get('date_range'):
            start_date, end_date = filters['date_range']
            filtered = []
            for doc in results:
                doc_date_str = doc.get('metadata', {}).get('date')
                if doc_date_str:
                    doc_date = datetime.fromisoformat(doc_date_str)
                    if start_date <= doc_date <= end_date:
                        filtered.append(doc)
            results = filtered

        # Apply version filter
        if filters.get('version'):
            results = [doc for doc in results
                      if doc.get('metadata', {}).get('version') == filters['version']]

        return results

    def fuzzy_search(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """Fuzzy text search (simple implementation using LIKE)"""
        # This is a simplified version - could be enhanced with Levenshtein distance
        words = query.lower().split()
        all_results = []

        for word in words:
            results = self.db.search_documents(word)
            all_results.extend(results)

        # Remove duplicates and sort by relevance (simplified)
        seen = set()
        unique_results = []
        for doc in all_results:
            if doc['doc_id'] not in seen:
                seen.add(doc['doc_id'])
                unique_results.append(doc)

        return unique_results

    def get_trending_topics(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending topics based on recent document creation"""
        from datetime import timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.entity_name, m.entity_type, COUNT(*) as mention_count
                FROM mentions m
                JOIN documents d ON m.doc_id = d.doc_id
                WHERE m.created_at >= ?
                GROUP BY m.entity_name, m.entity_type
                ORDER BY mention_count DESC
                LIMIT ?
            """, (start_date.isoformat(), limit))

            return [
                {
                    'entity': row['entity_name'],
                    'type': row['entity_type'],
                    'mentions': row['mention_count']
                }
                for row in cursor.fetchall()
            ]
