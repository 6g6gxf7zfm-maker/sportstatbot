"""Google Docs API integration for document creation and management."""
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Google API imports (install with: pip install google-auth google-auth-oauthlib google-api-python-client)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")


class GoogleDocsIntegration:
    """
    Google Docs API integration.

    Features:
    - OAuth authentication
    - Document creation
    - Folder management
    - Tagging and metadata
    - Automatic folder naming: {sport}_{date}_{type}
    """

    # OAuth scopes
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize Google Docs integration.

        Args:
            credentials_path: Path to OAuth client credentials
            token_path: Path to store access token
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries not installed")

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.docs_service = None
        self.drive_service = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google APIs.

        Returns:
            True if authentication successful
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

            # If credentials are invalid or don't exist, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())

            # Build services
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)

            logger.info("Google Docs authentication successful")
            return True

        except Exception as e:
            logger.error(f"Google Docs authentication failed: {e}")
            return False

    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive.

        Args:
            folder_name: Name of the folder
            parent_folder_id: ID of parent folder (None for root)

        Returns:
            Folder ID if successful
        """
        if not self.drive_service:
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created folder: {folder_name} (ID: {folder_id})")
            return folder_id

        except HttpError as error:
            logger.error(f"Error creating folder: {error}")
            return None

    def get_or_create_folder(
        self,
        sport: str,
        date: Optional[str] = None,
        folder_type: str = 'digest',
        parent_folder_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get or create a folder with automatic naming: {sport}_{date}_{type}.

        Args:
            sport: Sport identifier
            date: Date string (YYYY-MM-DD), defaults to today
            folder_type: Type of folder (digest, analysis, etc.)
            parent_folder_id: ID of parent folder

        Returns:
            Folder ID if successful
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        folder_name = f"{sport.upper()}_{date}_{folder_type}"

        # Check if folder already exists
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"

            results = self.drive_service.files().list(
                q=query,
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])
            if files:
                folder_id = files[0]['id']
                logger.info(f"Found existing folder: {folder_name} (ID: {folder_id})")
                return folder_id

        except HttpError as error:
            logger.error(f"Error checking for existing folder: {error}")

        # Create new folder
        return self.create_folder(folder_name, parent_folder_id)

    def create_document(
        self,
        title: str,
        content: str,
        folder_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a Google Doc with content.

        Args:
            title: Document title
            content: Document content (plain text or markdown)
            folder_id: ID of folder to place document in
            metadata: Additional metadata for the document

        Returns:
            Dictionary with document info (id, url) if successful
        """
        if not self.docs_service or not self.drive_service:
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            # Create document
            doc = self.docs_service.documents().create(body={'title': title}).execute()
            doc_id = doc.get('documentId')

            # Insert content
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

            # Move to folder if specified
            if folder_id:
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    fields='id, parents'
                ).execute()

            # Add metadata as properties
            if metadata:
                properties = {
                    'properties': {
                        key: str(value) for key, value in metadata.items()
                    }
                }
                self.drive_service.files().update(
                    fileId=doc_id,
                    body=properties
                ).execute()

            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            logger.info(f"Created document: {title} (ID: {doc_id})")

            return {
                'id': doc_id,
                'title': title,
                'url': doc_url,
                'folder_id': folder_id
            }

        except HttpError as error:
            logger.error(f"Error creating document: {error}")
            return None

    def move_to_archive(
        self,
        file_id: str,
        archive_folder_id: str,
        days_old: Optional[int] = None
    ) -> bool:
        """
        Move a file to archive folder.

        Args:
            file_id: ID of file to archive
            archive_folder_id: ID of archive folder
            days_old: Only archive if file is older than this many days

        Returns:
            True if successful
        """
        if not self.drive_service:
            logger.error("Not authenticated. Call authenticate() first.")
            return False

        try:
            # Get file metadata
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='id, name, createdTime, parents'
            ).execute()

            # Check age if specified
            if days_old:
                created_time = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
                age = (datetime.now(created_time.tzinfo) - created_time).days
                if age < days_old:
                    logger.info(f"File too recent to archive: {file['name']} ({age} days old)")
                    return False

            # Move to archive
            previous_parents = ','.join(file.get('parents', []))
            self.drive_service.files().update(
                fileId=file_id,
                addParents=archive_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            logger.info(f"Archived file: {file['name']}")
            return True

        except HttpError as error:
            logger.error(f"Error archiving file: {error}")
            return False

    def list_documents_in_folder(self, folder_id: str) -> List[Dict]:
        """
        List all documents in a folder.

        Args:
            folder_id: ID of folder

        Returns:
            List of document info dictionaries
        """
        if not self.drive_service:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        try:
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
            results = self.drive_service.files().list(
                q=query,
                fields='files(id, name, createdTime, modifiedTime)'
            ).execute()

            files = results.get('files', [])
            return [
                {
                    'id': f['id'],
                    'name': f['name'],
                    'url': f"https://docs.google.com/document/d/{f['id']}/edit",
                    'created': f['createdTime'],
                    'modified': f['modifiedTime']
                }
                for f in files
            ]

        except HttpError as error:
            logger.error(f"Error listing documents: {error}")
            return []
