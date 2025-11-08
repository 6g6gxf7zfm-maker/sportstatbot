"""
Quality scoring system

Calculates accuracy, clarity, and timeliness scores for reports
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .models import QualityScore, FactCheckResult, DataSource


class QualityScorer:
    """
    Calculate comprehensive quality scores

    Evaluates:
    - Accuracy: Based on fact-checking results
    - Clarity: Based on readability and structure
    - Timeliness: Based on data freshness
    """

    def __init__(self):
        self.weights = {
            'accuracy': 0.4,
            'clarity': 0.3,
            'timeliness': 0.3
        }

    def calculate_quality_score(
        self,
        content: str,
        fact_checks: List[FactCheckResult],
        data_sources: List[DataSource],
        speculation_flags: int = 0,
        citations_count: int = 0
    ) -> QualityScore:
        """
        Calculate comprehensive quality score

        Args:
            content: Report content
            fact_checks: List of fact-check results
            data_sources: Data sources used
            speculation_flags: Number of speculation flags
            citations_count: Number of citations

        Returns:
            QualityScore object
        """
        # Calculate individual scores
        accuracy = self._calculate_accuracy(fact_checks, speculation_flags)
        clarity = self._calculate_clarity(content, citations_count)
        timeliness = self._calculate_timeliness(data_sources)

        # Get data freshness
        data_freshness_hours = self._get_data_freshness(data_sources)

        # Count facts verified
        facts_verified = sum(1 for fc in fact_checks if fc.matches)

        score = QualityScore(
            accuracy_score=accuracy,
            clarity_score=clarity,
            timeliness_score=timeliness,
            overall_score=0.0,  # Will be calculated
            citations_count=citations_count,
            facts_verified=facts_verified,
            speculation_flags=speculation_flags,
            data_freshness_hours=data_freshness_hours
        )

        score.calculate_overall()
        return score

    def _calculate_accuracy(
        self,
        fact_checks: List[FactCheckResult],
        speculation_flags: int
    ) -> float:
        """
        Calculate accuracy score (0-100)

        Based on:
        - Fact-check pass rate
        - Number of speculation flags
        - Confidence levels
        """
        if not fact_checks:
            # No fact-checks performed - assume moderate accuracy
            base_score = 70.0
        else:
            # Calculate pass rate
            passed = sum(1 for fc in fact_checks if fc.matches)
            total = len(fact_checks)
            pass_rate = (passed / total) * 100

            # Weight by confidence
            avg_confidence = sum(fc.confidence for fc in fact_checks) / total
            base_score = pass_rate * avg_confidence

        # Penalize for speculation
        speculation_penalty = min(30.0, speculation_flags * 5.0)
        accuracy = max(0.0, base_score - speculation_penalty)

        return min(100.0, accuracy)

    def _calculate_clarity(
        self,
        content: str,
        citations_count: int
    ) -> float:
        """
        Calculate clarity score (0-100)

        Based on:
        - Readability metrics
        - Structure and formatting
        - Presence of citations
        - Content length appropriateness
        """
        # Basic metrics
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])

        # Calculate readability (simplified Flesch-Kincaid)
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Optimal sentence length: 15-20 words
        if 15 <= avg_sentence_length <= 20:
            readability_score = 100.0
        elif avg_sentence_length < 10:
            readability_score = 70.0  # Too choppy
        elif avg_sentence_length > 30:
            readability_score = 60.0  # Too complex
        else:
            readability_score = 85.0

        # Structure score
        has_headers = bool(re.search(r'^#{1,3}\s+.+$', content, re.MULTILINE))
        has_bullets = bool(re.search(r'^[\*\-\+]\s+.+$', content, re.MULTILINE))
        has_formatting = bool(re.search(r'\*\*.+\*\*|__.+__', content))

        structure_elements = sum([has_headers, has_bullets, has_formatting])
        structure_score = (structure_elements / 3) * 100

        # Citation bonus
        citation_score = min(100.0, (citations_count / 5) * 100)

        # Content length appropriateness
        if word_count < 100:
            length_score = 50.0  # Too short
        elif 200 <= word_count <= 800:
            length_score = 100.0  # Ideal
        elif word_count > 1500:
            length_score = 70.0  # Too long
        else:
            length_score = 85.0

        # Weighted average
        clarity = (
            readability_score * 0.3 +
            structure_score * 0.2 +
            citation_score * 0.2 +
            length_score * 0.3
        )

        return min(100.0, clarity)

    def _calculate_timeliness(self, data_sources: List[DataSource]) -> float:
        """
        Calculate timeliness score (0-100)

        Based on data source freshness
        """
        if not data_sources:
            return 50.0  # Neutral if no sources

        # Get ages of all sources
        now = datetime.utcnow()
        ages_hours = [
            (now - source.timestamp).total_seconds() / 3600
            for source in data_sources
        ]

        # Average age
        avg_age_hours = sum(ages_hours) / len(ages_hours)

        # Score based on age
        # Excellent: < 6 hours
        # Good: 6-12 hours
        # Fair: 12-24 hours
        # Poor: > 24 hours

        if avg_age_hours < 6:
            score = 100.0
        elif avg_age_hours < 12:
            score = 90.0
        elif avg_age_hours < 24:
            score = 75.0
        elif avg_age_hours < 48:
            score = 50.0
        else:
            score = max(0.0, 50.0 - (avg_age_hours - 48) * 2)

        return min(100.0, score)

    def _get_data_freshness(self, data_sources: List[DataSource]) -> float:
        """Get average data freshness in hours"""
        if not data_sources:
            return 0.0

        now = datetime.utcnow()
        ages = [
            (now - source.timestamp).total_seconds() / 3600
            for source in data_sources
        ]

        return sum(ages) / len(ages)

    def assess_quality_level(self, score: QualityScore) -> str:
        """
        Assess quality level from score

        Returns:
            Quality level string
        """
        overall = score.overall_score

        if overall >= 90:
            return "Excellent"
        elif overall >= 80:
            return "Good"
        elif overall >= 70:
            return "Fair"
        elif overall >= 60:
            return "Poor"
        else:
            return "Unacceptable"

    def get_improvement_recommendations(
        self,
        score: QualityScore,
        content: str
    ) -> List[str]:
        """
        Generate recommendations for improvement

        Args:
            score: Current quality score
            content: Report content

        Returns:
            List of recommendations
        """
        recommendations = []

        # Accuracy recommendations
        if score.accuracy_score < 80:
            if score.speculation_flags > 0:
                recommendations.append(
                    f"Remove or verify {score.speculation_flags} speculative statement(s)"
                )
            if score.facts_verified == 0:
                recommendations.append("Add fact-checking against authoritative sources")

        # Clarity recommendations
        if score.clarity_score < 80:
            word_count = len(content.split())

            if word_count < 100:
                recommendations.append("Expand content with more detail and context")

            if score.citations_count < 3:
                recommendations.append("Add more citations to support claims")

            if not re.search(r'^#{1,3}\s+.+$', content, re.MULTILINE):
                recommendations.append("Add section headers to improve structure")

        # Timeliness recommendations
        if score.timeliness_score < 80:
            if score.data_freshness_hours > 24:
                recommendations.append(
                    f"Refresh data (current: {score.data_freshness_hours:.1f} hours old)"
                )

        # Overall recommendations
        if score.overall_score < 70:
            recommendations.append("Content does not meet minimum quality threshold (70%)")

        return recommendations
