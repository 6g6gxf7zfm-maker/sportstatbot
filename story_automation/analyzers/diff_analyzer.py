"""
Diff Analyzer - Compare story versions and track changes
"""

import difflib
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import json
from pathlib import Path


class DiffAnalyzer:
    """Analyze differences between story versions"""

    def __init__(self, history_path: str = 'story_history'):
        """
        Initialize diff analyzer

        Args:
            history_path: Path to store story history
        """
        self.history_path = Path(history_path)
        self.history_path.mkdir(parents=True, exist_ok=True)

    def save_version(
        self,
        story: Dict[str, Any],
        sport: str,
        version_label: Optional[str] = None
    ) -> str:
        """
        Save a story version for comparison

        Args:
            story: Story dictionary
            sport: Sport name
            version_label: Optional version label

        Returns:
            Version ID
        """
        timestamp = datetime.now()
        version_id = timestamp.strftime('%Y%m%d_%H%M%S')

        if version_label:
            version_id = f"{version_id}_{version_label}"

        # Create version file
        sport_dir = self.history_path / sport.lower()
        sport_dir.mkdir(exist_ok=True)

        version_file = sport_dir / f"{version_id}.json"

        version_data = {
            'version_id': version_id,
            'timestamp': timestamp.isoformat(),
            'sport': sport,
            'story': story,
            'label': version_label
        }

        version_file.write_text(json.dumps(version_data, indent=2), encoding='utf-8')

        return version_id

    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str,
        sport: str
    ) -> Dict[str, Any]:
        """
        Compare two story versions

        Args:
            version_id_1: First version ID
            version_id_2: Second version ID
            sport: Sport name

        Returns:
            Comparison results dictionary
        """
        # Load versions
        version_1 = self._load_version(version_id_1, sport)
        version_2 = self._load_version(version_id_2, sport)

        if not version_1 or not version_2:
            return {'error': 'Version not found'}

        story_1 = version_1['story']
        story_2 = version_2['story']

        # Compare each component
        comparison = {
            'version_1': version_id_1,
            'version_2': version_id_2,
            'timestamp_1': version_1['timestamp'],
            'timestamp_2': version_2['timestamp'],
            'changes': {}
        }

        # Compare headlines
        if story_1.get('headline') != story_2.get('headline'):
            comparison['changes']['headline'] = {
                'old': story_1.get('headline', ''),
                'new': story_2.get('headline', ''),
                'diff': self._text_diff(
                    story_1.get('headline', ''),
                    story_2.get('headline', '')
                )
            }

        # Compare body
        if story_1.get('body') != story_2.get('body'):
            comparison['changes']['body'] = {
                'old_length': len(story_1.get('body', '')),
                'new_length': len(story_2.get('body', '')),
                'diff': self._text_diff(
                    story_1.get('body', ''),
                    story_2.get('body', '')
                ),
                'line_changes': self._line_diff(
                    story_1.get('body', ''),
                    story_2.get('body', '')
                )
            }

        # Compare TL;DR
        if story_1.get('tldr') != story_2.get('tldr'):
            comparison['changes']['tldr'] = {
                'old': story_1.get('tldr', ''),
                'new': story_2.get('tldr', ''),
                'diff': self._text_diff(
                    story_1.get('tldr', ''),
                    story_2.get('tldr', '')
                )
            }

        # Summary statistics
        comparison['summary'] = {
            'total_changes': len(comparison['changes']),
            'components_changed': list(comparison['changes'].keys())
        }

        return comparison

    def compare_with_latest(
        self,
        story: Dict[str, Any],
        sport: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare story with latest saved version

        Args:
            story: Current story
            sport: Sport name

        Returns:
            Comparison results or None if no previous version
        """
        # Get latest version
        latest = self._get_latest_version(sport)

        if not latest:
            return None

        # Save current as temp version
        temp_id = self.save_version(story, sport, 'temp')

        # Compare
        comparison = self.compare_versions(latest['version_id'], temp_id, sport)

        return comparison

    def get_version_history(
        self,
        sport: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a sport

        Args:
            sport: Sport name
            limit: Optional limit on number of versions

        Returns:
            List of version metadata
        """
        sport_dir = self.history_path / sport.lower()

        if not sport_dir.exists():
            return []

        versions = []

        for version_file in sorted(sport_dir.glob('*.json'), reverse=True):
            try:
                data = json.loads(version_file.read_text(encoding='utf-8'))
                versions.append({
                    'version_id': data['version_id'],
                    'timestamp': data['timestamp'],
                    'label': data.get('label'),
                    'file': str(version_file)
                })

                if limit and len(versions) >= limit:
                    break

            except Exception:
                continue

        return versions

    def generate_diff_view(
        self,
        comparison: Dict[str, Any],
        format_type: str = 'markdown'
    ) -> str:
        """
        Generate formatted diff view

        Args:
            comparison: Comparison results
            format_type: Output format (markdown, html, unified)

        Returns:
            Formatted diff string
        """
        if format_type == 'markdown':
            return self._format_markdown_diff(comparison)
        elif format_type == 'html':
            return self._format_html_diff(comparison)
        elif format_type == 'unified':
            return self._format_unified_diff(comparison)
        else:
            return str(comparison)

    def _text_diff(self, text1: str, text2: str) -> List[str]:
        """Generate text diff"""
        diff = difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            lineterm=''
        )
        return list(diff)

    def _line_diff(self, text1: str, text2: str) -> Dict[str, int]:
        """Calculate line-level changes"""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        diff = difflib.SequenceMatcher(None, lines1, lines2)

        added = 0
        removed = 0
        changed = 0

        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            if tag == 'insert':
                added += (j2 - j1)
            elif tag == 'delete':
                removed += (i2 - i1)
            elif tag == 'replace':
                changed += max(i2 - i1, j2 - j1)

        return {
            'added': added,
            'removed': removed,
            'changed': changed
        }

    def _load_version(
        self,
        version_id: str,
        sport: str
    ) -> Optional[Dict[str, Any]]:
        """Load a specific version"""
        sport_dir = self.history_path / sport.lower()

        if not sport_dir.exists():
            return None

        # Look for version file
        version_file = sport_dir / f"{version_id}.json"

        if not version_file.exists():
            return None

        try:
            return json.loads(version_file.read_text(encoding='utf-8'))
        except Exception:
            return None

    def _get_latest_version(self, sport: str) -> Optional[Dict[str, Any]]:
        """Get latest version for sport"""
        versions = self.get_version_history(sport, limit=1)

        if versions:
            version_id = versions[0]['version_id']
            return self._load_version(version_id, sport)

        return None

    def _format_markdown_diff(self, comparison: Dict[str, Any]) -> str:
        """Format diff as markdown"""
        output = "# Story Comparison\n\n"

        output += f"**Version 1:** {comparison['version_1']} ({comparison['timestamp_1']})\n"
        output += f"**Version 2:** {comparison['version_2']} ({comparison['timestamp_2']})\n\n"

        output += f"**Total Changes:** {comparison['summary']['total_changes']}\n"
        output += f"**Components Changed:** {', '.join(comparison['summary']['components_changed'])}\n\n"

        # Detail each change
        for component, change_data in comparison.get('changes', {}).items():
            output += f"## {component.capitalize()} Changes\n\n"

            if 'line_changes' in change_data:
                stats = change_data['line_changes']
                output += f"- **Lines Added:** {stats['added']}\n"
                output += f"- **Lines Removed:** {stats['removed']}\n"
                output += f"- **Lines Changed:** {stats['changed']}\n\n"

            if 'old' in change_data and 'new' in change_data:
                output += f"**Before:**\n```\n{change_data['old']}\n```\n\n"
                output += f"**After:**\n```\n{change_data['new']}\n```\n\n"

        return output

    def _format_html_diff(self, comparison: Dict[str, Any]) -> str:
        """Format diff as HTML"""
        # Simplified HTML format
        return self._format_markdown_diff(comparison)

    def _format_unified_diff(self, comparison: Dict[str, Any]) -> str:
        """Format diff in unified diff format"""
        output = ""

        for component, change_data in comparison.get('changes', {}).items():
            if 'diff' in change_data:
                output += f"--- {component} (Version 1)\n"
                output += f"+++ {component} (Version 2)\n"
                output += ''.join(change_data['diff'])
                output += "\n"

        return output

    def cleanup_old_versions(
        self,
        sport: str,
        keep_count: int = 10
    ) -> int:
        """
        Clean up old versions keeping only recent ones

        Args:
            sport: Sport name
            keep_count: Number of recent versions to keep

        Returns:
            Number of versions deleted
        """
        versions = self.get_version_history(sport)

        if len(versions) <= keep_count:
            return 0

        # Delete old versions
        deleted = 0
        for version in versions[keep_count:]:
            try:
                Path(version['file']).unlink()
                deleted += 1
            except Exception:
                continue

        return deleted
