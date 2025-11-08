"""
Validators for Quality, Compliance & Audit Trail System

Includes:
- Timestamp verification
- Citation validation
- Speculation detection
- Data freshness checks
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .models import (
    TimestampVerification,
    Citation,
    SpeculationFlag,
    DataSource
)


class TimestampValidator:
    """Validate timestamps and data freshness"""

    def __init__(self, max_age_hours: int = 24, warning_threshold_hours: int = 12):
        self.max_age_hours = max_age_hours
        self.warning_threshold_hours = warning_threshold_hours

    def verify_timestamp(self, data_timestamp: datetime) -> TimestampVerification:
        """
        Verify a timestamp and check freshness

        Args:
            data_timestamp: The timestamp to verify

        Returns:
            TimestampVerification with freshness status
        """
        now = datetime.utcnow()
        age = now - data_timestamp
        age_hours = age.total_seconds() / 3600

        is_expired = age_hours > self.max_age_hours
        is_fresh = age_hours <= self.warning_threshold_hours

        warning_message = None
        if is_expired:
            warning_message = f"Data is expired ({age_hours:.1f} hours old, max: {self.max_age_hours})"
        elif not is_fresh:
            warning_message = f"Data is aging ({age_hours:.1f} hours old)"

        return TimestampVerification(
            data_timestamp=data_timestamp,
            verification_timestamp=now,
            age_hours=age_hours,
            is_fresh=is_fresh,
            is_expired=is_expired,
            warning_message=warning_message
        )

    def verify_data_source(self, source: DataSource) -> TimestampVerification:
        """Verify a data source timestamp"""
        return self.verify_timestamp(source.timestamp)

    def get_oldest_data(self, sources: List[DataSource]) -> Optional[DataSource]:
        """Find the oldest data source"""
        if not sources:
            return None
        return min(sources, key=lambda s: s.timestamp)

    def get_expired_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Get all expired data sources"""
        return [s for s in sources if s.is_expired(self.max_age_hours)]


class CitationValidator:
    """Validate citations and stat sources"""

    REQUIRED_CITATION_FIELDS = ['source', 'stat_type', 'value', 'timestamp']

    def __init__(self):
        self.verified_sources = {
            'ESPN',
            'The Odds API',
            'Official League Stats',
            'Team Website',
            'Official Announcement'
        }

    def validate_citation(self, citation: Citation) -> tuple[bool, List[str]]:
        """
        Validate a citation

        Args:
            citation: Citation to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check required fields
        if not citation.source:
            issues.append("Citation missing source")

        if not citation.stat_type:
            issues.append("Citation missing stat type")

        if citation.value is None:
            issues.append("Citation missing value")

        # Check source credibility
        if citation.source not in self.verified_sources:
            issues.append(f"Unverified source: {citation.source}")

        # Check timestamp freshness
        age = datetime.utcnow() - citation.timestamp
        if age > timedelta(hours=48):
            issues.append(f"Citation is stale ({age.total_seconds() / 3600:.1f} hours old)")

        # Check URL if provided
        if citation.url:
            if not self._is_valid_url(citation.url):
                issues.append(f"Invalid URL: {citation.url}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def validate_citations(self, citations: List[Citation]) -> Dict[str, Any]:
        """
        Validate multiple citations

        Returns:
            Dictionary with validation results
        """
        total = len(citations)
        valid = 0
        all_issues = []

        for citation in citations:
            is_valid, issues = self.validate_citation(citation)
            if is_valid:
                valid += 1
            else:
                all_issues.extend(issues)

        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'pass_rate': (valid / total * 100) if total > 0 else 0,
            'issues': all_issues,
            'all_valid': valid == total
        }

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class SpeculationDetector:
    """Detect speculative or unverified content"""

    def __init__(self):
        # Keywords that indicate speculation
        self.speculation_keywords = {
            'high': [
                'might', 'could be', 'possibly', 'rumored', 'unconfirmed',
                'reportedly', 'allegedly', 'speculation', 'sources say'
            ],
            'medium': [
                'likely', 'expected to', 'should', 'potential', 'may',
                'appears to', 'seems', 'probable'
            ],
            'low': [
                'trending toward', 'heading toward', 'looking like'
            ]
        }

        # Injury-related keywords that require verification
        self.injury_keywords = [
            'injury', 'injured', 'hurt', 'questionable', 'doubtful',
            'out', 'sidelined', 'day-to-day', 'week-to-week',
            'concussion protocol', 'IL', 'IR', 'DTD'
        ]

    def detect_speculation(self, content: str) -> List[SpeculationFlag]:
        """
        Detect speculative content

        Args:
            content: Text to analyze

        Returns:
            List of speculation flags
        """
        flags = []
        content_lower = content.lower()

        # Check for speculation keywords
        for severity, keywords in self.speculation_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Find the sentence containing the keyword
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            flags.append(SpeculationFlag(
                                content=sentence.strip(),
                                reason=f"Contains speculative language: '{keyword}'",
                                severity=severity,
                                suggested_removal=severity == 'high',
                                keywords_matched=[keyword]
                            ))

        return flags

    def detect_unverified_injuries(self, content: str) -> List[SpeculationFlag]:
        """
        Detect injury mentions that may need verification

        Args:
            content: Text to analyze

        Returns:
            List of flags for potential unverified injuries
        """
        flags = []
        content_lower = content.lower()

        # Look for injury keywords without verification markers
        verification_markers = ['confirmed', 'official', 'announced', 'verified']

        for keyword in self.injury_keywords:
            if keyword in content_lower:
                # Check if nearby text has verification
                sentences = content.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        has_verification = any(
                            marker in sentence.lower()
                            for marker in verification_markers
                        )

                        if not has_verification:
                            flags.append(SpeculationFlag(
                                content=sentence.strip(),
                                reason=f"Injury mention without verification: '{keyword}'",
                                severity='high',
                                suggested_removal=False,  # Don't remove, but flag for review
                                keywords_matched=[keyword]
                            ))

        return flags

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Comprehensive speculation analysis

        Returns:
            Analysis results with all flags
        """
        speculation_flags = self.detect_speculation(content)
        injury_flags = self.detect_unverified_injuries(content)

        all_flags = speculation_flags + injury_flags

        return {
            'total_flags': len(all_flags),
            'speculation_flags': len(speculation_flags),
            'injury_flags': len(injury_flags),
            'high_severity': len([f for f in all_flags if f.severity == 'high']),
            'medium_severity': len([f for f in all_flags if f.severity == 'medium']),
            'low_severity': len([f for f in all_flags if f.severity == 'low']),
            'flags': all_flags,
            'needs_review': any(f.severity == 'high' for f in all_flags),
            'clean': len(all_flags) == 0
        }


class DataFreshnessChecker:
    """Check data freshness across multiple sources"""

    def __init__(self, max_age_hours: int = 24):
        self.max_age_hours = max_age_hours

    def check_freshness(self, sources: List[DataSource]) -> Dict[str, Any]:
        """
        Check freshness across all data sources

        Returns:
            Freshness analysis
        """
        if not sources:
            return {
                'has_data': False,
                'all_fresh': False,
                'any_expired': False,
                'oldest_age_hours': 0,
                'freshness_score': 0
            }

        ages = [
            (datetime.utcnow() - s.timestamp).total_seconds() / 3600
            for s in sources
        ]

        oldest_age = max(ages)
        newest_age = min(ages)
        avg_age = sum(ages) / len(ages)

        expired_count = sum(1 for age in ages if age > self.max_age_hours)

        # Calculate freshness score (0-100)
        freshness_score = max(0, min(100, 100 - (avg_age / self.max_age_hours * 100)))

        return {
            'has_data': True,
            'total_sources': len(sources),
            'all_fresh': all(age <= self.max_age_hours for age in ages),
            'any_expired': expired_count > 0,
            'expired_count': expired_count,
            'oldest_age_hours': oldest_age,
            'newest_age_hours': newest_age,
            'average_age_hours': avg_age,
            'freshness_score': freshness_score,
            'needs_refresh': freshness_score < 70
        }
