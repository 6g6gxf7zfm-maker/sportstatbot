"""API token rotation and management system."""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
import secrets


class TokenManager:
    """
    Manages API token rotation for security and rate limit distribution.
    Supports multiple API keys per service for load distribution.
    """

    def __init__(self, config_file: str = "config/token_config.json"):
        """
        Initialize token manager.

        Args:
            config_file: Path to token configuration file
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

        # Track token usage
        self.usage_tracker = {}

    def _load_config(self) -> Dict:
        """Load token configuration."""
        default_config = {
            'rotation_enabled': True,
            'rotation_interval_days': 90,
            'tokens': {
                'odds_api': {
                    'primary': os.getenv('ODDS_API_KEY', ''),
                    'backup': [],
                    'last_rotated': None,
                    'next_rotation': None
                },
                'espn': {
                    'primary': '',  # ESPN doesn't require auth
                    'backup': [],
                    'last_rotated': None,
                    'next_rotation': None
                }
            },
            'load_balancing': {
                'enabled': False,
                'strategy': 'round_robin'  # or 'random', 'least_used'
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    custom_config = json.load(f)

                # Merge configurations
                for key in default_config:
                    if key in custom_config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(custom_config[key])
                        else:
                            default_config[key] = custom_config[key]

                return default_config
            except Exception as e:
                print(f"Error loading token config: {e}")

        return default_config

    def _save_config(self) -> None:
        """Save token configuration (without sensitive data)."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Create safe config without actual tokens
            safe_config = {
                'rotation_enabled': self.config['rotation_enabled'],
                'rotation_interval_days': self.config['rotation_interval_days'],
                'load_balancing': self.config['load_balancing'],
                'tokens': {}
            }

            # Save metadata only
            for api_name, token_info in self.config['tokens'].items():
                safe_config['tokens'][api_name] = {
                    'has_primary': bool(token_info['primary']),
                    'backup_count': len(token_info['backup']),
                    'last_rotated': token_info['last_rotated'],
                    'next_rotation': token_info['next_rotation']
                }

            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)

        except Exception as e:
            print(f"Error saving token config: {e}")

    def get_token(self, api_name: str) -> Optional[str]:
        """
        Get active token for an API.

        Args:
            api_name: API name (odds_api, espn, etc.)

        Returns:
            Active API token or None
        """
        if api_name not in self.config['tokens']:
            return None

        token_info = self.config['tokens'][api_name]

        # Check if rotation is needed
        if self.config['rotation_enabled']:
            self._check_rotation(api_name)

        # Load balancing if enabled
        if self.config['load_balancing']['enabled'] and token_info['backup']:
            return self._get_balanced_token(api_name)

        # Return primary token
        return token_info['primary'] or None

    def _get_balanced_token(self, api_name: str) -> Optional[str]:
        """
        Get token using load balancing strategy.

        Args:
            api_name: API name

        Returns:
            Selected token
        """
        token_info = self.config['tokens'][api_name]
        strategy = self.config['load_balancing']['strategy']

        all_tokens = [token_info['primary']] + token_info['backup']
        all_tokens = [t for t in all_tokens if t]  # Remove empty tokens

        if not all_tokens:
            return None

        if api_name not in self.usage_tracker:
            self.usage_tracker[api_name] = {
                'current_index': 0,
                'usage_counts': {token: 0 for token in all_tokens}
            }

        tracker = self.usage_tracker[api_name]

        if strategy == 'round_robin':
            # Rotate through tokens
            token = all_tokens[tracker['current_index'] % len(all_tokens)]
            tracker['current_index'] += 1

        elif strategy == 'random':
            # Random selection
            import random
            token = random.choice(all_tokens)

        elif strategy == 'least_used':
            # Use least used token
            token = min(tracker['usage_counts'], key=tracker['usage_counts'].get)

        else:
            # Default to first token
            token = all_tokens[0]

        # Track usage
        if token in tracker['usage_counts']:
            tracker['usage_counts'][token] += 1

        return token

    def _check_rotation(self, api_name: str) -> None:
        """
        Check if token rotation is needed.

        Args:
            api_name: API name
        """
        token_info = self.config['tokens'][api_name]

        # Initialize rotation dates if not set
        if not token_info['next_rotation']:
            next_rotation = datetime.now() + timedelta(
                days=self.config['rotation_interval_days']
            )
            token_info['next_rotation'] = next_rotation.isoformat()
            return

        # Check if rotation is due
        next_rotation = datetime.fromisoformat(token_info['next_rotation'])

        if datetime.now() >= next_rotation:
            self._rotate_token(api_name)

    def _rotate_token(self, api_name: str) -> None:
        """
        Rotate API token.

        Args:
            api_name: API name
        """
        token_info = self.config['tokens'][api_name]

        if not token_info['backup']:
            print(f"⚠️ No backup tokens available for {api_name}")
            return

        # Rotate: primary -> backup, first backup -> primary
        old_primary = token_info['primary']
        new_primary = token_info['backup'][0]

        token_info['primary'] = new_primary
        token_info['backup'] = token_info['backup'][1:] + [old_primary]

        # Update rotation dates
        token_info['last_rotated'] = datetime.now().isoformat()
        next_rotation = datetime.now() + timedelta(
            days=self.config['rotation_interval_days']
        )
        token_info['next_rotation'] = next_rotation.isoformat()

        print(f"🔄 Rotated API token for {api_name}")
        self._save_config()

    def add_backup_token(self, api_name: str, token: str) -> bool:
        """
        Add backup token for an API.

        Args:
            api_name: API name
            token: Backup token to add

        Returns:
            True if successful
        """
        if api_name not in self.config['tokens']:
            self.config['tokens'][api_name] = {
                'primary': '',
                'backup': [],
                'last_rotated': None,
                'next_rotation': None
            }

        if token not in self.config['tokens'][api_name]['backup']:
            self.config['tokens'][api_name]['backup'].append(token)
            self._save_config()
            print(f"✅ Added backup token for {api_name}")
            return True

        return False

    def remove_token(self, api_name: str, token: str) -> bool:
        """
        Remove a token.

        Args:
            api_name: API name
            token: Token to remove

        Returns:
            True if successful
        """
        if api_name not in self.config['tokens']:
            return False

        token_info = self.config['tokens'][api_name]

        if token_info['primary'] == token:
            # Promote backup to primary if available
            if token_info['backup']:
                token_info['primary'] = token_info['backup'].pop(0)
            else:
                token_info['primary'] = ''

            self._save_config()
            return True

        elif token in token_info['backup']:
            token_info['backup'].remove(token)
            self._save_config()
            return True

        return False

    def get_token_status(self, api_name: str) -> Dict:
        """
        Get token status for an API.

        Args:
            api_name: API name

        Returns:
            Status dictionary
        """
        if api_name not in self.config['tokens']:
            return {
                'api': api_name,
                'status': 'not_configured',
                'has_primary': False,
                'backup_count': 0
            }

        token_info = self.config['tokens'][api_name]

        status = {
            'api': api_name,
            'status': 'active' if token_info['primary'] else 'missing',
            'has_primary': bool(token_info['primary']),
            'backup_count': len(token_info['backup']),
            'rotation_enabled': self.config['rotation_enabled']
        }

        if token_info['last_rotated']:
            last_rotated = datetime.fromisoformat(token_info['last_rotated'])
            status['last_rotated'] = last_rotated.strftime('%Y-%m-%d')

        if token_info['next_rotation']:
            next_rotation = datetime.fromisoformat(token_info['next_rotation'])
            status['next_rotation'] = next_rotation.strftime('%Y-%m-%d')
            days_until = (next_rotation - datetime.now()).days
            status['days_until_rotation'] = max(0, days_until)

        return status

    def generate_token_report(self) -> str:
        """Generate token management status report."""
        report = []

        report.append("=" * 60)
        report.append("🔑 API TOKEN MANAGEMENT")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        report.append("⚙️ Configuration:")
        report.append(f"  Rotation Enabled: {'✅' if self.config['rotation_enabled'] else '❌'}")
        report.append(f"  Rotation Interval: {self.config['rotation_interval_days']} days")
        report.append(f"  Load Balancing: {'✅' if self.config['load_balancing']['enabled'] else '❌'}")

        if self.config['load_balancing']['enabled']:
            report.append(f"  Strategy: {self.config['load_balancing']['strategy']}")

        report.append("")
        report.append("🔐 API Tokens:")

        for api_name in self.config['tokens'].keys():
            status = self.get_token_status(api_name)

            status_emoji = '✅' if status['has_primary'] else '❌'
            report.append(f"\n  {status_emoji} {api_name.upper()}:")
            report.append(f"    Status: {status['status']}")

            if status['backup_count'] > 0:
                report.append(f"    Backup Tokens: {status['backup_count']}")

            if 'last_rotated' in status:
                report.append(f"    Last Rotated: {status['last_rotated']}")

            if 'next_rotation' in status:
                report.append(
                    f"    Next Rotation: {status['next_rotation']} "
                    f"({status['days_until_rotation']} days)"
                )

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
