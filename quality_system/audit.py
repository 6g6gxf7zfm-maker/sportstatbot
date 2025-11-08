"""
Audit logging system for all published outputs

Tracks every published report with full traceability
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from .models import AuditRecord, VersionDiff, DataSource


class AuditLogger:
    """
    Comprehensive audit logging system

    Logs every published output with full metadata,
    compliance status, and quality scores.
    """

    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.log_dir / "daily").mkdir(exist_ok=True)
        (self.log_dir / "reports").mkdir(exist_ok=True)
        (self.log_dir / "versions").mkdir(exist_ok=True)

    def log_publication(self, audit_record: AuditRecord) -> str:
        """
        Log a publication event

        Args:
            audit_record: Complete audit record

        Returns:
            Path to log file
        """
        # Update publication timestamp
        audit_record.published = True
        audit_record.published_timestamp = datetime.utcnow()

        # Generate filename
        timestamp_str = audit_record.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{audit_record.sport}_{timestamp_str}_{audit_record.record_id}.json"

        # Save to daily directory
        daily_dir = self.log_dir / "daily" / audit_record.timestamp.strftime("%Y-%m-%d")
        daily_dir.mkdir(parents=True, exist_ok=True)
        daily_path = daily_dir / filename

        # Save to reports directory (by sport)
        sport_dir = self.log_dir / "reports" / audit_record.sport
        sport_dir.mkdir(parents=True, exist_ok=True)
        sport_path = sport_dir / filename

        # Write audit record
        audit_json = audit_record.json(indent=2)

        with open(daily_path, 'w') as f:
            f.write(audit_json)

        with open(sport_path, 'w') as f:
            f.write(audit_json)

        # Update index
        self._update_index(audit_record)

        return str(daily_path)

    def _update_index(self, audit_record: AuditRecord):
        """Update master index of all publications"""
        index_file = self.log_dir / "index.jsonl"

        # Create index entry
        index_entry = {
            'record_id': audit_record.record_id,
            'timestamp': audit_record.timestamp.isoformat(),
            'sport': audit_record.sport,
            'report_type': audit_record.report_type,
            'compliance_level': audit_record.compliance_status.level.value,
            'quality_score': audit_record.quality_score.overall_score,
            'auto_approved': audit_record.auto_approved,
            'published': audit_record.published
        }

        # Append to index (JSONL format)
        with open(index_file, 'a') as f:
            f.write(json.dumps(index_entry) + '\n')

    def get_audit_record(self, record_id: str) -> Optional[AuditRecord]:
        """
        Retrieve an audit record by ID

        Args:
            record_id: Record identifier

        Returns:
            AuditRecord or None if not found
        """
        # Search in index
        index_file = self.log_dir / "index.jsonl"

        if not index_file.exists():
            return None

        with open(index_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry['record_id'] == record_id:
                    # Find and load the full record
                    sport = entry['sport']
                    # Search in sport directory
                    sport_dir = self.log_dir / "reports" / sport

                    for record_file in sport_dir.glob(f"*_{record_id}.json"):
                        with open(record_file, 'r') as rf:
                            data = json.load(rf)
                            return AuditRecord(**data)

        return None

    def query_records(
        self,
        sport: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_quality_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit records with filters

        Args:
            sport: Filter by sport
            start_date: Filter by start date
            end_date: Filter by end date
            min_quality_score: Minimum quality score

        Returns:
            List of matching index entries
        """
        index_file = self.log_dir / "index.jsonl"

        if not index_file.exists():
            return []

        results = []

        with open(index_file, 'r') as f:
            for line in f:
                entry = json.loads(line)

                # Apply filters
                if sport and entry['sport'] != sport:
                    continue

                entry_date = datetime.fromisoformat(entry['timestamp'])

                if start_date and entry_date < start_date:
                    continue

                if end_date and entry_date > end_date:
                    continue

                if min_quality_score and entry['quality_score'] < min_quality_score:
                    continue

                results.append(entry)

        return results

    def generate_audit_report(
        self,
        sport: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate summary audit report

        Args:
            sport: Optional sport filter
            days: Number of days to include

        Returns:
            Summary statistics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        records = self.query_records(
            sport=sport,
            start_date=start_date,
            end_date=end_date
        )

        if not records:
            return {
                'total_publications': 0,
                'period_days': days,
                'sport': sport or 'all'
            }

        total = len(records)
        auto_approved = sum(1 for r in records if r['auto_approved'])

        quality_scores = [r['quality_score'] for r in records]
        avg_quality = sum(quality_scores) / len(quality_scores)

        compliance_levels = {}
        for r in records:
            level = r['compliance_level']
            compliance_levels[level] = compliance_levels.get(level, 0) + 1

        return {
            'total_publications': total,
            'auto_approved': auto_approved,
            'manual_review': total - auto_approved,
            'auto_approve_rate': (auto_approved / total * 100) if total > 0 else 0,
            'average_quality_score': avg_quality,
            'compliance_breakdown': compliance_levels,
            'period_days': days,
            'sport': sport or 'all',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }


class VersionDiffTracker:
    """
    Track changes between versions of reports

    Enables comparison of what changed between digest versions
    """

    def __init__(self, storage_dir: str = "audit_logs/versions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_version(
        self,
        content: str,
        version_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a version of content

        Args:
            content: Content to version
            version_id: Version identifier
            metadata: Optional metadata

        Returns:
            Content hash
        """
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Save version
        version_file = self.storage_dir / f"{version_id}_{content_hash}.txt"

        with open(version_file, 'w') as f:
            f.write(content)

        # Save metadata
        if metadata:
            meta_file = self.storage_dir / f"{version_id}_{content_hash}.meta.json"
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        return content_hash

    def compare_versions(
        self,
        version_old: str,
        version_new: str
    ) -> VersionDiff:
        """
        Compare two versions and generate diff

        Args:
            version_old: Old version ID
            version_new: New version ID

        Returns:
            VersionDiff object
        """
        # Load versions
        old_files = list(self.storage_dir.glob(f"{version_old}_*.txt"))
        new_files = list(self.storage_dir.glob(f"{version_new}_*.txt"))

        if not old_files or not new_files:
            return VersionDiff(
                version_old=version_old,
                version_new=version_new,
                change_summary="Version files not found"
            )

        with open(old_files[0], 'r') as f:
            old_content = f.read()

        with open(new_files[0], 'r') as f:
            new_content = f.read()

        # Simple line-by-line diff
        old_lines = set(old_content.split('\n'))
        new_lines = set(new_content.split('\n'))

        additions = list(new_lines - old_lines)
        removals = list(old_lines - new_lines)
        unchanged = list(old_lines.intersection(new_lines))

        # Detect modifications (lines with similar content but changed)
        modifications = self._detect_modifications(
            list(old_lines),
            list(new_lines)
        )

        # Generate summary
        change_summary = self._generate_change_summary(
            additions, removals, modifications
        )

        return VersionDiff(
            version_old=version_old,
            version_new=version_new,
            changes={
                'additions_count': len(additions),
                'removals_count': len(removals),
                'modifications_count': len(modifications),
                'unchanged_count': len(unchanged)
            },
            additions=additions[:10],  # Limit to first 10
            removals=removals[:10],
            modifications=modifications[:10],
            change_summary=change_summary
        )

    def _detect_modifications(
        self,
        old_lines: List[str],
        new_lines: List[str]
    ) -> List[str]:
        """Detect lines that were modified"""
        modifications = []

        # Simple heuristic: lines with high similarity but not exact match
        for old_line in old_lines:
            for new_line in new_lines:
                if old_line != new_line:
                    # Calculate similarity
                    similarity = self._line_similarity(old_line, new_line)
                    if similarity > 0.7:  # 70% similar
                        modifications.append(f"{old_line} → {new_line}")

        return modifications

    def _line_similarity(self, line1: str, line2: str) -> float:
        """Calculate line similarity"""
        if not line1 or not line2:
            return 0.0

        words1 = set(line1.lower().split())
        words2 = set(line2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _generate_change_summary(
        self,
        additions: List[str],
        removals: List[str],
        modifications: List[str]
    ) -> str:
        """Generate human-readable change summary"""
        parts = []

        if additions:
            parts.append(f"{len(additions)} addition(s)")

        if removals:
            parts.append(f"{len(removals)} removal(s)")

        if modifications:
            parts.append(f"{len(modifications)} modification(s)")

        if not parts:
            return "No changes detected"

        return ", ".join(parts)


# Import timedelta
from datetime import timedelta
