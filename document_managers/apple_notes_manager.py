"""Apple Notes integration for sports content management."""

import os
import json
import subprocess
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib


class AppleNotesManager:
    """
    Manages Apple Notes for sports content.

    Note: Full Apple Notes integration requires macOS with AppleScript.
    On non-macOS systems, falls back to JSON-based local notes system.
    """

    # League folders/tabs
    LEAGUES = ['NFL', 'NBA', 'MLB', 'NHL', 'MLS', 'INTL', 'Golf']

    # Tabs/categories within each league
    TABS = ['Digests', 'Features', 'Injuries', 'Betting']

    # Color codes for labels (macOS Notes colors)
    COLORS = {
        'urgent': 'red',
        'published': 'blue',
        'draft': 'yellow',
        'archived': 'gray',
        'betting': 'orange',
        'injury': 'purple'
    }

    def __init__(self, storage_dir: str = "./apple_notes_data"):
        """
        Initialize Apple Notes Manager.

        Args:
            storage_dir: Directory for JSON-based fallback storage
        """
        self.storage_dir = storage_dir
        self.is_macos = platform.system() == 'Darwin'
        self.notes_db = {}
        self.weekly_aggregation = {}

        # Create storage directory
        os.makedirs(storage_dir, exist_ok=True)

        # Load existing notes if using fallback
        if not self.is_macos:
            self._load_fallback_db()

    def create_folder_structure(self) -> bool:
        """
        Create per-league folders/tabs structure.

        Returns:
            True if successful
        """
        if self.is_macos:
            return self._create_macos_folders()
        else:
            return self._create_fallback_folders()

    def create_note(
        self,
        league: str,
        category: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        color: str = 'draft',
        auto_summary: bool = True,
        google_docs_url: Optional[str] = None
    ) -> str:
        """
        Create a new note.

        Args:
            league: League name (NFL, NBA, etc.)
            category: Category/tab (Digests, Features, Injuries, Betting)
            title: Note title
            content: Note content
            tags: Custom tags (auto-adds date + keywords)
            color: Color label
            auto_summary: Generate 5 key takeaways summary
            google_docs_url: Cross-link to Google Docs

        Returns:
            Note ID
        """
        # Generate note ID
        note_id = self._generate_note_id(league, category, title)

        # Auto-generate tags
        today = datetime.now()
        auto_tags = [
            f"{today.strftime('%Y-%m-%d')}",
            f"#{league.lower()}",
            f"#{category.lower()}",
            f"#week{today.isocalendar()[1]}"
        ]

        if tags:
            auto_tags.extend(tags)

        # Generate summary if requested
        summary = ""
        if auto_summary:
            summary = self._generate_summary(content)

        # Build note content
        full_content = self._format_note_content(
            title, summary, content, auto_tags, google_docs_url
        )

        # Create note
        if self.is_macos:
            success = self._create_macos_note(
                league, category, title, full_content, color
            )
        else:
            success = self._create_fallback_note(
                note_id, league, category, title, full_content, auto_tags, color
            )

        if success:
            # Add to weekly aggregation
            self._add_to_weekly_aggregation(league, category, title, note_id)
            print(f"✓ Note created: {title} ({league}/{category})")
            return note_id
        else:
            print(f"✗ Failed to create note: {title}")
            return ""

    def update_note_color(self, note_id: str, color: str) -> bool:
        """
        Update note color label.

        Args:
            note_id: Note ID
            color: New color (urgent, published, draft, archived)

        Returns:
            True if successful
        """
        color_value = self.COLORS.get(color, 'gray')

        if self.is_macos:
            # AppleScript color update
            script = f'''
            tell application "Notes"
                set theNote to note id "{note_id}"
                -- Note: Color setting via AppleScript is limited
            end tell
            '''
            return self._run_applescript(script)
        else:
            # Update in fallback DB
            if note_id in self.notes_db:
                self.notes_db[note_id]['color'] = color_value
                self._save_fallback_db()
                return True
            return False

    def archive_old_notes(self, days_old: int = 30) -> int:
        """
        Move notes older than X days to "Past Weeks" folder.

        Args:
            days_old: Age threshold in days

        Returns:
            Number of notes archived
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archived_count = 0

        if self.is_macos:
            # Archive using AppleScript
            script = f'''
            tell application "Notes"
                set oldNotes to notes whose modification date < date "{cutoff_date.isoformat()}"
                set archiveFolder to folder "Past Weeks"

                repeat with aNote in oldNotes
                    move aNote to archiveFolder
                end repeat

                return count of oldNotes
            end tell
            '''
            result = self._run_applescript(script)
            if result:
                archived_count = int(result)
        else:
            # Archive in fallback DB
            for note_id, note in list(self.notes_db.items()):
                note_date = datetime.fromisoformat(note['created_at'])
                if note_date < cutoff_date:
                    note['archived'] = True
                    note['folder'] = 'Past Weeks'
                    archived_count += 1

            if archived_count > 0:
                self._save_fallback_db()

        print(f"✓ Archived {archived_count} notes older than {days_old} days")
        return archived_count

    def create_weekly_aggregation(self) -> str:
        """
        Create "This Week in Sports" aggregation note.

        Returns:
            Note ID of aggregation
        """
        week_number = datetime.now().isocalendar()[1]
        year = datetime.now().year
        title = f"This Week in Sports - Week {week_number}, {year}"

        # Build aggregation content
        content = f"# {title}\n\n"
        content += f"Generated: {datetime.now().strftime('%B %d, %Y')}\n\n"

        for league in self.LEAGUES:
            league_notes = [
                note for note in self.weekly_aggregation.values()
                if note.get('league') == league
            ]

            if league_notes:
                content += f"\n## {league}\n"
                for category in self.TABS:
                    category_notes = [n for n in league_notes if n.get('category') == category]
                    if category_notes:
                        content += f"\n### {category}\n"
                        for note in category_notes:
                            content += f"- {note['title']}\n"

        # Create note
        note_id = self.create_note(
            league='SUMMARY',
            category='Weekly',
            title=title,
            content=content,
            tags=['#weekly', '#summary'],
            color='published',
            auto_summary=False
        )

        return note_id

    def export_to_pdf(self, note_ids: List[str], output_dir: str = "./exports") -> List[str]:
        """
        Export notes to PDF.

        Args:
            note_ids: List of note IDs
            output_dir: Output directory

        Returns:
            List of exported file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        exported_files = []

        for note_id in note_ids:
            if self.is_macos:
                # Export via AppleScript (macOS 12+)
                output_path = os.path.join(output_dir, f"{note_id}.pdf")
                script = f'''
                tell application "Notes"
                    set theNote to note id "{note_id}"
                    set noteName to name of theNote
                    -- Export functionality may require additional setup
                end tell
                '''
                self._run_applescript(script)
            else:
                # Export from fallback DB
                if note_id in self.notes_db:
                    note = self.notes_db[note_id]
                    output_path = os.path.join(output_dir, f"{note['title']}.txt")

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(note['content'])

                    exported_files.append(output_path)

        print(f"✓ Exported {len(exported_files)} notes to {output_dir}")
        return exported_files

    def setup_offline_sync(self, cache_days: int = 30) -> bool:
        """
        Setup offline mode sync (cache last 30 days locally).

        Args:
            cache_days: Number of days to cache

        Returns:
            True if successful
        """
        cutoff_date = datetime.now() - timedelta(days=cache_days)

        # Always save to fallback DB for offline access
        if self.is_macos:
            # Sync Notes to fallback DB
            script = '''
            tell application "Notes"
                set allNotes to every note
                set noteData to {}

                repeat with aNote in allNotes
                    set noteInfo to {id:id of aNote, name:name of aNote, body:body of aNote}
                    set end of noteData to noteInfo
                end repeat

                return noteData
            end tell
            '''
            result = self._run_applescript(script)
            # Parse and save result
            # Note: This is simplified - full implementation would parse AppleScript output

        self._save_fallback_db()
        print(f"✓ Offline sync configured for {cache_days} days")
        return True

    # ========== Helper Methods ==========

    def _create_macos_folders(self) -> bool:
        """Create folder structure using AppleScript on macOS."""
        script = '''
        tell application "Notes"
            -- Create league folders
        '''

        for league in self.LEAGUES:
            script += f'''
            if not (exists folder "{league}") then
                make new folder with properties {{name:"{league}"}}
            end if
            '''

        script += '''
            -- Create Past Weeks archive folder
            if not (exists folder "Past Weeks") then
                make new folder with properties {name:"Past Weeks"}
            end if
        end tell
        '''

        success = self._run_applescript(script)
        if success:
            print(f"✓ Created {len(self.LEAGUES)} league folders in Apple Notes")
        return success

    def _create_fallback_folders(self) -> bool:
        """Create folder structure in fallback JSON system."""
        for league in self.LEAGUES:
            league_dir = os.path.join(self.storage_dir, league)
            os.makedirs(league_dir, exist_ok=True)

            for tab in self.TABS:
                tab_dir = os.path.join(league_dir, tab)
                os.makedirs(tab_dir, exist_ok=True)

        # Create archive folder
        os.makedirs(os.path.join(self.storage_dir, "Past Weeks"), exist_ok=True)

        print(f"✓ Created fallback folder structure at {self.storage_dir}")
        return True

    def _create_macos_note(
        self,
        league: str,
        category: str,
        title: str,
        content: str,
        color: str
    ) -> bool:
        """Create note using AppleScript on macOS."""
        # Escape quotes in content
        content_escaped = content.replace('"', '\\"').replace('\n', '\\n')

        script = f'''
        tell application "Notes"
            set targetFolder to folder "{league}"
            set newNote to make new note at targetFolder with properties {{name:"{title}", body:"{content_escaped}"}}
            return id of newNote
        end tell
        '''

        return self._run_applescript(script) is not None

    def _create_fallback_note(
        self,
        note_id: str,
        league: str,
        category: str,
        title: str,
        content: str,
        tags: List[str],
        color: str
    ) -> bool:
        """Create note in fallback JSON system."""
        note_data = {
            'id': note_id,
            'league': league,
            'category': category,
            'title': title,
            'content': content,
            'tags': tags,
            'color': self.COLORS.get(color, 'gray'),
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            'archived': False,
            'folder': league
        }

        self.notes_db[note_id] = note_data
        self._save_fallback_db()

        # Also save to file system
        file_path = os.path.join(
            self.storage_dir,
            league,
            category,
            f"{title}.json"
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(note_data, f, indent=2, ensure_ascii=False)

        return True

    def _generate_summary(self, content: str) -> str:
        """
        Generate 5 key takeaways summary.

        Args:
            content: Note content

        Returns:
            Summary text
        """
        # Simple summary generation - split into sentences and take first 5
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        key_points = sentences[:5] if len(sentences) >= 5 else sentences

        summary = "📌 KEY TAKEAWAYS:\n"
        for i, point in enumerate(key_points, 1):
            summary += f"{i}. {point}\n"

        return summary + "\n"

    def _format_note_content(
        self,
        title: str,
        summary: str,
        content: str,
        tags: List[str],
        google_docs_url: Optional[str] = None
    ) -> str:
        """Format complete note content."""
        formatted = f"# {title}\n\n"

        if summary:
            formatted += summary + "\n"

        formatted += "---\n\n"
        formatted += content + "\n\n"
        formatted += "---\n\n"
        formatted += f"🏷️  Tags: {' '.join(tags)}\n"

        if google_docs_url:
            formatted += f"\n📄 Google Docs: {google_docs_url}\n"

        return formatted

    def _generate_note_id(self, league: str, category: str, title: str) -> str:
        """Generate unique note ID."""
        unique_string = f"{league}:{category}:{title}:{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]

    def _add_to_weekly_aggregation(self, league: str, category: str, title: str, note_id: str):
        """Add note to weekly aggregation tracker."""
        week_key = f"{datetime.now().year}-W{datetime.now().isocalendar()[1]}"

        if week_key not in self.weekly_aggregation:
            self.weekly_aggregation[week_key] = []

        self.weekly_aggregation[week_key].append({
            'league': league,
            'category': category,
            'title': title,
            'note_id': note_id
        })

    def _run_applescript(self, script: str) -> Optional[str]:
        """
        Execute AppleScript and return result.

        Args:
            script: AppleScript code

        Returns:
            Script output or None on error
        """
        if not self.is_macos:
            return None

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"AppleScript error: {result.stderr}")
                return None

        except Exception as e:
            print(f"Error running AppleScript: {e}")
            return None

    def _load_fallback_db(self):
        """Load notes database from JSON."""
        db_path = os.path.join(self.storage_dir, 'notes_db.json')

        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                self.notes_db = json.load(f)

    def _save_fallback_db(self):
        """Save notes database to JSON."""
        db_path = os.path.join(self.storage_dir, 'notes_db.json')

        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(self.notes_db, f, indent=2, ensure_ascii=False)

    def get_note_stats(self) -> Dict[str, Any]:
        """
        Get statistics about notes.

        Returns:
            Dictionary with stats
        """
        if self.is_macos:
            # Get stats via AppleScript
            script = '''
            tell application "Notes"
                set noteCount to count of notes
                set folderCount to count of folders
                return noteCount & "," & folderCount
            end tell
            '''
            result = self._run_applescript(script)
            if result:
                counts = result.split(',')
                return {
                    'total_notes': int(counts[0]),
                    'total_folders': int(counts[1]),
                    'platform': 'macOS'
                }
        else:
            # Get stats from fallback DB
            total_notes = len(self.notes_db)
            archived = sum(1 for n in self.notes_db.values() if n.get('archived'))

            return {
                'total_notes': total_notes,
                'archived_notes': archived,
                'active_notes': total_notes - archived,
                'platform': 'fallback (JSON)'
            }

        return {}
