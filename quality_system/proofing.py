"""
Proofing queue with auto-approve thresholds

Manages content review workflow with automatic approval
for high-quality content.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from queue import PriorityQueue
from .models import (
    ProofingQueueItem,
    QualityReport,
    PeerReviewChecklist,
    ComplianceLevel
)


class ProofingQueue:
    """
    Manage proofing queue with auto-approval

    Content that meets quality and compliance thresholds
    is automatically approved. Other content requires manual review.
    """

    def __init__(
        self,
        storage_dir: str = "proofing_queue",
        auto_approve_threshold: float = 85.0,
        min_compliance_level: ComplianceLevel = ComplianceLevel.WARNING
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.auto_approve_threshold = auto_approve_threshold
        self.min_compliance_level = min_compliance_level

        # Priority queue (lower number = higher priority)
        self.queue: List[ProofingQueueItem] = []

        self._load_queue()

    def add_to_queue(
        self,
        content: str,
        quality_report: QualityReport,
        priority: int = 3
    ) -> ProofingQueueItem:
        """
        Add item to proofing queue

        Args:
            content: Content to review
            quality_report: Quality assessment
            priority: Priority level (1=highest, 5=lowest)

        Returns:
            ProofingQueueItem
        """
        # Generate queue ID
        timestamp = datetime.utcnow()
        queue_id = f"{timestamp.strftime('%Y%m%d%H%M%S')}_{quality_report.report_id}"

        # Create queue item
        item = ProofingQueueItem(
            queue_id=queue_id,
            content=content,
            quality_report=quality_report,
            status="pending",
            priority=priority,
            created_at=timestamp
        )

        # Check if should auto-approve
        if self._should_auto_approve(quality_report):
            item.status = "approved"
            item.quality_report.auto_approve = True
            item.reviewed_at = timestamp

        # Add to queue
        self.queue.append(item)
        self._save_item(item)

        return item

    def _should_auto_approve(self, quality_report: QualityReport) -> bool:
        """
        Determine if item should be auto-approved

        Criteria:
        - Quality score >= threshold
        - Compliance level acceptable
        - All required checks passed
        """
        # Check quality score
        if quality_report.quality.overall_score < self.auto_approve_threshold:
            return False

        # Check compliance level
        if quality_report.compliance.level == ComplianceLevel.FAIL:
            return False

        if quality_report.compliance.level == ComplianceLevel.BLOCKED:
            return False

        # Check peer review checklist
        pr = quality_report.compliance.peer_review
        pr.calculate_pass_rate()

        if pr.pass_rate < 90.0:  # Require 90% pass rate
            return False

        # All checks passed
        return True

    def get_next_item(
        self,
        status: str = "pending",
        priority_order: bool = True
    ) -> Optional[ProofingQueueItem]:
        """
        Get next item from queue

        Args:
            status: Filter by status
            priority_order: Sort by priority

        Returns:
            Next queue item or None
        """
        # Filter by status
        filtered = [item for item in self.queue if item.status == status]

        if not filtered:
            return None

        # Sort by priority
        if priority_order:
            filtered.sort(key=lambda x: (x.priority, x.created_at))

        return filtered[0]

    def approve_item(
        self,
        queue_id: str,
        reviewer_notes: str = ""
    ) -> Optional[ProofingQueueItem]:
        """
        Approve an item

        Args:
            queue_id: Queue item ID
            reviewer_notes: Optional reviewer notes

        Returns:
            Updated item or None
        """
        item = self._get_item_by_id(queue_id)

        if not item:
            return None

        item.status = "approved"
        item.reviewed_at = datetime.utcnow()
        item.reviewer_notes = reviewer_notes

        self._save_item(item)
        return item

    def reject_item(
        self,
        queue_id: str,
        reviewer_notes: str
    ) -> Optional[ProofingQueueItem]:
        """
        Reject an item

        Args:
            queue_id: Queue item ID
            reviewer_notes: Required rejection reason

        Returns:
            Updated item or None
        """
        item = self._get_item_by_id(queue_id)

        if not item:
            return None

        item.status = "rejected"
        item.reviewed_at = datetime.utcnow()
        item.reviewer_notes = reviewer_notes

        self._save_item(item)
        return item

    def publish_item(self, queue_id: str) -> Optional[ProofingQueueItem]:
        """
        Mark item as published

        Args:
            queue_id: Queue item ID

        Returns:
            Updated item or None
        """
        item = self._get_item_by_id(queue_id)

        if not item:
            return None

        if item.status != "approved":
            # Can't publish non-approved items
            return None

        item.status = "published"
        item.published_at = datetime.utcnow()

        self._save_item(item)
        return item

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics

        Returns:
            Queue stats
        """
        total = len(self.queue)

        by_status = {}
        for item in self.queue:
            by_status[item.status] = by_status.get(item.status, 0) + 1

        by_priority = {}
        for item in self.queue:
            by_priority[item.priority] = by_priority.get(item.priority, 0) + 1

        auto_approved = sum(
            1 for item in self.queue
            if item.quality_report.auto_approve
        )

        # Average quality scores
        quality_scores = [
            item.quality_report.quality.overall_score
            for item in self.queue
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        return {
            'total_items': total,
            'by_status': by_status,
            'by_priority': by_priority,
            'auto_approved': auto_approved,
            'auto_approve_rate': (auto_approved / total * 100) if total > 0 else 0,
            'average_quality_score': avg_quality,
            'pending_review': by_status.get('pending', 0)
        }

    def _get_item_by_id(self, queue_id: str) -> Optional[ProofingQueueItem]:
        """Find item by queue ID"""
        for item in self.queue:
            if item.queue_id == queue_id:
                return item
        return None

    def _save_item(self, item: ProofingQueueItem):
        """Save item to disk"""
        item_file = self.storage_dir / f"{item.queue_id}.json"

        with open(item_file, 'w') as f:
            f.write(item.json(indent=2))

    def _load_queue(self):
        """Load queue from disk"""
        if not self.storage_dir.exists():
            return

        for item_file in self.storage_dir.glob("*.json"):
            try:
                with open(item_file, 'r') as f:
                    data = json.load(f)
                    item = ProofingQueueItem(**data)
                    self.queue.append(item)
            except Exception as e:
                # Skip corrupted files
                print(f"Warning: Could not load {item_file}: {e}")

        # Sort queue by priority and creation time
        self.queue.sort(key=lambda x: (x.priority, x.created_at))


class PeerReviewAgent:
    """
    Automated peer review checklist agent

    Performs systematic checks on content quality
    """

    def __init__(self):
        pass

    def perform_review(
        self,
        quality_report: QualityReport
    ) -> PeerReviewChecklist:
        """
        Perform peer review checks

        Args:
            quality_report: Quality report to review

        Returns:
            Completed peer review checklist
        """
        checklist = PeerReviewChecklist()

        # Check betting disclaimer
        checklist.has_betting_disclaimer = (
            quality_report.compliance.betting_disclaimer.is_present
        )

        # Check data sources
        checklist.has_data_sources = (
            len(quality_report.compliance.data_sources) > 0
        )

        # Check speculation
        checklist.no_speculation = (
            len(quality_report.compliance.speculation_flags) == 0
        )

        # Check facts verified
        checklist.facts_verified = (
            len(quality_report.audit.fact_checks) > 0 and
            all(fc.matches for fc in quality_report.audit.fact_checks)
        )

        # Check data freshness
        checklist.data_is_fresh = (
            quality_report.compliance.timestamp_verification.is_fresh and
            not quality_report.compliance.timestamp_verification.is_expired
        )

        # Check embargo
        if quality_report.compliance.embargo_check:
            checklist.embargo_respected = (
                quality_report.compliance.embargo_check.can_publish
            )
        else:
            checklist.embargo_respected = True  # No embargo = respected

        # Check citations
        checklist.citations_present = (
            len(quality_report.audit.citations) > 0
        )

        # Check quality threshold (70% minimum)
        checklist.quality_threshold_met = (
            quality_report.quality.overall_score >= 70.0
        )

        # Calculate pass rate
        checklist.calculate_pass_rate()

        return checklist

    def generate_review_report(
        self,
        checklist: PeerReviewChecklist
    ) -> str:
        """
        Generate human-readable review report

        Args:
            checklist: Completed checklist

        Returns:
            Formatted report
        """
        lines = [
            "=" * 60,
            "PEER REVIEW CHECKLIST",
            "=" * 60,
            "",
            f"Pass Rate: {checklist.pass_rate:.1f}% ({checklist.passed_items}/{checklist.total_items})",
            ""
        ]

        # List all checks
        checks = [
            ("Betting Disclaimer", checklist.has_betting_disclaimer),
            ("Data Sources", checklist.has_data_sources),
            ("No Speculation", checklist.no_speculation),
            ("Facts Verified", checklist.facts_verified),
            ("Data Fresh", checklist.data_is_fresh),
            ("Embargo Respected", checklist.embargo_respected),
            ("Citations Present", checklist.citations_present),
            ("Quality Threshold", checklist.quality_threshold_met)
        ]

        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            lines.append(f"{check_name:.<40} {status}")

        lines.append("")
        lines.append("=" * 60)

        return '\n'.join(lines)
