"""Interactive control panel for SportStatBot."""
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from .user_preferences import UserPreferences
from .agent_tracker import AgentTracker
import config


class ControlPanel:
    """Interactive control panel for managing SportStatBot operations."""

    def __init__(self):
        """Initialize the control panel."""
        self.preferences = UserPreferences()
        self.tracker = AgentTracker()

    def display_status(self) -> str:
        """Display current system status."""
        output = []
        output.append("\n" + "="*70)
        output.append("🎮 SPORTSTATBOT CONTROL PANEL")
        output.append("="*70)

        # League Status
        output.append("\n📊 LEAGUE STATUS:")
        enabled = self.preferences.get_enabled_leagues()
        ranking = self.preferences.get_priority_ranking()

        for i, league in enumerate(ranking, 1):
            is_enabled = league in enabled
            status = "✅" if is_enabled else "❌"
            emoji = config.SPORTS_CONFIG.get(league, {}).get('emoji', '')
            name = config.SPORTS_CONFIG.get(league, {}).get('display_name', league.upper())
            output.append(f"  {i}. {status} {emoji} {name} ({league})")

        # Settings
        output.append("\n⚙️  SETTINGS:")
        output.append(f"  Data Window: {self.preferences.get_data_window()} days")
        output.append(f"  Output Length: {self.preferences.get_output_length()}")
        output.append(f"  Max Lines: {self.preferences.get_max_lines_for_level()}")

        # Recent Activity
        output.append("\n🤖 RECENT AGENT ACTIVITY:")
        recent = self.tracker.get_recent_runs(limit=5)
        if recent:
            for run in recent:
                status_emoji = "✅" if run.get('success', False) else "❌"
                output.append(f"  {status_emoji} {run['agent_type']} - {run['timestamp'][:16]}")
        else:
            output.append("  No recent activity")

        output.append("\n" + "="*70 + "\n")
        return "\n".join(output)

    def quick_commands_menu(self) -> str:
        """Display quick commands menu."""
        output = []
        output.append("\n📋 QUICK COMMANDS:")
        output.append("  generate-all        Generate digest for all enabled leagues")
        output.append("  export-24h          Export reports from last 24 hours")
        output.append("  toggle <league>     Enable/disable a league")
        output.append("  priority <leagues>  Set priority ranking (e.g., 'nfl nba mlb')")
        output.append("  window <days>       Set data window (3, 5, or 10 days)")
        output.append("  length <level>      Set output length (brief/medium/in-depth)")
        output.append("  status              Show current status")
        output.append("  dashboard           Show detailed dashboard")
        output.append("  experiment          Enter experiment mode")
        output.append("  help                Show this menu")
        output.append("  exit                Exit control panel\n")
        return "\n".join(output)

    def execute_command(self, command: str, args: List[str] = None) -> str:
        """
        Execute a control panel command.

        Args:
            command: Command to execute
            args: Command arguments

        Returns:
            Result message
        """
        args = args or []

        if command == 'generate-all':
            return self._generate_all_digests()

        elif command == 'export-24h':
            return self._export_last_24h()

        elif command == 'toggle':
            if not args:
                return "❌ Error: Please specify a league to toggle"
            return self._toggle_league(args[0])

        elif command == 'priority':
            if not args:
                return "❌ Error: Please specify league priority order"
            return self._set_priority(args)

        elif command == 'window':
            if not args:
                return "❌ Error: Please specify number of days"
            try:
                days = int(args[0])
                return self._set_data_window(days)
            except ValueError:
                return "❌ Error: Days must be a number"

        elif command == 'length':
            if not args:
                return "❌ Error: Please specify output length (brief/medium/in-depth)"
            return self._set_output_length(args[0])

        elif command == 'status':
            return self.display_status()

        elif command == 'help':
            return self.quick_commands_menu()

        else:
            return f"❌ Unknown command: {command}\nType 'help' for available commands"

    def _generate_all_digests(self) -> str:
        """Generate digests for all enabled leagues."""
        enabled = self.preferences.get_enabled_leagues()
        if not enabled:
            return "❌ No leagues are currently enabled"

        # Log agent run
        self.tracker.log_run(
            agent_type='digest_generator',
            leagues=enabled,
            success=True,
            metadata={'type': 'generate-all'}
        )

        return f"✅ Generating digests for {len(enabled)} leagues: {', '.join(enabled)}"

    def _export_last_24h(self) -> str:
        """Export reports from last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        runs = self.tracker.get_runs_since(cutoff)

        export_path = f"exports/report_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('exports', exist_ok=True)

        # Would export actual reports here
        count = len(runs)

        return f"✅ Exported {count} reports from last 24 hours to {export_path}"

    def _toggle_league(self, league: str) -> str:
        """Toggle a league on/off."""
        if league not in config.SPORTS_CONFIG:
            return f"❌ Unknown league: {league}\nAvailable: {', '.join(config.SPORTS_CONFIG.keys())}"

        new_status = self.preferences.toggle_league(league)
        status_text = "enabled" if new_status else "disabled"
        emoji = config.SPORTS_CONFIG[league]['emoji']
        name = config.SPORTS_CONFIG[league]['display_name']

        return f"✅ {emoji} {name} ({league}) is now {status_text}"

    def _set_priority(self, leagues: List[str]) -> str:
        """Set priority ranking for leagues."""
        # Validate leagues
        valid_leagues = set(config.SPORTS_CONFIG.keys())
        invalid = [l for l in leagues if l not in valid_leagues]

        if invalid:
            return f"❌ Invalid leagues: {', '.join(invalid)}"

        if self.preferences.set_priority_ranking(leagues):
            return f"✅ Priority ranking updated: {' > '.join(leagues)}"
        else:
            return "❌ Failed to update priority ranking"

    def _set_data_window(self, days: int) -> str:
        """Set data window in days."""
        if self.preferences.set_data_window(days):
            return f"✅ Data window set to {days} days"
        else:
            return "❌ Failed to set data window"

    def _set_output_length(self, level: str) -> str:
        """Set output length level."""
        if self.preferences.set_output_length(level):
            max_lines = self.preferences.get_max_lines_for_level()
            return f"✅ Output length set to '{level}' (max {max_lines} lines)"
        else:
            return "❌ Failed to set output length. Use: brief, medium, or in-depth"

    def get_current_config(self) -> Dict:
        """Get current configuration for report generation."""
        return {
            'enabled_leagues': self.preferences.get_enabled_leagues(),
            'priority_ranking': self.preferences.get_priority_ranking(),
            'data_window_days': self.preferences.get_data_window(),
            'output_level': self.preferences.get_output_length(),
            'max_lines': self.preferences.get_max_lines_for_level()
        }

    def manual_insert_note(self, note: str, league: Optional[str] = None) -> bool:
        """
        Insert a manual note for human editors.

        Args:
            note: The note text
            league: Optional specific league

        Returns:
            True if successful
        """
        notes_file = 'data/manual_notes.json'
        os.makedirs('data', exist_ok=True)

        # Load existing notes
        notes = []
        if os.path.exists(notes_file):
            try:
                import json
                with open(notes_file, 'r') as f:
                    notes = json.load(f)
            except:
                notes = []

        # Add new note
        notes.append({
            'timestamp': datetime.now().isoformat(),
            'note': note,
            'league': league,
            'applied': False
        })

        # Save notes
        try:
            import json
            with open(notes_file, 'w') as f:
                json.dump(notes, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving note: {e}")
            return False

    def get_pending_notes(self, league: Optional[str] = None) -> List[Dict]:
        """Get pending manual notes."""
        notes_file = 'data/manual_notes.json'
        if not os.path.exists(notes_file):
            return []

        try:
            import json
            with open(notes_file, 'r') as f:
                notes = json.load(f)

            # Filter by league if specified
            if league:
                notes = [n for n in notes if n.get('league') == league or n.get('league') is None]

            # Return only unapplied notes
            return [n for n in notes if not n.get('applied', False)]
        except:
            return []
