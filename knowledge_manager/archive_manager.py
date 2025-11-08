"""
Archive Manager - Auto-archive old documents and cleanup routines
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import json

from .database_handler import DatabaseHandler
from .models import DocumentVersion


class ArchiveManager:
    """Manages document archiving and cleanup"""

    def __init__(
        self,
        db_path: str = "knowledge_manager/database/sports_knowledge.db",
        storage_path: str = "knowledge_manager/storage",
        archive_path: str = "knowledge_manager/archive"
    ):
        self.db = DatabaseHandler(db_path)
        self.storage_path = Path(storage_path)
        self.archive_path = Path(archive_path)
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def auto_archive(self, days_old: int = 30, dry_run: bool = False) -> Dict:
        """
        Automatically archive documents older than specified days

        Args:
            days_old: Archive documents older than this many days
            dry_run: If True, only report what would be archived without archiving
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.date') < ?
                AND json_extract(metadata, '$.version') != ?
            """, (cutoff_date.isoformat(), DocumentVersion.ARCHIVED.value))

            candidates = [self.db._row_to_dict(row) for row in cursor.fetchall()]

        archived_count = 0
        archived_docs = []

        for doc in candidates:
            if not dry_run:
                success = self.archive_document(doc['doc_id'])
                if success:
                    archived_count += 1
                    archived_docs.append({
                        'doc_id': doc['doc_id'],
                        'title': doc['title'],
                        'date': doc['metadata']['date']
                    })
            else:
                archived_docs.append({
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'date': doc['metadata']['date']
                })
                archived_count += 1

        return {
            'cutoff_date': cutoff_date.isoformat(),
            'candidates': len(candidates),
            'archived': archived_count,
            'documents': archived_docs,
            'dry_run': dry_run
        }

    def archive_document(self, doc_id: str) -> bool:
        """Archive a single document"""
        doc = self.db.get_document(doc_id)
        if not doc:
            return False

        # Create archive folder structure
        doc_date = datetime.fromisoformat(doc['metadata']['date'])
        year_month = doc_date.strftime('%Y-%m')
        archive_folder = self.archive_path / year_month
        archive_folder.mkdir(parents=True, exist_ok=True)

        # Move document file to archive
        source_file = self.storage_path / f"{doc_id}.md"
        if source_file.exists():
            dest_file = archive_folder / f"{doc_id}.md"
            shutil.move(str(source_file), str(dest_file))

        # Update document version in database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE documents
                SET metadata = json_set(metadata, '$.version', ?)
                WHERE doc_id = ?
            """, (DocumentVersion.ARCHIVED.value, doc_id))

        # Save archive metadata
        self._save_archive_metadata(doc_id, doc, archive_folder)

        return True

    def restore_document(self, doc_id: str) -> bool:
        """Restore an archived document"""
        doc = self.db.get_document(doc_id)
        if not doc:
            return False

        # Find archived file
        doc_date = datetime.fromisoformat(doc['metadata']['date'])
        year_month = doc_date.strftime('%Y-%m')
        archive_folder = self.archive_path / year_month
        source_file = archive_folder / f"{doc_id}.md"

        if not source_file.exists():
            return False

        # Move back to storage
        dest_file = self.storage_path / f"{doc_id}.md"
        shutil.move(str(source_file), str(dest_file))

        # Update version
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE documents
                SET metadata = json_set(metadata, '$.version', ?)
                WHERE doc_id = ?
            """, (DocumentVersion.PUBLISHED.value, doc_id))

        return True

    def cleanup_old_revisions(self, keep_recent: int = 10) -> Dict:
        """
        Clean up old revision history, keeping only recent revisions

        Args:
            keep_recent: Number of recent revisions to keep per document
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get all documents
            cursor.execute("SELECT DISTINCT doc_id FROM revisions")
            doc_ids = [row['doc_id'] for row in cursor.fetchall()]

            total_deleted = 0

            for doc_id in doc_ids:
                # Get revisions for this document
                cursor.execute("""
                    SELECT revision_id FROM revisions
                    WHERE doc_id = ?
                    ORDER BY timestamp DESC
                """, (doc_id,))

                revisions = [row['revision_id'] for row in cursor.fetchall()]

                # Delete old revisions
                if len(revisions) > keep_recent:
                    to_delete = revisions[keep_recent:]
                    for revision_id in to_delete:
                        cursor.execute("""
                            DELETE FROM revisions WHERE revision_id = ?
                        """, (revision_id,))
                        total_deleted += 1

        return {
            'documents_processed': len(doc_ids),
            'revisions_deleted': total_deleted,
            'kept_per_document': keep_recent
        }

    def get_archive_stats(self) -> Dict:
        """Get statistics about archived documents"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Total archived
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE json_extract(metadata, '$.version') = ?
            """, (DocumentVersion.ARCHIVED.value,))
            total_archived = cursor.fetchone()['count']

            # Archived by league
            cursor.execute("""
                SELECT
                    json_extract(metadata, '$.league') as league,
                    COUNT(*) as count
                FROM documents
                WHERE json_extract(metadata, '$.version') = ?
                GROUP BY league
            """, (DocumentVersion.ARCHIVED.value,))

            by_league = {row['league']: row['count'] for row in cursor.fetchall()}

            # Archive size (file system)
            total_size = sum(
                f.stat().st_size
                for f in self.archive_path.rglob('*.md')
            )

        return {
            'total_archived': total_archived,
            'by_league': by_league,
            'archive_size_mb': round(total_size / (1024 * 1024), 2),
            'archive_path': str(self.archive_path)
        }

    def list_archived_documents(
        self,
        year_month: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List archived documents"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.version') = ?
            """
            params = [DocumentVersion.ARCHIVED.value]

            if year_month:
                # Filter by year-month
                start = f"{year_month}-01"
                # Calculate end of month
                year, month = year_month.split('-')
                if month == '12':
                    end = f"{int(year)+1}-01-01"
                else:
                    end = f"{year}-{int(month)+1:02d}-01"

                query += " AND json_extract(metadata, '$.date') BETWEEN ? AND ?"
                params.extend([start, end])

            query += " ORDER BY json_extract(metadata, '$.date') DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [self.db._row_to_dict(row) for row in cursor.fetchall()]

    def schedule_cleanup(self) -> Dict:
        """Run all cleanup routines"""
        results = {
            'auto_archive': self.auto_archive(days_old=30),
            'revision_cleanup': self.cleanup_old_revisions(keep_recent=10),
            'timestamp': datetime.now().isoformat()
        }

        return results

    def _save_archive_metadata(self, doc_id: str, doc: Dict, archive_folder: Path):
        """Save metadata about archived document"""
        metadata_file = archive_folder / f"{doc_id}_metadata.json"

        metadata = {
            'doc_id': doc_id,
            'archived_at': datetime.now().isoformat(),
            'original_metadata': doc.get('metadata', {}),
            'title': doc['title'],
            'revision_count': doc.get('revision_count', 0)
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def export_archive_index(self, output_file: str = "archive_index.json"):
        """Export complete archive index to JSON"""
        archived_docs = self.list_archived_documents(limit=10000)

        index = {
            'generated_at': datetime.now().isoformat(),
            'total_documents': len(archived_docs),
            'documents': [
                {
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'date': doc['metadata']['date'],
                    'league': doc['metadata']['league'],
                    'type': doc['metadata']['document_type']
                }
                for doc in archived_docs
            ]
        }

        output_path = self.archive_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

        return str(output_path)
