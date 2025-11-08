# ⚡ Operations Quick Start

## 🚀 Getting Started (30 seconds)

```bash
# 1. Run health check
python operations_manager.py --health-check

# 2. Interactive mode
python operations_manager.py --interactive

# 3. Daily operations
python operations_manager.py --daily-ops
```

---

## 📊 Common Tasks

### Check System Health
```bash
python operations_manager.py --health-check
```
Shows: health status, freshness heatmap, cache stats

### Generate Reports
```bash
python operations_manager.py --master-report
```
Creates comprehensive system report

### Create Backup
```python
from storage.backup_manager import BackupManager
BackupManager().create_backup()
```

### Cleanup Old Data
```python
from pipeline.retention_policy import RetentionPolicy
RetentionPolicy().cleanup_all()
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Health check | `--health-check` |
| Daily ops | `--daily-ops` |
| Master report | `--master-report` |
| Interactive | `--interactive` |

---

## 📡 Status Indicators

| Icon | Meaning | Age |
|------|---------|-----|
| 🟢 | Fresh | < 1 hour |
| 🟡 | Stale | 1-24 hours |
| 🔴 | Critical | > 24 hours |
| ⚪ | No data | N/A |

---

## 🔧 Troubleshooting

**High error rate?**
→ Check rate limits: Interactive menu → Option 9

**Stale data?**
→ Run health check, verify API status

**Disk full?**
→ Run cleanup: Interactive menu → Option 8

**Backup failed?**
→ Check disk space and permissions

---

## 📁 Key Files

- `operations_manager.py` - Main operations interface
- `OPERATIONS_GUIDE.md` - Complete documentation
- `config/` - All configuration files
- `reports/monitoring/` - Generated reports
- `cache/` - Cached data
- `backups/` - Local backups

---

## ⚙️ Configuration Files

- `config/rate_limits.json` - API rate limits
- `config/offline_mode.json` - Offline mode settings
- `config/smart_throttling.json` - Event-based throttling
- `config/retention_policy.json` - Data retention
- `config/cloud_storage.json` - Cloud sync settings
- `config/sheets_config.json` - Google Sheets integration

---

## 🔄 Automation

### Hourly Health Check
```bash
crontab -e
# Add: 0 * * * * cd /path/to/sportstatbot && python operations_manager.py --health-check
```

### Daily Operations (2 AM)
```bash
# Add: 0 2 * * * cd /path/to/sportstatbot && python operations_manager.py --daily-ops
```

---

## 💡 Pro Tips

1. Run health check daily
2. Enable auto-cleanup
3. Set up cloud backups
4. Monitor disk space
5. Review error logs weekly

---

For full documentation, see **OPERATIONS_GUIDE.md**
