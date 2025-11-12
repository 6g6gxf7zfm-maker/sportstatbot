# Sports Reel Automation Bot

**Automated sports highlight detection, video editing, and Instagram Reel preparation system**

Transform your sports Instagram account with automated, AI-powered reel creation. This system monitors live sports games, detects highlights, edits them into perfect 9:16 Instagram Reels, and generates viral captions—all automatically.

## Features

### 🎬 Automated Video Processing
- **Smart Cropping**: Automatically crops horizontal sports footage to vertical 9:16 format
- **Action Detection**: Uses computer vision to center the crop on where the action happens
- **Perfect Length**: Trims videos to 15 seconds max for optimal Instagram engagement
- **Professional Editing**: Applies speed ramping and effects for dramatic impact

### 🤖 AI-Powered Captions
- **Viral Caption Generation**: Uses Claude AI to create engaging, format-optimized captions
- **Multiple Styles**: Choose from hype, analytical, funny, or casual caption styles
- **Smart Hashtags**: Generates 15 targeted hashtags (5 broad, 5 community, 5 specific)
- **Hook Structure**: 3-word ALL CAPS hook + context + engagement question

### 📊 Intelligent Scoring
- **Viral Potential Calculator**: Scores highlights 1-10 based on:
  - Game importance (playoffs, rivalries)
  - Play type (buzzer beaters, dunks, etc.)
  - Player popularity
  - Historical engagement patterns
- **Smart Filtering**: Only processes high-potential content

### 🏆 Multi-Sport Coverage
Supports: NBA, NFL, MLB, MLS, EPL, La Liga, Champions League (NO HOCKEY)

### 📱 Dashboard & Analytics
- **Web Dashboard**: Beautiful Next.js interface to preview and manage reels
- **Posting Queue**: Drag-and-drop scheduling with optimal time suggestions
- **Performance Tracking**: Monitor views, likes, comments, and engagement rates
- **Sport Analytics**: See which sports perform best for your audience

## System Architecture

```
reel_automation/
├── backend/                    # Python processing engine
│   ├── sports_reel_bot.py     # Main orchestrator
│   ├── reel_scheduler.py      # Automation scheduler
│   ├── config_loader.py       # Configuration management
│   ├── video_processing/      # Video editing pipeline
│   │   └── video_processor.py
│   ├── api_clients/           # External API integrations
│   │   ├── espn_highlights_fetcher.py
│   │   └── caption_generator.py
│   └── utils/
│       ├── viral_score.py     # Viral potential calculator
│       └── supabase_client.py # Database client
├── frontend/                   # Next.js 14 dashboard
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   ├── queue/page.tsx     # Posting queue
│   │   ├── analytics/page.tsx # Performance analytics
│   │   └── settings/page.tsx  # Configuration
│   └── lib/
│       └── supabase.ts        # Supabase client
├── database/
│   └── schema.sql             # Supabase database schema
└── config/
    └── config.json            # System configuration
```

## Quick Start

### Prerequisites

- **Python 3.8+** (for backend processing)
- **Node.js 18+** (for dashboard)
- **FFmpeg** (for video processing)
- **Anthropic API Key** (for caption generation)
- **Supabase Account** (for database - free tier works)

### Installation

#### 1. Install Python Dependencies

```bash
cd reel_automation/backend
pip install -r requirements.txt
```

#### 2. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

#### 3. Install Node.js Dependencies

```bash
cd reel_automation/frontend
npm install
```

#### 4. Set Up Supabase

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Run the schema in `database/schema.sql` in the SQL Editor
4. Get your project URL and anon key

#### 5. Configure Environment Variables

**Backend (.env):**
```bash
cd reel_automation
cp .env.example .env
# Edit .env with your keys:
ANTHROPIC_API_KEY=your_claude_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

**Frontend (.env.local):**
```bash
cd frontend
cp ../.env.example .env.local
# Add your Supabase public credentials
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### 6. Configure Settings

Edit `config/config.json` to customize:
- Sports to monitor
- Viral score threshold
- Posts per day target
- Caption style
- Output directory

## Usage

### Running the Bot Manually

```bash
cd reel_automation/backend
python sports_reel_bot.py
```

This will:
1. Fetch highlights from the last 24 hours
2. Calculate viral scores
3. Process videos (download, crop, edit)
4. Generate captions
5. Save to organized folders
6. Store metadata in database

### Running the Automated Scheduler

```bash
cd reel_automation/backend
python reel_scheduler.py
```

The scheduler runs every 30 minutes during game times:
- **Weekdays**: 6 PM - midnight, noon - 4 PM
- **Weekends**: Noon - midnight
- **Daily cleanup**: 3 AM
- **Weekly reports**: Monday 10 AM

### Running the Dashboard

```bash
cd reel_automation/frontend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

**Dashboard Features:**
- **Dashboard (/)**: View all processed reels, preview videos, copy captions
- **Queue (/queue)**: See scheduled posts and optimal posting times
- **Analytics (/analytics)**: Track performance by sport
- **Settings (/settings)**: Configure preferences

## Workflow

### 1. Automated Processing

The bot runs on schedule and:
1. Fetches highlights from ESPN and other sources
2. Scores each highlight for viral potential
3. Filters by threshold (default: 7/10)
4. Downloads and processes videos
5. Generates captions with Claude AI
6. Saves everything to organized folders

### 2. File Organization

```
~/Desktop/reels_ready/
├── 2024-11-12/
│   ├── NBA/
│   │   ├── 1830_Lakers_Celtics_reel.mp4
│   │   ├── 1830_Lakers_Celtics_caption.txt
│   │   └── 1830_Lakers_Celtics_metadata.json
│   ├── NFL/
│   │   └── ...
│   └── posting_schedule.json
```

### 3. Posting Workflow

1. Open dashboard to preview reels
2. Check viral scores and captions
3. Add to posting queue with suggested times
4. Download videos to your phone (via iCloud/Dropbox sync)
5. Post to Instagram with pre-written captions

### 4. Performance Tracking

- Manually update performance metrics in dashboard
- System learns from historical data
- Improves viral score predictions over time

## Configuration

### Sports Selection

Edit `config.json`:
```json
{
  "sports": ["NBA", "NFL", "MLB", "MLS", "EPL"],
  "exclude_sports": ["NHL", "Hockey"]
}
```

### Viral Score Threshold

Higher threshold = fewer but higher quality reels:
- **5-6**: More quantity, mixed quality
- **7**: Balanced (recommended)
- **8-9**: Very selective, only top highlights
- **10**: Only game-winners and exceptional plays

### Caption Styles

- **hype**: "UNREAL PLAY 🔥" - energetic with CAPS and emojis
- **analytical**: Focus on strategy and skill
- **funny**: Humorous with wordplay
- **casual**: Conversational, relatable

### Optimal Posting Times

Default times (EST):
- 7:30 AM - Morning commute
- 12:15 PM - Lunch break
- 6:00 PM - Evening commute
- 8:30 PM - Prime time
- 10:00 PM - Night scrollers

Customize in `config.json`

## API Keys

### Anthropic Claude API

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

**Cost**: ~$0.01-0.03 per caption (very affordable)

### ESPN API

The system uses ESPN's public API endpoints (no key required for basic features). For enhanced features, you can add an ESPN API key if you have one.

## Troubleshooting

### Videos Not Processing

- **Check FFmpeg**: Run `ffmpeg -version`
- **Check temp directory**: Ensure write permissions
- **Check video URL**: Some sources may be protected

### Captions Not Generating

- **Verify API key**: Check `ANTHROPIC_API_KEY` in `.env`
- **Check quota**: Ensure you have API credits
- **Fallback captions**: System uses templates if API fails

### No Highlights Found

- **Check sports schedule**: No games = no highlights
- **ESPN API limits**: May be temporarily rate-limited
- **Alternative sources**: Enable YouTube fetching in code

### Database Errors

- **Verify Supabase credentials**: Check URL and keys
- **Check schema**: Ensure schema.sql was run
- **Network**: Supabase requires internet connection

## Performance Tips

### Growing Your Account

1. **Consistency**: Post 3-5 times daily
2. **Optimal Times**: Use suggested posting times
3. **Engagement**: Respond to comments quickly
4. **Quality Over Quantity**: Use threshold 7+ for best content
5. **Mix Sports**: Diversify content based on what's trending

### Viral Score Optimization

The viral score improves as you track performance:
1. Post reels and note their performance
2. Update engagement metrics in dashboard
3. System learns which content performs best
4. Future predictions become more accurate

### Resource Management

- **Cleanup old files**: Runs automatically at 3 AM
- **Limit max highlights**: Set in code (default: 10 per run)
- **Adjust schedule**: Fewer runs = less processing

## Advanced Features

### Custom Sports Sources

Add new highlight sources in `backend/api_clients/`:
- Twitter/X video scraping
- YouTube Sports channels
- Direct team APIs

### Speed Ramping

Enhance the video processor to add:
- Slow motion at peak moments
- Zoom effects on key plays
- Custom transitions

### Instagram API Integration

For full automation (requires Instagram Business account):
1. Set up Facebook Developer account
2. Get Instagram Graph API access
3. Implement posting in code

### Machine Learning

The system includes a performance tracking system that can be enhanced with:
- Engagement prediction models
- Optimal time learning
- Caption A/B testing

## Deployment

### Backend (Processing Bot)

Run on a server or your local machine:

**Using systemd (Linux):**
```bash
# Create service file
sudo nano /etc/systemd/system/reel-bot.service

[Unit]
Description=Sports Reel Automation Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/reel_automation/backend
ExecStart=/usr/bin/python3 reel_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable reel-bot
sudo systemctl start reel-bot
```

**Using cron (macOS/Linux):**
```bash
crontab -e
# Add:
*/30 18-23 * * * cd /path/to/backend && python sports_reel_bot.py
```

### Frontend (Dashboard)

Deploy to Vercel (recommended):

```bash
cd reel_automation/frontend
vercel deploy
```

Or any Next.js hosting platform.

## Roadmap

- [ ] Mobile app for easier posting
- [ ] Direct Instagram posting integration
- [ ] Multi-language caption support
- [ ] TikTok format adaptation
- [ ] YouTube Shorts support
- [ ] Advanced analytics and insights
- [ ] Caption A/B testing
- [ ] Automated thumbnail generation
- [ ] Voice-over integration
- [ ] Chrome extension for one-click processing

## Contributing

This is a personal project, but feel free to fork and customize for your needs!

## License

For personal use. Respect API terms of service and rate limits.

## Credits

Built with:
- **Python** - Backend processing
- **Next.js 14** - Dashboard
- **Supabase** - Database
- **Anthropic Claude** - AI captions
- **FFmpeg** - Video processing
- **ESPN API** - Sports data

---

**Ready to automate your sports content creation? Let's go! 🚀**

For questions or issues, check the code comments or create an issue.
