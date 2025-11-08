"""Apple Notes integration via Shortcuts automation."""
import logging
import subprocess
import json
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AppleNotesIntegration:
    """
    Apple Notes integration via Shortcuts.

    Features:
    - Create notes via AppleScript
    - Organize notes in folders
    - Dynamic folder/tab creation
    - Automatic naming: {sport}_{date}_{type}

    Note: Requires macOS with Apple Notes and permissions.
    """

    def __init__(self):
        """Initialize Apple Notes integration."""
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Apple Notes is available (macOS only)."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "Notes" to get name'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Apple Notes not available: {e}")
            return False

    def create_folder(self, folder_name: str) -> bool:
        """
        Create a folder in Apple Notes.

        Args:
            folder_name: Name of the folder

        Returns:
            True if successful
        """
        if not self.available:
            logger.error("Apple Notes not available")
            return False

        try:
            script = f'''
            tell application "Notes"
                try
                    make new folder with properties {{name:"{folder_name}"}}
                    return true
                on error
                    return false
                end try
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            success = result.returncode == 0
            if success:
                logger.info(f"Created Apple Notes folder: {folder_name}")
            else:
                logger.error(f"Failed to create folder: {result.stderr}")

            return success

        except Exception as e:
            logger.error(f"Error creating Apple Notes folder: {e}")
            return False

    def get_or_create_folder(
        self,
        sport: str,
        date: Optional[str] = None,
        folder_type: str = 'digest'
    ) -> Optional[str]:
        """
        Get or create a folder with automatic naming: {sport}_{date}_{type}.

        Args:
            sport: Sport identifier
            date: Date string (YYYY-MM-DD), defaults to today
            folder_type: Type of folder

        Returns:
            Folder name if successful
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        folder_name = f"{sport.upper()}_{date}_{folder_type}"

        # Check if folder exists
        if self._folder_exists(folder_name):
            logger.info(f"Found existing Apple Notes folder: {folder_name}")
            return folder_name

        # Create folder
        if self.create_folder(folder_name):
            return folder_name

        return None

    def _folder_exists(self, folder_name: str) -> bool:
        """Check if a folder exists."""
        if not self.available:
            return False

        try:
            script = f'''
            tell application "Notes"
                try
                    get folder "{folder_name}"
                    return true
                on error
                    return false
                end try
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            return 'true' in result.stdout.lower()

        except Exception:
            return False

    def create_note(
        self,
        title: str,
        content: str,
        folder_name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a note in Apple Notes.

        Args:
            title: Note title
            content: Note content (plain text or HTML)
            folder_name: Name of folder to place note in

        Returns:
            Dictionary with note info if successful
        """
        if not self.available:
            logger.error("Apple Notes not available")
            return None

        try:
            # Escape quotes in content
            content_escaped = content.replace('"', '\\"').replace('\n', '\\n')
            title_escaped = title.replace('"', '\\"')

            if folder_name:
                script = f'''
                tell application "Notes"
                    try
                        set targetFolder to folder "{folder_name}"
                        set newNote to make new note at targetFolder with properties {{name:"{title_escaped}", body:"{content_escaped}"}}
                        return id of newNote
                    on error errMsg
                        return "ERROR: " & errMsg
                    end try
                end tell
                '''
            else:
                script = f'''
                tell application "Notes"
                    try
                        set newNote to make new note with properties {{name:"{title_escaped}", body:"{content_escaped}"}}
                        return id of newNote
                    on error errMsg
                        return "ERROR: " & errMsg
                    end try
                end tell
                '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0 and 'ERROR' not in result.stdout:
                note_id = result.stdout.strip()
                logger.info(f"Created Apple Note: {title}")
                return {
                    'id': note_id,
                    'title': title,
                    'folder': folder_name
                }
            else:
                logger.error(f"Failed to create note: {result.stdout}")
                return None

        except Exception as e:
            logger.error(f"Error creating Apple Note: {e}")
            return None

    def create_note_with_auto_folder(
        self,
        title: str,
        content: str,
        sport: str,
        date: Optional[str] = None,
        note_type: str = 'digest'
    ) -> Optional[Dict]:
        """
        Create a note with automatic folder naming.

        Args:
            title: Note title
            content: Note content
            sport: Sport identifier
            date: Date string, defaults to today
            note_type: Type of note

        Returns:
            Dictionary with note info if successful
        """
        folder_name = self.get_or_create_folder(sport, date, note_type)
        if not folder_name:
            logger.error("Failed to get/create folder")
            return None

        return self.create_note(title, content, folder_name)

    def export_to_shortcuts(
        self,
        shortcut_name: str,
        data: Dict
    ) -> bool:
        """
        Send data to an Apple Shortcut for processing.

        Args:
            shortcut_name: Name of the Shortcut
            data: Data to pass to the Shortcut (will be JSON encoded)

        Returns:
            True if successful
        """
        if not self.available:
            logger.error("Apple Notes/Shortcuts not available")
            return False

        try:
            # Convert data to JSON
            json_data = json.dumps(data)

            # Run shortcut with URL scheme
            # shortcuts://run-shortcut?name=[name]&input=[input]
            import urllib.parse
            encoded_name = urllib.parse.quote(shortcut_name)
            encoded_input = urllib.parse.quote(json_data)

            url = f"shortcuts://run-shortcut?name={encoded_name}&input={encoded_input}"

            # Open URL (macOS)
            subprocess.run(['open', url], timeout=10)

            logger.info(f"Triggered Apple Shortcut: {shortcut_name}")
            return True

        except Exception as e:
            logger.error(f"Error running Apple Shortcut: {e}")
            return False

    def list_notes_in_folder(self, folder_name: str) -> list:
        """
        List all notes in a folder.

        Args:
            folder_name: Name of folder

        Returns:
            List of note titles
        """
        if not self.available:
            return []

        try:
            script = f'''
            tell application "Notes"
                try
                    set noteList to {{}}
                    set targetFolder to folder "{folder_name}"
                    repeat with aNote in notes of targetFolder
                        set end of noteList to name of aNote
                    end repeat
                    return noteList
                on error
                    return {{}}
                end try
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                # Parse AppleScript list output
                notes = [n.strip() for n in result.stdout.split(',') if n.strip()]
                return notes

            return []

        except Exception as e:
            logger.error(f"Error listing notes: {e}")
            return []
