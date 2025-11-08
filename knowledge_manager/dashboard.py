"""
Editor Dashboard - Task management and editorial workflow
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid

from .database_handler import DatabaseHandler
from .models import EditorTask


class EditorDashboard:
    """Dashboard for editorial task management and workflow"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def create_task(
        self,
        title: str,
        description: str = "",
        doc_id: Optional[str] = None,
        assignee: Optional[str] = None,
        priority: str = "medium",
        deadline: Optional[datetime] = None
    ) -> EditorTask:
        """Create a new editorial task"""
        task = EditorTask(
            task_id=str(uuid.uuid4()),
            doc_id=doc_id,
            title=title,
            description=description,
            assignee=assignee,
            status="pending",
            priority=priority,
            deadline=deadline,
            created_at=datetime.now()
        )

        self.db.save_task(task.to_dict())
        return task

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a task by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM editor_tasks WHERE task_id = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                return self.db._row_to_dict(row)
        return None

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status"""
        task = self.get_task(task_id)
        if not task:
            return False

        task['status'] = status
        if status == 'completed':
            task['completed_at'] = datetime.now().isoformat()

        self.db.save_task(task)
        return True

    def assign_task(self, task_id: str, assignee: str) -> bool:
        """Assign task to someone"""
        task = self.get_task(task_id)
        if not task:
            return False

        task['assignee'] = assignee
        self.db.save_task(task)
        return True

    def get_dashboard_view(self, assignee: Optional[str] = None) -> Dict:
        """Get complete dashboard view"""
        pending_tasks = self.db.get_pending_tasks(assignee)

        # Organize tasks
        by_priority = {
            'urgent': [],
            'high': [],
            'medium': [],
            'low': []
        }

        overdue = []
        due_soon = []

        now = datetime.now()
        soon_threshold = now + timedelta(days=3)

        for task in pending_tasks:
            # By priority
            priority = task.get('priority', 'medium')
            by_priority[priority].append(task)

            # By deadline
            if task.get('deadline'):
                deadline = datetime.fromisoformat(task['deadline'])
                if deadline < now:
                    overdue.append(task)
                elif deadline < soon_threshold:
                    due_soon.append(task)

        # Get document stats
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Drafts
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE json_extract(metadata, '$.version') = '1.0'
            """)
            draft_count = cursor.fetchone()['count']

            # In edit
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE json_extract(metadata, '$.version') = '1.1'
            """)
            edit_count = cursor.fetchone()['count']

            # Ready to publish (version 1.1 and no pending tasks)
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE json_extract(metadata, '$.version') = '1.1'
                AND doc_id NOT IN (
                    SELECT doc_id FROM editor_tasks
                    WHERE status != 'completed'
                    AND doc_id IS NOT NULL
                )
            """)
            ready_count = cursor.fetchone()['count']

        return {
            'tasks': {
                'total_pending': len(pending_tasks),
                'by_priority': {k: len(v) for k, v in by_priority.items()},
                'overdue': len(overdue),
                'due_soon': len(due_soon)
            },
            'documents': {
                'drafts': draft_count,
                'in_edit': edit_count,
                'ready_to_publish': ready_count
            },
            'urgent_tasks': by_priority['urgent'],
            'overdue_tasks': overdue,
            'due_soon_tasks': due_soon,
            'assignee': assignee,
            'generated_at': datetime.now().isoformat()
        }

    def get_pending_stories(
        self,
        assignee: Optional[str] = None,
        status: str = "pending"
    ) -> List[Dict]:
        """Get pending stories with details"""
        pending_tasks = self.db.get_pending_tasks(assignee)

        stories = []
        for task in pending_tasks:
            if task.get('doc_id'):
                doc = self.db.get_document(task['doc_id'])
                if doc:
                    stories.append({
                        'task': task,
                        'document': {
                            'doc_id': doc['doc_id'],
                            'title': doc['title'],
                            'league': doc['metadata']['league'],
                            'version': doc['metadata']['version'],
                            'updated_at': doc['updated_at']
                        }
                    })

        return stories

    def get_team_workload(self) -> Dict:
        """Get workload distribution across team members"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assignee, status, COUNT(*) as count
                FROM editor_tasks
                WHERE assignee IS NOT NULL
                GROUP BY assignee, status
            """)

            workload = {}
            for row in cursor.fetchall():
                assignee = row['assignee']
                status = row['status']
                count = row['count']

                if assignee not in workload:
                    workload[assignee] = {
                        'pending': 0,
                        'in_progress': 0,
                        'completed': 0,
                        'total': 0
                    }

                workload[assignee][status] = count
                workload[assignee]['total'] += count

        return workload

    def create_document_task(
        self,
        doc_id: str,
        task_type: str = "review",
        assignee: Optional[str] = None,
        deadline: Optional[datetime] = None
    ) -> EditorTask:
        """Create a task for a specific document"""
        doc = self.db.get_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        task_titles = {
            'review': f"Review: {doc['title']}",
            'edit': f"Edit: {doc['title']}",
            'fact_check': f"Fact check: {doc['title']}",
            'publish': f"Publish: {doc['title']}"
        }

        title = task_titles.get(task_type, f"Task for: {doc['title']}")

        return self.create_task(
            title=title,
            description=f"{task_type.title()} required for document",
            doc_id=doc_id,
            assignee=assignee,
            priority='medium',
            deadline=deadline
        )

    def get_weekly_summary(self, assignee: Optional[str] = None) -> Dict:
        """Get weekly summary of activity"""
        week_ago = datetime.now() - timedelta(days=7)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Tasks created this week
            query = """
                SELECT COUNT(*) as count FROM editor_tasks
                WHERE created_at >= ?
            """
            params = [week_ago.isoformat()]

            if assignee:
                query += " AND assignee = ?"
                params.append(assignee)

            cursor.execute(query, params)
            tasks_created = cursor.fetchone()['count']

            # Tasks completed this week
            query = """
                SELECT COUNT(*) as count FROM editor_tasks
                WHERE completed_at >= ?
            """
            params = [week_ago.isoformat()]

            if assignee:
                query += " AND assignee = ?"
                params.append(assignee)

            cursor.execute(query, params)
            tasks_completed = cursor.fetchone()['count']

            # Documents published this week
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE updated_at >= ?
                AND json_extract(metadata, '$.version') = '2.0'
            """, (week_ago.isoformat(),))
            docs_published = cursor.fetchone()['count']

        return {
            'week_start': week_ago.isoformat(),
            'tasks_created': tasks_created,
            'tasks_completed': tasks_completed,
            'documents_published': docs_published,
            'assignee': assignee,
            'completion_rate': round(
                (tasks_completed / tasks_created * 100) if tasks_created > 0 else 0,
                1
            )
        }

    def get_beat_deadlines(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming beat deadlines"""
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM editor_tasks
                WHERE status != 'completed'
                AND deadline BETWEEN ? AND ?
                ORDER BY deadline ASC
            """, (now.isoformat(), future.isoformat()))

            deadlines = []
            for row in cursor.fetchall():
                task = self.db._row_to_dict(row)
                deadline = datetime.fromisoformat(task['deadline'])
                days_until = (deadline - now).days

                deadlines.append({
                    'task': task,
                    'deadline': task['deadline'],
                    'days_until': days_until,
                    'urgency': 'urgent' if days_until <= 1 else 'soon'
                })

        return deadlines

    def add_comment_to_task(self, task_id: str, author: str, comment: str) -> bool:
        """Add a comment to a task"""
        task = self.get_task(task_id)
        if not task:
            return False

        # Add to document if task is linked to a doc
        if task.get('doc_id'):
            doc = self.db.get_document(task['doc_id'])
            if doc:
                comments = doc.get('comments', [])
                comments.append({
                    'author': author,
                    'comment': f"[Task: {task['title']}] {comment}",
                    'timestamp': datetime.now().isoformat()
                })
                doc['comments'] = comments
                self.db.save_document(doc)

        return True
