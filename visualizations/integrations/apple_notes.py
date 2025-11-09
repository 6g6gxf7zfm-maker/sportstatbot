"""
Apple Notes Integration
Feature #50: Interactive chart-to-note link (click → append to Apple Note)
"""

import subprocess
import os
from typing import Dict, Any
from datetime import datetime


class AppleNotesIntegration:
    """
    Feature #50: Interactive chart-to-note link

    Allows exporting visualizations directly to Apple Notes.
    """

    def __init__(self):
        self.notes_available = self._check_notes_availability()

    def _check_notes_availability(self) -> bool:
        """Check if running on macOS with Notes available"""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "Notes" to get name'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def export_to_notes(
        self,
        chart_path: str,
        note_title: str = None,
        note_body: str = "",
        folder: str = "Sports Analytics"
    ) -> bool:
        """
        Export chart to Apple Notes

        Args:
            chart_path: Path to saved chart image/HTML
            note_title: Title for the note
            note_body: Additional text to include
            folder: Notes folder name

        Returns:
            Success status
        """
        if not self.notes_available:
            print("Apple Notes not available on this system")
            return False

        if not os.path.exists(chart_path):
            print(f"Chart file not found: {chart_path}")
            return False

        if not note_title:
            note_title = f"Sports Analytics - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # AppleScript to create note
        applescript = f'''
        tell application "Notes"
            activate

            -- Create folder if it doesn't exist
            if not (exists folder "{folder}") then
                make new folder with properties {{name:"{folder}"}}
            end if

            -- Create new note
            tell folder "{folder}"
                set theNote to make new note
                tell theNote
                    set name to "{note_title}"
                    set body to "{note_body}"
                end tell
            end tell

            -- Add attachment
            tell theNote
                set theAttachment to make new attachment with data (POSIX file "{chart_path}")
            end tell

            show theNote
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"✓ Chart exported to Apple Notes: {note_title}")
                return True
            else:
                print(f"✗ Failed to export: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ Error exporting to Notes: {e}")
            return False

    def create_note_link(self, chart_path: str, title: str = None) -> Dict[str, Any]:
        """
        Create clickable link to export to Notes

        Args:
            chart_path: Path to chart file
            title: Note title

        Returns:
            Dictionary with link info
        """

        return {
            'action': 'export_to_notes',
            'chart_path': chart_path,
            'title': title or f"Chart Export {datetime.now().strftime('%Y-%m-%d')}",
            'available': self.notes_available,
            'handler': lambda: self.export_to_notes(chart_path, title)
        }

    def append_to_existing_note(
        self,
        note_title: str,
        chart_path: str,
        folder: str = "Sports Analytics"
    ) -> bool:
        """
        Append chart to existing note

        Args:
            note_title: Title of existing note
            chart_path: Path to chart file
            folder: Notes folder name

        Returns:
            Success status
        """
        if not self.notes_available:
            return False

        applescript = f'''
        tell application "Notes"
            activate

            -- Find existing note
            set theNote to first note of folder "{folder}" whose name is "{note_title}"

            -- Append attachment
            tell theNote
                set theAttachment to make new attachment with data (POSIX file "{chart_path}")
            end tell

            show theNote
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            return result.returncode == 0

        except Exception:
            return False
