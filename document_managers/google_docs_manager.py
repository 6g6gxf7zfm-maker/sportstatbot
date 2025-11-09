"""Google Docs and Drive integration for automated document management."""

import os
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
except ImportError:
    print("Warning: Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GoogleDocsManager:
    """Manages Google Docs and Drive operations for sports content."""

    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents'
    ]

    # Folder structure for each league
    SUBFOLDERS = ['Digests', 'Features', 'Previews', 'Betting']

    # League configurations
    LEAGUES = {
        'NFL': {'color': '#013369', 'emoji': '🏈'},
        'NBA': {'color': '#17408B', 'emoji': '🏀'},
        'MLB': {'color': '#041E42', 'emoji': '⚾'},
        'NHL': {'color': '#000000', 'emoji': '🏒'},
        'MLS': {'color': '#005DAA', 'emoji': '⚽'},
        'INTL': {'color': '#006400', 'emoji': '🌍'},
        'Golf': {'color': '#006633', 'emoji': '⛳'}
    }

    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Google Docs Manager.

        Args:
            credentials_path: Path to Google API credentials JSON
            token_path: Path to store/load OAuth token
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GOOGLE_TOKEN_PATH', 'token.pickle')
        self.creds = None
        self.drive_service = None
        self.docs_service = None
        self.folder_cache = {}  # Cache folder IDs
        self.toc_doc_id = None  # Table of Contents document ID

    def authenticate(self) -> bool:
        """
        Authenticate with Google APIs.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)

            # Refresh or create new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        print(f"Credentials file not found: {self.credentials_path}")
                        print("Please download OAuth 2.0 credentials from Google Cloud Console")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build services
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

            print("✓ Google API authentication successful")
            return True

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def setup_league_folders(self, root_folder_name: str = "SportStatBot Reports") -> Dict[str, str]:
        """
        Create per-league folder structure automatically.

        Structure:
        SportStatBot Reports/
        ├── NFL/
        │   ├── Digests/
        │   ├── Features/
        │   ├── Previews/
        │   └── Betting/
        ├── NBA/
        │   └── ...
        └── Table of Contents

        Args:
            root_folder_name: Name of root folder

        Returns:
            Dictionary mapping league names to folder IDs
        """
        if not self.drive_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        folder_structure = {}

        # Create or find root folder
        root_folder_id = self._create_or_find_folder(root_folder_name)
        folder_structure['root'] = root_folder_id

        # Create league folders with subfolders
        for league in self.LEAGUES.keys():
            league_folder_id = self._create_or_find_folder(
                league,
                parent_id=root_folder_id
            )
            folder_structure[league] = league_folder_id

            # Create subfolders
            folder_structure[f"{league}_subfolders"] = {}
            for subfolder in self.SUBFOLDERS:
                subfolder_id = self._create_or_find_folder(
                    subfolder,
                    parent_id=league_folder_id
                )
                folder_structure[f"{league}_subfolders"][subfolder] = subfolder_id

        # Create Story Archive folder
        archive_id = self._create_or_find_folder(
            "Story Archive",
            parent_id=root_folder_id
        )
        folder_structure['archive'] = archive_id

        # Cache folder structure
        self.folder_cache = folder_structure

        # Create Table of Contents document
        self._create_toc_document(root_folder_id)

        print(f"✓ Folder structure created: {len(self.LEAGUES)} leagues with {len(self.SUBFOLDERS)} subfolders each")
        return folder_structure

    def create_document(
        self,
        title: str,
        content: str,
        league: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None,
        add_header: bool = True
    ) -> str:
        """
        Create a new Google Doc with formatted content.

        Args:
            title: Document title
            content: Document content (markdown or plain text)
            league: League name (NFL, NBA, etc.)
            category: Category (Digests, Features, Previews, Betting)
            metadata: Additional metadata (author, word count, etc.)
            add_header: Whether to add formatted header

        Returns:
            Document ID
        """
        if not self.docs_service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Get target folder
        if not self.folder_cache:
            raise RuntimeError("Folder structure not set up. Call setup_league_folders() first.")

        target_folder = self.folder_cache.get(f"{league}_subfolders", {}).get(category)
        if not target_folder:
            raise ValueError(f"Invalid league/category: {league}/{category}")

        # Create document
        doc = self.docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc['documentId']

        # Move to appropriate folder
        self.drive_service.files().update(
            fileId=doc_id,
            addParents=target_folder,
            removeParents='root',
            fields='id, parents'
        ).execute()

        # Add date tag
        today = datetime.now().strftime('%Y-%m-%d')
        self._add_file_properties(doc_id, {
            'date': today,
            'league': league,
            'category': category,
            'tags': f"{league},{category},{today}"
        })

        # Format document
        if add_header:
            self._add_document_header(doc_id, title, league, metadata)

        # Add content
        self._add_content_to_document(doc_id, content)

        # Update Table of Contents
        self._update_toc(doc_id, title, league, category)

        print(f"✓ Document created: {title} ({league}/{category})")
        return doc_id

    def _add_document_header(
        self,
        doc_id: str,
        title: str,
        league: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add formatted header to document with league logo, timestamp, author, word count.

        Args:
            doc_id: Document ID
            title: Document title
            league: League name
            metadata: Additional metadata
        """
        metadata = metadata or {}
        league_info = self.LEAGUES.get(league, {})

        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        author = metadata.get('author', 'SportStatBot EIC')
        word_count = metadata.get('word_count', 'N/A')

        # Create header content
        header_text = f"{league_info.get('emoji', '')} {league} - {title}\n"
        header_text += f"{'─' * 60}\n"
        header_text += f"📅 {timestamp}\n"
        header_text += f"✍️  Author: {author}\n"
        header_text += f"📊 Word Count: {word_count}\n"
        header_text += f"{'─' * 60}\n\n"

        # Insert header
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': header_text
                }
            },
            # Format title as heading
            {
                'updateParagraphStyle': {
                    'range': {'startIndex': 1, 'endIndex': len(header_text.split('\n')[0]) + 1},
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_1',
                        'alignment': 'CENTER'
                    },
                    'fields': 'namedStyleType,alignment'
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

    def _add_content_to_document(self, doc_id: str, content: str):
        """
        Add content to document.

        Args:
            doc_id: Document ID
            content: Content to add
        """
        # Get current document length
        doc = self.docs_service.documents().get(documentId=doc_id).execute()
        doc_length = doc['body']['content'][-1]['endIndex']

        # Insert content at end
        requests = [
            {
                'insertText': {
                    'location': {'index': doc_length - 1},
                    'text': content
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

    def lock_document(self, doc_id: str):
        """
        Lock document from edits (make read-only for viewers).

        Args:
            doc_id: Document ID
        """
        # Set permissions to view-only
        self.drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()

        # Add custom property to track lock status
        self._add_file_properties(doc_id, {'locked': 'true', 'published': 'true'})
        print(f"✓ Document locked: {doc_id}")

    def archive_old_documents(self, days_old: int = 30) -> int:
        """
        Move documents older than X days to Story Archive.

        Args:
            days_old: Age threshold in days

        Returns:
            Number of documents archived
        """
        if not self.folder_cache:
            raise RuntimeError("Folder structure not set up.")

        archive_folder = self.folder_cache.get('archive')
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archived_count = 0

        # Search all league folders
        for league in self.LEAGUES.keys():
            league_folder = self.folder_cache.get(league)

            # Query old documents
            query = f"'{league_folder}' in parents and modifiedTime < '{cutoff_date.isoformat()}'"
            results = self.drive_service.files().list(
                q=query,
                fields='files(id, name, parents)'
            ).execute()

            files = results.get('files', [])

            for file in files:
                # Move to archive
                self.drive_service.files().update(
                    fileId=file['id'],
                    addParents=archive_folder,
                    removeParents=','.join(file.get('parents', [])),
                    fields='id, parents'
                ).execute()
                archived_count += 1

        print(f"✓ Archived {archived_count} documents older than {days_old} days")
        return archived_count

    def export_to_pdf(self, doc_ids: List[str], output_dir: str = "./exports") -> List[str]:
        """
        Export documents to PDF.

        Args:
            doc_ids: List of document IDs
            output_dir: Output directory for PDFs

        Returns:
            List of exported file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        exported_files = []

        for doc_id in doc_ids:
            try:
                # Get document name
                file_metadata = self.drive_service.files().get(
                    fileId=doc_id,
                    fields='name'
                ).execute()

                filename = f"{file_metadata['name']}.pdf"
                filepath = os.path.join(output_dir, filename)

                # Export as PDF
                request = self.drive_service.files().export_media(
                    fileId=doc_id,
                    mimeType='application/pdf'
                )

                with io.FileIO(filepath, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()

                exported_files.append(filepath)
                print(f"✓ Exported: {filename}")

            except Exception as e:
                print(f"Error exporting {doc_id}: {e}")

        return exported_files

    def add_cross_reference(self, doc_id: str, reference_doc_id: str, reference_title: str):
        """
        Add cross-reference link to another document.

        Args:
            doc_id: Document to add reference to
            reference_doc_id: Document being referenced
            reference_title: Title of referenced document
        """
        doc = self.docs_service.documents().get(documentId=doc_id).execute()
        doc_length = doc['body']['content'][-1]['endIndex']

        reference_text = f"\n\nSee also: {reference_title}"
        reference_url = f"https://docs.google.com/document/d/{reference_doc_id}"

        requests = [
            {
                'insertText': {
                    'location': {'index': doc_length - 1},
                    'text': reference_text
                }
            },
            {
                'updateTextStyle': {
                    'range': {
                        'startIndex': doc_length - 1,
                        'endIndex': doc_length + len(reference_text) - 1
                    },
                    'textStyle': {
                        'link': {'url': reference_url}
                    },
                    'fields': 'link'
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

    def _create_or_find_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """
        Create folder or return existing folder ID.

        Args:
            name: Folder name
            parent_id: Parent folder ID (None = root)

        Returns:
            Folder ID
        """
        # Search for existing folder
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = results.get('files', [])
        if files:
            return files[0]['id']

        # Create new folder
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return folder['id']

    def _add_file_properties(self, file_id: str, properties: Dict[str, str]):
        """
        Add custom properties to file for tagging and metadata.

        Args:
            file_id: File ID
            properties: Dictionary of properties
        """
        self.drive_service.files().update(
            fileId=file_id,
            body={'properties': properties}
        ).execute()

    def _create_toc_document(self, root_folder_id: str):
        """
        Create Table of Contents index document.

        Args:
            root_folder_id: Root folder ID
        """
        doc = self.docs_service.documents().create(
            body={'title': '📋 Table of Contents - SportStatBot'}
        ).execute()

        self.toc_doc_id = doc['documentId']

        # Move to root folder
        self.drive_service.files().update(
            fileId=self.toc_doc_id,
            addParents=root_folder_id,
            removeParents='root',
            fields='id, parents'
        ).execute()

        # Initialize with header
        header = "📋 SportStatBot Content Index\n"
        header += "=" * 60 + "\n"
        header += f"Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"

        for league in self.LEAGUES.keys():
            header += f"\n{self.LEAGUES[league]['emoji']} {league}\n"
            header += "-" * 40 + "\n"

        self._add_content_to_document(self.toc_doc_id, header)

    def _update_toc(self, doc_id: str, title: str, league: str, category: str):
        """
        Update Table of Contents with new document link.

        Args:
            doc_id: New document ID
            title: Document title
            league: League name
            category: Category
        """
        if not self.toc_doc_id:
            return

        doc = self.docs_service.documents().get(documentId=self.toc_doc_id).execute()
        doc_length = doc['body']['content'][-1]['endIndex']

        doc_url = f"https://docs.google.com/document/d/{doc_id}"
        entry = f"  • [{category}] {title}\n"

        # Insert entry
        requests = [
            {
                'insertText': {
                    'location': {'index': doc_length - 1},
                    'text': entry
                }
            },
            {
                'updateTextStyle': {
                    'range': {
                        'startIndex': doc_length - 1,
                        'endIndex': doc_length + len(entry) - 1
                    },
                    'textStyle': {
                        'link': {'url': doc_url}
                    },
                    'fields': 'link'
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=self.toc_doc_id,
            body={'requests': requests}
        ).execute()
