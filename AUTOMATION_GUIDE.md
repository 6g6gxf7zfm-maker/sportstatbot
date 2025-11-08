# SportStatBot Automation & Integration Guide

Complete guide to the automation and integration features of SportStatBot.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Setup](#setup)
4. [Dashboard](#dashboard)
5. [Workflows](#workflows)
6. [Integrations](#integrations)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)

## Overview

SportStatBot now includes a comprehensive automation framework that enables:

- **Automated Workflows**: Multi-step pipelines (Harvest → Beat → Copy → Export)
- **Task Queue Management**: Priority-based task scheduling with retry logic
- **Multi-Destination Export**: Publish to Google Docs, Apple Notes, PDF, and more
- **Smart Rate Limiting**: Automatic API quota management
- **Data Freshness Monitoring**: Auto-refresh stale data
- **Web Dashboard**: Control and monitor all automation features

## Features

### 1. Scheduler Dashboard

Control digest generation frequency per league:

```bash
# Start the dashboard
python dashboard/app.py
```

Access at: http://localhost:5000

Features:
- Real-time task monitoring
- Manual digest triggering
- Schedule configuration per sport
- System health monitoring

### 2. Multi-Step Workflows

Pre-defined workflow types:

#### Full Digest Workflow
```
Harvest → Beat → Copy → Export
```

- **Harvest**: Fetch fresh data from APIs
- **Beat**: Analyze and generate insights
- **Copy**: Format with templates
- **Export**: Publish to destinations

#### Quick Update Workflow
```
Harvest → Beat → Export
```

Skips formatting for faster updates.

### 3. Task Dependency Graph

Visualize workflow pipelines:

```python
from automation.dependency_graph import DependencyGraph
from automation.workflow_definitions import WorkflowDefinitions

# Create workflow
workflow = WorkflowDefinitions.create_full_digest_workflow('nfl')

# Generate dependency graph
graph = DependencyGraph.from_workflow(workflow)

# Export as Mermaid diagram
print(graph.to_mermaid())

# Or ASCII visualization
print(graph.to_ascii())
```

### 4. Google Docs Integration

Automated document creation and organization:

```python
from integrations.google_docs import GoogleDocsIntegration

# Initialize
docs = GoogleDocsIntegration(
    credentials_path='credentials.json',
    token_path='token.json'
)

# Authenticate
docs.authenticate()

# Create organized folder structure
folder_id = docs.get_or_create_folder(
    sport='nfl',
    date='2025-11-07',
    folder_type='digest'
)

# Create document
doc_info = docs.create_document(
    title='NFL Digest 2025-11-07',
    content='Your digest content here',
    folder_id=folder_id
)

print(f"Document created: {doc_info['url']}")
```

### 5. Apple Notes Automation

Create notes via AppleScript (macOS only):

```python
from integrations.apple_notes import AppleNotesIntegration

notes = AppleNotesIntegration()

# Create note with auto-organized folder
note_info = notes.create_note_with_auto_folder(
    title='NFL Digest',
    content='Your digest content',
    sport='nfl',
    note_type='digest'
)
```

### 6. Automatic Folder Naming

All exports use consistent naming: `{sport}_{date}_{type}`

Examples:
- `NFL_2025-11-07_digest`
- `NBA_2025-11-08_analysis`
- `MLB_2025-11-09_quick`

### 7. Auto-Cleanup

Archive old documents automatically:

```python
from exporters.cleanup_manager import CleanupManager

cleanup = CleanupManager()

# Set retention policy
cleanup.set_retention_policy('nfl', days=30)

# Run cleanup
stats = cleanup.cleanup_directory(
    directory=Path('reports/NFL'),
    sport='nfl',
    dry_run=False  # Set True to preview
)

print(f"Archived {stats['archived']} files")
```

### 8. Multi-Folder Export

Export same content to multiple destinations:

```python
from exporters.export_manager import ExportManager, GoogleDocsExporter, AppleNotesExporter, PDFExporter

manager = ExportManager()

# Register destinations
manager.register_destination('google_docs', GoogleDocsExporter(docs_integration))
manager.register_destination('apple_notes', AppleNotesExporter(notes_integration))
manager.register_destination('pdf', PDFExporter())

# Export to all destinations
content = {
    'title': 'NFL Digest 2025-11-07',
    'content': 'Your digest content',
    'metadata': {'sport': 'nfl', 'date': '2025-11-07'}
}

results = manager.export(content)
print(f"Exported to {results['summary']['successful']} destinations")
```

### 9. Email Notifications

Get notified when digests are ready:

```python
from integrations.email_notifier import EmailNotifier

notifier = EmailNotifier()

# Send digest ready notification
notifier.send_digest_ready_notification(
    to_emails=['user@example.com'],
    sport='nfl',
    digest_url='https://docs.google.com/...',
    metadata={'date': '2025-11-07'}
)

# Send error notification
notifier.send_error_notification(
    to_emails=['admin@example.com'],
    error_type='API Error',
    error_message='Rate limit exceeded',
    context={'api': 'ESPN', 'sport': 'nfl'}
)
```

### 10. Auto-Versioning

Automatic semantic versioning:

```python
from exporters.version_manager import VersionManager

vm = VersionManager()

# Generate versioned name
name = vm.generate_version_name(
    sport='nfl',
    date='2025-11-07',
    digest_type='Digest',
    auto_increment=True
)

print(name)  # NFL_Digest_2025-11-07_v1.0

# Next generation auto-increments
name2 = vm.generate_version_name(sport='nfl', date='2025-11-07')
print(name2)  # NFL_Digest_2025-11-07_v1.1
```

### 11. Template Syncing

Apply consistent styling (TODO):

```python
# Coming soon: Template management system
```

### 12. Cloud-Based Queue Manager

Priority-based task scheduling:

```python
from automation.task_queue import TaskQueue, TaskPriority

queue = TaskQueue(max_workers=5)
queue.start()

# Add high-priority task
task = queue.add_task(
    task_id='nfl_digest_001',
    name='NFL Digest',
    action=generate_digest_function,
    sport='nfl',
    priority=TaskPriority.HIGH
)

# Monitor queue
stats = queue.get_statistics()
print(f"Running: {stats['running']}, Queued: {stats['queued']}")
```

### 13. Retry Logic

Automatic retry with exponential backoff:

```python
from automation.workflow_engine import WorkflowStep

step = WorkflowStep(
    name='fetch_data',
    action=fetch_function,
    retry_count=3,  # Retry up to 3 times
    timeout=300
)

# Automatic retry: 2s, 4s, 8s delays
```

### 14. Data Freshness Monitoring

Auto-trigger re-harvest:

```python
from automation.freshness_monitor import FreshnessMonitor

monitor = FreshnessMonitor()

# Set threshold
monitor.set_threshold('nfl', minutes=15)

# Register callback
monitor.register_harvest_callback('nfl', harvest_nfl_data)

# Start monitoring
monitor.start_monitoring()

# Data older than 15 minutes will trigger auto re-harvest
```

### 15. Multi-Environment Support

Configure staging vs production:

```bash
# .env
ENVIRONMENT=production
GOOGLE_PARENT_FOLDER_ID=production_folder_id

# .env.staging
ENVIRONMENT=staging
GOOGLE_PARENT_FOLDER_ID=staging_folder_id
```

### 16. Manual Override Interface

Control via dashboard or API:

```python
# Pause workflow
POST /api/workflow/nfl_full_digest/pause

# Resume workflow
POST /api/workflow/nfl_full_digest/resume

# Force refresh
POST /api/freshness/nfl/refresh

# Rerun digest
POST /api/digest/run
{
  "sport": "nfl",
  "type": "full"
}
```

### 17. Smart Rate Limiting

Prevent API bans:

```python
from automation.rate_limiter import RateLimiter

limiter = RateLimiter()

# Configure limits
limiter.set_limit(
    api_name='espn',
    calls_per_minute=60,
    calls_per_hour=1000
)

# Make rate-limited call
result = limiter.make_call(
    api_name='espn',
    func=fetch_espn_data,
    sport='nfl'
)

# Check quota
status = limiter.get_quota_status('espn')
print(f"Used: {status['usage']['per_minute']['used']}/{status['usage']['per_minute']['limit']}")
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy and edit `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Email notifications
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAILS=recipient@example.com

# Google Docs
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json

# Automation
AUTO_CLEANUP_ENABLED=true
AUTO_CLEANUP_DAYS=30
DATA_FRESHNESS_CHECK_INTERVAL=300
```

### 3. Google Docs Setup

1. Enable Google Docs and Drive APIs in Google Cloud Console
2. Download OAuth credentials as `credentials.json`
3. Run authentication:

```python
from integrations.google_docs import GoogleDocsIntegration
docs = GoogleDocsIntegration()
docs.authenticate()  # Opens browser for OAuth
```

### 4. Start Dashboard

```bash
python dashboard/app.py
```

Access at: http://localhost:5000

## Dashboard

### Main Features

1. **System Status**: Monitor all services
2. **Task Queue**: View running/queued tasks
3. **Data Freshness**: Check data age per sport
4. **Rate Limits**: Monitor API quota usage
5. **Quick Actions**: Run digests manually
6. **Workflow Control**: Pause/resume workflows

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status |
| `/api/queue/status` | GET | Task queue statistics |
| `/api/queue/tasks` | GET | List tasks |
| `/api/digest/run` | POST | Run digest |
| `/api/workflow/run` | POST | Run workflow |
| `/api/freshness` | GET | Freshness report |
| `/api/rate-limits` | GET | Rate limit status |
| `/api/cleanup/run` | POST | Run cleanup |

## Workflows

### Creating Custom Workflows

```python
from automation.workflow_engine import Workflow, WorkflowStep

# Create workflow
workflow = Workflow(
    name='custom_workflow',
    description='My custom workflow'
)

# Add steps
step1 = WorkflowStep(
    name='step1',
    action=my_function,
    dependencies=[],
    retry_count=3
)

step2 = WorkflowStep(
    name='step2',
    action=my_other_function,
    dependencies=['step1']  # Runs after step1
)

workflow.add_step(step1)
workflow.add_step(step2)

# Execute
from automation.workflow_engine import WorkflowEngine
engine = WorkflowEngine()
engine.register_workflow(workflow)
result = engine.execute_workflow('custom_workflow')
```

## Configuration

### Retention Policies

```python
cleanup.retention_policies = {
    'nfl': 30,   # Keep 30 days
    'nba': 30,
    'mlb': 30,
    'nhl': 30,
    'mls': 14,
    'soccer': 14,
    'golf': 14
}
```

### Freshness Thresholds

```python
monitor.thresholds = {
    'nfl': 15,   # Re-harvest after 15 minutes
    'nba': 10,
    'mlb': 15,
    'nhl': 15
}
```

### Rate Limits

```python
limiter.default_limits = {
    'espn': {
        'calls_per_minute': 60,
        'calls_per_hour': 1000,
        'calls_per_day': 10000
    },
    'odds': {
        'calls_per_minute': 10,
        'calls_per_hour': 500,
        'calls_per_day': 5000
    }
}
```

## Troubleshooting

### Google Docs Authentication Issues

```bash
# Delete token and re-authenticate
rm token.json
python -c "from integrations.google_docs import GoogleDocsIntegration; GoogleDocsIntegration().authenticate()"
```

### Apple Notes Not Working

- Requires macOS
- Grant permissions in System Preferences
- Check AppleScript is enabled

### Rate Limit Errors

```python
# Check quota
status = limiter.get_quota_status('espn')
print(status)

# Reset if needed (use carefully!)
limiter.reset_quota('espn')
```

## Examples

### Complete Automation Pipeline

```python
from automation.workflow_definitions import WorkflowDefinitions
from automation.workflow_engine import WorkflowEngine
from exporters.export_manager import ExportManager
from integrations.email_notifier import EmailNotifier

# 1. Create workflow
workflow = WorkflowDefinitions.create_full_digest_workflow('nfl')

# 2. Execute workflow
engine = WorkflowEngine()
engine.register_workflow(workflow)
result = engine.execute_workflow(workflow.name)

# 3. Export results
manager = ExportManager()
# ... register exporters ...
export_result = manager.export(result['context']['copy']['content'])

# 4. Send notification
notifier = EmailNotifier()
notifier.send_digest_ready_notification(
    to_emails=['user@example.com'],
    sport='nfl',
    digest_url=export_result['results']['google_docs']['url']
)
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/sportstatbot/issues
- Documentation: See README.md and USAGE_GUIDE.md

## License

See LICENSE file for details.
