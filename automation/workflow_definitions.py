"""Pre-defined workflow definitions for sports content pipeline."""
import logging
from typing import Dict, Any
from datetime import datetime

from .workflow_engine import Workflow, WorkflowStep
from report_generator import SportsReportGenerator
import config

logger = logging.getLogger(__name__)


class WorkflowDefinitions:
    """Pre-defined workflows for common sports content pipelines."""

    @staticmethod
    def harvest_action(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Harvest step: Fetch fresh data from sports APIs.

        Args:
            context: Workflow context containing sport, date, etc.

        Returns:
            Dictionary with harvested data
        """
        sport = context.get('sport')
        logger.info(f"Harvesting data for {sport}")

        generator = SportsReportGenerator()
        sport_data = generator._generate_sport_data(sport)

        return {
            'sport': sport,
            'data': sport_data,
            'harvested_at': datetime.now().isoformat()
        }

    @staticmethod
    def beat_action(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Beat step: Analyze data and generate insights/narratives.

        Args:
            context: Workflow context containing harvested data

        Returns:
            Dictionary with analysis and narratives
        """
        sport = context.get('sport')
        harvest_result = context.get('harvest', {})
        data = harvest_result.get('data', {})

        logger.info(f"Generating beat analysis for {sport}")

        # Generate formatted report
        generator = SportsReportGenerator()
        report = generator.generate_sport_report(sport, quick=False)

        return {
            'sport': sport,
            'report': report,
            'analyzed_at': datetime.now().isoformat()
        }

    @staticmethod
    def copy_action(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Copy step: Format content with templates and style.

        Args:
            context: Workflow context containing beat analysis

        Returns:
            Dictionary with formatted content
        """
        sport = context.get('sport')
        beat_result = context.get('beat', {})
        report = beat_result.get('report', '')

        logger.info(f"Formatting copy for {sport}")

        # Apply templates and styling
        # TODO: Integrate with template manager
        formatted_content = {
            'title': f"{config.SPORTS_CONFIG[sport]['display_name']} Digest - {datetime.now().strftime('%Y-%m-%d')}",
            'content': report,
            'metadata': {
                'sport': sport,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'format': 'markdown'
            }
        }

        return {
            'sport': sport,
            'content': formatted_content,
            'formatted_at': datetime.now().isoformat()
        }

    @staticmethod
    def export_action(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export step: Publish content to multiple destinations.

        Args:
            context: Workflow context containing formatted content

        Returns:
            Dictionary with export results
        """
        sport = context.get('sport')
        copy_result = context.get('copy', {})
        content = copy_result.get('content', {})

        logger.info(f"Exporting content for {sport}")

        # Export to multiple destinations
        # TODO: Integrate with export manager
        export_results = {
            'google_docs': {'status': 'pending', 'url': None},
            'apple_notes': {'status': 'pending', 'id': None},
            'pdf': {'status': 'pending', 'path': None}
        }

        return {
            'sport': sport,
            'exports': export_results,
            'exported_at': datetime.now().isoformat()
        }

    @classmethod
    def create_full_digest_workflow(cls, sport: str) -> Workflow:
        """
        Create a complete digest workflow: Harvest → Beat → Copy → Export.

        Args:
            sport: Sport identifier

        Returns:
            Configured Workflow instance
        """
        workflow = Workflow(
            name=f"{sport}_full_digest",
            description=f"Complete digest workflow for {sport}",
            metadata={'sport': sport, 'type': 'full_digest'}
        )

        # Add harvest step
        harvest_step = WorkflowStep(
            name='harvest',
            action=cls.harvest_action,
            dependencies=[],
            retry_count=3,
            metadata={'type': 'harvest', 'sport': sport}
        )
        workflow.add_step(harvest_step)

        # Add beat step (depends on harvest)
        beat_step = WorkflowStep(
            name='beat',
            action=cls.beat_action,
            dependencies=['harvest'],
            retry_count=2,
            metadata={'type': 'beat', 'sport': sport}
        )
        workflow.add_step(beat_step)

        # Add copy step (depends on beat)
        copy_step = WorkflowStep(
            name='copy',
            action=cls.copy_action,
            dependencies=['beat'],
            retry_count=2,
            metadata={'type': 'copy', 'sport': sport}
        )
        workflow.add_step(copy_step)

        # Add export step (depends on copy)
        export_step = WorkflowStep(
            name='export',
            action=cls.export_action,
            dependencies=['copy'],
            retry_count=3,
            metadata={'type': 'export', 'sport': sport}
        )
        workflow.add_step(export_step)

        # Set initial context
        workflow.context = {'sport': sport}

        return workflow

    @classmethod
    def create_quick_update_workflow(cls, sport: str) -> Workflow:
        """
        Create a quick update workflow: Harvest → Beat → Export.

        Skips the copy/formatting step for faster updates.

        Args:
            sport: Sport identifier

        Returns:
            Configured Workflow instance
        """
        workflow = Workflow(
            name=f"{sport}_quick_update",
            description=f"Quick update workflow for {sport}",
            metadata={'sport': sport, 'type': 'quick_update'}
        )

        # Add harvest step
        harvest_step = WorkflowStep(
            name='harvest',
            action=cls.harvest_action,
            dependencies=[],
            retry_count=2,
            metadata={'type': 'harvest', 'sport': sport}
        )
        workflow.add_step(harvest_step)

        # Add beat step (depends on harvest)
        beat_step = WorkflowStep(
            name='beat',
            action=cls.beat_action,
            dependencies=['harvest'],
            retry_count=1,
            metadata={'type': 'beat', 'sport': sport}
        )
        workflow.add_step(beat_step)

        # Add export step (depends on beat)
        export_step = WorkflowStep(
            name='export',
            action=cls.export_action,
            dependencies=['beat'],
            retry_count=2,
            metadata={'type': 'export', 'sport': sport}
        )
        workflow.add_step(export_step)

        # Set initial context
        workflow.context = {'sport': sport}

        return workflow

    @classmethod
    def create_multi_sport_workflow(cls, sports: list) -> Workflow:
        """
        Create a workflow for multiple sports in parallel.

        Args:
            sports: List of sport identifiers

        Returns:
            Configured Workflow instance
        """
        workflow = Workflow(
            name="multi_sport_digest",
            description=f"Multi-sport digest for {', '.join(sports)}",
            metadata={'sports': sports, 'type': 'multi_sport'}
        )

        # Create parallel harvest steps for each sport
        for sport in sports:
            harvest_step = WorkflowStep(
                name=f'harvest_{sport}',
                action=cls.harvest_action,
                dependencies=[],
                retry_count=3,
                metadata={'type': 'harvest', 'sport': sport}
            )
            workflow.add_step(harvest_step)

        # Create beat steps (each depends on its harvest)
        for sport in sports:
            beat_step = WorkflowStep(
                name=f'beat_{sport}',
                action=cls.beat_action,
                dependencies=[f'harvest_{sport}'],
                retry_count=2,
                metadata={'type': 'beat', 'sport': sport}
            )
            workflow.add_step(beat_step)

        # Create aggregation step (depends on all beats)
        def aggregate_action(context: Dict[str, Any]) -> Dict[str, Any]:
            logger.info("Aggregating multi-sport content")
            all_reports = {}
            for sport in sports:
                beat_result = context.get(f'beat_{sport}', {})
                all_reports[sport] = beat_result.get('report', '')

            return {
                'sports': sports,
                'reports': all_reports,
                'aggregated_at': datetime.now().isoformat()
            }

        aggregate_step = WorkflowStep(
            name='aggregate',
            action=aggregate_action,
            dependencies=[f'beat_{sport}' for sport in sports],
            retry_count=1,
            metadata={'type': 'aggregate', 'sports': sports}
        )
        workflow.add_step(aggregate_step)

        # Create export step (depends on aggregation)
        export_step = WorkflowStep(
            name='export',
            action=cls.export_action,
            dependencies=['aggregate'],
            retry_count=3,
            metadata={'type': 'export', 'sports': sports}
        )
        workflow.add_step(export_step)

        # Set initial context
        workflow.context = {'sports': sports}

        return workflow
