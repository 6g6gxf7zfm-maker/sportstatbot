"""Workflow execution engine for multi-step automated processes."""
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from enum import Enum
import json
import time

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Individual step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(
        self,
        name: str,
        action: Callable,
        dependencies: Optional[List[str]] = None,
        retry_count: int = 3,
        timeout: int = 300,
        metadata: Optional[Dict] = None
    ):
        self.name = name
        self.action = action
        self.dependencies = dependencies or []
        self.retry_count = retry_count
        self.timeout = timeout
        self.metadata = metadata or {}
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.attempts = 0

    def execute(self, context: Dict) -> Any:
        """Execute the step action with retry logic."""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()

        for attempt in range(1, self.retry_count + 1):
            self.attempts = attempt
            try:
                logger.info(f"Executing step '{self.name}' (attempt {attempt}/{self.retry_count})")
                self.result = self.action(context)
                self.status = StepStatus.COMPLETED
                self.completed_at = datetime.now()
                logger.info(f"Step '{self.name}' completed successfully")
                return self.result

            except Exception as e:
                logger.error(f"Step '{self.name}' failed (attempt {attempt}/{self.retry_count}): {e}")
                self.error = str(e)

                if attempt < self.retry_count:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.status = StepStatus.FAILED
                    self.completed_at = datetime.now()
                    raise

        return None

    def to_dict(self) -> Dict:
        """Convert step to dictionary for serialization."""
        return {
            'name': self.name,
            'status': self.status.value,
            'dependencies': self.dependencies,
            'metadata': self.metadata,
            'attempts': self.attempts,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error
        }


class Workflow:
    """Represents a complete workflow with multiple steps."""

    def __init__(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ):
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.steps: Dict[str, WorkflowStep] = {}
        self.status = WorkflowStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.context: Dict[str, Any] = {}

    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps[step.name] = step

    def get_execution_order(self) -> List[str]:
        """
        Determine the execution order based on dependencies.
        Returns list of step names in topological order.
        """
        visited = set()
        order = []

        def visit(step_name: str):
            if step_name in visited:
                return

            step = self.steps.get(step_name)
            if not step:
                return

            # Visit dependencies first
            for dep in step.dependencies:
                visit(dep)

            visited.add(step_name)
            order.append(step_name)

        # Visit all steps
        for step_name in self.steps:
            visit(step_name)

        return order

    def to_dict(self) -> Dict:
        """Convert workflow to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'metadata': self.metadata,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'steps': {name: step.to_dict() for name, step in self.steps.items()},
            'execution_order': self.get_execution_order()
        }


class WorkflowEngine:
    """
    Main workflow execution engine.

    Executes multi-step workflows with dependency resolution,
    retry logic, and comprehensive error handling.
    """

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflow: Optional[str] = None

    def register_workflow(self, workflow: Workflow):
        """Register a workflow for execution."""
        self.workflows[workflow.name] = workflow
        logger.info(f"Registered workflow: {workflow.name}")

    def execute_workflow(
        self,
        workflow_name: str,
        initial_context: Optional[Dict] = None
    ) -> Dict:
        """
        Execute a workflow by name.

        Args:
            workflow_name: Name of the workflow to execute
            initial_context: Initial context data for the workflow

        Returns:
            Workflow execution results
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        self.active_workflow = workflow_name
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        workflow.context = initial_context or {}

        logger.info(f"Starting workflow: {workflow_name}")

        try:
            execution_order = workflow.get_execution_order()
            logger.info(f"Execution order: {' → '.join(execution_order)}")

            # Execute steps in order
            for step_name in execution_order:
                # Check if workflow is paused
                if workflow.status == WorkflowStatus.PAUSED:
                    logger.info(f"Workflow paused at step: {step_name}")
                    break

                step = workflow.steps[step_name]

                # Check if dependencies are met
                if not self._check_dependencies(workflow, step):
                    logger.warning(f"Dependencies not met for step: {step_name}, skipping")
                    step.status = StepStatus.SKIPPED
                    continue

                # Execute step
                result = step.execute(workflow.context)

                # Store result in context for next steps
                workflow.context[step_name] = result

            # Check if all steps completed
            if all(step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
                   for step in workflow.steps.values()):
                workflow.status = WorkflowStatus.COMPLETED
                logger.info(f"Workflow completed: {workflow_name}")
            else:
                workflow.status = WorkflowStatus.FAILED
                logger.error(f"Workflow failed: {workflow_name}")

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            workflow.status = WorkflowStatus.FAILED
            raise

        finally:
            workflow.completed_at = datetime.now()
            self.active_workflow = None

        return workflow.to_dict()

    def _check_dependencies(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """Check if all dependencies for a step are completed."""
        for dep_name in step.dependencies:
            dep_step = workflow.steps.get(dep_name)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        return True

    def pause_workflow(self, workflow_name: str):
        """Pause a running workflow."""
        workflow = self.workflows.get(workflow_name)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            logger.info(f"Workflow paused: {workflow_name}")

    def resume_workflow(self, workflow_name: str) -> Dict:
        """Resume a paused workflow."""
        workflow = self.workflows.get(workflow_name)
        if workflow and workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            logger.info(f"Resuming workflow: {workflow_name}")
            return self.execute_workflow(workflow_name, workflow.context)
        return {}

    def cancel_workflow(self, workflow_name: str):
        """Cancel a running or paused workflow."""
        workflow = self.workflows.get(workflow_name)
        if workflow:
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            logger.info(f"Workflow cancelled: {workflow_name}")

    def get_workflow_status(self, workflow_name: str) -> Optional[Dict]:
        """Get current status of a workflow."""
        workflow = self.workflows.get(workflow_name)
        return workflow.to_dict() if workflow else None

    def list_workflows(self) -> List[Dict]:
        """List all registered workflows."""
        return [workflow.to_dict() for workflow in self.workflows.values()]
