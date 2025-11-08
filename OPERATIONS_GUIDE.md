# 🔧 SportStatBot Operations Guide

Comprehensive guide for managing the SportStatBot data pipeline and operations system.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Systems](#core-systems)
4. [Configuration](#configuration)
5. [Daily Operations](#daily-operations)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Overview

SportStatBot includes a comprehensive operations system with:

- **Automated Data Pipeline** - Hourly refresh with incremental caching
- **Health Monitoring** - Track data freshness and API status
- **Error Recovery** - Automatic retry with exponential backoff
- **Rate Limiting** - API-friendly request management
- **Smart Throttling** - Event-based update frequency
- **Offline Mode** - Continue operating with cached data
- **Backup System** - Rolling backups to multiple destinations
- **Data Retention** - Automatic cleanup of old data

---

## Quick Start

### 1. Basic Health Check

```bash
python operations_manager.py --health-check
```

This shows:
- Current system health
- Data freshness heatmap
- Cache statistics
- API rate limit status

### 2. Run Daily Operations

```bash
python operations_manager.py --daily-ops
```

This performs:
- Generate daily digest report
- Cleanup old data
- Create backup
- Reset 24-hour counters

### 3. Interactive Mode

```bash
python operations_manager.py --interactive
```

Provides an interactive menu for all operations tasks.

### 4. Generate Master Report

```bash
python operations_manager.py --master-report
```

Creates a comprehensive report of all systems.

---

## Core Systems

### 🔄 Cache Manager

**Purpose:** Incremental caching to minimize API calls

**Features:**
- 7-day rolling cache by default
- Automatic diff detection
- Cache freshness tracking
- Configurable retention

**Usage:**
```python
from pipeline.cache_manager import CacheManager

cache = CacheManager()

# Get cached data (max 1 hour old)
data = cache.get('nfl', 'scoreboard', max_age_hours=1)

# Store new data
cache.set('nfl', 'scoreboard', fresh_data)

# Get cache statistics
stats = cache.get_cache_stats()
```

**Configuration:** `cache/` directory
**Retention:** 7 days (configurable)

---

### 🏥 Health Monitor

**Purpose:** Track staleness and health of each data source

**Features:**
- Per-beat status tracking
- Success rate monitoring
- Staleness detection
- Response time tracking

**Usage:**
```python
from pipeline.health_monitor import HealthMonitor

health = HealthMonitor()

# Record successful fetch
health.record_beat('nfl', 'scoreboard', success=True, response_time_ms=234)

# Record failed fetch
health.record_beat('nfl', 'scoreboard', success=False, error="API timeout")

# Get status
status = health.get_beat_status('nfl', 'scoreboard')

# Generate daily digest
report = health.generate_daily_digest()
```

**Status Indicators:**
- 🟢 Green: Fresh (< 1 hour old)
- 🟡 Yellow: Stale (1-24 hours)
- 🔴 Red: Critical (> 24 hours)

---

### 🔧 Error Recovery Bot

**Purpose:** Automatically retry failed API requests

**Features:**
- Exponential backoff (2s, 4s, 8s, 16s)
- Configurable max retries
- Recovery statistics
- Failure tracking

**Usage:**
```python
from pipeline.error_recovery import ErrorRecoveryBot

recovery = ErrorRecoveryBot(max_retries=3)

# Execute with automatic retry
result = recovery.execute_with_retry(
    api_function,
    arg1, arg2,
    operation_name="Fetch NFL Scores"
)

# Get recovery statistics
stats = recovery.get_recovery_stats()
```

---

### ⏱️ Rate Limiter

**Purpose:** Prevent API rate limit violations

**Features:**
- Per-API rate limits
- Burst protection
- Request tracking
- Automatic waiting

**Default Limits:**
- ESPN: 30/minute, 500/hour
- Odds API: 10/minute, 100/hour
- NHL API: 20/minute, 300/hour
- MLB API: 20/minute, 300/hour

**Usage:**
```python
from pipeline.rate_limiter import RateLimiter

limiter = RateLimiter()

# Check if request allowed
if limiter.check_rate_limit('espn'):
    # Make API request
    data = fetch_data()
    limiter.record_request('espn')

# Wait if needed (up to 60s)
if limiter.wait_if_needed('espn', max_wait_seconds=60):
    # Proceed with request
    data = fetch_data()
```

**Configuration:** `config/rate_limits.json`

---

### ✅ Schema Validator

**Purpose:** Validate data integrity on ingest

**Features:**
- Schema validation
- Data quality checks
- Completeness scoring
- Freshness validation

**Usage:**
```python
from pipeline.schema_validator import SchemaValidator

validator = SchemaValidator()

# Validate single item
result = validator.validate(data, 'scoreboard')

if result['valid']:
    print("Data is valid")
else:
    print(f"Errors: {result['errors']}")

# Quality check
quality = validator.check_data_quality(data, 'scoreboard')
print(f"Overall score: {quality['overall_score']}")
```

---

### 📡 Offline Mode

**Purpose:** Continue operating when APIs are unavailable

**Features:**
- Automatic fallback to cache
- Cache-first strategy option
- Configurable max cache age
- Available sports tracking

**Usage:**
```python
from pipeline.offline_mode import OfflineMode

offline = OfflineMode()

# Get data with offline support
data = offline.get_data(
    'nfl',
    'scoreboard',
    fetch_func=lambda: api.get_scoreboard('nfl')
)

# Force offline mode
offline.force_offline_mode(offline=True)

# Get available cached sports
sports = offline.get_available_cached_sports()
```

**Configuration:** `config/offline_mode.json`

---

### 🔑 Token Manager

**Purpose:** Manage API token rotation and load balancing

**Features:**
- Automatic token rotation
- Multiple tokens per API
- Load balancing strategies
- Usage tracking

**Usage:**
```python
from pipeline.token_manager import TokenManager

tokens = TokenManager()

# Get active token
api_key = tokens.get_token('odds_api')

# Add backup token
tokens.add_backup_token('odds_api', 'backup_key_here')

# Check token status
status = tokens.get_token_status('odds_api')
```

**Load Balancing Strategies:**
- `round_robin`: Rotate through tokens
- `random`: Random selection
- `least_used`: Use least-used token

---

### ⚡ Smart Throttling

**Purpose:** Adjust update frequency based on events

**Features:**
- Major event detection (Super Bowl, Finals, etc.)
- Game day adjustments
- Time-of-day optimization
- Automatic frequency scaling

**Major Events:**
- Super Bowl: 4x more frequent updates
- NBA Finals: 2x more frequent
- World Series: 2x more frequent
- Stanley Cup Finals: 2x more frequent
- March Madness: 1.6x more frequent

**Usage:**
```python
from pipeline.smart_throttling import SmartThrottling

throttle = SmartThrottling()

# Get current interval for sport
interval_seconds = throttle.get_interval('nfl', 'scoreboard')

# Get throttling status
status = throttle.get_throttling_status('nfl')
```

**Configuration:** `config/smart_throttling.json`

---

### 🗂️ Retention Policy

**Purpose:** Automatic cleanup of old data

**Features:**
- Configurable retention windows
- Category-based policies
- Archive before delete option
- Disk space management

**Default Retention:**
- Cache: 7-14 days
- Reports: 30 days
- Logs: 30-60 days
- Backups: 14-90 days

**Usage:**
```python
from pipeline.retention_policy import RetentionPolicy

retention = RetentionPolicy()

# Cleanup all old data
results = retention.cleanup_all()

# Cleanup specific category
results = retention.cleanup_cache()
results = retention.cleanup_reports()
results = retention.cleanup_logs()
```

**Configuration:** `config/retention_policy.json`

---

## Monitoring & Alerts

### Daily Health Digest

Automatically generated report showing:
- Overall system health
- Data freshness by sport
- Error recovery statistics
- Rate limit status
- Recommendations

**Generate manually:**
```bash
python operations_manager.py --health-check
```

### Freshness Heatmap

Visual representation of data freshness:
- 🟢 Green: Fresh (< 1 hour)
- 🟡 Yellow: Stale (1-24 hours)
- 🔴 Red: Critical (> 24 hours)
- ⚪ Gray: No data

**View heatmap:**
```python
from monitoring.heatmap_generator import FreshnessHeatmap

heatmap = FreshnessHeatmap()

# Text format
print(heatmap.render_text_heatmap())

# HTML format
heatmap.save_heatmap(format='html')
```

### Master Report

Comprehensive report including all systems:
```bash
python operations_manager.py --master-report
```

Includes:
- Health monitor status
- Recovery statistics
- Rate limit status
- Offline mode status
- Backup status
- Cloud sync status
- Token management
- Retention policy

---

## Backup & Recovery

### Local Backups

**Create backup:**
```python
from storage.backup_manager import BackupManager

backup = BackupManager()

# Create full backup
backup_path = backup.create_backup(
    include_data=True,
    include_reports=True,
    include_config=True
)

# List backups
backups = backup.list_backups('local')

# Restore from backup
backup.restore_backup(backup_path, target_dir='.')
```

**Configuration:**
- Location: `backups/`
- Retention: 14 backups or 7 days
- Auto-cleanup: Yes

### Cloud Sync

**AWS S3:**
```python
from storage.cloud_sync import CloudStorageSync

cloud = CloudStorageSync()

# Sync to S3
cloud.sync_to_s3('backups', s3_key='sportstatbot/backup.zip')

# Download from S3
cloud.download_from_s3('sportstatbot/backup.zip', 'restored_backup.zip')
```

**Configuration:** `config/cloud_storage.json`

**Google Cloud Storage:**
```python
# Sync to GCS
cloud.sync_to_gcs('backups', gcs_key='sportstatbot/backup.zip')
```

### iCloud Sync

Automatic sync to iCloud Drive folder:
- Path: `~/Library/Mobile Documents/com~apple~CloudDocs/SportStatBot`
- Auto-sync: Configurable
- No additional setup required

---

## Configuration

### Directory Structure

```
sportstatbot/
├── pipeline/              # Pipeline components
│   ├── cache_manager.py
│   ├── health_monitor.py
│   ├── error_recovery.py
│   ├── rate_limiter.py
│   ├── schema_validator.py
│   ├── offline_mode.py
│   ├── token_manager.py
│   ├── smart_throttling.py
│   └── retention_policy.py
├── monitoring/            # Monitoring & reporting
│   ├── report_generator.py
│   └── heatmap_generator.py
├── storage/              # Storage & backup
│   ├── backup_manager.py
│   ├── cloud_sync.py
│   └── sheets_bridge.py
├── config/               # Configuration files
│   ├── rate_limits.json
│   ├── offline_mode.json
│   ├── smart_throttling.json
│   ├── retention_policy.json
│   ├── cloud_storage.json
│   └── sheets_config.json
├── cache/                # Cached data
├── reports/              # Generated reports
├── backups/              # Local backups
├── monitoring/health/    # Health monitoring data
└── operations_manager.py # Main operations interface
```

### Environment Variables

Add to `.env`:
```bash
# API Keys
ODDS_API_KEY=your_api_key_here

# Slack Integration
SLACK_WEBHOOK_URL=your_webhook_url

# Timezone
REPORT_TIMEZONE=America/New_York
```

---

## Daily Operations

### Automated Hourly Refresh

Set up cron job for hourly data refresh:

```bash
# Edit crontab
crontab -e

# Add hourly refresh (on the hour)
0 * * * * cd /path/to/sportstatbot && python operations_manager.py --health-check >> logs/cron.log 2>&1
```

### Daily Maintenance

Run once daily (recommended: 2 AM):

```bash
# Daily operations at 2 AM
0 2 * * * cd /path/to/sportstatbot && python operations_manager.py --daily-ops >> logs/daily_ops.log 2>&1
```

This performs:
1. Generate daily digest
2. Cleanup old data
3. Create backup
4. Reset counters
5. Sync to cloud (if configured)

---

## Troubleshooting

### High Error Rate

**Symptom:** Many failed API requests

**Solutions:**
1. Check rate limits: `python operations_manager.py --interactive` → Option 9
2. Verify API keys in `.env`
3. Enable offline mode temporarily
4. Check error recovery report

### Stale Data

**Symptom:** Red/yellow indicators in heatmap

**Solutions:**
1. Check API status
2. Verify network connectivity
3. Check error logs: `logs/error.json`
4. Force cache refresh

### High Disk Usage

**Symptom:** Running out of disk space

**Solutions:**
1. Run cleanup: `python operations_manager.py --interactive` → Option 8
2. Adjust retention windows in `config/retention_policy.json`
3. Delete old backups manually
4. Enable cloud sync

### Cache Issues

**Symptom:** No cached data or cache misses

**Solutions:**
1. Check cache directory: `cache/`
2. Verify permissions
3. Check cache stats: `cache_manager.get_cache_stats()`
4. Clear and rebuild cache

### Backup Failures

**Symptom:** Backups not being created

**Solutions:**
1. Check disk space
2. Verify backup directory permissions
3. Check backup config: `config/backup_config.json`
4. Review backup report

---

## Advanced Features

### Google Sheets Integration

Sync data to Google Sheets for manual overrides:

1. Set up service account in Google Cloud Console
2. Download credentials JSON
3. Place in `config/google_sheets_credentials.json`
4. Configure spreadsheet ID in `config/sheets_config.json`
5. Use `GoogleSheetsbridge` class

### Load Balancing

Distribute requests across multiple API keys:

```python
from pipeline.token_manager import TokenManager

tokens = TokenManager()

# Add backup tokens
tokens.add_backup_token('odds_api', 'key2')
tokens.add_backup_token('odds_api', 'key3')

# Enable load balancing
tokens.config['load_balancing']['enabled'] = True
tokens.config['load_balancing']['strategy'] = 'round_robin'
```

### Custom Throttling

Add custom major events:

```python
from pipeline.smart_throttling import SmartThrottling

throttle = SmartThrottling()

# Add custom event
throttle.add_major_event(
    'custom_tournament',
    date_range=['07-15', '07-31'],
    multiplier=0.5,  # 2x more frequent
    duration_hours=8
)
```

---

## Best Practices

1. **Monitor Daily** - Check health digest every day
2. **Review Logs** - Scan error logs weekly
3. **Backup Regularly** - Enable daily backups
4. **Update Tokens** - Rotate API tokens quarterly
5. **Clean Up** - Run cleanup weekly
6. **Test Offline Mode** - Verify cache works
7. **Document Changes** - Note configuration updates

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run health check for diagnostics
3. Review error recovery report
4. Check system status JSON

---

## Version History

- **v2.0.0** - Complete operations system implementation
- **v1.0.0** - Initial SportStatBot release

---

**Happy Monitoring! 🚀**
