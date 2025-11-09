"""Configuration settings for SportStatBot."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ODDS_API_KEY = os.getenv('ODDS_API_KEY', '')

# Slack Configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')

# Report Settings
REPORT_TIMEZONE = os.getenv('REPORT_TIMEZONE', 'America/New_York')

# Document Management Settings
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
GOOGLE_TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', 'token.pickle')
GOOGLE_DOCS_ROOT_FOLDER = os.getenv('GOOGLE_DOCS_ROOT_FOLDER', 'SportStatBot Reports')
APPLE_NOTES_STORAGE_DIR = os.getenv('APPLE_NOTES_STORAGE_DIR', './apple_notes_data')

# Document Automation Settings
AUTO_ARCHIVE_DAYS = int(os.getenv('AUTO_ARCHIVE_DAYS', '30'))
ENABLE_AUTO_SUMMARY = os.getenv('ENABLE_AUTO_SUMMARY', 'true').lower() == 'true'
DEFAULT_AUTHOR = os.getenv('DEFAULT_AUTHOR', 'SportStatBot EIC')
OFFLINE_CACHE_DAYS = int(os.getenv('OFFLINE_CACHE_DAYS', '30'))

# API Endpoints
ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports"
NHL_API_BASE = "https://statsapi.web.nhl.com/api/v1"
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Sport configurations
SPORTS_CONFIG = {
    'nfl': {
        'espn_league': 'football/nfl',
        'display_name': 'NFL',
        'emoji': '🏈',
        'season_active': True
    },
    'nba': {
        'espn_league': 'basketball/nba',
        'display_name': 'NBA',
        'emoji': '🏀',
        'season_active': True
    },
    'mlb': {
        'espn_league': 'baseball/mlb',
        'display_name': 'MLB',
        'emoji': '⚾',
        'season_active': True
    },
    'nhl': {
        'espn_league': 'hockey/nhl',
        'display_name': 'NHL',
        'emoji': '🏒',
        'season_active': True
    },
    'mls': {
        'espn_league': 'soccer/usa.1',
        'display_name': 'MLS',
        'emoji': '⚽',
        'season_active': True
    },
    'soccer': {
        'espn_league': 'soccer/eng.1',  # Premier League as default
        'display_name': 'Premier League',
        'emoji': '⚽',
        'season_active': True
    },
    'golf': {
        'espn_league': 'golf/pga',
        'display_name': 'PGA Tour',
        'emoji': '⛳',
        'season_active': True
    }
}
