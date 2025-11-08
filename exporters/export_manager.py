"""Multi-destination export manager for content publishing."""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportDestination:
    """Base class for export destinations."""

    def export(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export content to destination.

        Args:
            content: Content to export

        Returns:
            Export result with status and metadata
        """
        raise NotImplementedError


class GoogleDocsExporter(ExportDestination):
    """Export to Google Docs."""

    def __init__(self, integration):
        """
        Initialize Google Docs exporter.

        Args:
            integration: GoogleDocsIntegration instance
        """
        self.integration = integration

    def export(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Export content to Google Docs."""
        try:
            title = content.get('title', 'Untitled')
            body = content.get('content', '')
            metadata = content.get('metadata', {})
            sport = metadata.get('sport')
            date = metadata.get('date')

            # Get or create folder
            folder_id = None
            if sport and date:
                folder_id = self.integration.get_or_create_folder(
                    sport=sport,
                    date=date,
                    folder_type='digest'
                )

            # Create document
            doc_info = self.integration.create_document(
                title=title,
                content=body,
                folder_id=folder_id,
                metadata=metadata
            )

            if doc_info:
                return {
                    'status': 'success',
                    'destination': 'google_docs',
                    'url': doc_info['url'],
                    'id': doc_info['id'],
                    'folder_id': folder_id
                }
            else:
                return {
                    'status': 'failed',
                    'destination': 'google_docs',
                    'error': 'Failed to create document'
                }

        except Exception as e:
            logger.error(f"Google Docs export error: {e}")
            return {
                'status': 'failed',
                'destination': 'google_docs',
                'error': str(e)
            }


class AppleNotesExporter(ExportDestination):
    """Export to Apple Notes."""

    def __init__(self, integration):
        """
        Initialize Apple Notes exporter.

        Args:
            integration: AppleNotesIntegration instance
        """
        self.integration = integration

    def export(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Export content to Apple Notes."""
        try:
            title = content.get('title', 'Untitled')
            body = content.get('content', '')
            metadata = content.get('metadata', {})
            sport = metadata.get('sport')
            date = metadata.get('date')

            # Create note with auto folder
            if sport:
                note_info = self.integration.create_note_with_auto_folder(
                    title=title,
                    content=body,
                    sport=sport,
                    date=date,
                    note_type='digest'
                )
            else:
                note_info = self.integration.create_note(
                    title=title,
                    content=body
                )

            if note_info:
                return {
                    'status': 'success',
                    'destination': 'apple_notes',
                    'id': note_info['id'],
                    'folder': note_info.get('folder')
                }
            else:
                return {
                    'status': 'failed',
                    'destination': 'apple_notes',
                    'error': 'Failed to create note'
                }

        except Exception as e:
            logger.error(f"Apple Notes export error: {e}")
            return {
                'status': 'failed',
                'destination': 'apple_notes',
                'error': str(e)
            }


class PDFExporter(ExportDestination):
    """Export to PDF."""

    def __init__(self, output_dir: str = 'reports/pdf'):
        """
        Initialize PDF exporter.

        Args:
            output_dir: Directory for PDF files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Export content to PDF."""
        try:
            title = content.get('title', 'Untitled')
            body = content.get('content', '')
            metadata = content.get('metadata', {})

            # Generate filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.pdf"
            filepath = self.output_dir / filename

            # For now, save as text file (PDF generation requires additional libraries)
            # TODO: Implement actual PDF generation with reportlab or similar
            text_filepath = filepath.with_suffix('.txt')
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n\n")
                f.write(body)

            return {
                'status': 'success',
                'destination': 'pdf',
                'path': str(text_filepath),
                'note': 'PDF generation pending - saved as text for now'
            }

        except Exception as e:
            logger.error(f"PDF export error: {e}")
            return {
                'status': 'failed',
                'destination': 'pdf',
                'error': str(e)
            }


class MarkdownExporter(ExportDestination):
    """Export to Markdown file."""

    def __init__(self, output_dir: str = 'reports'):
        """
        Initialize Markdown exporter.

        Args:
            output_dir: Directory for markdown files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Export content to Markdown file."""
        try:
            title = content.get('title', 'Untitled')
            body = content.get('content', '')
            metadata = content.get('metadata', {})

            # Generate filename
            date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
            sport = metadata.get('sport', 'report')
            filename = f"{sport}_{date}.md"
            filepath = self.output_dir / filename

            # Write markdown file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                if metadata:
                    f.write("## Metadata\n\n")
                    for key, value in metadata.items():
                        f.write(f"- **{key}**: {value}\n")
                    f.write("\n")
                f.write(body)

            return {
                'status': 'success',
                'destination': 'markdown',
                'path': str(filepath)
            }

        except Exception as e:
            logger.error(f"Markdown export error: {e}")
            return {
                'status': 'failed',
                'destination': 'markdown',
                'error': str(e)
            }


class ExportManager:
    """
    Multi-destination export manager.

    Features:
    - Export to multiple destinations simultaneously
    - Retry logic for failed exports
    - Export tracking and history
    - Destination-specific formatting
    """

    def __init__(self):
        """Initialize export manager."""
        self.destinations: Dict[str, ExportDestination] = {}
        self.export_history: List[Dict] = []

    def register_destination(self, name: str, exporter: ExportDestination):
        """
        Register an export destination.

        Args:
            name: Destination name
            exporter: Exporter instance
        """
        self.destinations[name] = exporter
        logger.info(f"Registered export destination: {name}")

    def export(
        self,
        content: Dict[str, Any],
        destinations: Optional[List[str]] = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Export content to specified destinations.

        Args:
            content: Content to export
            destinations: List of destination names (None = all)
            retry_count: Number of retry attempts for failed exports

        Returns:
            Dictionary with export results for each destination
        """
        if destinations is None:
            destinations = list(self.destinations.keys())

        results = {}
        export_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        for dest_name in destinations:
            if dest_name not in self.destinations:
                logger.warning(f"Destination not found: {dest_name}")
                results[dest_name] = {
                    'status': 'failed',
                    'error': 'Destination not registered'
                }
                continue

            exporter = self.destinations[dest_name]

            # Retry logic
            for attempt in range(1, retry_count + 1):
                try:
                    logger.info(f"Exporting to {dest_name} (attempt {attempt}/{retry_count})")
                    result = exporter.export(content)
                    results[dest_name] = result

                    if result['status'] == 'success':
                        logger.info(f"Export to {dest_name} successful")
                        break
                    else:
                        logger.warning(f"Export to {dest_name} failed: {result.get('error')}")
                        if attempt < retry_count:
                            import time
                            wait_time = 2 ** attempt
                            logger.info(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)

                except Exception as e:
                    logger.error(f"Export to {dest_name} error (attempt {attempt}): {e}")
                    results[dest_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }

        # Record export in history
        self.export_history.append({
            'export_id': export_id,
            'timestamp': datetime.now().isoformat(),
            'content_title': content.get('title'),
            'destinations': destinations,
            'results': results
        })

        return {
            'export_id': export_id,
            'results': results,
            'summary': self._get_summary(results)
        }

    def _get_summary(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Get summary of export results."""
        summary = {
            'total': len(results),
            'successful': len([r for r in results.values() if r['status'] == 'success']),
            'failed': len([r for r in results.values() if r['status'] == 'failed'])
        }
        return summary

    def get_export_history(self, limit: int = 50) -> List[Dict]:
        """
        Get export history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of export records
        """
        return self.export_history[-limit:]

    def get_destination_statistics(self) -> Dict[str, Dict]:
        """
        Get statistics for each destination.

        Returns:
            Dictionary with statistics per destination
        """
        stats = {}

        for dest_name in self.destinations.keys():
            stats[dest_name] = {
                'total_exports': 0,
                'successful': 0,
                'failed': 0
            }

        for export_record in self.export_history:
            for dest_name, result in export_record['results'].items():
                if dest_name in stats:
                    stats[dest_name]['total_exports'] += 1
                    if result['status'] == 'success':
                        stats[dest_name]['successful'] += 1
                    else:
                        stats[dest_name]['failed'] += 1

        return stats
