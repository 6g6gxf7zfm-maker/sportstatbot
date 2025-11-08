# Quick Start Guide - SportStatBot Cursor Dashboard

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Node.js 18 or higher (`node --version`)
- ✅ Python 3.8 or higher (`python --version`)
- ✅ npm or yarn (`npm --version`)

## Installation

### Step 1: Install Frontend Dependencies

```bash
cd cursor-dashboard
npm install
```

This installs all React, TypeScript, and UI dependencies (~2 minutes).

### Step 2: Install Backend Dependencies

```bash
cd cursor-dashboard/backend
pip install -r requirements.txt
```

This installs Flask and Python dependencies (~1 minute).

### Step 3: Configure Environment

```bash
# In cursor-dashboard directory
cp .env.example .env
```

Edit `.env` and add your API keys (optional for demo):
```env
VITE_API_URL=http://localhost:8000
ESPN_API_KEY=your_key_here  # Optional
ODDS_API_KEY=your_key_here  # Optional
```

## Running the Dashboard

### Option 1: Run Both Servers (Recommended)

**Terminal 1 - Backend API**:
```bash
cd cursor-dashboard/backend
python api_server.py
```

You should see:
```
Starting SportStatBot API Server...
Dashboard will be available at http://localhost:3000
API running at http://localhost:8000
```

**Terminal 2 - Frontend**:
```bash
cd cursor-dashboard
npm run dev
```

You should see:
```
VITE v5.0.8  ready in 300 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Option 2: Quick Start Script

Create a startup script:

**start-dashboard.sh** (Mac/Linux):
```bash
#!/bin/bash
cd cursor-dashboard/backend && python api_server.py &
cd cursor-dashboard && npm run dev
```

**start-dashboard.bat** (Windows):
```batch
@echo off
start cmd /k "cd cursor-dashboard\backend && python api_server.py"
start cmd /k "cd cursor-dashboard && npm run dev"
```

## First Use

### 1. Open Dashboard
Navigate to `http://localhost:3000`

### 2. Select a League
Click on "NFL" (or any league) in the top navigation

### 3. Create Your First Story
**Method A - Command Palette**:
- Press `⌘K` (Mac) or `Ctrl+K` (Windows)
- Type "generate digest"
- Press Enter

**Method B - Template Picker**:
- The template modal should open automatically
- Click "Daily Digest"

### 4. Start Writing
The editor will open with:
- Your selected template
- Current league context
- AI co-author ready on the right
- Writing feedback panel available

### 5. Use AI Assistance
- Start typing your story
- Watch AI suggestions appear in right sidebar
- Click "Accept" to insert suggestions
- Or click "Generate Next Paragraph" for more

### 6. Export Your Story
When done:
- Click "Preview" to review
- Click "Export to Google Docs" (or)
- Click "Markdown" to download

## Testing the System

### Quick Test Checklist

✅ **Dashboard Loads**: `http://localhost:3000` shows the dashboard

✅ **League Switching**: Click different league tabs (NFL, NBA, etc.)

✅ **Command Palette**: Press `⌘K`, palette opens

✅ **Template Modal**: Create new story, template picker appears

✅ **Editor Works**: Type in the editor, text appears

✅ **Keyboard Shortcuts**: Try `⌘E` to expand paragraph

✅ **Sidebar Toggle**: Click "Hide/Show AI Co-Author"

✅ **Tabs Work**: Switch between Editor, Queue, Logs, History

## Common First-Time Issues

### Dashboard shows "Cannot connect to server"
**Problem**: Backend not running
**Fix**:
```bash
cd cursor-dashboard/backend
python api_server.py
```

### "Module not found" errors
**Problem**: Dependencies not installed
**Fix**:
```bash
cd cursor-dashboard
npm install
# and
cd backend
pip install -r requirements.txt
```

### Port 3000 or 8000 already in use
**Problem**: Another app using those ports
**Fix - Frontend**:
```bash
# Edit vite.config.ts, change port: 3000 to port: 3001
npm run dev
```

**Fix - Backend**:
```bash
# Edit api_server.py, change port=8000 to port=8001
# Also update .env: VITE_API_URL=http://localhost:8001
```

### API requests fail
**Problem**: CORS or API URL mismatch
**Fix**: Verify in `.env`:
```env
VITE_API_URL=http://localhost:8000
```
Restart frontend after changing.

## Next Steps

Now that you're running:

1. **Explore Features**: See [FEATURES.md](FEATURES.md) for detailed feature docs

2. **Customize**:
   - Add your own templates
   - Customize keyboard shortcuts
   - Adjust color scheme

3. **Configure APIs**:
   - Get ESPN API key for real data
   - Get The Odds API key for betting data
   - Set up Google Docs integration

4. **Learn Shortcuts**: See keyboard shortcuts in [FEATURES.md](FEATURES.md)

5. **Read Full Docs**: Check [README.md](README.md) for complete documentation

## Demo Workflow

Try this complete workflow:

### 1. Create NBA Digest (5 min)

```
1. Click "NBA" league tab
2. Press ⌘K, select "Generate Digest"
3. Wait for AI to suggest opening paragraph
4. Accept suggestion
5. Type additional context
6. Click "Generate Next Paragraph"
7. Review and edit
8. Preview and export
```

### 2. Explore Agent Logs (2 min)

```
1. Click "Agent Logs" tab
2. See what Fetcher/Analyzer did
3. Filter by agent type
4. Expand log entry to see data
```

### 3. Check Writing History (2 min)

```
1. Click "Writing History" tab
2. See your first story counted
3. View stats and charts
```

## Video Tutorials (Coming Soon)

- [ ] Dashboard Overview (3 min)
- [ ] Creating Your First Story (5 min)
- [ ] Using AI Co-Author (4 min)
- [ ] Export and Publishing (3 min)
- [ ] Advanced Features (8 min)

## Getting Help

### Resources
- **Full Documentation**: [README.md](README.md)
- **Feature Guide**: [FEATURES.md](FEATURES.md)
- **GitHub Issues**: Report bugs and request features

### Support Channels
- Email: support@sportstatbot.com
- Discord: [Coming Soon]
- Twitter: @sportstatbot

## What's Next?

After mastering the basics:

1. **Set up real API keys** for live sports data
2. **Configure Google Docs** export
3. **Customize templates** for your needs
4. **Create keyboard shortcuts** for your workflow
5. **Integrate with your CMS** via API

---

**Estimated Setup Time**: 5-10 minutes
**Skill Level**: Beginner-friendly
**Support**: Available 24/7

Happy writing! 🎉
