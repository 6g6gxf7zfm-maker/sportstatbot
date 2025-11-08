"""
Compliance enforcers for Quality System

Includes:
- Betting disclaimer enforcement
- Embargo management
- Transparency tagging
- Compliance summary generation
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .models import (
    BettingDisclaimer,
    EmbargoTimer,
    DataSource,
    ComplianceStatus,
    ComplianceLevel,
    PeerReviewChecklist,
    TimestampVerification,
    SpeculationFlag
)


class BettingDisclaimerEnforcer:
    """Enforce betting disclaimers in all content"""

    DEFAULT_DISCLAIMERS = [
        "This analysis is for informational purposes only. Please gamble responsibly.",
        "Betting odds and analysis provided for entertainment only. Gamble responsibly.",
        "All betting information is for educational purposes. If you or someone you know has a gambling problem, call 1-800-GAMBLER.",
    ]

    REQUIRED_KEYWORDS = ['gamble responsibly', 'informational purposes', 'entertainment']

    def __init__(self, custom_disclaimer: Optional[str] = None):
        self.custom_disclaimer = custom_disclaimer or self.DEFAULT_DISCLAIMERS[0]

    def check_disclaimer_present(self, content: str) -> BettingDisclaimer:
        """
        Check if betting disclaimer is present in content

        Args:
            content: Content to check

        Returns:
            BettingDisclaimer status
        """
        content_lower = content.lower()

        # Check if any required keywords are present
        has_keywords = any(
            keyword in content_lower
            for keyword in self.REQUIRED_KEYWORDS
        )

        # Try to find disclaimer placement
        placement = self._detect_placement(content)

        return BettingDisclaimer(
            disclaimer_text=self.custom_disclaimer,
            placement=placement or "missing",
            is_present=has_keywords,
            timestamp=datetime.utcnow()
        )

    def _detect_placement(self, content: str) -> Optional[str]:
        """Detect where disclaimer is placed"""
        content_lower = content.lower()
        lines = content.split('\n')

        # Check header (first 5 lines)
        header = '\n'.join(lines[:5]).lower()
        if any(kw in header for kw in self.REQUIRED_KEYWORDS):
            return "header"

        # Check footer (last 5 lines)
        footer = '\n'.join(lines[-5:]).lower()
        if any(kw in footer for kw in self.REQUIRED_KEYWORDS):
            return "footer"

        # Check if it's inline somewhere
        if any(kw in content_lower for kw in self.REQUIRED_KEYWORDS):
            return "inline"

        return None

    def inject_disclaimer(
        self,
        content: str,
        placement: str = "footer",
        include_betting_content: bool = True
    ) -> str:
        """
        Inject disclaimer into content if not present

        Args:
            content: Original content
            placement: Where to place it ("header", "footer")
            include_betting_content: Only inject if betting content detected

        Returns:
            Content with disclaimer
        """
        # Check if disclaimer already present
        disclaimer_status = self.check_disclaimer_present(content)
        if disclaimer_status.is_present:
            return content

        # Check if betting content is present
        if include_betting_content and not self._has_betting_content(content):
            return content

        # Inject disclaimer
        formatted_disclaimer = f"\n\n---\n**DISCLAIMER:** {self.custom_disclaimer}\n---\n"

        if placement == "header":
            return formatted_disclaimer + content
        else:  # footer
            return content + formatted_disclaimer

    def _has_betting_content(self, content: str) -> bool:
        """Check if content contains betting-related information"""
        betting_keywords = [
            'odds', 'spread', 'over/under', 'moneyline', 'betting',
            'wager', 'line', 'favorite', 'underdog', 'value bet'
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in betting_keywords)


class EmbargoManager:
    """Manage content embargoes"""

    def __init__(self):
        self.active_embargoes: Dict[str, EmbargoTimer] = {}

    def create_embargo(
        self,
        content_id: str,
        embargo_until: datetime
    ) -> EmbargoTimer:
        """
        Create an embargo for content

        Args:
            content_id: Unique identifier for content
            embargo_until: DateTime when embargo lifts

        Returns:
            EmbargoTimer object
        """
        now = datetime.utcnow()
        is_embargoed = now < embargo_until

        timer = EmbargoTimer(
            content_id=content_id,
            embargo_until=embargo_until,
            is_embargoed=is_embargoed,
            can_publish=not is_embargoed
        )

        self.active_embargoes[content_id] = timer
        return timer

    def check_embargo(self, content_id: str) -> Optional[EmbargoTimer]:
        """Check embargo status for content"""
        if content_id not in self.active_embargoes:
            return None

        embargo = self.active_embargoes[content_id]

        # Update status
        now = datetime.utcnow()
        embargo.is_embargoed = now < embargo.embargo_until
        embargo.can_publish = not embargo.is_embargoed

        return embargo

    def clear_expired_embargoes(self) -> int:
        """Remove expired embargoes and return count"""
        now = datetime.utcnow()
        expired = [
            content_id
            for content_id, embargo in self.active_embargoes.items()
            if now >= embargo.embargo_until
        ]

        for content_id in expired:
            del self.active_embargoes[content_id]

        return len(expired)

    def get_active_embargoes(self) -> List[EmbargoTimer]:
        """Get all active embargoes"""
        return [
            embargo
            for embargo in self.active_embargoes.values()
            if embargo.is_embargoed
        ]


class TransparencyTagger:
    """Add transparency tags with data sources"""

    def __init__(self):
        pass

    def create_transparency_tag(self, sources: List[DataSource]) -> str:
        """
        Create transparency tag listing all data sources

        Args:
            sources: List of data sources used

        Returns:
            Formatted transparency tag
        """
        if not sources:
            return "\n\n---\n**DATA SOURCES:** No external sources used\n---\n"

        # Group by source name
        source_groups: Dict[str, List[DataSource]] = {}
        for source in sources:
            if source.name not in source_groups:
                source_groups[source.name] = []
            source_groups[source.name].append(source)

        # Build tag
        lines = ["\n\n---", "**DATA SOURCES:**"]

        for source_name, source_list in source_groups.items():
            data_types = list(set(s.data_type for s in source_list))
            timestamps = [s.timestamp for s in source_list]
            most_recent = max(timestamps)

            age = datetime.utcnow() - most_recent
            age_str = self._format_age(age)

            line = f"- **{source_name}** ({', '.join(data_types)}) - Updated {age_str}"

            # Add URL if available
            url = next((s.url for s in source_list if s.url), None)
            if url:
                line += f" - [{url}]"

            lines.append(line)

        lines.append("---\n")
        return '\n'.join(lines)

    def inject_transparency_tag(self, content: str, sources: List[DataSource]) -> str:
        """
        Inject transparency tag into content

        Args:
            content: Original content
            sources: Data sources to tag

        Returns:
            Content with transparency tag
        """
        tag = self.create_transparency_tag(sources)
        return content + tag

    def _format_age(self, age: timedelta) -> str:
        """Format age timedelta to human-readable string"""
        total_seconds = age.total_seconds()

        if total_seconds < 60:
            return "just now"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(total_seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"


class ComplianceSummaryGenerator:
    """Generate compliance summary sheets"""

    def __init__(self):
        pass

    def generate_summary(self, compliance: ComplianceStatus) -> str:
        """
        Generate human-readable compliance summary

        Args:
            compliance: ComplianceStatus object

        Returns:
            Formatted compliance summary
        """
        lines = [
            "=" * 60,
            "COMPLIANCE SUMMARY",
            "=" * 60,
            ""
        ]

        # Overall status
        status_emoji = {
            ComplianceLevel.PASS: "✅",
            ComplianceLevel.WARNING: "⚠️",
            ComplianceLevel.FAIL: "❌",
            ComplianceLevel.BLOCKED: "🚫"
        }

        emoji = status_emoji.get(compliance.level, "❓")
        lines.append(f"Overall Status: {emoji} {compliance.level.value.upper()}")
        lines.append("")

        # Betting disclaimer
        lines.append("📋 BETTING DISCLAIMER:")
        disclaimer_status = "✅ Present" if compliance.betting_disclaimer.is_present else "❌ Missing"
        lines.append(f"  Status: {disclaimer_status}")
        lines.append(f"  Placement: {compliance.betting_disclaimer.placement}")
        lines.append("")

        # Timestamp verification
        lines.append("🕐 TIMESTAMP VERIFICATION:")
        ts = compliance.timestamp_verification
        freshness_status = "✅ Fresh" if ts.is_fresh else ("⚠️ Aging" if not ts.is_expired else "❌ Expired")
        lines.append(f"  Status: {freshness_status}")
        lines.append(f"  Data Age: {ts.age_hours:.1f} hours")
        if ts.warning_message:
            lines.append(f"  Warning: {ts.warning_message}")
        lines.append("")

        # Citations
        lines.append("📚 CITATIONS:")
        citation_status = "✅ Valid" if compliance.citations_valid else "❌ Invalid"
        lines.append(f"  Status: {citation_status}")
        lines.append(f"  Sources: {len(compliance.data_sources)}")
        lines.append("")

        # Speculation
        lines.append("🔍 SPECULATION CHECK:")
        spec_count = len(compliance.speculation_flags)
        if spec_count == 0:
            lines.append("  Status: ✅ No speculation detected")
        else:
            lines.append(f"  Status: ⚠️ {spec_count} flag(s) detected")
            high_severity = len([f for f in compliance.speculation_flags if f.severity == 'high'])
            if high_severity > 0:
                lines.append(f"  High Severity: {high_severity}")
        lines.append("")

        # Embargo
        if compliance.embargo_check:
            lines.append("⏰ EMBARGO STATUS:")
            if compliance.embargo_check.can_publish:
                lines.append("  Status: ✅ Can publish (embargo lifted)")
            else:
                lines.append(f"  Status: 🚫 Embargoed ({compliance.embargo_check.time_remaining} remaining)")
            lines.append("")

        # Peer review
        lines.append("✓ PEER REVIEW CHECKLIST:")
        pr = compliance.peer_review
        pr.calculate_pass_rate()
        lines.append(f"  Pass Rate: {pr.pass_rate:.1f}% ({pr.passed_items}/{pr.total_items})")
        lines.append(f"  - Betting Disclaimer: {'✅' if pr.has_betting_disclaimer else '❌'}")
        lines.append(f"  - Data Sources: {'✅' if pr.has_data_sources else '❌'}")
        lines.append(f"  - No Speculation: {'✅' if pr.no_speculation else '❌'}")
        lines.append(f"  - Facts Verified: {'✅' if pr.facts_verified else '❌'}")
        lines.append(f"  - Data Fresh: {'✅' if pr.data_is_fresh else '❌'}")
        lines.append(f"  - Embargo Respected: {'✅' if pr.embargo_respected else '❌'}")
        lines.append(f"  - Citations Present: {'✅' if pr.citations_present else '❌'}")
        lines.append(f"  - Quality Threshold: {'✅' if pr.quality_threshold_met else '❌'}")
        lines.append("")

        # Issues and warnings
        if compliance.issues:
            lines.append("❌ ISSUES:")
            for issue in compliance.issues:
                lines.append(f"  - {issue}")
            lines.append("")

        if compliance.warnings:
            lines.append("⚠️ WARNINGS:")
            for warning in compliance.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        lines.append("=" * 60)

        return '\n'.join(lines)

    def generate_json_summary(self, compliance: ComplianceStatus) -> Dict[str, Any]:
        """Generate machine-readable JSON summary"""
        pr = compliance.peer_review
        pr.calculate_pass_rate()

        return {
            'overall_status': compliance.level.value,
            'betting_disclaimer': {
                'present': compliance.betting_disclaimer.is_present,
                'placement': compliance.betting_disclaimer.placement
            },
            'timestamp': {
                'fresh': compliance.timestamp_verification.is_fresh,
                'expired': compliance.timestamp_verification.is_expired,
                'age_hours': compliance.timestamp_verification.age_hours
            },
            'citations_valid': compliance.citations_valid,
            'speculation_flags': len(compliance.speculation_flags),
            'data_sources': len(compliance.data_sources),
            'embargo': {
                'active': compliance.embargo_check.is_embargoed if compliance.embargo_check else False,
                'can_publish': compliance.embargo_check.can_publish if compliance.embargo_check else True
            },
            'peer_review': {
                'pass_rate': pr.pass_rate,
                'passed_items': pr.passed_items,
                'total_items': pr.total_items
            },
            'issues_count': len(compliance.issues),
            'warnings_count': len(compliance.warnings)
        }
