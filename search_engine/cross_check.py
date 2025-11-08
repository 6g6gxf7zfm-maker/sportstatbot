"""Auto cross-check system for verifying stat consistency across sources."""
from typing import Dict, List, Optional, Tuple
import re


class CrossCheckVerifier:
    """
    Automatic cross-check verification system.
    Verifies stat consistency across multiple data sources.
    """

    def __init__(self, data_sources: Optional[List] = None):
        """
        Initialize cross-check verifier.

        Args:
            data_sources: List of data source fetchers
        """
        self.data_sources = data_sources or []
        self.discrepancies = []

    def verify_stat(self, stat_name: str, expected_value: Any,
                   entity: str, context: Optional[Dict] = None) -> Dict:
        """
        Verify a statistic across multiple sources.

        Args:
            stat_name: Name of the stat to verify
            expected_value: Expected value to check
            entity: Entity (player/team) the stat is about
            context: Additional context (date, game, etc.)

        Returns:
            Verification result dictionary
        """
        # Fetch stat from multiple sources
        source_values = self._fetch_from_sources(stat_name, entity, context)

        # Compare values
        consistent = self._check_consistency(expected_value, source_values)

        result = {
            'stat': stat_name,
            'entity': entity,
            'expected_value': expected_value,
            'source_values': source_values,
            'consistent': consistent,
            'confidence': self._calculate_confidence(source_values),
            'recommended_value': self._get_recommended_value(source_values)
        }

        if not consistent:
            self.discrepancies.append(result)

        return result

    def verify_game_result(self, game_data: Dict) -> Dict:
        """
        Verify a game result across sources.

        Args:
            game_data: Game data to verify (teams, score, date, etc.)

        Returns:
            Verification result
        """
        verifications = {}

        # Verify final score
        if 'score' in game_data:
            verifications['score'] = self.verify_stat(
                'final_score',
                game_data['score'],
                f"{game_data.get('home_team')} vs {game_data.get('away_team')}",
                {'date': game_data.get('date')}
            )

        # Verify key stats
        for stat_name, value in game_data.get('stats', {}).items():
            verifications[stat_name] = self.verify_stat(
                stat_name,
                value,
                game_data.get('team'),
                {'date': game_data.get('date')}
            )

        return {
            'game': game_data,
            'verifications': verifications,
            'overall_consistency': self._check_overall_consistency(verifications)
        }

    def verify_player_stats(self, player: str, stats: Dict,
                           context: Optional[Dict] = None) -> Dict:
        """
        Verify player statistics across sources.

        Args:
            player: Player name
            stats: Dictionary of stats to verify
            context: Optional context (game date, season, etc.)

        Returns:
            Verification results
        """
        verifications = {}

        for stat_name, value in stats.items():
            verifications[stat_name] = self.verify_stat(
                stat_name,
                value,
                player,
                context
            )

        return {
            'player': player,
            'verifications': verifications,
            'overall_consistency': self._check_overall_consistency(verifications),
            'flagged_stats': self._get_flagged_stats(verifications)
        }

    def verify_report(self, report_data: Dict) -> Dict:
        """
        Verify all statistics in a report.

        Args:
            report_data: Report data with stats to verify

        Returns:
            Full verification report
        """
        all_verifications = []

        # Verify player stats
        for player_data in report_data.get('players', []):
            verification = self.verify_player_stats(
                player_data.get('name'),
                player_data.get('stats', {}),
                report_data.get('context')
            )
            all_verifications.append(verification)

        # Verify team stats
        for team_data in report_data.get('teams', []):
            for stat_name, value in team_data.get('stats', {}).items():
                verification = self.verify_stat(
                    stat_name,
                    value,
                    team_data.get('name'),
                    report_data.get('context')
                )
                all_verifications.append(verification)

        # Verify game results
        for game in report_data.get('games', []):
            verification = self.verify_game_result(game)
            all_verifications.append(verification)

        return {
            'report_id': report_data.get('id'),
            'verifications': all_verifications,
            'total_stats_checked': len(all_verifications),
            'discrepancies_found': len(self.discrepancies),
            'overall_quality': self._calculate_quality_score(all_verifications)
        }

    def cross_reference(self, stat1: Dict, stat2: Dict) -> Dict:
        """
        Cross-reference two related statistics for logical consistency.

        Args:
            stat1: First stat dictionary
            stat2: Second stat dictionary

        Returns:
            Cross-reference result
        """
        # Check if stats are logically consistent
        consistent = self._check_logical_consistency(stat1, stat2)

        return {
            'stat1': stat1,
            'stat2': stat2,
            'logically_consistent': consistent,
            'explanation': self._explain_consistency(stat1, stat2, consistent)
        }

    def _fetch_from_sources(self, stat_name: str, entity: str,
                           context: Optional[Dict]) -> List[Tuple[str, Any]]:
        """Fetch stat value from multiple sources."""
        values = []

        for source in self.data_sources:
            try:
                value = source.get_stat(stat_name, entity, context)
                if value is not None:
                    values.append((source.name, value))
            except Exception as e:
                # Source failed, skip it
                continue

        return values

    def _check_consistency(self, expected: Any, source_values: List[Tuple[str, Any]]) -> bool:
        """
        Check if values are consistent.

        Args:
            expected: Expected value
            source_values: List of (source_name, value) tuples

        Returns:
            True if consistent
        """
        if not source_values:
            return False

        # Allow small variations for numerical values
        if isinstance(expected, (int, float)):
            tolerance = self._get_tolerance(expected)

            for source, value in source_values:
                try:
                    value_num = float(value)
                    if abs(value_num - expected) > tolerance:
                        return False
                except (ValueError, TypeError):
                    return False

            return True

        else:
            # For non-numeric values, require exact match
            for source, value in source_values:
                if str(value).strip() != str(expected).strip():
                    return False

            return True

    def _get_tolerance(self, value: float) -> float:
        """Get acceptable tolerance for a numerical value."""
        # 1% tolerance or 0.5, whichever is larger
        return max(abs(value * 0.01), 0.5)

    def _calculate_confidence(self, source_values: List[Tuple[str, Any]]) -> float:
        """
        Calculate confidence score based on source agreement.

        Returns:
            Confidence score from 0.0 to 1.0
        """
        if not source_values:
            return 0.0

        if len(source_values) == 1:
            return 0.6  # Moderate confidence with single source

        # Count how many sources agree
        values = [v for _, v in source_values]

        # For numbers, check if they're within tolerance
        if isinstance(values[0], (int, float)):
            primary_value = values[0]
            tolerance = self._get_tolerance(primary_value)

            agreeing = sum(1 for v in values if abs(float(v) - primary_value) <= tolerance)
        else:
            # For strings, exact match
            primary_value = str(values[0])
            agreeing = sum(1 for v in values if str(v) == primary_value)

        agreement_ratio = agreeing / len(values)

        # More sources = higher confidence
        source_bonus = min(len(source_values) * 0.1, 0.3)

        return min(agreement_ratio + source_bonus, 1.0)

    def _get_recommended_value(self, source_values: List[Tuple[str, Any]]) -> Any:
        """Get recommended value based on source values."""
        if not source_values:
            return None

        values = [v for _, v in source_values]

        # For numbers, use median
        if all(isinstance(v, (int, float)) for v in values):
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2

            if len(sorted_values) % 2 == 0:
                return (sorted_values[mid - 1] + sorted_values[mid]) / 2
            else:
                return sorted_values[mid]

        # For strings, use most common
        from collections import Counter
        counts = Counter(str(v) for v in values)
        return counts.most_common(1)[0][0]

    def _check_overall_consistency(self, verifications: Dict) -> bool:
        """Check if all verifications are consistent."""
        if not verifications:
            return True

        return all(
            v.get('consistent', False)
            for v in verifications.values()
            if isinstance(v, dict)
        )

    def _get_flagged_stats(self, verifications: Dict) -> List[str]:
        """Get list of stats that failed verification."""
        flagged = []

        for stat_name, verification in verifications.items():
            if isinstance(verification, dict) and not verification.get('consistent', True):
                flagged.append(stat_name)

        return flagged

    def _calculate_quality_score(self, verifications: List[Dict]) -> float:
        """
        Calculate overall quality score for verifications.

        Returns:
            Quality score from 0.0 to 100.0
        """
        if not verifications:
            return 0.0

        total_confidence = 0
        count = 0

        for verification in verifications:
            if isinstance(verification, dict):
                # Handle nested verifications
                if 'verifications' in verification:
                    for v in verification['verifications'].values():
                        if isinstance(v, dict) and 'confidence' in v:
                            total_confidence += v['confidence']
                            count += 1
                elif 'confidence' in verification:
                    total_confidence += verification['confidence']
                    count += 1

        if count == 0:
            return 0.0

        average_confidence = total_confidence / count
        return average_confidence * 100

    def _check_logical_consistency(self, stat1: Dict, stat2: Dict) -> bool:
        """
        Check if two stats are logically consistent.

        For example:
        - Points per game should be less than total points
        - Field goals made should be less than field goals attempted
        - Win percentage should be between 0 and 100
        """
        name1 = stat1.get('name', '').lower()
        name2 = stat2.get('name', '').lower()
        value1 = stat1.get('value')
        value2 = stat2.get('value')

        if value1 is None or value2 is None:
            return True  # Can't check

        try:
            value1 = float(value1)
            value2 = float(value2)
        except (ValueError, TypeError):
            return True  # Can't compare non-numeric

        # Check specific logical relationships
        # Made vs Attempted
        if 'made' in name1 and 'attempted' in name2:
            return value1 <= value2

        if 'attempted' in name1 and 'made' in name2:
            return value2 <= value1

        # Per game vs Total
        if 'per game' in name1 and 'total' in name2:
            return value1 <= value2

        # Percentage checks
        if 'percentage' in name1 or '%' in name1:
            if not (0 <= value1 <= 100):
                return False

        if 'percentage' in name2 or '%' in name2:
            if not (0 <= value2 <= 100):
                return False

        return True

    def _explain_consistency(self, stat1: Dict, stat2: Dict, consistent: bool) -> str:
        """Explain why stats are or aren't consistent."""
        if consistent:
            return "Stats are logically consistent with each other"

        name1 = stat1.get('name', 'Stat 1')
        name2 = stat2.get('name', 'Stat 2')
        value1 = stat1.get('value')
        value2 = stat2.get('value')

        # Try to explain the inconsistency
        if 'made' in name1.lower() and 'attempted' in name2.lower():
            return f"{name1} ({value1}) cannot be greater than {name2} ({value2})"

        if 'percentage' in name1.lower() or '%' in name1.lower():
            if value1 > 100:
                return f"{name1} ({value1}) cannot exceed 100%"

        return f"{name1} ({value1}) appears inconsistent with {name2} ({value2})"

    def get_discrepancy_report(self) -> str:
        """
        Generate a formatted report of all discrepancies found.

        Returns:
            Formatted report string
        """
        if not self.discrepancies:
            return "No discrepancies found. All stats verified successfully!"

        report = f"**DISCREPANCY REPORT**\n\n"
        report += f"Total discrepancies found: {len(self.discrepancies)}\n\n"

        for i, disc in enumerate(self.discrepancies, 1):
            report += f"{i}. {disc['stat']} for {disc['entity']}\n"
            report += f"   Expected: {disc['expected_value']}\n"
            report += f"   Sources:\n"

            for source, value in disc['source_values']:
                report += f"     - {source}: {value}\n"

            report += f"   Recommended: {disc['recommended_value']}\n"
            report += f"   Confidence: {disc['confidence']:.2f}\n\n"

        return report
