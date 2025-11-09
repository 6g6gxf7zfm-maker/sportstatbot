# Document Automation Quick Start

Get started with Google Docs and Apple Notes automation in 5 minutes!

## 📋 Prerequisites

- Python 3.8+
- Google Cloud account (free)
- macOS (optional, for full Apple Notes support)

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable these APIs:
   - Google Docs API
   - Google Drive API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Download the JSON file
5. Save as `credentials.json` in project root

### Step 3: Configure Environment

```bash
cp .env.example .env
```

The defaults work fine! Only customize if needed.

### Step 4: First Run

```bash
python example_document_automation.py
```

This will:
1. ✅ Open browser for Google authentication (one-time)
2. ✅ Create folder structure in Google Drive
3. ✅ Setup Apple Notes folders
4. ✅ Generate and publish sample sports content
5. ✅ Show you what's possible!

## 🎯 5-Minute Tutorial

### Publish Your First Report

```python
from document_managers import DocumentOrchestrator
from report_generator import SportsReportGenerator

# Setup
orchestrator = DocumentOrchestrator()
orchestrator.setup_all()

# Generate NFL report
report_gen = SportsReportGenerator()
nfl_data = report_gen._generate_sport_data('nfl')

# Publish to both Google Docs and Apple Notes
results = orchestrator.publish_sports_report(
    report_data=nfl_data,
    league='NFL',
    report_type='Digests'
)

# Done! Check your Google Drive and Apple Notes
print(f"Published to: {results['google_docs_url']}")
```

### What You Get

**In Google Drive:**
```
SportStatBot Reports/
├── Table of Contents (index with all your docs)
├── NFL/
│   ├── Digests/
│   │   └── NFL Digests - 2025-11-09.gdoc ✨
│   ├── Features/
│   ├── Previews/
│   └── Betting/
└── [Other leagues...]
```

**In Apple Notes:**
```
NFL/
├── Digests
│   └── NFL Digests - 2025-11-09 ✨
├── Features
├── Injuries
└── Betting
```

## 🎨 Customize

### Change Author Name

Edit `.env`:
```bash
DEFAULT_AUTHOR=Your Name Here
```

### Adjust Auto-Archive

Edit `.env`:
```bash
AUTO_ARCHIVE_DAYS=60  # Archive after 60 days instead of 30
```

### Disable Auto-Summary

Edit `.env`:
```bash
ENABLE_AUTO_SUMMARY=false
```

## 📖 Next Steps

- Read full guide: [DOCUMENT_AUTOMATION_GUIDE.md](DOCUMENT_AUTOMATION_GUIDE.md)
- Explore examples: [example_document_automation.py](example_document_automation.py)
- Automate with scheduler: See guide for integration with `scheduler.py`

## ❓ Troubleshooting

### "Authentication failed"

- Make sure `credentials.json` is in the project root
- Delete `token.pickle` and try again
- Check APIs are enabled in Google Cloud Console

### "No module named 'googleapiclient'"

```bash
pip install -r requirements.txt
```

### Apple Notes not working

- On macOS: Grant Terminal access to Notes in System Preferences
- On other OS: Uses JSON fallback automatically (still works!)

### Need help?

Check the full guide: [DOCUMENT_AUTOMATION_GUIDE.md](DOCUMENT_AUTOMATION_GUIDE.md)

---

**Ready to automate your sports content? Run the example and see it in action! 🚀**
