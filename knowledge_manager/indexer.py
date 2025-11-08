"""
Auto-Indexer - Builds tables of contents by week, sport, and story type
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .database_handler import DatabaseHandler
from .models import League, DocumentType


class AutoIndexer:
    """Automatically generates indexes and tables of contents"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def build_weekly_index(
        self,
        league: Optional[League] = None,
        weeks_back: int = 4
    ) -> Dict:
        """Build index organized by week"""
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)

        # Get all documents in date range
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.date') BETWEEN ? AND ?
            """
            params = [start_date.isoformat(), end_date.isoformat()]

            if league:
                query += " AND json_extract(metadata, '$.league') = ?"
                params.append(league.value)

            query += " ORDER BY json_extract(metadata, '$.date') DESC"

            cursor.execute(query, params)
            docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

        # Organize by week
        weekly_index = defaultdict(list)

        for doc in docs:
            doc_date = datetime.fromisoformat(doc['metadata']['date'])
            # Get week start (Monday)
            week_start = doc_date - timedelta(days=doc_date.weekday())
            week_key = week_start.strftime('%Y-W%U')  # Year-Week format

            weekly_index[week_key].append({
                'doc_id': doc['doc_id'],
                'title': doc['title'],
                'date': doc['metadata']['date'],
                'type': doc['metadata']['document_type'],
                'league': doc['metadata']['league']
            })

        # Sort weeks
        sorted_index = {
            week: sorted(docs, key=lambda x: x['date'], reverse=True)
            for week, docs in sorted(weekly_index.items(), reverse=True)
        }

        return {
            'type': 'weekly',
            'league': league.value if league else 'all',
            'weeks': sorted_index,
            'total_documents': len(docs),
            'generated_at': datetime.now().isoformat()
        }

    def build_sport_index(self) -> Dict:
        """Build index organized by sport/league"""
        sport_index = {}

        for league in League:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM documents
                    WHERE json_extract(metadata, '$.league') = ?
                    ORDER BY json_extract(metadata, '$.date') DESC
                    LIMIT 100
                """, (league.value,))

                docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

                sport_index[league.value] = {
                    'total': len(docs),
                    'recent_documents': [
                        {
                            'doc_id': doc['doc_id'],
                            'title': doc['title'],
                            'date': doc['metadata']['date'],
                            'type': doc['metadata']['document_type']
                        }
                        for doc in docs[:20]
                    ]
                }

        return {
            'type': 'sport',
            'sports': sport_index,
            'generated_at': datetime.now().isoformat()
        }

    def build_story_type_index(self, league: Optional[League] = None) -> Dict:
        """Build index organized by story type"""
        type_index = {}

        for doc_type in DocumentType:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT * FROM documents
                    WHERE json_extract(metadata, '$.document_type') = ?
                """
                params = [doc_type.value]

                if league:
                    query += " AND json_extract(metadata, '$.league') = ?"
                    params.append(league.value)

                query += " ORDER BY json_extract(metadata, '$.date') DESC LIMIT 50"

                cursor.execute(query, params)
                docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

                type_index[doc_type.value] = {
                    'total': len(docs),
                    'documents': [
                        {
                            'doc_id': doc['doc_id'],
                            'title': doc['title'],
                            'date': doc['metadata']['date'],
                            'league': doc['metadata']['league']
                        }
                        for doc in docs
                    ]
                }

        return {
            'type': 'story_type',
            'league': league.value if league else 'all',
            'story_types': type_index,
            'generated_at': datetime.now().isoformat()
        }

    def build_master_index(self) -> Dict:
        """Build comprehensive master index with all organizations"""
        return {
            'weekly': self.build_weekly_index(),
            'by_sport': self.build_sport_index(),
            'by_type': self.build_story_type_index(),
            'generated_at': datetime.now().isoformat()
        }

    def generate_table_of_contents(
        self,
        league: League,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Generate markdown table of contents"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.league') = ?
                AND json_extract(metadata, '$.date') BETWEEN ? AND ?
                ORDER BY json_extract(metadata, '$.date') DESC
            """, (league.value, start_date.isoformat(), end_date.isoformat()))

            docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

        # Generate markdown
        toc = f"# Table of Contents - {league.value.upper()}\n\n"
        toc += f"**Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n"
        toc += f"**Total Documents:** {len(docs)}\n\n"

        # Group by type
        by_type = defaultdict(list)
        for doc in docs:
            doc_type = doc['metadata']['document_type']
            by_type[doc_type].append(doc)

        # Generate sections
        for doc_type, type_docs in sorted(by_type.items()):
            toc += f"## {doc_type.replace('_', ' ').title()} ({len(type_docs)})\n\n"
            for doc in type_docs:
                date = datetime.fromisoformat(doc['metadata']['date']).strftime('%Y-%m-%d')
                toc += f"- [{doc['title']}](doc:{doc['doc_id']}) - {date}\n"
            toc += "\n"

        toc += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return toc

    def build_team_index(self, team_name: str) -> Dict:
        """Build index of all documents mentioning a specific team"""
        mentions = self.db.find_mentions(team_name, limit=1000)

        docs_by_type = defaultdict(list)
        docs_by_month = defaultdict(list)

        for mention in mentions:
            doc = self.db.get_document(mention['doc_id'])
            if doc:
                doc_type = doc['metadata']['document_type']
                date = datetime.fromisoformat(doc['metadata']['date'])
                month_key = date.strftime('%Y-%m')

                doc_entry = {
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'date': doc['metadata']['date'],
                    'type': doc_type
                }

                docs_by_type[doc_type].append(doc_entry)
                docs_by_month[month_key].append(doc_entry)

        return {
            'team': team_name,
            'total_mentions': len(mentions),
            'by_type': dict(docs_by_type),
            'by_month': dict(sorted(docs_by_month.items(), reverse=True)),
            'generated_at': datetime.now().isoformat()
        }

    def build_player_index(self, player_name: str) -> Dict:
        """Build index of all documents mentioning a specific player"""
        mentions = self.db.find_mentions(player_name, limit=1000)

        timeline = []
        by_league = defaultdict(list)

        for mention in mentions:
            doc = self.db.get_document(mention['doc_id'])
            if doc:
                league = doc['metadata']['league']
                doc_entry = {
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'date': doc['metadata']['date'],
                    'type': doc['metadata']['document_type'],
                    'league': league
                }

                timeline.append(doc_entry)
                by_league[league].append(doc_entry)

        # Sort timeline
        timeline.sort(key=lambda x: x['date'], reverse=True)

        return {
            'player': player_name,
            'total_mentions': len(mentions),
            'timeline': timeline,
            'by_league': dict(by_league),
            'generated_at': datetime.now().isoformat()
        }

    def generate_archive_summary(self, days_back: int = 7) -> str:
        """Generate 'This Week in Sports Intelligence' summary"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.date') BETWEEN ? AND ?
                ORDER BY json_extract(metadata, '$.date') DESC
            """, (start_date.isoformat(), end_date.isoformat()))

            docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

        # Generate summary
        summary = f"# This Week in Sports Intelligence\n\n"
        summary += f"**{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}**\n\n"

        # Stats
        summary += f"📊 **Total Coverage:** {len(docs)} documents\n\n"

        # By league
        by_league = defaultdict(int)
        by_type = defaultdict(int)
        for doc in docs:
            by_league[doc['metadata']['league']] += 1
            by_type[doc['metadata']['document_type']] += 1

        summary += "## Coverage by League\n\n"
        for league, count in sorted(by_league.items(), key=lambda x: x[1], reverse=True):
            summary += f"- **{league.upper()}**: {count} stories\n"

        summary += "\n## Coverage by Type\n\n"
        for doc_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary += f"- **{doc_type.replace('_', ' ').title()}**: {count}\n"

        summary += "\n## Recent Headlines\n\n"
        for doc in docs[:10]:
            date = datetime.fromisoformat(doc['metadata']['date']).strftime('%b %d')
            summary += f"- **{date}** - {doc['title']} ({doc['metadata']['league'].upper()})\n"

        summary += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return summary
