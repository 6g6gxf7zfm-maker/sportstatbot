"""
Data models for the Quality, Compliance & Audit Trail System

Uses Pydantic for strong typing and validation
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class ComplianceLevel(str, Enum):
    """Compliance status levels"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    BLOCKED = "blocked"


class DataSource(BaseModel):
    """Track data sources for transparency"""
    name: str
    url: Optional[str] = None
    api_endpoint: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_type: str  # e.g., "scores", "odds", "news", "stats"

    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if data source is older than max age"""
        age = datetime.utcnow() - self.timestamp
        return age > timedelta(hours=max_age_hours)


class TimestampVerification(BaseModel):
    """Timestamp verification results"""
    data_timestamp: datetime
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow)
    age_hours: float
    is_fresh: bool
    is_expired: bool
    warning_message: Optional[str] = None

    @validator('age_hours', always=True)
    def calculate_age(cls, v, values):
        """Calculate age in hours"""
        if 'data_timestamp' in values and 'verification_timestamp' in values:
            delta = values['verification_timestamp'] - values['data_timestamp']
            return delta.total_seconds() / 3600
        return v


class Citation(BaseModel):
    """Citation information for stats"""
    source: str
    stat_type: str
    value: Any
    timestamp: datetime
    url: Optional[str] = None
    verified: bool = False


class SpeculationFlag(BaseModel):
    """Flag for speculative content"""
    content: str
    reason: str
    severity: str  # "low", "medium", "high"
    suggested_removal: bool
    keywords_matched: List[str] = []


class BettingDisclaimer(BaseModel):
    """Betting disclaimer tracking"""
    disclaimer_text: str
    placement: str  # "header", "footer", "inline"
    is_present: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FactCheckResult(BaseModel):
    """Result of fact-checking operation"""
    stat_name: str
    claimed_value: Any
    verified_value: Any
    source: str
    matches: bool
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class QualityScore(BaseModel):
    """Quality score for a story/report"""
    accuracy_score: float = Field(ge=0.0, le=100.0)
    clarity_score: float = Field(ge=0.0, le=100.0)
    timeliness_score: float = Field(ge=0.0, le=100.0)
    overall_score: float = Field(ge=0.0, le=100.0)

    citations_count: int = 0
    facts_verified: int = 0
    speculation_flags: int = 0
    data_freshness_hours: float = 0.0

    def calculate_overall(self):
        """Calculate overall quality score"""
        self.overall_score = (
            self.accuracy_score * 0.4 +
            self.clarity_score * 0.3 +
            self.timeliness_score * 0.3
        )
        return self.overall_score


class PeerReviewChecklist(BaseModel):
    """Peer review checklist items"""
    has_betting_disclaimer: bool = False
    has_data_sources: bool = False
    no_speculation: bool = False
    facts_verified: bool = False
    data_is_fresh: bool = False
    embargo_respected: bool = True
    citations_present: bool = False
    quality_threshold_met: bool = False

    passed_items: int = 0
    total_items: int = 8
    pass_rate: float = 0.0

    def calculate_pass_rate(self):
        """Calculate percentage of checks passed"""
        passed = sum([
            self.has_betting_disclaimer,
            self.has_data_sources,
            self.no_speculation,
            self.facts_verified,
            self.data_is_fresh,
            self.embargo_respected,
            self.citations_present,
            self.quality_threshold_met
        ])
        self.passed_items = passed
        self.pass_rate = (passed / self.total_items) * 100
        return self.pass_rate


class EmbargoTimer(BaseModel):
    """Embargo timer for scheduled releases"""
    content_id: str
    embargo_until: datetime
    is_embargoed: bool
    can_publish: bool
    time_remaining: Optional[str] = None

    @validator('can_publish', always=True)
    def check_embargo(cls, v, values):
        """Check if embargo has lifted"""
        if 'embargo_until' in values:
            return datetime.utcnow() >= values['embargo_until']
        return v

    @validator('time_remaining', always=True)
    def calculate_time_remaining(cls, v, values):
        """Calculate time remaining until embargo lift"""
        if 'embargo_until' in values and 'can_publish' in values:
            if not values['can_publish']:
                delta = values['embargo_until'] - datetime.utcnow()
                hours = delta.total_seconds() / 3600
                if hours < 1:
                    return f"{int(delta.total_seconds() / 60)} minutes"
                return f"{hours:.1f} hours"
        return "Embargo lifted"


class VersionDiff(BaseModel):
    """Track changes between versions"""
    version_old: str
    version_new: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changes: Dict[str, Any] = {}
    additions: List[str] = []
    removals: List[str] = []
    modifications: List[str] = []
    change_summary: str = ""


class ComplianceStatus(BaseModel):
    """Overall compliance status for a report"""
    level: ComplianceLevel
    betting_disclaimer: BettingDisclaimer
    timestamp_verification: TimestampVerification
    citations_valid: bool
    speculation_flags: List[SpeculationFlag] = []
    data_sources: List[DataSource] = []
    embargo_check: Optional[EmbargoTimer] = None
    peer_review: PeerReviewChecklist

    issues: List[str] = []
    warnings: List[str] = []

    def determine_level(self) -> ComplianceLevel:
        """Determine overall compliance level"""
        if len(self.issues) > 0:
            return ComplianceLevel.FAIL
        if len(self.warnings) > 0:
            return ComplianceLevel.WARNING
        if self.embargo_check and self.embargo_check.is_embargoed:
            return ComplianceLevel.BLOCKED
        return ComplianceLevel.PASS


class AuditRecord(BaseModel):
    """Audit record for a published output"""
    record_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sport: str
    report_type: str

    compliance_status: ComplianceStatus
    quality_score: QualityScore
    fact_checks: List[FactCheckResult] = []

    data_sources: List[DataSource] = []
    citations: List[Citation] = []

    published: bool = False
    published_timestamp: Optional[datetime] = None
    auto_approved: bool = False

    metadata: Dict[str, Any] = {}

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QualityReport(BaseModel):
    """Comprehensive quality report"""
    report_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sport: str

    compliance: ComplianceStatus
    quality: QualityScore
    audit: AuditRecord

    can_publish: bool = False
    auto_approve: bool = False

    summary: str = ""
    recommendations: List[str] = []

    def determine_publish_status(self, auto_approve_threshold: float = 85.0):
        """Determine if content can be published"""
        # Check compliance
        if self.compliance.level == ComplianceLevel.BLOCKED:
            self.can_publish = False
            self.auto_approve = False
            return

        if self.compliance.level == ComplianceLevel.FAIL:
            self.can_publish = False
            self.auto_approve = False
            return

        # Check quality score
        self.quality.calculate_overall()

        if self.quality.overall_score >= auto_approve_threshold:
            self.can_publish = True
            self.auto_approve = True
        elif self.quality.overall_score >= 70.0:
            self.can_publish = True
            self.auto_approve = False
        else:
            self.can_publish = False
            self.auto_approve = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProofingQueueItem(BaseModel):
    """Item in the proofing queue"""
    queue_id: str
    content: str
    quality_report: QualityReport

    status: str = "pending"  # pending, approved, rejected, published
    priority: int = Field(ge=1, le=5, default=3)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    reviewer_notes: str = ""

    def should_auto_approve(self) -> bool:
        """Check if item meets auto-approve criteria"""
        return self.quality_report.auto_approve
