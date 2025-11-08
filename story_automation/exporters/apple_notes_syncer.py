"""
Apple Notes Syncer - Sync stories to Apple Notes with folder organization
"""

import os
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class AppleNotesSyncer:
    """
    Sync stories to Apple Notes with automatic folder organization

    Features:
    - Separate folders for Digests, Features, Previews, Betting Insights
    - Sport-based sub-organization
    - Rich text formatting preservation
    - Automatic syncing across devices via iCloud
    """

    STORY_CATEGORIES = {
        'digests': 'Daily Digests',
        'features': 'Feature Stories',
        'previews': 'Game Previews',
        'betting_insights': 'Betting Insights',
        'analysis': 'Deep Analysis'
    }

    def __init__(self, base_folder: str = 'SportStatBot'):
        """
        Initialize Apple Notes syncer

        Args:
            base_folder: Base folder name in Apple Notes
        """
        self.base_folder = base_folder
        self.platform = self._detect_platform()
        self.notes_available = self._check_notes_availability()

    def _detect_platform(self) -> str:
        """Detect operating system platform"""
        import platform
        system = platform.system()
        return system.lower()

    def _check_notes_availability(self) -> bool:
        """Check if Apple Notes is available"""
        if self.platform != 'darwin':  # macOS
            return False

        try:
            # Check if Notes app exists
            result = subprocess.run(
                ['osascript', '-e', 'tell application "Notes" to version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def sync_story(
        self,
        story: Dict[str, Any],
        sport: str,
        category: str = 'digests',
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync a story to Apple Notes

        Args:
            story: Story data dictionary
            sport: Sport name
            category: Story category
            title: Optional custom title

        Returns:
            Dictionary with sync result
        """
        if not self.notes_available:
            # Fallback to local markdown export
            return self._export_as_markdown(story, sport, category, title)

        # Generate title
        if not title:
            title = self._generate_title(story, sport, category)

        # Get folder structure
        folder_name = self._get_folder_name(sport, category)

        # Create note content
        content = self._story_to_html(story)

        # Create note using AppleScript
        result = self._create_apple_note(title, content, folder_name)

        return result

    def batch_sync(
        self,
        stories: List[Dict[str, Any]],
        sport: str
    ) -> List[Dict[str, Any]]:
        """
        Batch sync multiple stories

        Args:
            stories: List of story dictionaries
            sport: Sport name

        Returns:
            List of sync results
        """
        results = []

        for story in stories:
            category = story.get('type', 'digests')
            result = self.sync_story(story, sport, category)
            results.append(result)

        return results

    def organize_by_sport(self, sport: str) -> Dict[str, List[str]]:
        """
        Get folder organization structure for a sport

        Args:
            sport: Sport name

        Returns:
            Dictionary mapping categories to folder paths
        """
        organization = {}

        for category_key, category_name in self.STORY_CATEGORIES.items():
            folder_path = f"{self.base_folder} / {sport.upper()} / {category_name}"
            organization[category_key] = folder_path

        return organization

    def _generate_title(
        self,
        story: Dict[str, Any],
        sport: str,
        category: str
    ) -> str:
        """Generate note title"""
        timestamp = datetime.now()
        date_str = timestamp.strftime('%b %d, %Y')

        if story.get('headline'):
            return f"{story['headline']} - {date_str}"
        else:
            category_name = self.STORY_CATEGORIES.get(category, category.capitalize())
            return f"{sport.upper()} {category_name} - {date_str}"

    def _get_folder_name(self, sport: str, category: str) -> str:
        """Get folder name for organization"""
        category_name = self.STORY_CATEGORIES.get(category, category.capitalize())
        return f"{self.base_folder}/{sport.upper()}/{category_name}"

    def _story_to_html(self, story: Dict[str, Any]) -> str:
        """Convert story to HTML for Notes"""
        html = ""

        # Title
        if story.get('headline'):
            html += f"<h1>{story['headline']}</h1>"

        # Subhead
        if story.get('subhead'):
            html += f"<p><em>{story['subhead']}</em></p>"

        # TL;DR
        if story.get('tldr'):
            html += f"<p><strong>TL;DR:</strong> {story['tldr']}</p>"

        # Body - convert markdown to HTML
        if story.get('body'):
            from story_automation.formatters.markdown_converter import MarkdownConverter
            converter = MarkdownConverter()
            body_html = converter.to_html(story['body'])
            html += body_html

        # Sidebars
        if story.get('sidebars'):
            for sidebar in story['sidebars']:
                html += f"<hr><h3>{sidebar.get('title', 'Sidebar')}</h3>"
                # Format sidebar content
                for item in sidebar.get('items', []):
                    html += f"<p>{item}</p>"

        # Pull quotes
        if story.get('pullquotes'):
            html += "<hr><h3>Key Quotes</h3>"
            for quote in story['pullquotes']:
                quote_text = quote.get('text', quote) if isinstance(quote, dict) else quote
                html += f"<blockquote>{quote_text}</blockquote>"

        # Metadata
        html += f"<hr><p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></p>"

        return html

    def _create_apple_note(
        self,
        title: str,
        content: str,
        folder_name: str
    ) -> Dict[str, Any]:
        """Create note using AppleScript"""
        try:
            # Escape content for AppleScript
            title_escaped = title.replace('"', '\\"')
            content_escaped = content.replace('"', '\\"').replace('\n', '\\n')
            folder_escaped = folder_name.replace('"', '\\"')

            # AppleScript to create note
            applescript = f'''
                tell application "Notes"
                    activate

                    -- Create folder structure if needed
                    set folderPath to "{folder_escaped}"
                    set folderParts to my splitText(folderPath, "/")

                    set currentFolder to default account
                    repeat with folderName in folderParts
                        try
                            set currentFolder to folder folderName of currentFolder
                        on error
                            set currentFolder to make new folder at currentFolder with properties {{name:folderName}}
                        end try
                    end repeat

                    -- Create note
                    set newNote to make new note at currentFolder with properties {{name:"{title_escaped}", body:"{content_escaped}"}}

                    return id of newNote
                end tell

                on splitText(theText, theDelimiter)
                    set AppleScript's text item delimiters to theDelimiter
                    set theTextItems to every text item of theText
                    set AppleScript's text item delimiters to ""
                    return theTextItems
                end splitText
            '''

            # Execute AppleScript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                note_id = result.stdout.strip()
                return {
                    'success': True,
                    'note_id': note_id,
                    'title': title,
                    'folder': folder_name,
                    'platform': 'apple_notes'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'title': title,
                    'platform': 'apple_notes'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'platform': 'apple_notes'
            }

    def _export_as_markdown(
        self,
        story: Dict[str, Any],
        sport: str,
        category: str,
        title: Optional[str]
    ) -> Dict[str, Any]:
        """Fallback: Export as markdown file"""
        try:
            # Create folder structure
            folder_name = self._get_folder_name(sport, category)
            folder_path = Path('exports') / folder_name.replace('/', os.sep)
            folder_path.mkdir(parents=True, exist_ok=True)

            # Generate title
            if not title:
                title = self._generate_title(story, sport, category)

            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{title[:50]}_{timestamp}.md"

            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()

            file_path = folder_path / filename

            # Convert story to markdown
            from story_automation.exporters.google_docs_exporter import GoogleDocsExporter
            exporter = GoogleDocsExporter()
            markdown_content = exporter._story_to_markdown(story)

            # Write file
            file_path.write_text(markdown_content, encoding='utf-8')

            return {
                'success': True,
                'file_path': str(file_path),
                'title': title,
                'folder': folder_name,
                'platform': 'local_markdown'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'platform': 'local_markdown'
            }

    def list_notes(
        self,
        sport: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List synced notes

        Args:
            sport: Optional sport filter
            category: Optional category filter

        Returns:
            List of note metadata
        """
        if not self.notes_available:
            return []

        try:
            # Build folder path
            folder_parts = [self.base_folder]
            if sport:
                folder_parts.append(sport.upper())
            if category:
                folder_parts.append(self.STORY_CATEGORIES.get(category, category))

            folder_path = "/".join(folder_parts)

            # AppleScript to list notes
            applescript = f'''
                tell application "Notes"
                    set noteList to {{}}
                    set targetFolder to folder "{folder_path}"

                    repeat with aNote in notes of targetFolder
                        set end of noteList to {{name:name of aNote, id:id of aNote, creationDate:creation date of aNote}}
                    end repeat

                    return noteList
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse result (simplified - actual parsing would be more complex)
                return []
            else:
                return []

        except Exception:
            return []

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note by ID

        Args:
            note_id: Apple Notes note ID

        Returns:
            Success boolean
        """
        if not self.notes_available:
            return False

        try:
            applescript = f'''
                tell application "Notes"
                    delete note id "{note_id}"
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                timeout=5
            )

            return result.returncode == 0

        except Exception:
            return False
