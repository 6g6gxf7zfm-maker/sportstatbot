"""Google Sheets integration bridge for manual overrides and quick edits."""
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


class GoogleSheetsbridge:
    """
    Bridge to Google Sheets for:
    - Manual data overrides
    - Quick edits without code changes
    - Collaborative data management
    - Configuration management
    - Permissions and access control
    """

    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize Google Sheets bridge.

        Args:
            credentials_file: Path to Google service account credentials JSON
        """
        self.credentials_file = credentials_file or "config/google_sheets_credentials.json"
        self.config_file = Path("config/sheets_config.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load sheets configuration."""
        default_config = {
            'enabled': False,
            'spreadsheet_id': '',
            'sheets': {
                'data_overrides': 'Data Overrides',
                'configuration': 'Configuration',
                'manual_edits': 'Manual Edits',
                'team_info': 'Team Information'
            },
            'sync_interval_minutes': 15,
            'allow_manual_overrides': True,
            'permissions': {
                'editors': [],
                'viewers': [],
                'admins': []
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)
                return {**default_config, **custom_config}
            except Exception as e:
                print(f"Error loading sheets config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save sheets configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving sheets config: {e}")

    def connect(self) -> bool:
        """
        Establish connection to Google Sheets.

        Returns:
            True if successful
        """
        if not self.config['enabled']:
            print("Google Sheets integration is disabled")
            return False

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            # Define required scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Load credentials
            if not Path(self.credentials_file).exists():
                print(f"❌ Credentials file not found: {self.credentials_file}")
                print("   Please download service account credentials from Google Cloud Console")
                return False

            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )

            # Connect to Google Sheets
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.config['spreadsheet_id'])

            print(f"✅ Connected to Google Sheets: {self.spreadsheet.title}")
            return True

        except ImportError:
            print("❌ gspread not installed. Install with: pip install gspread google-auth")
            return False

        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            return False

    def read_data_overrides(self) -> List[Dict]:
        """
        Read data overrides from Google Sheets.

        Returns:
            List of override dictionaries
        """
        try:
            sheet_name = self.config['sheets']['data_overrides']
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # Get all records
            records = worksheet.get_all_records()

            # Filter active overrides
            active_overrides = [
                record for record in records
                if record.get('active', '').lower() == 'true'
            ]

            return active_overrides

        except Exception as e:
            print(f"Error reading data overrides: {e}")
            return []

    def write_data_to_sheet(self, sheet_name: str, data: List[Dict],
                           headers: Optional[List[str]] = None) -> bool:
        """
        Write data to a Google Sheet.

        Args:
            sheet_name: Name of the sheet
            data: List of dictionaries to write
            headers: Optional list of headers (auto-detected if None)

        Returns:
            True if successful
        """
        try:
            # Get or create worksheet
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except:
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=len(data) + 100,
                    cols=20
                )

            if not data:
                return True

            # Determine headers
            if headers is None:
                headers = list(data[0].keys())

            # Prepare data for writing
            rows = [headers]
            for item in data:
                row = [item.get(header, '') for header in headers]
                rows.append(row)

            # Write data
            worksheet.update('A1', rows)

            print(f"✅ Wrote {len(data)} rows to sheet: {sheet_name}")
            return True

        except Exception as e:
            print(f"Error writing to sheet: {e}")
            return False

    def read_configuration(self) -> Dict:
        """
        Read configuration from Google Sheets.

        Returns:
            Configuration dictionary
        """
        try:
            sheet_name = self.config['sheets']['configuration']
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # Read key-value pairs
            records = worksheet.get_all_records()

            config = {}
            for record in records:
                key = record.get('key', '')
                value = record.get('value', '')

                if key:
                    # Try to parse JSON values
                    try:
                        config[key] = json.loads(value)
                    except:
                        config[key] = value

            return config

        except Exception as e:
            print(f"Error reading configuration: {e}")
            return {}

    def export_standings_to_sheets(self, sport: str, standings_data: Dict) -> bool:
        """
        Export standings data to Google Sheets.

        Args:
            sport: Sport identifier
            standings_data: Standings data to export

        Returns:
            True if successful
        """
        sheet_name = f"{sport.upper()} Standings"

        # Parse standings data into rows
        rows = []

        # This is a simplified example - actual implementation depends on data structure
        if 'children' in standings_data:
            for division in standings_data['children']:
                if 'standings' in division:
                    for entry in division['standings'].get('entries', []):
                        team = entry.get('team', {})
                        stats = entry.get('stats', [])

                        row = {
                            'Team': team.get('displayName', ''),
                            'Division': division.get('name', ''),
                            'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                        }

                        # Add stats
                        for stat in stats:
                            row[stat.get('displayName', '')] = stat.get('value', '')

                        rows.append(row)

        return self.write_data_to_sheet(sheet_name, rows)

    def export_scores_to_sheets(self, sport: str, scores_data: Dict) -> bool:
        """
        Export game scores to Google Sheets.

        Args:
            sport: Sport identifier
            scores_data: Scoreboard data to export

        Returns:
            True if successful
        """
        sheet_name = f"{sport.upper()} Recent Games"

        rows = []

        if 'events' in scores_data:
            for event in scores_data['events']:
                # Extract game information
                game_info = {
                    'Date': event.get('date', ''),
                    'Game': event.get('name', ''),
                    'Status': event.get('status', {}).get('type', {}).get('description', ''),
                    'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M')
                }

                # Add competition details
                if 'competitions' in event and event['competitions']:
                    comp = event['competitions'][0]

                    if 'competitors' in comp:
                        for competitor in comp['competitors']:
                            team_name = competitor.get('team', {}).get('displayName', '')
                            score = competitor.get('score', '')
                            home_away = 'Home' if competitor.get('homeAway') == 'home' else 'Away'

                            game_info[f'{home_away} Team'] = team_name
                            game_info[f'{home_away} Score'] = score

                rows.append(game_info)

        return self.write_data_to_sheet(sheet_name, rows)

    def manage_permissions(self, email: str, role: str = 'viewer') -> bool:
        """
        Manage spreadsheet permissions.

        Args:
            email: Email address to grant access
            role: Access role ('viewer', 'editor', 'writer')

        Returns:
            True if successful
        """
        try:
            # Map roles
            role_mapping = {
                'viewer': 'reader',
                'editor': 'writer',
                'writer': 'writer'
            }

            gspread_role = role_mapping.get(role, 'reader')

            # Share spreadsheet
            self.spreadsheet.share(
                email,
                perm_type='user',
                role=gspread_role,
                notify=True
            )

            print(f"✅ Granted {role} access to {email}")

            # Update config
            if role not in self.config['permissions']:
                self.config['permissions'][role + 's'] = []

            if email not in self.config['permissions'][role + 's']:
                self.config['permissions'][role + 's'].append(email)
                self._save_config()

            return True

        except Exception as e:
            print(f"Error managing permissions: {e}")
            return False

    def generate_sheets_report(self) -> str:
        """Generate Google Sheets status report."""
        report = []

        report.append("=" * 60)
        report.append("📊 GOOGLE SHEETS INTEGRATION STATUS")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        report.append("⚙️ Configuration:")
        report.append(f"  Enabled: {'✅' if self.config['enabled'] else '❌'}")

        if self.config['enabled']:
            report.append(f"  Spreadsheet ID: {self.config['spreadsheet_id']}")
            report.append(f"  Sync Interval: {self.config['sync_interval_minutes']} minutes")
            report.append(f"  Manual Overrides: {'✅' if self.config['allow_manual_overrides'] else '❌'}")

            report.append("\n  Configured Sheets:")
            for key, sheet_name in self.config['sheets'].items():
                report.append(f"    • {key}: {sheet_name}")

            report.append("\n  Permissions:")
            for role, users in self.config['permissions'].items():
                if users:
                    report.append(f"    {role.title()}: {len(users)} user(s)")

        else:
            report.append("\n  ℹ️ Enable Google Sheets integration in config/sheets_config.json")
            report.append("  ℹ️ Add service account credentials to config/google_sheets_credentials.json")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
