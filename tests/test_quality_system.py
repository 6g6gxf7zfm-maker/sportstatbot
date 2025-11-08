"""
Comprehensive tests for Quality, Compliance & Audit Trail System
"""

import pytest
from datetime import datetime, timedelta
from quality_system.core import QualityController
from quality_system.models import (
    DataSource,
    Citation,
    FactCheckResult,
    ComplianceLevel
)
from quality_system.validators import (
    TimestampValidator,
    CitationValidator,
    SpeculationDetector
)
from quality_system.compliance import (
    BettingDisclaimerEnforcer,
    EmbargoManager,
    TransparencyTagger
)
from quality_system.fact_checker import FactChecker
from quality_system.quality_scorer import QualityScorer


class TestTimestampValidator:
    """Test timestamp verification system"""

    def test_fresh_data(self):
        """Test detection of fresh data"""
        validator = TimestampValidator(max_age_hours=24)
        timestamp = datetime.utcnow() - timedelta(hours=2)

        result = validator.verify_timestamp(timestamp)

        assert result.is_fresh
        assert not result.is_expired
        assert result.age_hours < 24

    def test_expired_data(self):
        """Test detection of expired data"""
        validator = TimestampValidator(max_age_hours=24)
        timestamp = datetime.utcnow() - timedelta(hours=30)

        result = validator.verify_timestamp(timestamp)

        assert not result.is_fresh
        assert result.is_expired
        assert result.warning_message is not None

    def test_aging_data(self):
        """Test detection of aging data"""
        validator = TimestampValidator(max_age_hours=24, warning_threshold_hours=12)
        timestamp = datetime.utcnow() - timedelta(hours=18)

        result = validator.verify_timestamp(timestamp)

        assert not result.is_fresh
        assert not result.is_expired
        assert result.warning_message is not None


class TestCitationValidator:
    """Test citation validation"""

    def test_valid_citation(self):
        """Test validation of proper citation"""
        validator = CitationValidator()
        citation = Citation(
            source="ESPN",
            stat_type="points",
            value=25,
            timestamp=datetime.utcnow(),
            url="https://espn.com/stats"
        )

        is_valid, issues = validator.validate_citation(citation)

        assert is_valid
        assert len(issues) == 0

    def test_missing_source(self):
        """Test detection of missing source"""
        validator = CitationValidator()
        citation = Citation(
            source="",
            stat_type="points",
            value=25,
            timestamp=datetime.utcnow()
        )

        is_valid, issues = validator.validate_citation(citation)

        assert not is_valid
        assert any("source" in issue.lower() for issue in issues)

    def test_unverified_source(self):
        """Test detection of unverified source"""
        validator = CitationValidator()
        citation = Citation(
            source="Random Blog",
            stat_type="points",
            value=25,
            timestamp=datetime.utcnow()
        )

        is_valid, issues = validator.validate_citation(citation)

        assert not is_valid
        assert any("unverified" in issue.lower() for issue in issues)


class TestSpeculationDetector:
    """Test speculation detection"""

    def test_detect_speculation_keywords(self):
        """Test detection of speculative language"""
        detector = SpeculationDetector()
        content = "The team might win tonight. They could be the champions."

        flags = detector.detect_speculation(content)

        assert len(flags) > 0
        assert any(f.severity == 'high' for f in flags)

    def test_detect_unverified_injury(self):
        """Test detection of unverified injury mentions"""
        detector = SpeculationDetector()
        content = "Player X is injured and may miss the game."

        flags = detector.detect_unverified_injuries(content)

        assert len(flags) > 0
        assert 'injury' in flags[0].keywords_matched[0].lower()

    def test_clean_content(self):
        """Test clean content with no speculation"""
        detector = SpeculationDetector()
        content = "The team won 95-87. Player scored 25 points."

        analysis = detector.analyze_content(content)

        assert analysis['clean']
        assert analysis['total_flags'] == 0


class TestBettingDisclaimerEnforcer:
    """Test betting disclaimer enforcement"""

    def test_disclaimer_present(self):
        """Test detection of disclaimer"""
        enforcer = BettingDisclaimerEnforcer()
        content = "Great game tonight! Gamble responsibly."

        result = enforcer.check_disclaimer_present(content)

        assert result.is_present

    def test_disclaimer_missing(self):
        """Test detection of missing disclaimer"""
        enforcer = BettingDisclaimerEnforcer()
        content = "Great game tonight! Lakers won 105-98."

        result = enforcer.check_disclaimer_present(content)

        assert not result.is_present

    def test_inject_disclaimer(self):
        """Test disclaimer injection"""
        enforcer = BettingDisclaimerEnforcer()
        content = "Check out these great odds!"

        enhanced = enforcer.inject_disclaimer(content)

        assert "gamble responsibly" in enhanced.lower()
        assert len(enhanced) > len(content)


class TestEmbargoManager:
    """Test embargo management"""

    def test_active_embargo(self):
        """Test active embargo"""
        manager = EmbargoManager()
        future = datetime.utcnow() + timedelta(hours=2)

        embargo = manager.create_embargo("test-1", future)

        assert embargo.is_embargoed
        assert not embargo.can_publish

    def test_expired_embargo(self):
        """Test expired embargo"""
        manager = EmbargoManager()
        past = datetime.utcnow() - timedelta(hours=2)

        embargo = manager.create_embargo("test-2", past)

        assert not embargo.is_embargoed
        assert embargo.can_publish

    def test_clear_expired_embargoes(self):
        """Test clearing expired embargoes"""
        manager = EmbargoManager()

        # Add some embargoes
        manager.create_embargo("test-1", datetime.utcnow() - timedelta(hours=1))
        manager.create_embargo("test-2", datetime.utcnow() + timedelta(hours=1))

        count = manager.clear_expired_embargoes()

        assert count == 1
        assert len(manager.get_active_embargoes()) == 1


class TestFactChecker:
    """Test fact-checking system"""

    def test_exact_match(self):
        """Test exact value match"""
        checker = FactChecker()

        result = checker.check_fact(
            stat_name="points",
            claimed_value=25,
            verified_value=25,
            source="ESPN"
        )

        assert result.matches
        assert result.confidence == 1.0

    def test_numeric_tolerance(self):
        """Test numeric tolerance"""
        checker = FactChecker()

        result = checker.check_fact(
            stat_name="points",
            claimed_value=25,
            verified_value=24.5,
            source="ESPN",
            tolerance=1.0
        )

        assert result.matches

    def test_value_mismatch(self):
        """Test value mismatch"""
        checker = FactChecker()

        result = checker.check_fact(
            stat_name="points",
            claimed_value=25,
            verified_value=15,
            source="ESPN"
        )

        assert not result.matches
        assert result.confidence < 1.0


class TestQualityScorer:
    """Test quality scoring system"""

    def test_high_quality_score(self):
        """Test high-quality content scores well"""
        scorer = QualityScorer()

        content = """
# Game Analysis

The Lakers defeated the Celtics 105-98 last night in a thrilling matchup.

**Key Stats:**
- LeBron James: 28 points, 8 rebounds, 7 assists
- Anthony Davis: 22 points, 12 rebounds

This game showcased excellent teamwork and defensive intensity.

Data sources: ESPN, NBA.com
"""

        data_sources = [
            DataSource(
                name="ESPN",
                data_type="scores",
                timestamp=datetime.utcnow()
            )
        ]

        score = scorer.calculate_quality_score(
            content=content,
            fact_checks=[],
            data_sources=data_sources,
            citations_count=2
        )

        assert score.clarity_score > 70
        assert score.timeliness_score > 70

    def test_low_quality_score(self):
        """Test low-quality content scores poorly"""
        scorer = QualityScorer()

        content = "Short content."

        old_source = DataSource(
            name="ESPN",
            data_type="scores",
            timestamp=datetime.utcnow() - timedelta(days=3)
        )

        score = scorer.calculate_quality_score(
            content=content,
            fact_checks=[],
            data_sources=[old_source],
            speculation_flags=5
        )

        assert score.overall_score < 70


class TestQualityController:
    """Test integrated quality controller"""

    def test_full_processing_pipeline(self):
        """Test complete processing pipeline"""
        controller = QualityController()

        content = """
# NBA Game Analysis

The Lakers defeated the Celtics 105-98 in an exciting matchup.

**Disclaimer:** All information is for entertainment purposes. Gamble responsibly.
"""

        data_sources = [
            DataSource(
                name="ESPN",
                data_type="scores",
                timestamp=datetime.utcnow()
            )
        ]

        citations = [
            Citation(
                source="ESPN",
                stat_type="final_score",
                value="105-98",
                timestamp=datetime.utcnow()
            )
        ]

        report = controller.process_content(
            content=content,
            sport="nba",
            data_sources=data_sources,
            citations=citations
        )

        assert report is not None
        assert report.compliance.betting_disclaimer.is_present
        assert report.quality.overall_score > 0

    def test_auto_approve_high_quality(self):
        """Test auto-approval for high-quality content"""
        controller = QualityController(auto_approve_threshold=80.0)

        content = """
# NBA Game Analysis

The Lakers won 105-98 against the Celtics tonight, improving to 15-10.

**Key Highlights:**
- LeBron James scored 28 points confirmed by official stats
- Game was played at Staples Center
- Lakers extend home winning streak to 7 games

All betting information for entertainment only. Gamble responsibly.

**Sources:** ESPN, NBA.com (updated 1 hour ago)
"""

        data_sources = [
            DataSource(
                name="ESPN",
                data_type="scores",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            )
        ]

        citations = [
            Citation(
                source="ESPN",
                stat_type="final_score",
                value="105-98",
                timestamp=datetime.utcnow(),
                verified=True
            )
        ]

        fact_checks = [
            {
                'stat_name': 'final_score',
                'claimed_value': '105-98',
                'verified_value': '105-98',
                'source': 'ESPN'
            }
        ]

        report = controller.process_content(
            content=content,
            sport="nba",
            data_sources=data_sources,
            citations=citations,
            fact_checks=fact_checks
        )

        # Should have high quality score
        assert report.quality.overall_score >= 70

    def test_embargo_blocking(self):
        """Test embargo blocks publication"""
        controller = QualityController()

        content = "Exclusive: Team announces major signing!"

        data_sources = [
            DataSource(
                name="Team Press Release",
                data_type="news",
                timestamp=datetime.utcnow()
            )
        ]

        # Embargo for 2 hours in future
        embargo_time = datetime.utcnow() + timedelta(hours=2)

        report = controller.process_content(
            content=content,
            sport="nba",
            data_sources=data_sources,
            embargo_until=embargo_time
        )

        assert report.compliance.embargo_check is not None
        assert report.compliance.embargo_check.is_embargoed
        assert report.compliance.level == ComplianceLevel.BLOCKED


class TestTransparencyTagger:
    """Test transparency tagging"""

    def test_create_transparency_tag(self):
        """Test transparency tag creation"""
        tagger = TransparencyTagger()

        sources = [
            DataSource(
                name="ESPN",
                data_type="scores",
                timestamp=datetime.utcnow() - timedelta(hours=2),
                url="https://espn.com"
            ),
            DataSource(
                name="The Odds API",
                data_type="odds",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            )
        ]

        tag = tagger.create_transparency_tag(sources)

        assert "DATA SOURCES" in tag
        assert "ESPN" in tag
        assert "The Odds API" in tag

    def test_inject_transparency_tag(self):
        """Test tag injection into content"""
        tagger = TransparencyTagger()

        content = "Great game tonight!"
        sources = [
            DataSource(
                name="ESPN",
                data_type="scores",
                timestamp=datetime.utcnow()
            )
        ]

        enhanced = tagger.inject_transparency_tag(content, sources)

        assert len(enhanced) > len(content)
        assert "DATA SOURCES" in enhanced


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
