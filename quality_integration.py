"""
Integration layer between SportStatBot and Quality System

This module wraps the existing SportStatBot with quality controls
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

from quality_system.core import QualityController
from quality_system.models import DataSource, Citation

from report_generator import ReportGenerator


class QualityEnabledReportGenerator(ReportGenerator):
    """
    Enhanced ReportGenerator with integrated quality controls

    This extends the existing ReportGenerator to add:
    - Quality scoring
    - Compliance checking
    - Audit logging
    - Auto-approval workflow
    """

    def __init__(
        self,
        timezone: str = 'America/New_York',
        enable_quality_controls: bool = True,
        auto_approve_threshold: float = 85.0,
        max_data_age_hours: int = 24,
        audit_log_dir: str = "audit_logs",
        proofing_queue_dir: str = "proofing_queue"
    ):
        """
        Initialize quality-enabled report generator

        Args:
            timezone: Timezone for reports
            enable_quality_controls: Enable quality system
            auto_approve_threshold: Quality score for auto-approval
            max_data_age_hours: Maximum age for data freshness
            audit_log_dir: Directory for audit logs
            proofing_queue_dir: Directory for proofing queue
        """
        super().__init__(timezone)

        self.enable_quality_controls = enable_quality_controls

        if self.enable_quality_controls:
            self.quality_controller = QualityController(
                audit_log_dir=audit_log_dir,
                proofing_queue_dir=proofing_queue_dir,
                auto_approve_threshold=auto_approve_threshold,
                max_data_age_hours=max_data_age_hours
            )

    def generate_report_with_quality(
        self,
        sport: str,
        output_format: str = 'slack',
        embargo_until: Optional[datetime] = None,
        skip_proofing_queue: bool = False
    ) -> Dict[str, Any]:
        """
        Generate report with complete quality pipeline

        Args:
            sport: Sport to generate report for
            output_format: Output format (slack, text, etc.)
            embargo_until: Optional embargo datetime
            skip_proofing_queue: Skip adding to proofing queue

        Returns:
            Dictionary with report, quality assessment, and metadata
        """
        # Generate base report using parent class
        base_report = self.generate_report(sport, output_format)

        if not self.enable_quality_controls:
            # Quality controls disabled, return base report
            return {
                'success': True,
                'report': base_report,
                'quality_enabled': False
            }

        # Extract data sources from report generation
        data_sources = self._extract_data_sources(sport)

        # Extract citations from report
        citations = self._extract_citations(base_report)

        # Build fact-check data from known stats
        fact_checks = self._build_fact_checks(sport)

        # Process through quality pipeline
        quality_report = self.quality_controller.process_content(
            content=base_report,
            sport=sport,
            data_sources=data_sources,
            citations=citations,
            embargo_until=embargo_until,
            fact_checks=fact_checks
        )

        # Get compliance summary
        compliance_summary = self.quality_controller.get_compliance_summary(
            quality_report.compliance
        )

        # Get peer review report
        peer_review_report = self.quality_controller.get_peer_review_report(
            quality_report.compliance.peer_review
        )

        result = {
            'success': True,
            'report': base_report,
            'quality_enabled': True,
            'quality_report': quality_report,
            'compliance_summary': compliance_summary,
            'peer_review': peer_review_report,
            'can_publish': quality_report.can_publish,
            'auto_approved': quality_report.auto_approve,
            'quality_score': quality_report.quality.overall_score,
            'recommendations': quality_report.recommendations
        }

        # If can publish, enhance and publish
        if quality_report.can_publish:
            publication_result = self.quality_controller.publish_content(
                content=base_report,
                quality_report=quality_report,
                add_disclaimer=True,
                add_transparency_tag=True
            )

            result['enhanced_report'] = publication_result['enhanced_content']
            result['audit_log_path'] = publication_result['audit_log_path']
            result['version_hash'] = publication_result['version_hash']

            # Add to proofing queue unless auto-approved or skipped
            if not quality_report.auto_approve and not skip_proofing_queue:
                queue_id = self.quality_controller.add_to_proofing_queue(
                    content=base_report,
                    quality_report=quality_report,
                    priority=2  # Medium-high priority
                )
                result['queue_id'] = queue_id
                result['queued_for_review'] = True
            else:
                result['queued_for_review'] = False

        else:
            # Cannot publish - add to queue for review
            if not skip_proofing_queue:
                queue_id = self.quality_controller.add_to_proofing_queue(
                    content=base_report,
                    quality_report=quality_report,
                    priority=1  # High priority for failed content
                )
                result['queue_id'] = queue_id
                result['queued_for_review'] = True

        return result

    def _extract_data_sources(self, sport: str) -> List[DataSource]:
        """
        Extract data sources from report generation

        Args:
            sport: Sport being reported on

        Returns:
            List of data sources with timestamps
        """
        sources = []
        now = datetime.utcnow()

        # ESPN source (used for scores, standings, news, etc.)
        sources.append(DataSource(
            name="ESPN",
            url=f"https://www.espn.com/{sport}",
            api_endpoint=f"https://site.api.espn.com/apis/site/v2/sports/{sport.upper()}",
            timestamp=now,
            data_type="scores,standings,news,schedule"
        ))

        # Odds API source (if odds fetcher is enabled)
        if hasattr(self, 'odds_fetcher') and self.odds_fetcher:
            sources.append(DataSource(
                name="The Odds API",
                url="https://the-odds-api.com",
                api_endpoint="https://api.the-odds-api.com/v4",
                timestamp=now,
                data_type="odds,betting"
            ))

        return sources

    def _extract_citations(self, report: str) -> List[Citation]:
        """
        Extract citations from report content

        This is a simple implementation that could be enhanced
        to parse structured data from the report.

        Args:
            report: Report content

        Returns:
            List of citations
        """
        citations = []
        now = datetime.utcnow()

        # For now, add generic citations
        # In a production system, this would parse actual stats from report

        if "ESPN" in report or "espn" in report:
            citations.append(Citation(
                source="ESPN",
                stat_type="game_data",
                value="various",
                timestamp=now,
                verified=True
            ))

        if "odds" in report.lower() or "betting" in report.lower():
            citations.append(Citation(
                source="The Odds API",
                stat_type="betting_odds",
                value="various",
                timestamp=now,
                verified=True
            ))

        return citations

    def _build_fact_checks(self, sport: str) -> List[Dict[str, Any]]:
        """
        Build fact-check data for verification

        In a production system, this would compare claimed stats
        against authoritative API responses.

        Args:
            sport: Sport being reported on

        Returns:
            List of fact-check dictionaries
        """
        # Placeholder - in production, this would fetch actual stats
        # and compare them against what's in the report
        return []

    def get_quality_stats(self, sport: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """
        Get quality statistics for published reports

        Args:
            sport: Optional sport filter
            days: Number of days to analyze

        Returns:
            Quality statistics
        """
        if not self.enable_quality_controls:
            return {'quality_enabled': False}

        audit_report = self.quality_controller.get_audit_report(sport=sport, days=days)
        queue_stats = self.quality_controller.get_queue_stats()

        return {
            'quality_enabled': True,
            'audit_report': audit_report,
            'queue_stats': queue_stats
        }


def create_quality_enabled_generator(**kwargs) -> QualityEnabledReportGenerator:
    """
    Factory function to create quality-enabled report generator

    Args:
        **kwargs: Configuration options

    Returns:
        Configured QualityEnabledReportGenerator
    """
    return QualityEnabledReportGenerator(**kwargs)


# Example usage
if __name__ == "__main__":
    # Create quality-enabled generator
    generator = create_quality_enabled_generator(
        timezone='America/New_York',
        enable_quality_controls=True,
        auto_approve_threshold=85.0
    )

    # Generate report for NBA with quality controls
    result = generator.generate_report_with_quality(
        sport='nba',
        output_format='slack'
    )

    print("=" * 60)
    print("REPORT GENERATION COMPLETE")
    print("=" * 60)
    print(f"Quality Enabled: {result['quality_enabled']}")
    print(f"Can Publish: {result.get('can_publish', 'N/A')}")
    print(f"Auto-Approved: {result.get('auto_approved', 'N/A')}")
    print(f"Quality Score: {result.get('quality_score', 'N/A')}")
    print()

    if result.get('compliance_summary'):
        print(result['compliance_summary'])

    if result.get('peer_review'):
        print()
        print(result['peer_review'])

    if result.get('recommendations'):
        print()
        print("RECOMMENDATIONS:")
        for rec in result['recommendations']:
            print(f"  - {rec}")

    print()
    print("=" * 60)
