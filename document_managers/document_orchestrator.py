"""Document orchestrator for managing both Google Docs and Apple Notes."""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .google_docs_manager import GoogleDocsManager
from .apple_notes_manager import AppleNotesManager
import config


class DocumentOrchestrator:
    """
    Orchestrates document creation and management across Google Docs and Apple Notes.
    Provides unified interface for cross-platform document automation.
    """

    def __init__(self):
        """Initialize document orchestrator with both managers."""
        self.google_docs = GoogleDocsManager(
            credentials_path=config.GOOGLE_CREDENTIALS_PATH,
            token_path=config.GOOGLE_TOKEN_PATH
        )
        self.apple_notes = AppleNotesManager(
            storage_dir=config.APPLE_NOTES_STORAGE_DIR
        )
        self.cross_references = {}  # Track links between Docs and Notes

    def setup_all(self) -> Dict[str, bool]:
        """
        Setup both Google Docs and Apple Notes folder structures.

        Returns:
            Dictionary with setup status for each platform
        """
        status = {}

        # Setup Google Docs
        try:
            if self.google_docs.authenticate():
                self.google_docs.setup_league_folders(config.GOOGLE_DOCS_ROOT_FOLDER)
                status['google_docs'] = True
            else:
                status['google_docs'] = False
                status['google_docs_error'] = 'Authentication failed'
        except Exception as e:
            status['google_docs'] = False
            status['google_docs_error'] = str(e)

        # Setup Apple Notes
        try:
            self.apple_notes.create_folder_structure()
            status['apple_notes'] = True
        except Exception as e:
            status['apple_notes'] = False
            status['apple_notes_error'] = str(e)

        return status

    def publish_content(
        self,
        title: str,
        content: str,
        league: str,
        category: str,
        to_google_docs: bool = True,
        to_apple_notes: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Publish content to both Google Docs and Apple Notes with cross-linking.

        Args:
            title: Content title
            content: Content body
            league: League (NFL, NBA, etc.)
            category: Category (Digests, Features, Previews, Betting)
            to_google_docs: Whether to publish to Google Docs
            to_apple_notes: Whether to publish to Apple Notes
            metadata: Additional metadata

        Returns:
            Dictionary with document IDs for each platform
        """
        results = {}
        metadata = metadata or {}

        # Default metadata
        if 'author' not in metadata:
            metadata['author'] = config.DEFAULT_AUTHOR
        if 'word_count' not in metadata:
            metadata['word_count'] = len(content.split())

        # Publish to Google Docs
        google_doc_id = None
        google_doc_url = None

        if to_google_docs:
            try:
                google_doc_id = self.google_docs.create_document(
                    title=title,
                    content=content,
                    league=league,
                    category=category,
                    metadata=metadata
                )
                google_doc_url = f"https://docs.google.com/document/d/{google_doc_id}"
                results['google_docs_id'] = google_doc_id
                results['google_docs_url'] = google_doc_url
            except Exception as e:
                results['google_docs_error'] = str(e)

        # Publish to Apple Notes with cross-link
        if to_apple_notes:
            try:
                # Extract tags from metadata
                tags = metadata.get('tags', [])

                apple_note_id = self.apple_notes.create_note(
                    league=league,
                    category=category,
                    title=title,
                    content=content,
                    tags=tags,
                    auto_summary=config.ENABLE_AUTO_SUMMARY,
                    google_docs_url=google_doc_url
                )
                results['apple_notes_id'] = apple_note_id

                # Cross-reference in tracking
                if google_doc_id and apple_note_id:
                    self.cross_references[google_doc_id] = apple_note_id

            except Exception as e:
                results['apple_notes_error'] = str(e)

        return results

    def publish_sports_report(
        self,
        report_data: Dict[str, Any],
        league: str,
        report_type: str = 'Digests'
    ) -> Dict[str, str]:
        """
        Publish formatted sports report to both platforms.

        Args:
            report_data: Report data from SportsReportGenerator
            league: League name
            report_type: Report category

        Returns:
            Publication results
        """
        # Generate title
        date_str = datetime.now().strftime('%Y-%m-%d')
        title = f"{league} {report_type} - {date_str}"

        # Format content
        content = self._format_report_content(report_data)

        # Extract metadata
        metadata = {
            'author': config.DEFAULT_AUTHOR,
            'word_count': len(content.split()),
            'report_type': report_type,
            'tags': [f'#{league.lower()}', f'#{report_type.lower()}', '#digest']
        }

        # Publish to both platforms
        return self.publish_content(
            title=title,
            content=content,
            league=league,
            category=report_type,
            metadata=metadata
        )

    def archive_old_content(self, days_old: int = None) -> Dict[str, int]:
        """
        Archive old content on both platforms.

        Args:
            days_old: Age threshold (uses config default if not specified)

        Returns:
            Dictionary with archive counts per platform
        """
        days = days_old or config.AUTO_ARCHIVE_DAYS
        results = {}

        # Archive Google Docs
        try:
            google_count = self.google_docs.archive_old_documents(days)
            results['google_docs'] = google_count
        except Exception as e:
            results['google_docs_error'] = str(e)

        # Archive Apple Notes
        try:
            notes_count = self.apple_notes.archive_old_notes(days)
            results['apple_notes'] = notes_count
        except Exception as e:
            results['apple_notes_error'] = str(e)

        return results

    def create_weekly_summary(self) -> Dict[str, str]:
        """
        Create weekly aggregation summary across both platforms.

        Returns:
            Summary document IDs
        """
        results = {}

        # Create Apple Notes weekly aggregation
        try:
            apple_summary_id = self.apple_notes.create_weekly_aggregation()
            results['apple_notes_summary'] = apple_summary_id
        except Exception as e:
            results['apple_notes_error'] = str(e)

        # Could also create Google Docs summary if needed
        # This would aggregate all documents from the week

        return results

    def export_batch_pdf(
        self,
        platform: str = 'both',
        output_dir: str = './exports'
    ) -> Dict[str, List[str]]:
        """
        Export documents to PDF from both platforms.

        Args:
            platform: 'google_docs', 'apple_notes', or 'both'
            output_dir: Output directory

        Returns:
            Dictionary with exported file paths per platform
        """
        results = {}

        if platform in ['google_docs', 'both']:
            try:
                # Get all recent document IDs from cache
                doc_ids = self._get_recent_google_doc_ids()
                if doc_ids:
                    exported = self.google_docs.export_to_pdf(doc_ids, output_dir)
                    results['google_docs_files'] = exported
            except Exception as e:
                results['google_docs_error'] = str(e)

        if platform in ['apple_notes', 'both']:
            try:
                # Get all recent note IDs
                note_ids = list(self.apple_notes.notes_db.keys())
                if note_ids:
                    exported = self.apple_notes.export_to_pdf(note_ids, output_dir)
                    results['apple_notes_files'] = exported
            except Exception as e:
                results['apple_notes_error'] = str(e)

        return results

    def lock_published_documents(self, doc_ids: List[str]):
        """
        Lock Google Docs from further edits.

        Args:
            doc_ids: List of document IDs to lock
        """
        for doc_id in doc_ids:
            try:
                self.google_docs.lock_document(doc_id)
            except Exception as e:
                print(f"Error locking document {doc_id}: {e}")

    def setup_offline_mode(self):
        """Setup offline caching for Apple Notes."""
        try:
            self.apple_notes.setup_offline_sync(config.OFFLINE_CACHE_DAYS)
            print("✓ Offline mode configured")
        except Exception as e:
            print(f"Error setting up offline mode: {e}")

    def get_platform_stats(self) -> Dict[str, Any]:
        """
        Get statistics from both platforms.

        Returns:
            Combined statistics
        """
        stats = {}

        # Google Docs stats (would need to implement in manager)
        stats['google_docs'] = {
            'folders': len(self.google_docs.folder_cache),
            'authenticated': self.google_docs.creds is not None
        }

        # Apple Notes stats
        stats['apple_notes'] = self.apple_notes.get_note_stats()

        return stats

    # ========== Helper Methods ==========

    def _format_report_content(self, report_data: Dict[str, Any]) -> str:
        """
        Format report data into readable content.

        Args:
            report_data: Raw report data

        Returns:
            Formatted content string
        """
        content = ""

        # Recent Games
        if report_data.get('recent_games'):
            content += "## Recent Games\n\n"
            for game in report_data['recent_games'][:5]:
                content += f"- {game}\n"
            content += "\n"

        # Standout Players
        if report_data.get('standout_players'):
            content += "## Standout Players\n\n"
            for player in report_data['standout_players'][:5]:
                content += f"- {player}\n"
            content += "\n"

        # Injuries
        if report_data.get('injuries'):
            content += "## Injury Report\n\n"
            for injury in report_data['injuries'][:5]:
                content += f"- {injury}\n"
            content += "\n"

        # Betting Insights
        if report_data.get('betting_insights'):
            content += "## Betting Insights\n\n"
            insights = report_data['betting_insights']

            if insights.get('value_bets'):
                content += "### Value Bets\n"
                for bet in insights['value_bets'][:3]:
                    content += f"- {bet}\n"

            if insights.get('featured_games'):
                content += "\n### Featured Games\n"
                for game in insights['featured_games'][:3]:
                    content += f"- {game.get('matchup')}: Spread {game.get('spread')}, O/U {game.get('total')}\n"

            content += "\n"

        # Must Watch
        if report_data.get('must_watch'):
            content += "## Must-Watch Matchups\n\n"
            for matchup in report_data['must_watch'][:3]:
                content += f"- {matchup}\n"

        return content

    def _get_recent_google_doc_ids(self, limit: int = 20) -> List[str]:
        """
        Get recent Google Doc IDs.

        Args:
            limit: Maximum number of documents

        Returns:
            List of document IDs
        """
        # This would query Google Drive for recent documents
        # For now, return from cross-references
        return list(self.cross_references.keys())[:limit]
