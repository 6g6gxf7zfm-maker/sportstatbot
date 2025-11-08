"""
SportStatBot Quality, Compliance & Audit Trail System

This package provides comprehensive quality control, compliance checking,
and audit logging for all SportStatBot operations.

Components:
- Timestamp verification
- Betting disclaimers
- Citation validation
- Speculation filtering
- Audit logging
- Fact-checking
- Version diff tracking
- Compliance summaries
- Quality scoring
- Peer review automation
- Data expiration warnings
- Embargo management
- Transparency tagging
- Proofing queue
"""

from .core import QualityController
from .models import (
    QualityReport,
    ComplianceStatus,
    AuditRecord,
    QualityScore
)

__version__ = "1.0.0"

__all__ = [
    "QualityController",
    "QualityReport",
    "ComplianceStatus",
    "AuditRecord",
    "QualityScore"
]
