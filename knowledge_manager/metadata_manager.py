"""
Metadata Manager - Tagging and metadata operations
"""

from typing import List, Dict, Set, Optional
from datetime import datetime
from collections import Counter

from .database_handler import DatabaseHandler
from .models import DocumentMetadata, League, DocumentType


class MetadataManager:
    """Manages document metadata and tagging system"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def add_tags(self, doc_id: str, tags: Set[str]) -> bool:
        """Add multiple tags to a document"""
        for tag in tags:
            self.db.add_tag(doc_id, tag)
        return True

    def get_documents_by_tag(self, tag: str) -> List[Dict]:
        """Get all documents with a specific tag"""
        return self.db.get_documents_by_tag(tag)

    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, any]]:
        """Get most frequently used tags"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag_name, usage_count
                FROM tags
                ORDER BY usage_count DESC
                LIMIT ?
            """, (limit,))
            return [{'tag': row['tag_name'], 'count': row['usage_count']}
                   for row in cursor.fetchall()]

    def get_related_tags(self, tag: str, limit: int = 10) -> List[str]:
        """Get tags that frequently appear with this tag"""
        # Find documents with this tag
        docs = self.get_documents_by_tag(tag)

        # Collect all other tags from these documents
        tag_counter = Counter()
        for doc in docs:
            metadata = doc.get('metadata', {})
            doc_tags = metadata.get('tags', [])
            for doc_tag in doc_tags:
                if doc_tag != tag:
                    tag_counter[doc_tag] += 1

        return [tag for tag, _ in tag_counter.most_common(limit)]

    def search_by_tags(self, tags: Set[str], match_all: bool = True) -> List[Dict]:
        """Search documents by multiple tags"""
        if not tags:
            return []

        if match_all:
            # Documents must have ALL tags
            results = None
            for tag in tags:
                docs = self.db.get_documents_by_tag(tag)
                doc_ids = {doc['doc_id'] for doc in docs}

                if results is None:
                    results = doc_ids
                else:
                    results = results.intersection(doc_ids)

            if results:
                return [self.db.get_document(doc_id) for doc_id in results]
            return []
        else:
            # Documents can have ANY of the tags
            doc_ids = set()
            for tag in tags:
                docs = self.db.get_documents_by_tag(tag)
                doc_ids.update(doc['doc_id'] for doc in docs)

            return [self.db.get_document(doc_id) for doc_id in doc_ids]

    def auto_tag_document(self, content: str, title: str) -> Set[str]:
        """Automatically suggest tags for a document based on content"""
        suggested_tags = set()

        # Tag by content type
        content_lower = content.lower()
        title_lower = title.lower()

        # Content type tags
        if any(word in content_lower for word in ['injury', 'injured', 'out for']):
            suggested_tags.add('injury')
        if any(word in content_lower for word in ['preview', 'upcoming', 'matchup']):
            suggested_tags.add('preview')
        if any(word in content_lower for word in ['recap', 'final score', 'result']):
            suggested_tags.add('recap')
        if any(word in content_lower for word in ['feature', 'profile', 'spotlight']):
            suggested_tags.add('feature')
        if any(word in content_lower for word in ['betting', 'odds', 'spread']):
            suggested_tags.add('betting')
        if any(word in content_lower for word in ['stat', 'analytics', 'metrics']):
            suggested_tags.add('analytics')

        # Situation tags
        if any(word in content_lower for word in ['playoff', 'postseason']):
            suggested_tags.add('playoffs')
        if any(word in content_lower for word in ['trade', 'signing', 'roster']):
            suggested_tags.add('roster-moves')
        if any(word in content_lower for word in ['streak', 'winning', 'losing']):
            suggested_tags.add('trends')

        return suggested_tags

    def get_tag_stats(self) -> Dict:
        """Get statistics about tag usage"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Total tags
            cursor.execute("SELECT COUNT(*) as count FROM tags")
            total_tags = cursor.fetchone()['count']

            # Most used tag
            cursor.execute("""
                SELECT tag_name, usage_count FROM tags
                ORDER BY usage_count DESC LIMIT 1
            """)
            most_used = cursor.fetchone()

            # Average usage
            cursor.execute("SELECT AVG(usage_count) as avg FROM tags")
            avg_usage = cursor.fetchone()['avg']

            return {
                'total_tags': total_tags,
                'most_used_tag': most_used['tag_name'] if most_used else None,
                'most_used_count': most_used['usage_count'] if most_used else 0,
                'average_usage': round(avg_usage, 2) if avg_usage else 0
            }

    def merge_tags(self, old_tag: str, new_tag: str) -> bool:
        """Merge one tag into another (rename)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Update all document_tags entries
            cursor.execute("""
                UPDATE document_tags
                SET tag_name = ?
                WHERE tag_name = ?
            """, (new_tag, old_tag))

            # Update tag usage count
            cursor.execute("""
                UPDATE tags
                SET usage_count = usage_count + (
                    SELECT usage_count FROM tags WHERE tag_name = ?
                )
                WHERE tag_name = ?
            """, (old_tag, new_tag))

            # Delete old tag
            cursor.execute("DELETE FROM tags WHERE tag_name = ?", (old_tag,))

            return True

    def get_documents_by_league(self, league: League) -> List[Dict]:
        """Get all documents for a specific league"""
        return self.db.search_documents("", league=league.value)

    def get_documents_by_type(self, doc_type: DocumentType) -> List[Dict]:
        """Get all documents of a specific type"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.document_type') = ?
                ORDER BY updated_at DESC
            """, (doc_type.value,))
            return [self.db._row_to_dict(row) for row in cursor.fetchall()]

    def get_documents_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get documents within a date range"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.date') BETWEEN ? AND ?
                ORDER BY json_extract(metadata, '$.date') DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            return [self.db._row_to_dict(row) for row in cursor.fetchall()]

    def get_documents_by_author(self, author: str) -> List[Dict]:
        """Get all documents by an author"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # This is a simplified query - JSON array searching is complex in SQLite
            cursor.execute("""
                SELECT * FROM documents
                WHERE metadata LIKE ?
                ORDER BY updated_at DESC
            """, (f'%{author}%',))
            results = []
            for row in cursor.fetchall():
                doc = self.db._row_to_dict(row)
                if author in doc.get('metadata', {}).get('authors', []):
                    results.append(doc)
            return results
