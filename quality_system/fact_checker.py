"""
Fact-checking system with reference API comparison

Verifies stats against authoritative sources
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from .models import FactCheckResult, Citation, DataSource


class FactChecker:
    """
    Fact-check stats against reference APIs

    This system compares claimed stats against authoritative sources
    to ensure accuracy.
    """

    def __init__(self):
        self.cache: Dict[str, FactCheckResult] = {}

    def check_fact(
        self,
        stat_name: str,
        claimed_value: Any,
        verified_value: Any,
        source: str,
        tolerance: float = 0.0
    ) -> FactCheckResult:
        """
        Check a single fact

        Args:
            stat_name: Name of the statistic
            claimed_value: Value claimed in content
            verified_value: Value from authoritative source
            source: Source of verification
            tolerance: Acceptable difference for numeric values

        Returns:
            FactCheckResult
        """
        matches, confidence = self._compare_values(
            claimed_value,
            verified_value,
            tolerance
        )

        notes = None
        if not matches:
            notes = f"Claimed: {claimed_value}, Verified: {verified_value}"

        result = FactCheckResult(
            stat_name=stat_name,
            claimed_value=claimed_value,
            verified_value=verified_value,
            source=source,
            matches=matches,
            confidence=confidence,
            notes=notes
        )

        # Cache result
        cache_key = f"{stat_name}:{claimed_value}"
        self.cache[cache_key] = result

        return result

    def _compare_values(
        self,
        claimed: Any,
        verified: Any,
        tolerance: float = 0.0
    ) -> tuple[bool, float]:
        """
        Compare two values with optional tolerance

        Returns:
            Tuple of (matches, confidence)
        """
        # Handle None values
        if claimed is None or verified is None:
            return (claimed == verified), 0.0 if claimed is None else 1.0

        # Exact match
        if claimed == verified:
            return True, 1.0

        # Numeric comparison with tolerance
        try:
            claimed_num = float(claimed)
            verified_num = float(verified)

            diff = abs(claimed_num - verified_num)
            if diff <= tolerance:
                confidence = 1.0 - (diff / max(abs(verified_num), 1))
                return True, max(0.0, min(1.0, confidence))
            else:
                # Calculate confidence based on how far off
                confidence = max(0.0, 1.0 - (diff / max(abs(verified_num), 1)))
                return False, confidence

        except (ValueError, TypeError):
            pass

        # String comparison (case-insensitive)
        try:
            claimed_str = str(claimed).strip().lower()
            verified_str = str(verified).strip().lower()

            if claimed_str == verified_str:
                return True, 1.0

            # Fuzzy string matching (simple similarity)
            similarity = self._string_similarity(claimed_str, verified_str)
            matches = similarity > 0.9
            return matches, similarity

        except:
            return False, 0.0

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity (0-1)"""
        if not s1 or not s2:
            return 0.0

        # Simple ratio based on common characters
        s1_set = set(s1)
        s2_set = set(s2)

        intersection = len(s1_set.intersection(s2_set))
        union = len(s1_set.union(s2_set))

        if union == 0:
            return 0.0

        return intersection / union

    def bulk_check(
        self,
        facts: List[Dict[str, Any]],
        tolerance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Check multiple facts at once

        Args:
            facts: List of fact dictionaries with keys:
                   stat_name, claimed_value, verified_value, source
            tolerance: Acceptable difference for numeric values

        Returns:
            Summary of fact-checking results
        """
        results = []

        for fact in facts:
            result = self.check_fact(
                stat_name=fact['stat_name'],
                claimed_value=fact['claimed_value'],
                verified_value=fact['verified_value'],
                source=fact.get('source', 'Unknown'),
                tolerance=tolerance
            )
            results.append(result)

        total = len(results)
        passed = sum(1 for r in results if r.matches)
        failed = total - passed

        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0.0

        return {
            'total_checks': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'average_confidence': avg_confidence,
            'results': results,
            'all_passed': failed == 0
        }

    def verify_game_stats(
        self,
        claimed_stats: Dict[str, Any],
        verified_stats: Dict[str, Any],
        source: str = "ESPN API"
    ) -> List[FactCheckResult]:
        """
        Verify game statistics

        Common stats: score, team names, date, location, etc.

        Args:
            claimed_stats: Stats from content
            verified_stats: Stats from authoritative API
            source: Source of verified stats

        Returns:
            List of fact-check results
        """
        results = []

        # Compare all common keys
        common_keys = set(claimed_stats.keys()).intersection(
            set(verified_stats.keys())
        )

        for key in common_keys:
            result = self.check_fact(
                stat_name=key,
                claimed_value=claimed_stats[key],
                verified_value=verified_stats[key],
                source=source
            )
            results.append(result)

        return results

    def verify_player_stats(
        self,
        player_name: str,
        claimed_stats: Dict[str, Any],
        verified_stats: Dict[str, Any],
        source: str = "ESPN API",
        tolerance: float = 1.0  # Allow ±1 for counting stats
    ) -> List[FactCheckResult]:
        """
        Verify player statistics

        Args:
            player_name: Player name
            claimed_stats: Stats from content
            verified_stats: Stats from authoritative API
            source: Source of verified stats
            tolerance: Acceptable difference (default ±1 for rounding)

        Returns:
            List of fact-check results
        """
        results = []

        common_keys = set(claimed_stats.keys()).intersection(
            set(verified_stats.keys())
        )

        for key in common_keys:
            result = self.check_fact(
                stat_name=f"{player_name} - {key}",
                claimed_value=claimed_stats[key],
                verified_value=verified_stats[key],
                source=source,
                tolerance=tolerance
            )
            results.append(result)

        return results

    def get_accuracy_score(self, results: List[FactCheckResult]) -> float:
        """
        Calculate overall accuracy score from fact-check results

        Returns:
            Accuracy score 0-100
        """
        if not results:
            return 0.0

        # Weight by confidence
        total_confidence = sum(r.confidence for r in results)
        passed_confidence = sum(
            r.confidence for r in results if r.matches
        )

        if total_confidence == 0:
            return 0.0

        return (passed_confidence / total_confidence) * 100
