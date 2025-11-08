"""
Quick Recall Agent - Instant lookup for player/team mentions
Type a player or team name and instantly find their last 5 mentions
"""

from typing import List, Dict, Optional
from datetime import datetime

from .database_handler import DatabaseHandler
from .models import League


class QuickRecallAgent:
    """Quick recall system for finding entity mentions"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def recall(self, entity_name: str, limit: int = 5) -> Dict:
        """
        Quick recall - find last N mentions of a player or team

        Returns:
        - mentions: List of mention details
        - summary: Quick summary of mentions
        """
        mentions = self.db.find_mentions(entity_name, limit=limit)

        if not mentions:
            return {
                'entity': entity_name,
                'found': False,
                'mentions': [],
                'summary': f"No mentions found for '{entity_name}'"
            }

        # Get full document details
        detailed_mentions = []
        for mention in mentions:
            doc = self.db.get_document(mention['doc_id'])
            if doc:
                detailed_mentions.append({
                    'doc_id': mention['doc_id'],
                    'title': mention['title'],
                    'date': mention['doc_date'],
                    'entity_type': mention['entity_type'],
                    'mention_count': mention['mention_count'],
                    'context': mention.get('context', ''),
                    'league': doc.get('metadata', {}).get('league'),
                    'doc_type': doc.get('metadata', {}).get('document_type'),
                })

        summary = self._generate_summary(entity_name, detailed_mentions)

        return {
            'entity': entity_name,
            'found': True,
            'total_mentions': len(detailed_mentions),
            'mentions': detailed_mentions,
            'summary': summary
        }

    def recall_player(self, player_name: str, limit: int = 5) -> Dict:
        """Recall specific to players"""
        result = self.recall(player_name, limit)

        # Filter to only player mentions
        if result['found']:
            result['mentions'] = [
                m for m in result['mentions']
                if m['entity_type'] == 'player'
            ]

        return result

    def recall_team(self, team_name: str, limit: int = 5) -> Dict:
        """Recall specific to teams"""
        result = self.recall(team_name, limit)

        # Filter to only team mentions
        if result['found']:
            result['mentions'] = [
                m for m in result['mentions']
                if m['entity_type'] == 'team'
            ]

        return result

    def compare_entities(self, entity1: str, entity2: str, limit: int = 10) -> Dict:
        """Compare mentions of two entities (e.g., two players, two teams)"""
        mentions1 = self.recall(entity1, limit)
        mentions2 = self.recall(entity2, limit)

        # Find documents mentioning both
        docs1 = {m['doc_id'] for m in mentions1['mentions']}
        docs2 = {m['doc_id'] for m in mentions2['mentions']}
        common_docs = docs1.intersection(docs2)

        comparison = {
            'entity1': entity1,
            'entity2': entity2,
            'entity1_mentions': mentions1['total_mentions'],
            'entity2_mentions': mentions2['total_mentions'],
            'common_mentions': len(common_docs),
            'common_docs': [
                self.db.get_document(doc_id) for doc_id in common_docs
            ]
        }

        return comparison

    def get_entity_timeline(self, entity_name: str, limit: int = 20) -> List[Dict]:
        """Get chronological timeline of entity mentions"""
        mentions = self.db.find_mentions(entity_name, limit=limit)

        timeline = []
        for mention in mentions:
            doc = self.db.get_document(mention['doc_id'])
            if doc:
                timeline.append({
                    'date': mention['doc_date'],
                    'title': mention['title'],
                    'doc_id': mention['doc_id'],
                    'league': doc.get('metadata', {}).get('league'),
                    'type': doc.get('metadata', {}).get('document_type'),
                })

        # Sort by date
        timeline.sort(key=lambda x: x['date'], reverse=True)

        return timeline

    def get_entity_stats(self, entity_name: str) -> Dict:
        """Get statistics about an entity's mentions"""
        mentions = self.db.find_mentions(entity_name, limit=1000)

        if not mentions:
            return {
                'entity': entity_name,
                'total_mentions': 0,
                'documents': 0,
                'leagues': [],
                'first_mention': None,
                'last_mention': None,
                'avg_mentions_per_doc': 0
            }

        # Gather statistics
        doc_ids = set()
        leagues = set()
        dates = []
        total_mention_count = 0

        for mention in mentions:
            doc_ids.add(mention['doc_id'])
            total_mention_count += mention.get('mention_count', 1)
            dates.append(mention['doc_date'])

            doc = self.db.get_document(mention['doc_id'])
            if doc:
                league = doc.get('metadata', {}).get('league')
                if league:
                    leagues.add(league)

        dates.sort()

        return {
            'entity': entity_name,
            'total_mentions': len(mentions),
            'documents': len(doc_ids),
            'leagues': list(leagues),
            'first_mention': dates[0] if dates else None,
            'last_mention': dates[-1] if dates else None,
            'avg_mentions_per_doc': round(total_mention_count / len(doc_ids), 2) if doc_ids else 0
        }

    def search_similar_entities(self, entity_name: str, limit: int = 5) -> List[str]:
        """Find entities with similar names (fuzzy matching)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT entity_name
                FROM mentions
                WHERE entity_name LIKE ?
                LIMIT ?
            """, (f"%{entity_name}%", limit))

            return [row['entity_name'] for row in cursor.fetchall()]

    def _generate_summary(self, entity_name: str, mentions: List[Dict]) -> str:
        """Generate a quick summary of mentions"""
        if not mentions:
            return f"No recent mentions of {entity_name}"

        latest = mentions[0]
        count = len(mentions)

        summary = f"{entity_name} mentioned in {count} recent document(s). "
        summary += f"Latest: '{latest['title']}' ({latest['date']})"

        # Check for trends
        leagues = set(m['league'] for m in mentions if m.get('league'))
        if leagues:
            summary += f" | Leagues: {', '.join(leagues)}"

        return summary

    def batch_recall(self, entities: List[str], limit: int = 3) -> Dict[str, Dict]:
        """Recall multiple entities at once"""
        results = {}
        for entity in entities:
            results[entity] = self.recall(entity, limit)
        return results
