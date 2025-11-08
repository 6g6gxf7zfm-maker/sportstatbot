"""
Database handler for the knowledge management system
Uses SQLite for metadata, indexes, and relationships
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from datetime import datetime


class DatabaseHandler:
    """Manages SQLite database for knowledge management"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    folder_path TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    revision_count INTEGER DEFAULT 0,
                    linked_docs TEXT,
                    comments TEXT
                )
            """)

            # Folders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    path TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    parent_path TEXT,
                    children TEXT,
                    document_ids TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (parent_path) REFERENCES folders(path)
                )
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_name TEXT UNIQUE NOT NULL,
                    usage_count INTEGER DEFAULT 0
                )
            """)

            # Document-Tag mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_tags (
                    doc_id TEXT,
                    tag_name TEXT,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (doc_id, tag_name),
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
                    FOREIGN KEY (tag_name) REFERENCES tags(tag_name)
                )
            """)

            # Revisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revisions (
                    revision_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    author TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    change_summary TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
                )
            """)

            # Story links table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS story_links (
                    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_doc_id TEXT NOT NULL,
                    target_doc_id TEXT NOT NULL,
                    link_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    auto_detected INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_doc_id) REFERENCES documents(doc_id),
                    FOREIGN KEY (target_doc_id) REFERENCES documents(doc_id)
                )
            """)

            # Mentions table (for quick recall)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentions (
                    mention_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    mention_count INTEGER DEFAULT 1,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
                )
            """)

            # Stats index table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stat_mentions (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    entity_name TEXT,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
                )
            """)

            # Editor tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS editor_tasks (
                    task_id TEXT PRIMARY KEY,
                    doc_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    assignee TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    deadline TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_folder ON documents(folder_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_created ON documents(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentions_entity ON mentions(entity_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stat_name ON stat_mentions(stat_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stat_value ON stat_mentions(stat_value)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON story_links(source_doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_target ON story_links(target_doc_id)")

    def save_document(self, doc_data: Dict) -> bool:
        """Save or update a document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents
                (doc_id, title, content, folder_path, metadata, created_at, updated_at,
                 revision_count, linked_docs, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_data['doc_id'],
                doc_data['title'],
                doc_data['content'],
                doc_data['folder_path'],
                json.dumps(doc_data['metadata']),
                doc_data['created_at'],
                doc_data['updated_at'],
                doc_data.get('revision_count', 0),
                json.dumps(doc_data.get('linked_docs', [])),
                json.dumps(doc_data.get('comments', []))
            ))
            return True

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            return cursor.rowcount > 0

    def save_folder(self, folder_data: Dict) -> bool:
        """Save or update a folder"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO folders
                (path, name, parent_path, children, document_ids, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                folder_data['path'],
                folder_data['name'],
                folder_data.get('parent_path'),
                json.dumps(folder_data.get('children', [])),
                json.dumps(folder_data.get('document_ids', [])),
                json.dumps(folder_data.get('metadata', {})),
                folder_data['created_at']
            ))
            return True

    def get_folder(self, path: str) -> Optional[Dict]:
        """Retrieve a folder by path"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM folders WHERE path = ?", (path,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None

    def add_tag(self, doc_id: str, tag_name: str):
        """Add a tag to a document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Ensure tag exists
            cursor.execute("""
                INSERT OR IGNORE INTO tags (tag_name, usage_count)
                VALUES (?, 0)
            """, (tag_name,))
            # Link tag to document
            cursor.execute("""
                INSERT OR IGNORE INTO document_tags (doc_id, tag_name, created_at)
                VALUES (?, ?, ?)
            """, (doc_id, tag_name, datetime.now().isoformat()))
            # Increment usage count
            cursor.execute("""
                UPDATE tags SET usage_count = usage_count + 1
                WHERE tag_name = ?
            """, (tag_name,))

    def get_documents_by_tag(self, tag_name: str) -> List[Dict]:
        """Get all documents with a specific tag"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.* FROM documents d
                JOIN document_tags dt ON d.doc_id = dt.doc_id
                WHERE dt.tag_name = ?
                ORDER BY d.created_at DESC
            """, (tag_name,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def save_revision(self, revision_data: Dict) -> bool:
        """Save a document revision"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO revisions
                (revision_id, doc_id, version, content, metadata, author, timestamp, change_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                revision_data['revision_id'],
                revision_data['doc_id'],
                revision_data['version'],
                revision_data['content'],
                json.dumps(revision_data['metadata']),
                revision_data['author'],
                revision_data['timestamp'],
                revision_data.get('change_summary', '')
            ))
            return True

    def get_revisions(self, doc_id: str) -> List[Dict]:
        """Get all revisions for a document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM revisions WHERE doc_id = ?
                ORDER BY timestamp DESC
            """, (doc_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def add_story_link(self, link_data: Dict) -> bool:
        """Add a link between stories"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO story_links
                (source_doc_id, target_doc_id, link_type, strength, auto_detected, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                link_data['source_doc_id'],
                link_data['target_doc_id'],
                link_data['link_type'],
                link_data.get('strength', 1.0),
                link_data.get('auto_detected', True),
                link_data['created_at']
            ))
            return True

    def get_linked_documents(self, doc_id: str) -> List[Dict]:
        """Get all documents linked to this document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.*, sl.link_type, sl.strength
                FROM documents d
                JOIN story_links sl ON (d.doc_id = sl.target_doc_id OR d.doc_id = sl.source_doc_id)
                WHERE sl.source_doc_id = ? OR sl.target_doc_id = ?
                AND d.doc_id != ?
                ORDER BY sl.strength DESC
            """, (doc_id, doc_id, doc_id))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def add_mention(self, doc_id: str, entity_type: str, entity_name: str,
                    context: str = "", mention_count: int = 1):
        """Add an entity mention to the index"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mentions
                (doc_id, entity_type, entity_name, mention_count, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, entity_type, entity_name, mention_count, context,
                  datetime.now().isoformat()))

    def find_mentions(self, entity_name: str, limit: int = 5) -> List[Dict]:
        """Find last N mentions of a player/team"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, d.title, d.created_at as doc_date
                FROM mentions m
                JOIN documents d ON m.doc_id = d.doc_id
                WHERE m.entity_name LIKE ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (f"%{entity_name}%", limit))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def add_stat_mention(self, doc_id: str, stat_name: str, stat_value: float,
                        entity_name: str = "", context: str = ""):
        """Add a stat mention to the index"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stat_mentions
                (doc_id, stat_name, stat_value, entity_name, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, stat_name, stat_value, entity_name, context,
                  datetime.now().isoformat()))

    def search_by_stat(self, stat_name: str, operator: str = ">",
                      value: float = 0) -> List[Dict]:
        """Search documents by stat criteria"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            operators = {">": ">", ">=": ">=", "<": "<", "<=": "<=", "=": "="}
            op = operators.get(operator, ">")

            query = f"""
                SELECT DISTINCT d.*, sm.stat_value, sm.entity_name
                FROM documents d
                JOIN stat_mentions sm ON d.doc_id = sm.doc_id
                WHERE sm.stat_name = ? AND sm.stat_value {op} ?
                ORDER BY sm.stat_value DESC
            """
            cursor.execute(query, (stat_name, value))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def save_task(self, task_data: Dict) -> bool:
        """Save an editor task"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO editor_tasks
                (task_id, doc_id, title, description, assignee, status, priority,
                 deadline, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data['task_id'],
                task_data.get('doc_id'),
                task_data['title'],
                task_data.get('description', ''),
                task_data.get('assignee'),
                task_data['status'],
                task_data['priority'],
                task_data.get('deadline'),
                task_data['created_at'],
                task_data.get('completed_at')
            ))
            return True

    def get_pending_tasks(self, assignee: Optional[str] = None) -> List[Dict]:
        """Get pending tasks for dashboard"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if assignee:
                cursor.execute("""
                    SELECT * FROM editor_tasks
                    WHERE status != 'completed' AND assignee = ?
                    ORDER BY priority DESC, deadline ASC
                """, (assignee,))
            else:
                cursor.execute("""
                    SELECT * FROM editor_tasks
                    WHERE status != 'completed'
                    ORDER BY priority DESC, deadline ASC
                """)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary"""
        d = dict(row)
        # Parse JSON fields
        for key in ['metadata', 'linked_docs', 'comments', 'children', 'document_ids']:
            if key in d and d[key]:
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        return d

    def search_documents(self, query: str, league: Optional[str] = None,
                        folder: Optional[str] = None) -> List[Dict]:
        """Full-text search across documents"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            base_query = """
                SELECT * FROM documents
                WHERE (title LIKE ? OR content LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%"]

            if league:
                base_query += " AND json_extract(metadata, '$.league') = ?"
                params.append(league)

            if folder:
                base_query += " AND folder_path LIKE ?"
                params.append(f"{folder}%")

            base_query += " ORDER BY updated_at DESC"
            cursor.execute(base_query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
