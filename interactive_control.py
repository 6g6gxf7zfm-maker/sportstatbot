#!/usr/bin/env python3
"""Interactive control interface for SportStatBot."""
import sys
import argparse
from typing import List, Optional

from user_interface import (
    ControlPanel,
    Dashboard,
    ExperimentMode,
    UserPreferences
)
from user_interface.workflow_archive import WorkflowArchive
import config


class InteractiveControl:
    """Interactive control interface for SportStatBot."""

    def __init__(self):
        """Initialize the interactive control interface."""
        self.control_panel = ControlPanel()
        self.dashboard = Dashboard()
        self.experiment_mode = ExperimentMode()
        self.archive = WorkflowArchive()
        self.preferences = UserPreferences()
        self.running = False

    def start_interactive_mode(self):
        """Start interactive command-line mode."""
        self.running = True
        print("\n🎮 SportStatBot Interactive Control Panel")
        print("Type 'help' for available commands or 'exit' to quit\n")

        while self.running:
            try:
                # Get user input
                user_input = input("sportstat> ").strip()

                if not user_input:
                    continue

                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # Handle commands
                self.handle_command(command, args)

            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit")
                continue
            except EOFError:
                print("\n")
                break

        print("\n👋 Goodbye!\n")

    def handle_command(self, command: str, args: List[str]):
        """
        Handle a user command.

        Args:
            command: Command name
            args: Command arguments
        """
        # Control Panel commands
        if command in ['generate-all', 'export-24h', 'toggle', 'priority', 'window', 'length', 'status']:
            result = self.control_panel.execute_command(command, args)
            print(result)

        # Dashboard commands
        elif command == 'dashboard':
            hours = int(args[0]) if args else 24
            print(self.dashboard.render_full_dashboard(hours))

        elif command == 'compact':
            hours = int(args[0]) if args else 24
            print(self.dashboard.render_compact_dashboard(hours))

        elif command == 'alerts':
            alerts = self.dashboard.get_alerts()
            if alerts:
                print("\n⚠️  ALERTS:")
                for alert in alerts:
                    print(f"  {alert}")
                print()
            else:
                print("\n✅ No alerts - all systems nominal!\n")

        # Experiment Mode commands
        elif command == 'experiment':
            self.enter_experiment_mode(args)

        elif command == 'list-experiments':
            status = args[0] if args else None
            experiments = self.experiment_mode.list_experiments(status)
            if experiments:
                print("\n🔬 EXPERIMENTS:")
                for exp in experiments:
                    status_icon = {
                        'draft': '📝',
                        'active': '🟢',
                        'completed': '✅'
                    }.get(exp['status'], '❓')
                    print(f"  {status_icon} {exp['id']} - {exp['name']} ({exp['runs']} runs)")
                print()
            else:
                print("\nNo experiments found\n")

        # Archive commands
        elif command == 'archive':
            self.handle_archive_command(args)

        elif command == 'list-workflows':
            workflows = self.archive.list_workflows()
            if workflows:
                print("\n📚 ARCHIVED WORKFLOWS:")
                for wf in workflows:
                    print(f"  • {wf}")
                print()
            else:
                print("\nNo archived workflows\n")

        # Manual notes
        elif command == 'note':
            if not args:
                print("Usage: note <text> [league]")
                return

            note_text = ' '.join(args[:-1]) if len(args) > 1 and args[-1] in config.SPORTS_CONFIG else ' '.join(args)
            league = args[-1] if len(args) > 1 and args[-1] in config.SPORTS_CONFIG else None

            if self.control_panel.manual_insert_note(note_text, league):
                print(f"✅ Note added{' for ' + league if league else ''}")
            else:
                print("❌ Failed to add note")

        elif command == 'notes':
            league = args[0] if args else None
            notes = self.control_panel.get_pending_notes(league)

            if notes:
                print("\n📝 PENDING NOTES:")
                for note in notes:
                    league_tag = f"[{note['league']}]" if note.get('league') else "[ALL]"
                    print(f"  {league_tag} {note['timestamp'][:16]}: {note['note']}")
                print()
            else:
                print("\nNo pending notes\n")

        # Help
        elif command == 'help':
            self.show_help()

        # Exit
        elif command == 'exit' or command == 'quit':
            self.running = False

        else:
            print(f"❌ Unknown command: {command}")
            print("Type 'help' for available commands")

    def enter_experiment_mode(self, args: List[str]):
        """Enter experiment mode interface."""
        if not args:
            print("\nExperiment Mode Commands:")
            print("  experiment create <name> - Create new experiment")
            print("  experiment activate <id> - Activate experiment")
            print("  experiment show <id> - Show experiment details")
            print("  experiment compare <id1> <id2> - Compare experiments")
            return

        subcommand = args[0]

        if subcommand == 'create':
            if len(args) < 2:
                print("Usage: experiment create <name>")
                return

            name = ' '.join(args[1:])
            print(f"\nCreating experiment: {name}")
            print("Enter description:")
            description = input("  > ")
            print("Enter prompt variation (or 'default' to use current):")
            prompt = input("  > ")

            exp_id = self.experiment_mode.create_experiment(
                name=name,
                description=description,
                prompt_variation=prompt
            )
            print(f"\n✅ Created experiment: {exp_id}\n")

        elif subcommand == 'activate':
            if len(args) < 2:
                print("Usage: experiment activate <id>")
                return

            exp_id = args[1]
            if self.experiment_mode.activate_experiment(exp_id):
                print(f"✅ Activated experiment: {exp_id}")
            else:
                print(f"❌ Failed to activate experiment: {exp_id}")

        elif subcommand == 'show':
            if len(args) < 2:
                print("Usage: experiment show <id>")
                return

            exp_id = args[1]
            summary = self.experiment_mode.get_experiment_summary(exp_id)
            print(summary)

        elif subcommand == 'compare':
            if len(args) < 3:
                print("Usage: experiment compare <id1> <id2>")
                return

            comparison = self.experiment_mode.compare_with_baseline(args[1], args[2])
            print("\n🔬 EXPERIMENT COMPARISON:")
            print(f"Experiment: {comparison['experiment']}")
            print(f"Baseline: {comparison['baseline']}")
            print(f"\nDifferences:")
            for diff in comparison.get('differences', []):
                change = diff['change_percent']
                symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"  {symbol} {diff['metric']}: {diff['experiment_value']} vs {diff['baseline_value']} ({change:+.1f}%)")
            print()

    def handle_archive_command(self, args: List[str]):
        """Handle archive-related commands."""
        if not args:
            print("\nArchive Commands:")
            print("  archive list <workflow> - List versions")
            print("  archive show <workflow> [version] - Show version notes")
            print("  archive export <workflow> - Export workflow")
            return

        subcommand = args[0]

        if subcommand == 'list':
            if len(args) < 2:
                print("Usage: archive list <workflow>")
                return

            workflow = args[1]
            versions = self.archive.get_workflow_versions(workflow)

            if versions:
                print(f"\n📚 VERSIONS: {workflow}")
                for v in reversed(versions):
                    status = "🗄️ " if v.get('archived') else "✅ "
                    print(f"  {status}{v['version_id']} - {v['timestamp'][:16]} by {v['author']}")
                print()
            else:
                print(f"\nNo versions found for '{workflow}'\n")

        elif subcommand == 'show':
            if len(args) < 2:
                print("Usage: archive show <workflow> [version]")
                return

            workflow = args[1]
            version = args[2] if len(args) > 2 else None
            notes = self.archive.get_version_notes(workflow, version)
            print(notes)

        elif subcommand == 'export':
            if len(args) < 2:
                print("Usage: archive export <workflow>")
                return

            workflow = args[1]
            export_path = self.archive.export_workflow(workflow)

            if export_path:
                print(f"✅ Exported to: {export_path}")
            else:
                print("❌ Export failed")

    def show_help(self):
        """Display help information."""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    SPORTSTATBOT INTERACTIVE CONTROL                        ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 CONTROL PANEL COMMANDS:
  generate-all              Generate digest for all enabled leagues
  export-24h                Export reports from last 24 hours
  toggle <league>           Enable/disable a league
  priority <leagues...>     Set priority ranking (e.g., 'nfl nba mlb')
  window <days>             Set data window (3, 5, or 10 days)
  length <level>            Set output length (brief/medium/in-depth)
  status                    Show current status

📈 DASHBOARD COMMANDS:
  dashboard [hours]         Show full dashboard (default: 24h)
  compact [hours]           Show compact dashboard
  alerts                    Show system alerts

🔬 EXPERIMENT MODE:
  experiment create <name>  Create new experiment
  experiment activate <id>  Activate an experiment
  experiment show <id>      Show experiment details
  experiment compare <id1> <id2>  Compare two experiments
  list-experiments [status] List experiments (draft/active/completed)

📚 ARCHIVE COMMANDS:
  archive list <workflow>   List workflow versions
  archive show <workflow>   Show version notes
  archive export <workflow> Export workflow to file
  list-workflows            List all archived workflows

📝 MANUAL NOTES:
  note <text> [league]      Add a manual editor note
  notes [league]            Show pending notes

ℹ️  GENERAL:
  help                      Show this help
  exit                      Exit interactive mode

For more information, see the documentation or use individual command help.
        """
        print(help_text)


def main():
    """Main entry point for interactive control."""
    parser = argparse.ArgumentParser(
        description='SportStatBot Interactive Control Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--command',
        '-c',
        help='Execute a single command and exit'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show status and exit'
    )

    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Show dashboard and exit'
    )

    args = parser.parse_args()

    interface = InteractiveControl()

    # Handle non-interactive modes
    if args.status:
        print(interface.control_panel.display_status())
        return 0

    if args.dashboard:
        print(interface.dashboard.render_full_dashboard())
        return 0

    if args.command:
        # Execute single command
        parts = args.command.split()
        command = parts[0]
        cmd_args = parts[1:] if len(parts) > 1 else []
        interface.handle_command(command, cmd_args)
        return 0

    # Start interactive mode
    try:
        interface.start_interactive_mode()
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        return 130


if __name__ == '__main__':
    sys.exit(main())
