"""
Core Quality Controller

Orchestrates all quality, compliance, and audit components
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import (
    QualityReport,
    ComplianceStatus,
    ComplianceLevel,
    AuditRecord,
    QualityScore,
    DataSource,
    Citation,
    BettingDisclaimer,
    TimestampVerification,
    PeerReviewChecklist,
    EmbargoTimer
)

from .validators import (
    TimestampValidator,
    CitationValidator,
    SpeculationDetector,
    DataFreshnessChecker
)

from .compliance import (
    BettingDisclaimerEnforcer,
    EmbargoManager,
    TransparencyTagger,
    ComplianceSummaryGenerator
)

from .fact_checker import FactChecker
from .audit import AuditLogger, VersionDiffTracker
from .quality_scorer import QualityScorer
from .proofing import ProofingQueue, PeerReviewAgent


class QualityController:
    """
    Central controller for quality, compliance, and audit system

    This is the main entry point for integrating quality controls
    into the SportStatBot workflow.
    """

    def __init__(
        self,
        audit_log_dir: str = "audit_logs",
        proofing_queue_dir: str = "proofing_queue",
        auto_approve_threshold: float = 85.0,
        max_data_age_hours: int = 24
    ):
        # Initialize components
        self.timestamp_validator = TimestampValidator(max_age_hours=max_data_age_hours)
        self.citation_validator = CitationValidator()
        self.speculation_detector = SpeculationDetector()
        self.freshness_checker = DataFreshnessChecker(max_age_hours=max_data_age_hours)

        self.disclaimer_enforcer = BettingDisclaimerEnforcer()
        self.embargo_manager = EmbargoManager()
        self.transparency_tagger = TransparencyTagger()
        self.compliance_generator = ComplianceSummaryGenerator()

        self.fact_checker = FactChecker()
        self.quality_scorer = QualityScorer()

        self.audit_logger = AuditLogger(log_dir=audit_log_dir)
        self.version_tracker = VersionDiffTracker()

        self.proofing_queue = ProofingQueue(
            storage_dir=proofing_queue_dir,
            auto_approve_threshold=auto_approve_threshold
        )
        self.peer_reviewer = PeerReviewAgent()

        self.auto_approve_threshold = auto_approve_threshold

    def process_content(
        self,
        content: str,
        sport: str,
        data_sources: List[DataSource],
        citations: List[Citation] = None,
        embargo_until: Optional[datetime] = None,
        fact_checks: List[Dict[str, Any]] = None
    ) -> QualityReport:
        """
        Process content through complete quality pipeline

        Args:
            content: Content to process
            sport: Sport category
            data_sources: List of data sources
            citations: Optional citations
            embargo_until: Optional embargo datetime
            fact_checks: Optional fact-check data

        Returns:
            Complete quality report
        """
        citations = citations or []
        fact_checks = fact_checks or []

        # Generate report ID
        report_id = str(uuid.uuid4())[:8]

        # Step 1: Timestamp verification
        oldest_source = self.timestamp_validator.get_oldest_data(data_sources)
        if oldest_source:
            timestamp_verification = self.timestamp_validator.verify_data_source(oldest_source)
        else:
            timestamp_verification = TimestampVerification(
                data_timestamp=datetime.utcnow(),
                age_hours=0,
                is_fresh=True,
                is_expired=False
            )

        # Step 2: Betting disclaimer check
        betting_disclaimer = self.disclaimer_enforcer.check_disclaimer_present(content)

        # Step 3: Citation validation
        citation_results = self.citation_validator.validate_citations(citations)
        citations_valid = citation_results['all_valid']

        # Step 4: Speculation detection
        speculation_analysis = self.speculation_detector.analyze_content(content)
        speculation_flags = speculation_analysis['flags']

        # Step 5: Embargo check
        embargo_check = None
        if embargo_until:
            embargo_check = self.embargo_manager.create_embargo(
                content_id=report_id,
                embargo_until=embargo_until
            )

        # Step 6: Fact-checking
        fact_check_results = []
        if fact_checks:
            for fact in fact_checks:
                result = self.fact_checker.check_fact(**fact)
                fact_check_results.append(result)

        # Step 7: Quality scoring
        quality_score = self.quality_scorer.calculate_quality_score(
            content=content,
            fact_checks=fact_check_results,
            data_sources=data_sources,
            speculation_flags=len(speculation_flags),
            citations_count=len(citations)
        )

        # Step 8: Build compliance status
        compliance_status = ComplianceStatus(
            level=ComplianceLevel.PASS,  # Will be determined
            betting_disclaimer=betting_disclaimer,
            timestamp_verification=timestamp_verification,
            citations_valid=citations_valid,
            speculation_flags=speculation_flags,
            data_sources=data_sources,
            embargo_check=embargo_check,
            peer_review=PeerReviewChecklist()  # Will be filled
        )

        # Build audit record
        audit_record = AuditRecord(
            record_id=report_id,
            sport=sport,
            report_type="daily_digest",
            compliance_status=compliance_status,
            quality_score=quality_score,
            fact_checks=fact_check_results,
            data_sources=data_sources,
            citations=citations
        )

        # Build quality report
        quality_report = QualityReport(
            report_id=report_id,
            sport=sport,
            compliance=compliance_status,
            quality=quality_score,
            audit=audit_record
        )

        # Step 9: Peer review
        peer_review = self.peer_reviewer.perform_review(quality_report)
        compliance_status.peer_review = peer_review

        # Step 10: Determine compliance issues
        self._determine_compliance_issues(compliance_status, quality_score)

        # Step 11: Determine publish status
        quality_report.determine_publish_status(self.auto_approve_threshold)

        # Step 12: Generate recommendations
        quality_report.recommendations = self.quality_scorer.get_improvement_recommendations(
            quality_score,
            content
        )

        # Step 13: Generate summary
        quality_report.summary = self._generate_summary(quality_report)

        return quality_report

    def _determine_compliance_issues(
        self,
        compliance: ComplianceStatus,
        quality_score: QualityScore
    ):
        """Determine compliance issues and warnings"""
        issues = []
        warnings = []

        # Betting disclaimer
        if not compliance.betting_disclaimer.is_present:
            issues.append("Missing betting disclaimer")

        # Timestamp
        if compliance.timestamp_verification.is_expired:
            issues.append(
                f"Data expired ({compliance.timestamp_verification.age_hours:.1f} hours old)"
            )
        elif not compliance.timestamp_verification.is_fresh:
            warnings.append(
                f"Data aging ({compliance.timestamp_verification.age_hours:.1f} hours old)"
            )

        # Citations
        if not compliance.citations_valid:
            warnings.append("Some citations are invalid")

        # Speculation
        high_severity_speculation = len([
            f for f in compliance.speculation_flags
            if f.severity == 'high'
        ])
        if high_severity_speculation > 0:
            issues.append(
                f"{high_severity_speculation} high-severity speculation flag(s)"
            )

        # Quality
        if quality_score.overall_score < 70:
            issues.append(
                f"Quality score below minimum ({quality_score.overall_score:.1f}%)"
            )

        compliance.issues = issues
        compliance.warnings = warnings

        # Determine overall level
        compliance.level = compliance.determine_level()

    def _generate_summary(self, quality_report: QualityReport) -> str:
        """Generate summary of quality report"""
        parts = []

        # Overall status
        if quality_report.can_publish:
            if quality_report.auto_approve:
                parts.append("✅ Ready to publish (auto-approved)")
            else:
                parts.append("⚠️ Ready to publish (requires manual review)")
        else:
            parts.append("❌ Cannot publish (quality/compliance issues)")

        # Quality
        parts.append(
            f"Quality: {quality_report.quality.overall_score:.1f}% "
            f"({self.quality_scorer.assess_quality_level(quality_report.quality)})"
        )

        # Compliance
        parts.append(f"Compliance: {quality_report.compliance.level.value.upper()}")

        return " | ".join(parts)

    def publish_content(
        self,
        content: str,
        quality_report: QualityReport,
        add_disclaimer: bool = True,
        add_transparency_tag: bool = True
    ) -> Dict[str, Any]:
        """
        Publish content with enhancements

        Args:
            content: Original content
            quality_report: Quality assessment
            add_disclaimer: Add betting disclaimer if missing
            add_transparency_tag: Add transparency tag

        Returns:
            Publication result with enhanced content
        """
        enhanced_content = content

        # Add disclaimer if needed
        if add_disclaimer and not quality_report.compliance.betting_disclaimer.is_present:
            enhanced_content = self.disclaimer_enforcer.inject_disclaimer(
                enhanced_content
            )

        # Add transparency tag
        if add_transparency_tag:
            enhanced_content = self.transparency_tagger.inject_transparency_tag(
                enhanced_content,
                quality_report.compliance.data_sources
            )

        # Log to audit
        audit_path = self.audit_logger.log_publication(quality_report.audit)

        # Save version
        version_hash = self.version_tracker.save_version(
            content=enhanced_content,
            version_id=quality_report.report_id,
            metadata={
                'sport': quality_report.sport,
                'quality_score': quality_report.quality.overall_score,
                'compliance_level': quality_report.compliance.level.value
            }
        )

        return {
            'success': True,
            'report_id': quality_report.report_id,
            'enhanced_content': enhanced_content,
            'audit_log_path': audit_path,
            'version_hash': version_hash,
            'quality_score': quality_report.quality.overall_score,
            'auto_approved': quality_report.auto_approve
        }

    def add_to_proofing_queue(
        self,
        content: str,
        quality_report: QualityReport,
        priority: int = 3
    ) -> str:
        """
        Add content to proofing queue

        Args:
            content: Content to review
            quality_report: Quality assessment
            priority: Priority level

        Returns:
            Queue ID
        """
        item = self.proofing_queue.add_to_queue(
            content=content,
            quality_report=quality_report,
            priority=priority
        )

        return item.queue_id

    def get_compliance_summary(self, compliance: ComplianceStatus) -> str:
        """Get formatted compliance summary"""
        return self.compliance_generator.generate_summary(compliance)

    def get_peer_review_report(self, checklist: PeerReviewChecklist) -> str:
        """Get formatted peer review report"""
        return self.peer_reviewer.generate_review_report(checklist)

    def get_audit_report(self, sport: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get audit report for time period"""
        return self.audit_logger.generate_audit_report(sport=sport, days=days)

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get proofing queue statistics"""
        return self.proofing_queue.get_queue_stats()
