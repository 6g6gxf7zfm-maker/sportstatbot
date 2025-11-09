# 🏆 SportStatBot

Your expert sports analyst with 20+ years of experience covering NFL, NBA, MLB, NHL, MLS, international soccer, and golf. Get detailed, ESPN-style analysis reports delivered in beautiful Slack markdown format.

## Features

### 🎯 Comprehensive Coverage
- **NFL** 🏈 - Game results, player stats, playoff implications
- **NBA** 🏀 - Scores, standout performances, team trends
- **MLB** ⚾ - Latest results, pitching performances, division standings
- **NHL** 🏒 - Goals, assists, goalie stats, playoff picture
- **MLS** ⚽ - Match results, golden boot race, table standings
- **Soccer** ⚽ - Premier League and international coverage
- **Golf** ⛳ - PGA Tour leaderboards and tournament coverage

### 📊 Advanced Analysis
- **Key Trends** - Hot streaks 🔥, cold streaks ❄️, momentum shifts
- **Standout Players** - Top performances with detailed stats
- **Injury Reports** ⚠️ - Latest injury updates and return timelines
- **Roster Changes** - Trades, signings, and lineup adjustments
- **Betting Insights** 💰 - Point spreads, over/unders, value picks
- **Must-Watch Matchups** 👀 - Upcoming games you can't miss

### 🤖 Flexible Usage
- **On-Demand Reports** - Generate reports whenever you want
- **Automated Scheduling** - Daily morning and evening updates
- **Sport-Specific** - Focus on just the sports you care about
- **Quick Updates** - Fast summaries for busy schedules
- **Slack Integration** - Post directly to Slack channels

### 🎮 User Control Interface (NEW!)
- **Interactive Commands** - Generate digests, export reports, control all features
- **League Toggles** - Enable/disable leagues on the fly
- **Priority Ranking** - Set manual priorities (e.g., "NBA > NHL tonight")
- **Data Window Control** - Choose 3, 5, 10 day lookback periods
- **Output Length Sliders** - Brief, medium, or in-depth reports
- **Performance Dashboard** - Monitor agent runs, success rates, timeliness
- **Manual Editor Notes** - Add human notes before publishing
- **Experiment Mode** - Safely test new prompt variations
- **Workflow Archive** - Version control with detailed notes

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Try the demo** (see what reports look like)
   ```bash
   python demo_report.py
   ```

3. **Configure API keys** (optional - for betting data and Slack)
   ```bash
   cp .env.example .env
   # Edit .env to add API keys
   ```

That's it! See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage instructions.

## Usage

### Command Line Interface

#### Generate Full Report (All Sports)
```bash
python cli.py --all
```

#### Generate Report for Specific Sports
```bash
# Single sport
python cli.py --sports nfl

# Multiple sports
python cli.py --sports nfl nba mlb
```

#### Quick Updates
```bash
# Fast summary instead of full analysis
python cli.py --sports nfl --quick
```

#### Save to File
```bash
# Save report to markdown file
python cli.py --all --output today_report.md
```

#### List Available Sports
```bash
python cli.py --list-sports
```

### Automated Scheduling

Run the scheduler for automated daily reports:

```bash
# Start the scheduler
python scheduler.py

# Test with immediate report
python scheduler.py --test
```

**Default Schedule:**
- 🌅 **Morning Report**: 8:00 AM - Full recap of yesterday + today's previews
- 🌙 **Evening Report**: 6:00 PM - Today's results and analysis
- 🏈 **NFL Sundays**: Updates at 1:00 PM and 4:00 PM
- 🏀 **NBA Evenings**: Updates at 7:00 PM during season

### Slack Integration

To post reports directly to Slack:

1. Create a Slack webhook:
   - Go to your Slack workspace settings
   - Navigate to "Apps" → "Incoming Webhooks"
   - Create a new webhook and copy the URL

2. Add webhook to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. Run with Slack posting:
   ```bash
   python scheduler.py
   # Reports will automatically post to your Slack channel
   ```

### Interactive Control Interface 🎮

Take full control of SportStatBot with the interactive interface:

```bash
# Start interactive mode
python interactive_control.py

# Or execute single commands
python interactive_control.py --status
python interactive_control.py --dashboard
python interactive_control.py --command "generate-all"
```

**Key Features:**

- **Quick Commands**: `generate-all`, `export-24h`, `status`
- **League Control**: `toggle nfl`, `priority nfl nba mlb`
- **Customization**: `window 5`, `length in-depth`
- **Dashboard**: Real-time metrics and performance tracking
- **Experiments**: Test prompt variations safely
- **Archive**: Version control for workflows
- **Manual Notes**: Add editor notes before publishing

**Example Session:**

```
sportstat> status
# Shows enabled leagues, settings, recent activity

sportstat> toggle mlb
✅ ⚾ MLB (mlb) is now disabled

sportstat> priority nfl nba nhl
✅ Priority ranking updated: nfl > nba > nhl

sportstat> window 5
✅ Data window set to 5 days

sportstat> generate-all
✅ Generating digests for 6 leagues: nfl, nba, nhl, mls, soccer, golf

sportstat> dashboard
# Shows full performance dashboard

sportstat> exit
```

See the complete [USER_CONTROL_GUIDE.md](USER_CONTROL_GUIDE.md) for all features and commands.

## Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Betting Odds API (optional - get free key at https://the-odds-api.com/)
ODDS_API_KEY=your_api_key_here

# Slack Webhook (optional - for automated posting)
SLACK_WEBHOOK_URL=your_webhook_url_here

# Timezone for reports
REPORT_TIMEZONE=America/New_York
```

### Customizing Sports

Edit `config.py` to enable/disable specific sports or change display settings:

```python
SPORTS_CONFIG = {
    'nfl': {
        'espn_league': 'football/nfl',
        'display_name': 'NFL',
        'emoji': '🏈',
        'season_active': True  # Set to False to skip
    },
    # ... more sports
}
```

## Report Format

Reports are formatted in Slack-compatible markdown with:

- **Section headers** for each sport
- **Bullet points** for easy scanning
- **Bold text** for teams and players
- **Emoji indicators**:
  - 🔥 Hot teams on winning streaks
  - ❄️ Cold teams on losing streaks
  - ⚠️ Injury updates
  - 💰 Betting value picks
  - 👀 Must-watch games
  - ⭐ Standout performances

### Sample Output

```markdown
# 🏆 SPORTS UPDATE - November 8, 2025

## 🏈 NFL UPDATE

### 📈 KEY TRENDS

**🔥 Hot Teams:**
• Kansas City Chiefs - 5-game win streak
• San Francisco 49ers - 4-game win streak

**❄️ Cold Teams:**
• New York Giants - 4-game losing streak

### 📅 RECENT RESULTS

**Notable Games:**
• Kansas City Chiefs 31, Buffalo Bills 28 👀
  _Mahomes: 368 YDS, 3 TD | Allen: 342 YDS, 2 TD_

### ⭐ STANDOUT PERFORMANCES

• Patrick Mahomes (Chiefs) - 368 passing yards
• Christian McCaffrey (49ers) - 145 rushing yards
• Justin Jefferson (Vikings) - 156 receiving yards

### 💰 BETTING INSIGHTS

**Value Picks:**
• **Cowboys vs Eagles**
  Cowboys +7.5 (-110) - Better odds than market average

### 👀 MUST-WATCH MATCHUPS

• **Cowboys vs Eagles** - Sun 8:20 PM
  _Division game, Playoff implications_
```

## API Data Sources

SportStatBot uses free and public APIs:

- **ESPN API** (unofficial) - Game scores, standings, news
- **The Odds API** (optional) - Betting lines and odds
- **MLB Stats API** - Baseball statistics
- **NHL API** - Hockey data

All APIs are accessed respectfully with rate limiting and caching.

## Troubleshooting

### ESPN API Returns 403 Errors
ESPN's unofficial API sometimes blocks requests or has rate limits. This is normal and happens to all unofficial API users.

**Solutions:**
- Wait 15-30 minutes and try again (rate limits reset)
- Try during off-peak hours
- Use `python demo_report.py` to see the report format with sample data
- The bot handles API failures gracefully

**Note:** This bot uses ESPN's publicly accessible but unofficial API endpoints. If ESPN changes their API or implements stricter rate limiting, some features may be temporarily unavailable. Alternative data sources can be added in `data_fetchers/` if needed.

### No Data Showing
- Check your internet connection
- APIs may be temporarily down - try again in a few minutes
- Some sports are seasonal - check if season is active

### Betting Data Missing
- Betting insights require an API key from [The Odds API](https://the-odds-api.com/)
- Free tier provides 500 requests/month
- Reports work fine without betting data

### Slack Posting Not Working
- Verify webhook URL is correct in `.env`
- Test webhook with a simple curl command
- Check Slack workspace permissions

## Development

### Project Structure
```
sportstatbot/
├── cli.py                      # Command-line interface
├── scheduler.py                # Automated report scheduler
├── report_generator.py         # Main report orchestrator
├── config.py                   # Configuration settings
├── data_fetchers/             # API clients
│   ├── espn_fetcher.py        # ESPN data
│   └── odds_fetcher.py        # Betting odds
├── analyzers/                 # Analysis logic
│   ├── game_analyzer.py       # Game/team analysis
│   └── player_analyzer.py     # Player stats analysis
├── formatters/                # Output formatting
│   └── slack_formatter.py     # Slack markdown
└── reports/                   # Saved reports
```

### Adding New Features

1. **New Sport**: Add to `SPORTS_CONFIG` in `config.py`
2. **Custom Analysis**: Extend analyzers in `analyzers/`
3. **New Format**: Create formatter in `formatters/`
4. **Additional APIs**: Add fetcher in `data_fetchers/`

## Examples

### Example 1: Morning Routine
```bash
# Get your daily sports briefing
python cli.py --all --output morning_briefing.md
```

### Example 2: Game Day Updates
```bash
# Quick NFL update during Sunday games
python cli.py --sports nfl --quick
```

### Example 3: Multi-Sport Evening Recap
```bash
# Check results for major leagues
python cli.py --sports nfl nba nhl
```

### Example 4: Automated Daily Updates
```bash
# Set it and forget it
python scheduler.py
# Now get reports at 8 AM and 6 PM daily
```

## Contributing

Feel free to extend and customize for your needs! Some ideas:

- Add more sports (tennis, cricket, etc.)
- Integrate with Discord or other platforms
- Add historical trend analysis
- Create web dashboard
- Add ML predictions

## License

This project is for personal use. Please respect API terms of service and rate limits.

## Credits

Built with:
- ESPN's unofficial API for sports data
- The Odds API for betting information
- Python and open source libraries

---

**Enjoy your sports updates! 🏆🏈🏀⚾🏒⚽⛳**

For issues or questions, check the code comments or create an issue in the repository.
