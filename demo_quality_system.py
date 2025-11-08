#!/usr/bin/env python3
"""
Demo script for Quality, Compliance & Audit Trail System

This demonstrates all major features of the quality system.
"""

from datetime import datetime, timedelta
from quality_system import QualityController
from quality_system.models import DataSource, Citation


def demo_basic_quality_check():
    """Demo 1: Basic quality check"""
    print("=" * 70)
    print("DEMO 1: Basic Quality Check")
    print("=" * 70)

    controller = QualityController()

    content = """
# NBA Game Recap: Lakers vs Celtics

The Los Angeles Lakers defeated the Boston Celtics 105-98 in an exciting
matchup at Staples Center last night.

**Key Highlights:**
- LeBron James scored 28 points with 8 rebounds and 7 assists
- Anthony Davis added 22 points and 12 rebounds
- Lakers improve to 15-10 on the season

**Betting Note:** All betting information is for entertainment purposes only.
Please gamble responsibly.
"""

    sources = [
        DataSource(
            name="ESPN",
            url="https://espn.com/nba",
            timestamp=datetime.utcnow() - timedelta(hours=2),
            data_type="scores"
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
        data_sources=sources,
        citations=citations
    )

    print(f"\nQuality Score: {report.quality.overall_score:.1f}%")
    print(f"  - Accuracy: {report.quality.accuracy_score:.1f}%")
    print(f"  - Clarity: {report.quality.clarity_score:.1f}%")
    print(f"  - Timeliness: {report.quality.timeliness_score:.1f}%")
    print(f"\nCompliance Level: {report.compliance.level.value.upper()}")
    print(f"Can Publish: {'✅ Yes' if report.can_publish else '❌ No'}")
    print(f"Auto-Approved: {'✅ Yes' if report.auto_approve else '⚠️ No (needs review)'}")

    print("\n" + controller.get_compliance_summary(report.compliance))


def demo_speculation_detection():
    """Demo 2: Speculation detection"""
    print("\n" + "=" * 70)
    print("DEMO 2: Speculation Detection")
    print("=" * 70)

    controller = QualityController()

    # Content with speculation
    content = """
# NBA Injury Report

Player X might be out for tonight's game. Sources say he could miss
several weeks with a possible injury. The team will likely struggle
without him.
"""

    sources = [
        DataSource(
            name="Team Website",
            timestamp=datetime.utcnow(),
            data_type="injury_report"
        )
    ]

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=sources
    )

    print(f"\nSpeculation Flags Detected: {len(report.compliance.speculation_flags)}")

    for i, flag in enumerate(report.compliance.speculation_flags, 1):
        print(f"\nFlag {i}:")
        print(f"  Content: {flag.content}")
        print(f"  Reason: {flag.reason}")
        print(f"  Severity: {flag.severity}")
        print(f"  Should Remove: {'Yes' if flag.suggested_removal else 'No'}")

    print(f"\nQuality Score: {report.quality.overall_score:.1f}% (Lowered due to speculation)")


def demo_fact_checking():
    """Demo 3: Fact-checking"""
    print("\n" + "=" * 70)
    print("DEMO 3: Fact-Checking")
    print("=" * 70)

    controller = QualityController()

    content = """
# Player Stats Update

LeBron James scored 28 points last night. The Lakers won 105-98.
"""

    sources = [
        DataSource(
            name="ESPN",
            timestamp=datetime.utcnow(),
            data_type="stats"
        )
    ]

    # Fact-check data
    fact_checks = [
        {
            'stat_name': 'LeBron James Points',
            'claimed_value': 28,
            'verified_value': 28,  # Correct
            'source': 'ESPN'
        },
        {
            'stat_name': 'Final Score',
            'claimed_value': '105-98',
            'verified_value': '105-98',  # Correct
            'source': 'ESPN'
        }
    ]

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=sources,
        fact_checks=fact_checks
    )

    print(f"\nFact Checks Performed: {len(report.audit.fact_checks)}")

    for fc in report.audit.fact_checks:
        status = "✅ VERIFIED" if fc.matches else "❌ MISMATCH"
        print(f"\n{fc.stat_name}:")
        print(f"  Claimed: {fc.claimed_value}")
        print(f"  Verified: {fc.verified_value}")
        print(f"  Status: {status}")
        print(f"  Confidence: {fc.confidence * 100:.1f}%")

    print(f"\nAccuracy Score: {report.quality.accuracy_score:.1f}%")


def demo_embargo_system():
    """Demo 4: Embargo system"""
    print("\n" + "=" * 70)
    print("DEMO 4: Embargo System")
    print("=" * 70)

    controller = QualityController()

    content = """
# EXCLUSIVE: Major Trade Announcement

The Lakers have acquired a star player in a blockbuster trade.
Full details will be released at 3 PM EST.
"""

    sources = [
        DataSource(
            name="Team Press Release",
            timestamp=datetime.utcnow(),
            data_type="news"
        )
    ]

    # Set embargo for 2 hours in future
    embargo_time = datetime.utcnow() + timedelta(hours=2)

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=sources,
        embargo_until=embargo_time
    )

    print(f"\nEmbargo Status:")
    print(f"  Active: {'Yes' if report.compliance.embargo_check.is_embargoed else 'No'}")
    print(f"  Can Publish: {'Yes' if report.compliance.embargo_check.can_publish else 'No'}")
    print(f"  Time Remaining: {report.compliance.embargo_check.time_remaining}")
    print(f"\nCompliance Level: {report.compliance.level.value.upper()}")


def demo_data_expiration():
    """Demo 5: Data expiration warning"""
    print("\n" + "=" * 70)
    print("DEMO 5: Data Expiration Warning")
    print("=" * 70)

    controller = QualityController(max_data_age_hours=24)

    content = """
# Game Analysis

Based on recent stats and standings...
"""

    # Old data source (30 hours ago)
    old_source = DataSource(
        name="ESPN",
        timestamp=datetime.utcnow() - timedelta(hours=30),
        data_type="stats"
    )

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=[old_source]
    )

    ts = report.compliance.timestamp_verification
    print(f"\nData Age: {ts.age_hours:.1f} hours")
    print(f"Is Fresh: {'Yes' if ts.is_fresh else 'No'}")
    print(f"Is Expired: {'Yes' if ts.is_expired else 'No'}")

    if ts.warning_message:
        print(f"Warning: {ts.warning_message}")

    print(f"\nTimeliness Score: {report.quality.timeliness_score:.1f}%")


def demo_proofing_queue():
    """Demo 6: Proofing queue with auto-approve"""
    print("\n" + "=" * 70)
    print("DEMO 6: Proofing Queue & Auto-Approve")
    print("=" * 70)

    controller = QualityController(auto_approve_threshold=85.0)

    # High-quality content
    good_content = """
# NBA Game Recap: Lakers Win Big

The Los Angeles Lakers dominated the Boston Celtics with a convincing
115-95 victory at Staples Center tonight.

**Game Highlights:**
- LeBron James: 32 points, 10 rebounds, 8 assists (confirmed by ESPN)
- Anthony Davis: 28 points, 14 rebounds
- Lakers shot 52% from the field
- Celtics struggled with turnovers (18 total)

**Next Game:** Lakers host Warriors on Friday at 7:30 PM EST

**Disclaimer:** All information is for entertainment purposes only.
Please gamble responsibly.

**Data Sources:**
- ESPN (updated 1 hour ago)
- NBA.com Official Stats
"""

    sources = [
        DataSource(
            name="ESPN",
            timestamp=datetime.utcnow() - timedelta(hours=1),
            data_type="scores"
        )
    ]

    citations = [
        Citation(source="ESPN", stat_type="stats", value="various", timestamp=datetime.utcnow())
    ]

    report = controller.process_content(
        content=good_content,
        sport="nba",
        data_sources=sources,
        citations=citations
    )

    queue_id = controller.add_to_proofing_queue(
        content=good_content,
        quality_report=report
    )

    print(f"\nQuality Score: {report.quality.overall_score:.1f}%")
    print(f"Auto-Approved: {'✅ Yes' if report.auto_approve else '❌ No'}")
    print(f"Queue ID: {queue_id}")

    # Get queue stats
    stats = controller.get_queue_stats()
    print(f"\nQueue Statistics:")
    print(f"  Total Items: {stats['total_items']}")
    print(f"  Auto-Approved: {stats['auto_approved']}")
    print(f"  Auto-Approve Rate: {stats['auto_approve_rate']:.1f}%")
    print(f"  Average Quality: {stats['average_quality_score']:.1f}%")


def demo_transparency_tagging():
    """Demo 7: Transparency tagging"""
    print("\n" + "=" * 70)
    print("DEMO 7: Transparency Tagging")
    print("=" * 70)

    controller = QualityController()

    content = """
# NBA Analysis

Lakers look strong heading into playoffs.
"""

    sources = [
        DataSource(
            name="ESPN",
            url="https://espn.com/nba",
            timestamp=datetime.utcnow() - timedelta(hours=2),
            data_type="scores,standings"
        ),
        DataSource(
            name="The Odds API",
            url="https://the-odds-api.com",
            timestamp=datetime.utcnow() - timedelta(hours=1),
            data_type="odds"
        )
    ]

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=sources
    )

    # Publish with transparency tag
    result = controller.publish_content(
        content=content,
        quality_report=report,
        add_transparency_tag=True
    )

    print("\nEnhanced Content with Transparency Tag:")
    print("-" * 70)
    print(result['enhanced_content'])


def demo_peer_review():
    """Demo 8: Peer review checklist"""
    print("\n" + "=" * 70)
    print("DEMO 8: Peer Review Checklist")
    print("=" * 70)

    controller = QualityController()

    content = """
# Complete NBA Report

Lakers won 105-98. Great performance by LeBron (28 pts).

**Disclaimer:** For entertainment only. Gamble responsibly.
"""

    sources = [
        DataSource(name="ESPN", timestamp=datetime.utcnow(), data_type="scores")
    ]

    citations = [
        Citation(source="ESPN", stat_type="score", value="105-98", timestamp=datetime.utcnow())
    ]

    report = controller.process_content(
        content=content,
        sport="nba",
        data_sources=sources,
        citations=citations
    )

    print(controller.get_peer_review_report(report.compliance.peer_review))


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("QUALITY, COMPLIANCE & AUDIT TRAIL SYSTEM - DEMONSTRATION")
    print("=" * 70)

    demos = [
        demo_basic_quality_check,
        demo_speculation_detection,
        demo_fact_checking,
        demo_embargo_system,
        demo_data_expiration,
        demo_proofing_queue,
        demo_transparency_tagging,
        demo_peer_review
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nFor more details, see QUALITY_SYSTEM_README.md")
    print()


if __name__ == "__main__":
    main()
