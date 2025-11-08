"""
Google Docs Exporter - Export stories to Google Docs with organization
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class GoogleDocsExporter:
    """
    Export stories to Google Docs with automatic organization

    Features:
    - Subfolder organization by sport, date, and story type
    - Preserves markdown formatting (bold, emoji, etc.)
    - Auto-generates document titles
    - Batch export capabilities
    """

    STORY_TYPES = ['digests', 'features', 'previews', 'betting_insights', 'analysis']

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        root_folder_id: Optional[str] = None
    ):
        """
        Initialize Google Docs exporter

        Args:
            credentials_path: Path to Google API credentials JSON
            root_folder_id: Google Drive folder ID for root organization
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.root_folder_id = root_folder_id or os.getenv('GOOGLE_ROOT_FOLDER_ID')
        self.service = None

        # Try to initialize Google API client
        self._init_google_client()

    def _init_google_client(self):
        """Initialize Google API client (if credentials available)"""
        if not self.credentials_path:
            print("Warning: Google credentials not configured. Exporter will use local fallback.")
            return

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            # Load credentials
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/drive'
                ]
            )

            # Build services
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)

            print("Google API client initialized successfully")

        except ImportError:
            print("Warning: google-api-python-client not installed. Using local fallback.")
        except Exception as e:
            print(f"Warning: Failed to initialize Google API: {e}. Using local fallback.")

    def export_story(
        self,
        story: Dict[str, Any],
        sport: str,
        story_type: str = 'digests',
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export a single story to Google Docs

        Args:
            story: Story data dictionary
            sport: Sport name
            story_type: Type of story (digest, feature, preview, etc.)
            title: Optional custom title (auto-generated if None)

        Returns:
            Dictionary with export result including doc URL
        """
        # Generate title if not provided
        if not title:
            title = self._generate_title(story, sport, story_type)

        # Organize into folder structure
        folder_path = self._get_folder_path(sport, story_type)

        if self.docs_service:
            # Use Google Docs API
            return self._export_to_google_docs(story, title, folder_path)
        else:
            # Fallback to local file export
            return self._export_to_local(story, title, folder_path)

    def batch_export(
        self,
        stories: List[Dict[str, Any]],
        sport: str
    ) -> List[Dict[str, Any]]:
        """
        Batch export multiple stories

        Args:
            stories: List of story dictionaries
            sport: Sport name

        Returns:
            List of export results
        """
        results = []

        for story in stories:
            story_type = story.get('type', 'digests')
            result = self.export_story(story, sport, story_type)
            results.append(result)

        return results

    def _generate_title(
        self,
        story: Dict[str, Any],
        sport: str,
        story_type: str
    ) -> str:
        """Generate document title"""
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')

        # Use story headline if available
        if story.get('headline'):
            base_title = story['headline']
        else:
            base_title = f"{sport.upper()} {story_type.capitalize()}"

        return f"{base_title} - {date_str}"

    def _get_folder_path(self, sport: str, story_type: str) -> str:
        """
        Get folder path for organization

        Structure: /SportStatBot/{sport}/{year}/{month}/{story_type}/
        """
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m-%B')  # "01-January"

        return f"SportStatBot/{sport}/{year}/{month}/{story_type}"

    def _export_to_google_docs(
        self,
        story: Dict[str, Any],
        title: str,
        folder_path: str
    ) -> Dict[str, Any]:
        """Export using Google Docs API"""
        try:
            # Create or get folder
            folder_id = self._ensure_folder_structure(folder_path)

            # Create new document
            doc = self.docs_service.documents().create(body={
                'title': title
            }).execute()

            doc_id = doc['documentId']

            # Build content requests
            from story_automation.formatters.markdown_converter import MarkdownConverter
            converter = MarkdownConverter()

            # Convert story to markdown
            markdown_content = self._story_to_markdown(story)

            # Convert markdown to Google Docs format
            doc_requests = converter.to_google_docs(markdown_content)

            # Apply content to document
            if doc_requests['requests']:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': doc_requests['requests']}
                ).execute()

            # Move to appropriate folder
            if folder_id:
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    removeParents=self.root_folder_id or 'root',
                    fields='id, parents'
                ).execute()

            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

            return {
                'success': True,
                'doc_id': doc_id,
                'url': doc_url,
                'title': title,
                'folder_path': folder_path
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'title': title
            }

    def _export_to_local(
        self,
        story: Dict[str, Any],
        title: str,
        folder_path: str
    ) -> Dict[str, Any]:
        """Fallback: Export to local filesystem"""
        try:
            # Create local folder structure
            base_path = Path('exports') / folder_path
            base_path.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            filename = self._sanitize_filename(title) + '.md'
            file_path = base_path / filename

            # Convert story to markdown
            markdown_content = self._story_to_markdown(story)

            # Write to file
            file_path.write_text(markdown_content, encoding='utf-8')

            return {
                'success': True,
                'file_path': str(file_path),
                'title': title,
                'folder_path': folder_path,
                'mode': 'local'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'mode': 'local'
            }

    def _story_to_markdown(self, story: Dict[str, Any]) -> str:
        """Convert story dictionary to markdown"""
        md = ""

        # Title
        if story.get('headline'):
            md += f"# {story['headline']}\n\n"

        # Subhead
        if story.get('subhead'):
            md += f"_{story['subhead']}_\n\n"

        # TL;DR
        if story.get('tldr'):
            md += f"{story['tldr']}\n\n"

        # Body
        if story.get('body'):
            md += f"{story['body']}\n\n"

        # Sidebars
        if story.get('sidebars'):
            from story_automation.generators.sidebar_generator import SidebarGenerator
            sidebar_gen = SidebarGenerator()

            for sidebar in story['sidebars']:
                md += sidebar_gen.format_sidebar(sidebar, 'markdown')
                md += "\n"

        # Pull quotes
        if story.get('pullquotes'):
            md += "\n## Key Quotes\n\n"
            for quote in story['pullquotes']:
                quote_text = quote.get('text', quote) if isinstance(quote, dict) else quote
                md += f"> {quote_text}\n\n"

        # Trivia
        if story.get('trivia'):
            md += f"\n{story['trivia']}\n\n"

        # Conclusion
        if story.get('conclusion'):
            md += f"{story['conclusion']}\n\n"

        # Metadata footer
        if story.get('metadata'):
            md += "\n---\n"
            md += f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
            if story['metadata'].get('data_sources'):
                md += f"_Sources: {', '.join(story['metadata']['data_sources'])}_\n"

        return md

    def _ensure_folder_structure(self, folder_path: str) -> Optional[str]:
        """Ensure folder structure exists in Google Drive"""
        if not self.drive_service:
            return None

        try:
            parts = folder_path.split('/')
            current_parent = self.root_folder_id or 'root'

            for folder_name in parts:
                # Check if folder exists
                query = f"name='{folder_name}' and '{current_parent}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

                results = self.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()

                folders = results.get('files', [])

                if folders:
                    current_parent = folders[0]['id']
                else:
                    # Create folder
                    file_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [current_parent]
                    }

                    folder = self.drive_service.files().create(
                        body=file_metadata,
                        fields='id'
                    ).execute()

                    current_parent = folder['id']

            return current_parent

        except Exception as e:
            print(f"Error creating folder structure: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '-')

        # Limit length
        return filename[:200]

    def list_exported_docs(
        self,
        sport: Optional[str] = None,
        story_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List exported documents

        Args:
            sport: Optional sport filter
            story_type: Optional story type filter

        Returns:
            List of document metadata
        """
        if self.drive_service:
            return self._list_google_docs(sport, story_type)
        else:
            return self._list_local_files(sport, story_type)

    def _list_google_docs(
        self,
        sport: Optional[str],
        story_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """List documents from Google Drive"""
        # Implementation would query Google Drive API
        return []

    def _list_local_files(
        self,
        sport: Optional[str],
        story_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """List local export files"""
        exports_path = Path('exports/SportStatBot')

        if not exports_path.exists():
            return []

        files = []
        for file_path in exports_path.rglob('*.md'):
            files.append({
                'path': str(file_path),
                'name': file_path.stem,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            })

        return files
