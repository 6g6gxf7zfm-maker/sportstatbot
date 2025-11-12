# Quick Start Guide - Sports Reel Automation

Get up and running in 10 minutes!

## 1. Install Dependencies (5 minutes)

### Backend
```bash
cd reel_automation/backend
pip install -r requirements.txt
```

### Frontend
```bash
cd reel_automation/frontend
npm install
```

### FFmpeg
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## 2. Get API Keys (2 minutes)

### Anthropic Claude API
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create account and generate API key
3. Copy the key (starts with `sk-ant-`)

### Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Run `database/schema.sql` in SQL Editor
4. Copy URL and keys from Settings → API

## 3. Configure (1 minute)

```bash
cd reel_automation
cp .env.example .env
```

Edit `.env` and add:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

Also configure frontend:
```bash
cd frontend
cp ../.env.example .env.local
# Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY
```

## 4. Test (2 minutes)

### Test Backend
```bash
cd backend
python -c "from config_loader import config; print('✓ Config loaded')"
python -c "from api_clients.caption_generator import CaptionGenerator; print('✓ Caption generator ready')"
```

### Test Frontend
```bash
cd frontend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) - you should see the dashboard!

## 5. Run Your First Processing Job

```bash
cd backend
python reel_scheduler.py --test
```

This will attempt to fetch and process highlights. If there are no recent games, it will complete without creating reels (that's normal).

## Daily Usage

### Morning Routine
1. Open dashboard: [http://localhost:3000](http://localhost:3000)
2. Review overnight reels
3. Check viral scores
4. Copy captions for posting

### Posting
1. Download video to phone (via cloud sync)
2. Open Instagram
3. Create new Reel
4. Upload video
5. Paste caption
6. Post!

### Automation
To run continuously:
```bash
cd backend
python reel_scheduler.py
```

Leave this running (or set up as a service).

## File Locations

**Processed Reels:**
```
~/Desktop/reels_ready/
└── 2024-11-12/
    ├── NBA/
    │   ├── 1830_Lakers_Celtics_reel.mp4
    │   └── 1830_Lakers_Celtics_caption.txt
    └── posting_schedule.json
```

## Customization

Edit `config/config.json`:

```json
{
  "sports": ["NBA", "NFL", "MLB"],        // Your sports
  "viral_score_threshold": 7,             // Quality filter
  "posts_per_day": 5,                     // Target posts
  "caption_style": "hype"                 // Caption tone
}
```

## Troubleshooting

**No reels created?**
- Check if there are live games today
- Lower viral_score_threshold to 5 or 6
- Check logs for errors

**Captions not generating?**
- Verify ANTHROPIC_API_KEY is correct
- Check you have API credits

**Dashboard empty?**
- Run backend processing first
- Check Supabase connection
- Verify database schema is set up

## Next Steps

1. ✅ System is running
2. 📱 Set up phone sync (iCloud/Dropbox)
3. 📊 Track performance in Analytics tab
4. 🎯 Optimize settings based on results
5. 🚀 Grow your account!

---

**Need more detail?** See the full [README.md](README.md) and [SETUP_GUIDE.md](SETUP_GUIDE.md)
