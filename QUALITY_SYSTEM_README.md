# Quality, Compliance & Audit Trail System

## Overview

The Quality, Compliance & Audit Trail System is a comprehensive framework for ensuring high-quality, compliant, and auditable sports analysis reports from SportStatBot.

## Features

### ✅ Core Components

1. **Timestamp Verification System**
   - Tracks data freshness
   - Flags data older than 24 hours
   - Provides aging warnings

2. **Betting Disclaimer Enforcer**
   - Ensures all betting content includes responsible gambling disclaimers
   - Auto-injects disclaimers when missing
   - Tracks disclaimer placement (header, footer, inline)

3. **Stat-Source Citation Validator**
   - Validates citation completeness
   - Verifies source credibility
   - Checks URL validity
   - Flags stale citations

4. **"No Speculation" Rule Filter**
   - Detects speculative language (might, could, possibly, etc.)
   - Flags unverified injury reports
   - Categorizes speculation by severity (high, medium, low)

5. **Audit Log System**
   - Logs every published output
   - Maintains searchable index
   - Stores compliance status and quality scores
   - Generates audit reports

6. **Fact-Check Bot**
   - Compares stats against reference APIs
   - Calculates confidence scores
   - Supports numeric tolerance for rounding
   - Tracks verification sources

7. **Version Diff Tool**
   - Tracks changes between report versions
   - Identifies additions, removals, and modifications
   - Generates change summaries
   - Maintains version history

8. **Compliance Summary Sheet**
   - Generates comprehensive compliance reports
   - Shows pass/fail status for all checks
   - Lists issues and warnings
   - Provides JSON export

9. **Quality Score System**
   - **Accuracy Score** (0-100): Based on fact-checking and speculation
   - **Clarity Score** (0-100): Based on readability and structure
   - **Timeliness Score** (0-100): Based on data freshness
   - **Overall Score**: Weighted average (40% accuracy, 30% clarity, 30% timeliness)

10. **Peer Review Checklist Agent**
    - Automated systematic checks
    - 8-point checklist
    - Pass rate calculation
    - Recommendation generation

11. **Data Expiration Warning**
    - Warns when data exceeds 24 hours
    - Configurable thresholds
    - Freshness scoring

12. **Automated Embargo Timer**
    - Blocks publication until embargo lifts
    - Shows time remaining
    - Auto-releases when ready

13. **Transparency Tag**
    - Lists all data sources at bottom of reports
    - Shows data types and update times
    - Includes source URLs

14. **Proofing Queue with Auto-Approve**
    - Auto-approves content scoring ≥85%
    - Priority-based queue
    - Manual review for lower-quality content
    - Track approval rates

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Dependencies added:
- `pydantic==2.5.3` - Data validation and type checking
- `pytest==7.4.3` - Testing framework

## Quick Start

### Basic Usage

```python
from quality_system import QualityController
from quality_system.models import DataSource, Citation
from datetime import datetime

# Initialize controller
quality = QualityController(
    audit_log_dir="audit_logs",
    proofing_queue_dir="proofing_queue",
    auto_approve_threshold=85.0,
    max_data_age_hours=24
)

# Create data sources
sources = [
    DataSource(
        name="ESPN",
        url="https://espn.com",
        timestamp=datetime.utcnow(),
        data_type="scores"
    )
]

# Create citations
citations = [
    Citation(
        source="ESPN",
        stat_type="final_score",
        value="105-98",
        timestamp=datetime.utcnow()
    )
]

# Process content
report = quality.process_content(
    content="Lakers defeated Celtics 105-98...",
    sport="nba",
    data_sources=sources,
    citations=citations
)

# Check results
print(f"Can Publish: {report.can_publish}")
print(f"Auto-Approved: {report.auto_approve}")
print(f"Quality Score: {report.quality.overall_score}")
print(f"Compliance Level: {report.compliance.level}")

# Get compliance summary
summary = quality.get_compliance_summary(report.compliance)
print(summary)
```

### Integrated with SportStatBot

```python
from quality_integration import QualityEnabledReportGenerator

# Create quality-enabled generator
generator = QualityEnabledReportGenerator(
    timezone='America/New_York',
    enable_quality_controls=True,
    auto_approve_threshold=85.0
)

# Generate report with quality checks
result = generator.generate_report_with_quality(
    sport='nba',
    output_format='slack'
)

# Access results
if result['can_publish']:
    if result['auto_approved']:
        print("✅ Auto-approved! Publishing...")
        print(result['enhanced_report'])
    else:
        print("⚠️ Queued for manual review")
        print(f"Queue ID: {result['queue_id']}")
else:
    print("❌ Cannot publish - quality/compliance issues")
    for issue in result['recommendations']:
        print(f"  - {issue}")
```

## Configuration

### Auto-Approve Thresholds

```python
# Conservative (manual review for most content)
QualityController(auto_approve_threshold=90.0)

# Balanced (default)
QualityController(auto_approve_threshold=85.0)

# Permissive (auto-approve more content)
QualityController(auto_approve_threshold=75.0)
```

### Data Freshness Settings

```python
# Strict freshness requirements
QualityController(max_data_age_hours=12)

# Standard (default)
QualityController(max_data_age_hours=24)

# Relaxed
QualityController(max_data_age_hours=48)
```

## Quality Scoring Details

### Accuracy Score (40% weight)

Factors:
- Fact-check pass rate
- Average confidence level
- Speculation penalties (5 points per flag)

```
Base Score = (Passed Checks / Total Checks) × 100 × Avg Confidence
Final Score = Base Score - (Speculation Flags × 5)
```

### Clarity Score (30% weight)

Factors:
- Readability (sentence length)
- Structure (headers, bullets, formatting)
- Citations present
- Content length appropriateness

Optimal metrics:
- Sentence length: 15-20 words
- Word count: 200-800 words
- Citations: 3-5 sources

### Timeliness Score (30% weight)

Based on data age:
- **< 6 hours**: 100 points (Excellent)
- **6-12 hours**: 90 points (Good)
- **12-24 hours**: 75 points (Fair)
- **24-48 hours**: 50 points (Poor)
- **> 48 hours**: Declining (Poor+)

## Compliance Levels

1. **PASS** ✅
   - All checks passed
   - No critical issues
   - Ready to publish

2. **WARNING** ⚠️
   - Minor issues detected
   - Can publish with caution
   - Recommendations provided

3. **FAIL** ❌
   - Critical issues found
   - Cannot publish
   - Requires fixes

4. **BLOCKED** 🚫
   - Embargo in effect
   - Cannot publish until embargo lifts

## Peer Review Checklist

8-point automated checklist:

1. ✓ Betting disclaimer present
2. ✓ Data sources documented
3. ✓ No speculation detected
4. ✓ Facts verified
5. ✓ Data is fresh (< 24h)
6. ✓ Embargo respected
7. ✓ Citations present
8. ✓ Quality threshold met (≥70%)

**Pass Requirement**: 90% (7/8 checks)

## Audit Logging

### Log Structure

```
audit_logs/
├── index.jsonl              # Master index
├── daily/                   # Daily logs
│   └── 2025-11-08/
│       └── nba_20251108_120000_abc123.json
├── reports/                 # By sport
│   └── nba/
│       └── nba_20251108_120000_abc123.json
└── versions/                # Version history
    └── abc123_def456.txt
```

### Query Audit Logs

```python
# Query by filters
records = quality.audit_logger.query_records(
    sport="nba",
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 8),
    min_quality_score=80.0
)

# Generate audit report
report = quality.audit_logger.generate_audit_report(
    sport="nba",
    days=7
)

print(f"Total Publications: {report['total_publications']}")
print(f"Auto-Approve Rate: {report['auto_approve_rate']:.1f}%")
print(f"Avg Quality Score: {report['average_quality_score']:.1f}")
```

## Proofing Queue

### Queue Management

```python
# Get queue statistics
stats = quality.get_queue_stats()
print(f"Pending Review: {stats['pending_review']}")
print(f"Auto-Approve Rate: {stats['auto_approve_rate']:.1f}%")

# Get next item for review
item = quality.proofing_queue.get_next_item(status="pending")

# Approve item
quality.proofing_queue.approve_item(
    queue_id=item.queue_id,
    reviewer_notes="Looks good!"
)

# Reject item
quality.proofing_queue.reject_item(
    queue_id=item.queue_id,
    reviewer_notes="Needs more citations"
)

# Publish approved item
quality.proofing_queue.publish_item(queue_id=item.queue_id)
```

## Testing

Run comprehensive test suite:

```bash
# Run all tests
pytest tests/test_quality_system.py -v

# Run specific test class
pytest tests/test_quality_system.py::TestQualityController -v

# Run with coverage
pytest tests/test_quality_system.py --cov=quality_system
```

## API Reference

### QualityController

Main controller class for quality system.

**Methods:**

- `process_content()` - Process content through quality pipeline
- `publish_content()` - Publish content with enhancements
- `add_to_proofing_queue()` - Add to review queue
- `get_compliance_summary()` - Get formatted compliance summary
- `get_peer_review_report()` - Get peer review checklist report
- `get_audit_report()` - Get audit statistics
- `get_queue_stats()` - Get proofing queue statistics

### Models

**Core Models:**

- `QualityReport` - Complete quality assessment
- `ComplianceStatus` - Compliance status and checks
- `AuditRecord` - Audit log record
- `QualityScore` - Quality scoring breakdown

**Supporting Models:**

- `DataSource` - Data source tracking
- `Citation` - Citation information
- `FactCheckResult` - Fact verification result
- `SpeculationFlag` - Speculation detection flag
- `EmbargoTimer` - Embargo timing
- `VersionDiff` - Version comparison
- `ProofingQueueItem` - Queue item

## Best Practices

### 1. Always Track Data Sources

```python
sources = [
    DataSource(
        name="ESPN",
        url="https://espn.com/nba",
        timestamp=datetime.utcnow(),
        data_type="scores"
    )
]
```

### 2. Include Citations

```python
citations = [
    Citation(
        source="ESPN",
        stat_type="final_score",
        value="105-98",
        timestamp=datetime.utcnow(),
        url="https://espn.com/game/123"
    )
]
```

### 3. Perform Fact-Checking

```python
fact_checks = [
    {
        'stat_name': 'LeBron James Points',
        'claimed_value': 28,
        'verified_value': 28,
        'source': 'ESPN',
        'tolerance': 0.0
    }
]
```

### 4. Use Embargoes for Time-Sensitive Content

```python
from datetime import timedelta

embargo_time = datetime.utcnow() + timedelta(hours=2)

report = quality.process_content(
    content="Breaking news...",
    sport="nba",
    data_sources=sources,
    embargo_until=embargo_time
)
```

### 5. Review Quality Recommendations

```python
if not report.can_publish:
    print("Issues to fix:")
    for rec in report.recommendations:
        print(f"  - {rec}")
```

## Troubleshooting

### Low Quality Scores

**Issue**: Content consistently scores below 70%

**Solutions**:
- Add more citations (target: 3-5)
- Remove speculative language
- Ensure data is fresh (< 12 hours)
- Improve structure (add headers, bullets)
- Verify facts against authoritative sources

### False Speculation Flags

**Issue**: Clean content flagged for speculation

**Solutions**:
- Use definitive language ("is" instead of "might be")
- Add verification markers ("confirmed", "official", "announced")
- Include citations with unverified claims

### Compliance Failures

**Issue**: Content fails compliance checks

**Solutions**:
- Add betting disclaimer
- Refresh data sources
- Validate all citations
- Remove high-severity speculation
- Check embargo status

## Contributing

To extend the quality system:

1. Add new validators in `quality_system/validators.py`
2. Add new compliance rules in `quality_system/compliance.py`
3. Update models in `quality_system/models.py`
4. Add tests in `tests/test_quality_system.py`

## License

Part of SportStatBot - Expert sports analysis tool

## Support

For issues or questions:
- Review this documentation
- Check test examples in `tests/test_quality_system.py`
- See integration examples in `quality_integration.py`
