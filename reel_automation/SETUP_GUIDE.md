# Sports Reel Automation - Complete Setup Guide

This guide will walk you through setting up the entire Sports Reel Automation system from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Database Setup](#database-setup)
4. [Frontend Setup](#frontend-setup)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version  # Should be 18+
   npm --version
   ```

3. **FFmpeg** (for video processing)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

   Verify installation:
   ```bash
   ffmpeg -version
   ```

### Required Accounts

1. **Anthropic Claude API**
   - Sign up: [console.anthropic.com](https://console.anthropic.com)
   - Create an API key
   - Cost: ~$0.01-0.03 per caption (very affordable)

2. **Supabase** (Database)
   - Sign up: [supabase.com](https://supabase.com)
   - Free tier is sufficient to start
   - You'll need: Project URL and API keys

## Backend Setup

### Step 1: Install Python Dependencies

```bash
cd reel_automation/backend
pip install -r requirements.txt
```

**What gets installed:**
- `opencv-python` - Video analysis
- `ffmpeg-python` - Video processing
- `anthropic` - Claude API client
- `supabase` - Database client
- `schedule` - Task scheduling
- `requests` - HTTP requests
- And other utilities

**Troubleshooting:**
- If opencv fails: Try `pip install opencv-python-headless`
- If ffmpeg-python fails: Ensure FFmpeg is installed first
- Use a virtual environment: `python -m venv venv && source venv/bin/activate`

### Step 2: Configure Environment Variables

```bash
cd reel_automation
cp .env.example .env
```

Edit `.env`:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...  # Get from console.anthropic.com
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...  # From Supabase project settings

# Optional
OUTPUT_DIRECTORY=~/Desktop/reels_ready
PROCESSING_TEMP_DIR=/tmp/reel_processing
```

### Step 3: Test Backend

```bash
cd reel_automation/backend
python -c "from config_loader import config; print('Config loaded:', config.sports)"
```

Should print your configured sports list.

## Database Setup

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and set:
   - **Project name**: sports-reel-automation
   - **Database password**: (save this securely)
   - **Region**: Choose closest to you
4. Wait for project to be created (~2 minutes)

### Step 2: Get API Credentials

1. Go to **Project Settings** → **API**
2. Copy:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: For frontend
   - **service_role key**: For backend (keep secret!)

### Step 3: Run Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `database/schema.sql`
4. Paste and click **Run**
5. Should see "Success. No rows returned"

### Step 4: Verify Tables

Go to **Table Editor** in Supabase dashboard. You should see:
- `reels`
- `posting_history`
- `performance_preferences`
- `posting_queue`
- `app_settings`

### Step 5: Test Database Connection

```bash
cd reel_automation/backend
python -c "from utils.supabase_client import db; print('DB connected:', db.client is not None)"
```

## Frontend Setup

### Step 1: Install Dependencies

```bash
cd reel_automation/frontend
npm install
```

This installs:
- Next.js 14
- React 18
- Supabase client
- Tailwind CSS
- UI components

### Step 2: Configure Environment

```bash
cp ../.env.example .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...  # Use the anon public key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Step 3: Test Frontend

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

You should see the dashboard (it will be empty initially).

## Configuration

### Step 1: Edit config.json

```bash
cd reel_automation/config
nano config.json  # or use your preferred editor
```

**Key settings to customize:**

```json
{
  "sports": ["NBA", "NFL", "MLB"],  // Your preferred sports
  "viral_score_threshold": 7,        // Higher = more selective
  "posts_per_day": 5,                // Your posting goal
  "caption_style": "hype",           // hype, analytical, funny, casual
  "output_directory": "~/Desktop/reels_ready"  // Where files save
}
```

### Step 2: Create Output Directory

```bash
mkdir -p ~/Desktop/reels_ready
```

This is where your processed reels will be saved.

## Testing

### Test 1: Configuration Loading

```bash
cd reel_automation/backend
python -c "from config_loader import config; print('Sports:', config.sports)"
```

### Test 2: Video Processor (without actual video)

```bash
python -c "from video_processing.video_processor import VideoProcessor; vp = VideoProcessor(); print('Video processor ready')"
```

### Test 3: Caption Generator

```bash
python -c "
from api_clients.caption_generator import CaptionGenerator
gen = CaptionGenerator()
result = gen.generate_caption(
    sport='NBA',
    teams=['Lakers', 'Celtics'],
    players=['LeBron James'],
    play_description='Game-winning three pointer',
    play_type='buzzer_beater'
)
print('Caption:', result['caption'][:100])
"
```

This should generate a caption using Claude API.

### Test 4: Full Bot Run (Test Mode)

```bash
cd reel_automation/backend
python reel_scheduler.py --test
```

This runs a test processing job. It may not find highlights if there are no recent games.

### Test 5: Frontend Dashboard

1. Start the dashboard: `cd frontend && npm run dev`
2. Visit [http://localhost:3000](http://localhost:3000)
3. Navigate through all pages:
   - Dashboard
   - Queue
   - Analytics
   - Settings

## Production Deployment

### Backend Deployment

#### Option 1: Run Locally 24/7

**macOS/Linux - Using screen:**
```bash
screen -S reel-bot
cd reel_automation/backend
python reel_scheduler.py
# Press Ctrl+A then D to detach
```

Reattach later: `screen -r reel-bot`

**macOS/Linux - Using systemd:**

Create service file:
```bash
sudo nano /etc/systemd/system/reel-bot.service
```

Content:
```ini
[Unit]
Description=Sports Reel Automation Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/home/yourusername/sportstatbot/reel_automation/backend
Environment=PATH=/home/yourusername/.local/bin:/usr/bin
ExecStart=/usr/bin/python3 reel_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable reel-bot
sudo systemctl start reel-bot
sudo systemctl status reel-bot
```

#### Option 2: Cloud Server (DigitalOcean, AWS, etc.)

1. Create a small server ($5-10/month)
2. Install Python, FFmpeg
3. Clone your code
4. Set up systemd service (as above)
5. Ensure output directory syncs to cloud (Dropbox, iCloud)

### Frontend Deployment

#### Vercel (Recommended - Free)

```bash
cd reel_automation/frontend
npm install -g vercel
vercel login
vercel
```

Follow prompts:
- Set up project
- Add environment variables in Vercel dashboard
- Deploy

Your dashboard will be live at `https://your-project.vercel.app`

#### Alternative: Netlify, Railway, or any Next.js host

All support Next.js 14 with similar setup.

## File Syncing for Phone Access

To access processed videos on your phone:

### Option 1: iCloud Drive

```bash
# Change output directory in config.json
"output_directory": "~/Library/Mobile Documents/com~apple~CloudDocs/reels_ready"
```

Videos automatically sync to iPhone.

### Option 2: Dropbox

```bash
"output_directory": "~/Dropbox/reels_ready"
```

### Option 3: Google Drive

Install Google Drive desktop app, then:
```bash
"output_directory": "~/Google Drive/reels_ready"
```

## Maintenance

### Daily
- Check scheduler is running: `systemctl status reel-bot`
- Review processed reels in dashboard

### Weekly
- Check API usage (Anthropic console)
- Review performance metrics
- Adjust viral score threshold if needed

### Monthly
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review and optimize popular sports
- Clean up old files (automatic at 3 AM)

## Troubleshooting

### Backend Not Processing

1. Check logs:
   ```bash
   journalctl -u reel-bot -f  # If using systemd
   ```

2. Test manually:
   ```bash
   cd backend
   python sports_reel_bot.py
   ```

3. Common issues:
   - **No games found**: Check if sports are in season
   - **API errors**: Verify API keys
   - **Video processing fails**: Check FFmpeg installation

### Frontend Not Loading Data

1. Check browser console for errors
2. Verify Supabase credentials in `.env.local`
3. Test Supabase connection:
   ```bash
   npm run dev
   # Check browser console
   ```

### Database Issues

1. Check Supabase dashboard is accessible
2. Verify schema was applied correctly
3. Check Row Level Security policies are set

## Next Steps

1. **Test with Real Game**: Wait for a live game and let the bot process
2. **Review Results**: Check dashboard for processed reels
3. **Refine Settings**: Adjust viral score threshold based on results
4. **Start Posting**: Download reels to phone and start posting
5. **Track Performance**: Update metrics in dashboard
6. **Optimize**: Let the system learn from your data

## Support

If you encounter issues:

1. Check the main README.md for common solutions
2. Review code comments in relevant files
3. Check API documentation:
   - [Anthropic Claude API Docs](https://docs.anthropic.com)
   - [Supabase Docs](https://supabase.com/docs)
   - [Next.js Docs](https://nextjs.org/docs)

---

**You're all set! 🚀**

Your automated sports reel creation system is ready to help you grow your Instagram account.
