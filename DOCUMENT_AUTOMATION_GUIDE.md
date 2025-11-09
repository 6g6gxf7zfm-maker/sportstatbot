# Document & Folder Automation Guide

Complete guide for using SportStatBot's Google Docs and Apple Notes automation features.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Setup](#setup)
4. [Google Docs Integration](#google-docs-integration)
5. [Apple Notes Integration](#apple-notes-integration)
6. [Document Orchestrator](#document-orchestrator)
7. [Usage Examples](#usage-examples)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)

---

## Overview

SportStatBot now includes powerful document automation that automatically creates, organizes, and manages sports content across Google Docs and Apple Notes platforms.

### Key Capabilities

- **Automatic folder/tab organization** by league and category
- **Cross-platform publishing** to both Google Docs and Apple Notes
- **Intelligent metadata** including dates, tags, author info
- **Automatic summaries** with key takeaways
- **Document archival** for old content
- **PDF export** capabilities
- **Cross-linking** between platforms
- **Offline sync** support for Apple Notes

---

## Features

### Google Docs Features ✅

✅ **Per-League Folders**
- Automatically creates folders for: NFL, NBA, MLB, NHL, MLS, INTL, Golf
- Each league has 4 subfolders: Digests, Features, Previews, Betting

✅ **Auto-Tagging**
- Date tags: YYYY-MM-DD format
- League and category tags
- Custom metadata properties

✅ **Table of Contents**
- Linked index document
- Automatic updates when new docs are created
- Organized by league and category

✅ **Document Headers**
- League logo (emoji)
- Timestamp
- Author (configurable)
- Word count
- Professional formatting

✅ **Collaboration**
- Inline comments supported
- Sharing and permissions

✅ **Document Locking**
- Lock published docs from edits
- Maintain published versions

✅ **Auto-Sync & Backup**
- Automatic Google Drive sync
- Version history

✅ **Archival**
- "Story Archive" folder
- Moves docs older than X days (configurable)

✅ **PDF Export**
- Batch export to PDF
- Print-ready formatting

✅ **Cross-References**
- Link documents together
- "See also: Week 5 Recap" style references

### Apple Notes Features ✅

✅ **Per-League Tabs/Folders**
- NFL, NBA, MLB, NHL, MLS, INTL, Golf
- Sub-tabs: Digests, Features, Injuries, Betting

✅ **Smart Tagging**
- Date tags: YYYY-MM-DD
- Keywords: #injuries #digest #week10
- League-specific tags

✅ **Auto-Summarization**
- 5 key takeaways at top of each note
- Quick reference for readers

✅ **Color Labels**
- Red: Urgent
- Blue: Published
- Yellow: Draft
- Gray: Archived
- Orange: Betting
- Purple: Injury

✅ **Weekly Aggregation**
- "This Week in Sports" master note
- Combines all week's content
- Cross-links to individual notes

✅ **Cross-Platform Linking**
- Links Apple Notes to Google Docs URLs
- Seamless navigation between platforms

✅ **Archival**
- "Past Weeks" folder
- Automatic archival of old notes

✅ **PDF Export**
- Export notes to PDF
- Batch export support

✅ **Offline Mode**
- Cache 30 days of notes locally
- Works without internet connection
- Auto-sync when online

✅ **Cross-Platform Support**
- Full AppleScript integration on macOS
- JSON-based fallback on other platforms
- Seamless experience across systems

---

## Setup

### Prerequisites

1. **Python 3.8+**
2. **Google Cloud Account** (for Google Docs/Drive API)
3. **macOS** (optional, for full Apple Notes integration)

### Installation

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client` - Google Docs/Drive API
- `google-auth-httplib2` - Google authentication
- `google-auth-oauthlib` - OAuth 2.0 flow

2. **Google Cloud Setup**

a. Go to [Google Cloud Console](https://console.cloud.google.com/)

b. Create a new project or select existing

c. Enable APIs:
   - Google Docs API
   - Google Drive API

d. Create OAuth 2.0 Credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download the JSON file

e. Save as `credentials.json` in project root

3. **Configure Environment**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Google API credentials
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.pickle
GOOGLE_DOCS_ROOT_FOLDER=SportStatBot Reports

# Apple Notes storage (fallback mode)
APPLE_NOTES_STORAGE_DIR=./apple_notes_data

# Automation settings
AUTO_ARCHIVE_DAYS=30
ENABLE_AUTO_SUMMARY=true
DEFAULT_AUTHOR=SportStatBot EIC
OFFLINE_CACHE_DAYS=30
```

4. **First-Time Authentication**

Run the example script:

```bash
python example_document_automation.py
```

This will:
- Open browser for Google authentication
- Save token for future use
- Create folder structures
- Run demonstration workflow

---

## Google Docs Integration

### Folder Structure

When initialized, creates this structure in Google Drive:

```
SportStatBot Reports/
├── Table of Contents (index document)
├── Story Archive/
├── NFL/
│   ├── Digests/
│   ├── Features/
│   ├── Previews/
│   └── Betting/
├── NBA/
│   ├── Digests/
│   ├── Features/
│   ├── Previews/
│   └── Betting/
├── MLB/
│   └── ...
├── NHL/
│   └── ...
├── MLS/
│   └── ...
├── INTL/
│   └── ...
└── Golf/
    └── ...
```

### Creating Documents

```python
from document_managers import GoogleDocsManager

# Initialize
google_docs = GoogleDocsManager()
google_docs.authenticate()
google_docs.setup_league_folders()

# Create document
doc_id = google_docs.create_document(
    title="NFL Week 10 Digest",
    content="Your content here...",
    league="NFL",
    category="Digests",
    metadata={
        'author': 'John Doe',
        'word_count': 1500
    }
)

print(f"Document URL: https://docs.google.com/document/d/{doc_id}")
```

### Document Headers

Each document automatically includes:

```
🏈 NFL - Week 10 Digest
────────────────────────────────────────────────────────
📅 November 09, 2025 at 03:45 PM
✍️  Author: SportStatBot EIC
📊 Word Count: 1500
────────────────────────────────────────────────────────

[Your content here...]
```

### Locking Documents

Prevent edits after publishing:

```python
google_docs.lock_document(doc_id)
```

### Archiving Old Documents

Move documents older than 30 days to archive:

```python
archived_count = google_docs.archive_old_documents(days_old=30)
print(f"Archived {archived_count} documents")
```

### PDF Export

Export documents in batch:

```python
doc_ids = ['doc1_id', 'doc2_id', 'doc3_id']
exported_files = google_docs.export_to_pdf(doc_ids, output_dir='./exports')

for file in exported_files:
    print(f"Exported: {file}")
```

### Cross-Referencing

Link related documents:

```python
google_docs.add_cross_reference(
    doc_id="current_doc_id",
    reference_doc_id="related_doc_id",
    reference_title="Week 5 Recap"
)
```

This adds: "See also: Week 5 Recap" (linked) to the document.

---

## Apple Notes Integration

### Platform Support

- **macOS**: Full integration via AppleScript
- **Other OS**: JSON-based fallback system

The API automatically detects your platform and uses the appropriate backend.

### Folder Structure

Creates this organization in Apple Notes:

```
NFL/
├── Digests
├── Features
├── Injuries
└── Betting

NBA/
├── Digests
├── Features
├── Injuries
└── Betting

[... other leagues ...]

Past Weeks/ (archive)
```

### Creating Notes

```python
from document_managers import AppleNotesManager

# Initialize
apple_notes = AppleNotesManager()
apple_notes.create_folder_structure()

# Create note
note_id = apple_notes.create_note(
    league='NFL',
    category='Digests',
    title='NFL Week 10 Digest',
    content='Your content here...',
    tags=['#nfl', '#week10', '#digest'],
    color='published',
    auto_summary=True,
    google_docs_url='https://docs.google.com/document/d/xyz'
)
```

### Note Format

Each note includes:

```
# NFL Week 10 Digest

📌 KEY TAKEAWAYS:
1. Chiefs maintain lead in AFC
2. Bills bounce back with dominant win
3. Injury concerns for 49ers
4. Playoff picture taking shape
5. Rookie quarterbacks shine

---

[Your full content here...]

---

🏷️  Tags: 2025-11-09 #nfl #digests #week10
📄 Google Docs: https://docs.google.com/document/d/xyz
```

### Color Coding

Set note colors for organization:

```python
apple_notes.update_note_color(note_id, 'urgent')  # Red
apple_notes.update_note_color(note_id, 'published')  # Blue
apple_notes.update_note_color(note_id, 'draft')  # Yellow
```

### Weekly Aggregation

Create weekly summary note:

```python
summary_id = apple_notes.create_weekly_aggregation()
```

This creates a master note linking all the week's content:

```
# This Week in Sports - Week 45, 2025

Generated: November 09, 2025

## NFL

### Digests
- NFL Week 10 Digest
- AFC Playoff Race Update

### Previews
- Chiefs vs Bills Preview

### Injuries
- Week 10 Injury Report

...
```

### Offline Sync

Cache notes for offline access:

```python
apple_notes.setup_offline_sync(cache_days=30)
```

---

## Document Orchestrator

The `DocumentOrchestrator` provides unified interface for both platforms.

### Setup Both Platforms

```python
from document_managers import DocumentOrchestrator

orchestrator = DocumentOrchestrator()

# Setup both platforms at once
status = orchestrator.setup_all()

# Check status
if status['google_docs']:
    print("✓ Google Docs ready")
if status['apple_notes']:
    print("✓ Apple Notes ready")
```

### Publish to Both Platforms

```python
results = orchestrator.publish_content(
    title="NBA Injury Report",
    content="Latest injuries and their impact...",
    league="NBA",
    category="Injuries",
    to_google_docs=True,
    to_apple_notes=True,
    metadata={
        'author': 'SportStatBot',
        'tags': ['#nba', '#injuries']
    }
)

# Access created documents
print(f"Google Doc: {results['google_docs_url']}")
print(f"Apple Note: {results['apple_notes_id']}")
```

### Publish Sports Reports

Automatically publish generated reports:

```python
from report_generator import SportsReportGenerator

# Generate report
report_gen = SportsReportGenerator()
nfl_data = report_gen._generate_sport_data('nfl')

# Publish to both platforms
results = orchestrator.publish_sports_report(
    report_data=nfl_data,
    league='NFL',
    report_type='Digests'
)
```

### Archive Across Platforms

```python
results = orchestrator.archive_old_content(days_old=30)

print(f"Google Docs archived: {results['google_docs']}")
print(f"Apple Notes archived: {results['apple_notes']}")
```

### Batch PDF Export

```python
exported = orchestrator.export_batch_pdf(
    platform='both',  # or 'google_docs' or 'apple_notes'
    output_dir='./exports'
)

print(f"Exported {len(exported['google_docs_files'])} Google Docs")
print(f"Exported {len(exported['apple_notes_files'])} Apple Notes")
```

---

## Usage Examples

### Example 1: Daily Digest Automation

```python
from document_managers import DocumentOrchestrator
from report_generator import SportsReportGenerator
from datetime import datetime

orchestrator = DocumentOrchestrator()
orchestrator.setup_all()

report_gen = SportsReportGenerator()

# Generate daily digest for all active leagues
for league in ['nfl', 'nba', 'mlb', 'nhl']:
    print(f"Generating {league.upper()} digest...")

    # Get sport data
    data = report_gen._generate_sport_data(league)

    if data:
        # Publish to both platforms
        orchestrator.publish_sports_report(
            report_data=data,
            league=league.upper(),
            report_type='Digests'
        )

# Create weekly summary
orchestrator.create_weekly_summary()

print("✓ Daily digests published!")
```

### Example 2: Game Preview Publication

```python
# Create detailed game preview
preview_content = """
# Chiefs vs Bills - Sunday Night Football

## Game Info
- Date: November 12, 2025
- Time: 8:20 PM ET
- Location: Arrowhead Stadium

## Storylines
1. Battle of elite quarterbacks
2. AFC playoff implications
3. Revenge game for Buffalo

## Key Matchups
- Mahomes vs Bills defense
- Bills O-line vs Chiefs pass rush
- Special teams battle

## Prediction
Chiefs 31, Bills 28 - Expect overtime thriller
"""

results = orchestrator.publish_content(
    title="Chiefs vs Bills - Sunday Night Football Preview",
    content=preview_content,
    league='NFL',
    category='Previews',
    metadata={
        'author': 'SportStatBot',
        'tags': ['#nfl', '#preview', '#chiefs', '#bills', '#snf']
    }
)

# Lock the Google Doc after publishing
if 'google_docs_id' in results:
    orchestrator.lock_published_documents([results['google_docs_id']])
```

### Example 3: Automated Weekly Workflow

```python
import schedule
import time

def weekly_cleanup():
    """Run weekly maintenance tasks."""
    orchestrator = DocumentOrchestrator()

    # Archive old content
    print("Archiving old content...")
    orchestrator.archive_old_content(days_old=30)

    # Create weekly summary
    print("Creating weekly summary...")
    orchestrator.create_weekly_summary()

    # Export to PDF for backup
    print("Exporting to PDF...")
    orchestrator.export_batch_pdf(platform='both')

    # Setup offline sync
    print("Syncing for offline access...")
    orchestrator.setup_offline_mode()

    print("✓ Weekly cleanup complete!")

# Schedule weekly cleanup every Sunday at midnight
schedule.every().sunday.at("00:00").do(weekly_cleanup)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Example 4: Custom Report with Cross-Links

```python
from document_managers import GoogleDocsManager

google_docs = GoogleDocsManager()
google_docs.authenticate()

# Create main report
main_doc_id = google_docs.create_document(
    title="NFL Week 10 Complete Analysis",
    content="Comprehensive breakdown of Week 10...",
    league="NFL",
    category="Features"
)

# Create supplementary injury report
injury_doc_id = google_docs.create_document(
    title="NFL Week 10 Injury Impact Analysis",
    content="How injuries affected Week 10 outcomes...",
    league="NFL",
    category="Features"
)

# Cross-reference them
google_docs.add_cross_reference(
    doc_id=main_doc_id,
    reference_doc_id=injury_doc_id,
    reference_title="Week 10 Injury Impact Analysis"
)

google_docs.add_cross_reference(
    doc_id=injury_doc_id,
    reference_doc_id=main_doc_id,
    reference_title="Week 10 Complete Analysis"
)
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_PATH` | `credentials.json` | Path to Google OAuth credentials |
| `GOOGLE_TOKEN_PATH` | `token.pickle` | Path to save/load auth token |
| `GOOGLE_DOCS_ROOT_FOLDER` | `SportStatBot Reports` | Root folder name in Google Drive |
| `APPLE_NOTES_STORAGE_DIR` | `./apple_notes_data` | Fallback storage directory |
| `AUTO_ARCHIVE_DAYS` | `30` | Days before auto-archival |
| `ENABLE_AUTO_SUMMARY` | `true` | Enable automatic summaries |
| `DEFAULT_AUTHOR` | `SportStatBot EIC` | Default author name |
| `OFFLINE_CACHE_DAYS` | `30` | Days to cache for offline access |

### Customizing Folder Structure

Edit `document_managers/google_docs_manager.py`:

```python
# Add custom subfolder
SUBFOLDERS = ['Digests', 'Features', 'Previews', 'Betting', 'Analysis']

# Add custom league
LEAGUES = {
    'NFL': {'color': '#013369', 'emoji': '🏈'},
    'CUSTOM': {'color': '#FF0000', 'emoji': '⚡'},  # Your league
}
```

---

## Troubleshooting

### Google Docs Issues

**Problem: "Authentication failed"**

Solution:
1. Verify `credentials.json` is in correct location
2. Delete `token.pickle` and re-authenticate
3. Check that APIs are enabled in Google Cloud Console

**Problem: "Quota exceeded"**

Solution:
- Google APIs have daily quotas
- Wait 24 hours or request quota increase
- Batch operations to reduce API calls

**Problem: "Folder not found"**

Solution:
```python
# Clear cache and recreate
google_docs.folder_cache = {}
google_docs.setup_league_folders()
```

### Apple Notes Issues

**Problem: "AppleScript execution failed" (macOS)**

Solution:
1. Grant Terminal/Python access to Notes in System Preferences
2. Check Notes app is installed and running
3. Verify AppleScript syntax is supported on your macOS version

**Problem: "Fallback mode on macOS"**

Solution:
- Check `platform.system()` returns 'Darwin'
- Verify AppleScript is not disabled
- Check Notes app permissions

**Problem: "Notes not syncing"**

Solution:
```python
# Force sync
apple_notes.setup_offline_sync(cache_days=30)
```

### General Issues

**Problem: "Module not found"**

Solution:
```bash
pip install -r requirements.txt
```

**Problem: "Permission denied"**

Solution:
```bash
chmod +x example_document_automation.py
```

---

## Advanced Features

### Custom Document Templates

Create custom templates for different content types:

```python
def create_injury_report_template(google_docs, league, injuries):
    """Custom template for injury reports."""

    content = "# Injury Report\n\n"
    content += "## Questionable\n"
    for injury in injuries:
        if injury['status'] == 'questionable':
            content += f"- {injury['player']}: {injury['injury']}\n"

    content += "\n## Out\n"
    for injury in injuries:
        if injury['status'] == 'out':
            content += f"- {injury['player']}: {injury['injury']}\n"

    return google_docs.create_document(
        title=f"{league} Injury Report",
        content=content,
        league=league,
        category="Injuries"
    )
```

### Automated Scheduling

Integrate with existing `scheduler.py`:

```python
from scheduler import ReportScheduler
from document_managers import DocumentOrchestrator

scheduler = ReportScheduler()
orchestrator = DocumentOrchestrator()

# Add document automation to schedule
scheduler.schedule_task(
    func=orchestrator.archive_old_content,
    schedule_time="00:00",
    kwargs={'days_old': 30}
)
```

---

## API Reference

See individual module documentation:
- `document_managers/google_docs_manager.py`
- `document_managers/apple_notes_manager.py`
- `document_managers/document_orchestrator.py`

---

## Support

For issues or questions:
1. Check this guide
2. Review example scripts
3. Check code documentation
4. Open GitHub issue

---

## License

Part of SportStatBot project. See main README for license information.
