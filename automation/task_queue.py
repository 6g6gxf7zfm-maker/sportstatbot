"""Cloud-based task queue manager with priority support."""
import logging
import heapq
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


class TaskStatus(Enum):
    """Task execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class Task:
    """Represents a task in the queue."""
    priority: int = field(compare=True)
    task_id: str = field(compare=False)
    name: str = field(compare=False)
    action: Callable = field(compare=False, repr=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: Dict = field(default_factory=dict, compare=False)
    sport: Optional[str] = field(default=None, compare=False)
    metadata: Dict = field(default_factory=dict, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    started_at: Optional[datetime] = field(default=None, compare=False)
    completed_at: Optional[datetime] = field(default=None, compare=False)
    status: TaskStatus = field(default=TaskStatus.QUEUED, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    retry_count: int = field(default=3, compare=False)
    attempts: int = field(default=0, compare=False)

    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'priority': self.priority,
            'sport': self.sport,
            'status': self.status.value,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'attempts': self.attempts,
            'error': self.error
        }


class TaskQueue:
    """
    Priority-based task queue manager.

    Features:
    - Priority-based scheduling
    - Sport-based traffic management
    - Concurrent task execution
    - Automatic retries
    - Task monitoring and statistics
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.queue: List[Task] = []
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.lock = threading.Lock()
        self.workers: List[threading.Thread] = []
        self.running = False

        # Sport-based traffic priorities
        self.sport_priorities = {
            'nfl': TaskPriority.HIGH,
            'nba': TaskPriority.HIGH,
            'mlb': TaskPriority.NORMAL,
            'nhl': TaskPriority.NORMAL,
            'mls': TaskPriority.LOW,
            'soccer': TaskPriority.NORMAL,
            'golf': TaskPriority.LOW
        }

    def add_task(
        self,
        task_id: str,
        name: str,
        action: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        priority: Optional[TaskPriority] = None,
        sport: Optional[str] = None,
        metadata: Optional[Dict] = None,
        retry_count: int = 3
    ) -> Task:
        """
        Add a task to the queue.

        Args:
            task_id: Unique task identifier
            name: Task name
            action: Callable to execute
            args: Positional arguments for action
            kwargs: Keyword arguments for action
            priority: Task priority (auto-assigned based on sport if not provided)
            sport: Sport identifier
            metadata: Additional task metadata
            retry_count: Number of retry attempts

        Returns:
            Created task
        """
        # Auto-assign priority based on sport if not provided
        if priority is None and sport:
            priority = self.sport_priorities.get(sport, TaskPriority.NORMAL)
        elif priority is None:
            priority = TaskPriority.NORMAL

        task = Task(
            priority=priority.value,
            task_id=task_id,
            name=name,
            action=action,
            args=args,
            kwargs=kwargs or {},
            sport=sport,
            metadata=metadata or {},
            retry_count=retry_count
        )

        with self.lock:
            self.tasks[task_id] = task
            heapq.heappush(self.queue, task)
            logger.info(f"Task added to queue: {name} (priority: {priority.name}, sport: {sport})")

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued task."""
        with self.lock:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.QUEUED:
                task.status = TaskStatus.CANCELLED
                # Remove from queue
                self.queue = [t for t in self.queue if t.task_id != task_id]
                heapq.heapify(self.queue)
                logger.info(f"Task cancelled: {task.name}")
                return True
        return False

    def start(self):
        """Start the task queue workers."""
        if self.running:
            logger.warning("Task queue already running")
            return

        self.running = True
        logger.info(f"Starting task queue with {self.max_workers} workers")

        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, name=f"Worker-{i+1}", daemon=True)
            worker.start()
            self.workers.append(worker)

    def stop(self):
        """Stop the task queue workers."""
        logger.info("Stopping task queue...")
        self.running = False

        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)

        self.workers.clear()
        logger.info("Task queue stopped")

    def _worker(self):
        """Worker thread that processes tasks from the queue."""
        logger.info(f"{threading.current_thread().name} started")

        while self.running:
            task = None

            # Get next task
            with self.lock:
                if self.queue:
                    task = heapq.heappop(self.queue)
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    self.running_tasks[task.task_id] = task

            if task:
                # Execute task
                self._execute_task(task)
            else:
                # No tasks available, sleep
                time.sleep(1)

        logger.info(f"{threading.current_thread().name} stopped")

    def _execute_task(self, task: Task):
        """Execute a task with retry logic."""
        logger.info(f"Executing task: {task.name} (attempt {task.attempts + 1}/{task.retry_count})")

        for attempt in range(1, task.retry_count + 1):
            task.attempts = attempt

            try:
                # Execute task action
                result = task.action(*task.args, **task.kwargs)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()

                logger.info(f"Task completed: {task.name}")

                # Move to completed tasks
                with self.lock:
                    self.running_tasks.pop(task.task_id, None)
                    self.completed_tasks.append(task)

                return

            except Exception as e:
                logger.error(f"Task failed (attempt {attempt}/{task.retry_count}): {task.name} - {e}")
                task.error = str(e)

                if attempt < task.retry_count:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now()

                    # Move to completed tasks
                    with self.lock:
                        self.running_tasks.pop(task.task_id, None)
                        self.completed_tasks.append(task)

    def get_statistics(self) -> Dict:
        """Get queue statistics."""
        with self.lock:
            queued = len(self.queue)
            running = len(self.running_tasks)
            completed = len([t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED])
            failed = len([t for t in self.completed_tasks if t.status == TaskStatus.FAILED])

            # Sport-based statistics
            sport_stats = {}
            for task in self.tasks.values():
                if task.sport:
                    if task.sport not in sport_stats:
                        sport_stats[task.sport] = {
                            'queued': 0,
                            'running': 0,
                            'completed': 0,
                            'failed': 0
                        }
                    sport_stats[task.sport][task.status.value] = \
                        sport_stats[task.sport].get(task.status.value, 0) + 1

            return {
                'total_tasks': len(self.tasks),
                'queued': queued,
                'running': running,
                'completed': completed,
                'failed': failed,
                'workers': self.max_workers,
                'sport_statistics': sport_stats
            }

    def get_queued_tasks(self) -> List[Dict]:
        """Get list of queued tasks."""
        with self.lock:
            return [task.to_dict() for task in sorted(self.queue)]

    def get_running_tasks(self) -> List[Dict]:
        """Get list of running tasks."""
        with self.lock:
            return [task.to_dict() for task in self.running_tasks.values()]

    def get_completed_tasks(self, limit: int = 50) -> List[Dict]:
        """Get list of completed tasks."""
        with self.lock:
            return [task.to_dict() for task in self.completed_tasks[-limit:]]

    def clear_completed(self):
        """Clear completed tasks history."""
        with self.lock:
            self.completed_tasks.clear()
            logger.info("Completed tasks cleared")

    def update_sport_priority(self, sport: str, priority: TaskPriority):
        """Update priority for a sport."""
        self.sport_priorities[sport] = priority
        logger.info(f"Updated priority for {sport}: {priority.name}")
