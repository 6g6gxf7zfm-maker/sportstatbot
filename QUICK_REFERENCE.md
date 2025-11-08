# SportStatBot - Quick Reference Guide

**Location:** `/home/user/sportstatbot`  
**Branch:** `claude/cursor-dashboard-ux-011CUwHemdAY4bLzwzfjViC6`

---

## QUICK FILE REFERENCE

| Purpose | File Path | Key Classes/Functions |
|---------|-----------|----------------------|
| **CLI** | `cli.py` | `main()` |
| **Config** | `config.py` | `SPORTS_CONFIG`, `ODDS_API_KEY`, `SLACK_WEBHOOK_URL` |
| **Core Logic** | `report_generator.py` | `SportsReportGenerator` |
| **Scheduler** | `scheduler.py` | `ReportScheduler` |
| **ESPN Data** | `data_fetchers/espn_fetcher.py` | `ESPNFetcher` |
| **Odds Data** | `data_fetchers/odds_fetcher.py` | `OddsFetcher` |
| **Game Analysis** | `analyzers/game_analyzer.py` | `GameAnalyzer` |
| **Player Analysis** | `analyzers/player_analyzer.py` | `PlayerAnalyzer` |
| **Formatting** | `formatters/slack_formatter.py` | `SlackFormatter` |
| **Demo** | `demo_report.py` | `generate_demo_report()` |

---

## QUICK START COMMANDS

```bash
# View available sports
python cli.py --list-sports

# Generate full report
python cli.py --all

# Generate for specific sports
python cli.py --sports nfl nba

# Quick update
python cli.py --sports nfl --quick

# Save to file
python cli.py --all --output today.md

# Run scheduler
python scheduler.py

# Test scheduler
python scheduler.py --test

# View demo
python demo_report.py
```

---

## SUPPORTED SPORTS

| Key | Display Name | League Code | Active |
|-----|--------------|-------------|--------|
| `nfl` | NFL | football/nfl | Yes |
| `nba` | NBA | basketball/nba | Yes |
| `mlb` | MLB | baseball/mlb | Yes |
| `nhl` | NHL | hockey/nhl | Yes |
| `mls` | MLS | soccer/usa.1 | Yes |
| `soccer` | Premier League | soccer/eng.1 | Yes |
| `golf` | PGA Tour | golf/pga | Yes |

---

## CORE DATA MODELS (INPUT → OUTPUT)

### 1. Game Model
```python
Input:  ESPN event/competition data
Output: {
    'home_team': str,
    'away_team': str,
    'home_score': int,
    'away_score': int,
    'winner': str,
    'loser': str,
    'is_close': bool,      # ≤7 point diff
    'is_blowout': bool,    # ≥21 point diff
    'is_upset': bool,
    'leaders': {stat_category: {name, value}}
}
```

### 2. Trend Model
```python
Input:  Standings data (W-L records, streaks)
Output: {
    'type': 'hot_streak' | 'cold_streak',
    'team': str,
    'description': str
}
```

### 3. Player Performance Model
```python
Input:  Game leaders and stat thresholds
Output: {
    'player': str,
    'team': str,
    'stat_category': str,
    'value': str,           # e.g., "368 YDS, 3 TD"
    'game': str,
    'date': datetime
}
```

### 4. Injury/Roster Model
```python
Input:  News articles (keyword matching)
Output: {
    'headline': str,
    'description': str,
    'type': 'injury_update' | 'roster_change',
    'link': str,
    'published': datetime
}
```

### 5. Betting Insights Model
```python
Input:  The Odds API data
Output: {
    'value_bets': [
        {
            'game': str,
            'recommendation': str,
            'odds': int,
            'reason': str
        }
    ],
    'featured_games': [
        {
            'matchup': str,
            'spread': str,
            'total': str
        }
    ]
}
```

### 6. Complete Sport Data Model
```python
Input:  All API fetchers + analyzers
Output: {
    'enabled': bool,
    'trends': [Trend],
    'recent_games': [Game],
    'standout_players': [Player],
    'injuries': [Injury],
    'roster_changes': [Roster],
    'betting_insights': Betting,
    'must_watch': [Matchup]
}
```

---

## ANALYZER PERFORMANCE THRESHOLDS

### NFL
- Passing: 300+ yards
- Rushing: 100+ yards
- Receiving: 100+ yards
- Touchdowns: 3+

### NBA
- Points: 30+
- Rebounds: 12+
- Assists: 10+
- Triple-double eligible

### MLB
- Home runs: 2+
- RBIs: 4+
- Hits: 3+
- Strikeouts (P): 10+

### NHL
- Goals: 2+
- Assists: 3+
- Points: 3+
- Saves (G): 40+

### Streak Detection
- Hot streak: 3+ consecutive wins
- Cold streak: 3+ consecutive losses

---

## API ENDPOINTS

### ESPN API
**Base:** `https://site.api.espn.com/apis/site/v2/sports`

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/{league}/scoreboard` | Recent games | `{events: [game_data]}` |
| `/{league}/standings` | Team records | `{children: [standings]}` |
| `/{league}/news` | Latest news | `{articles: [article]}` |
| `/{league}/teams/{id}` | Team info | Team data object |
| `/{league}/athletes/{id}` | Player stats | Athlete data object |

### The Odds API
**Base:** `https://api.the-odds-api.com/v4`

| Endpoint | Purpose | Requires |
|----------|---------|----------|
| `/sports/{sport_key}/odds` | Betting odds | API key |

**Sport Keys:**
- `americanfootball_nfl` → NFL
- `basketball_nba` → NBA
- `baseball_mlb` → MLB
- `icehockey_nhl` → NHL
- `soccer_usa_mls` → MLS
- `soccer_epl` → Premier League
- `golf_pga_championship` → Golf

**Markets:**
- `h2h` - Head-to-head moneyline
- `spreads` - Point spreads
- `totals` - Over/under totals

---

## ENVIRONMENT VARIABLES (.env)

```bash
# Betting API (optional)
ODDS_API_KEY=your_api_key_here

# Slack Integration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Report Settings (optional)
REPORT_TIMEZONE=America/New_York
```

---

## KEY METHODS BY CLASS

### SportsReportGenerator
```
generate_full_report(sports=None)              → str (markdown)
generate_sport_report(sport, quick=False)      → str (markdown)
_generate_sport_data(sport)                    → dict (sport_data)
_analyze_betting_data(odds_data)               → dict (betting_insights)
save_report(report, filename=None)             → str (filepath)
```

### ESPNFetcher
```
get_scoreboard(sport, limit=20)                → dict (JSON)
get_standings(sport)                           → dict (JSON)
get_team_info(sport, team_id)                  → dict (JSON)
get_news(sport, limit=10)                      → dict (JSON)
get_player_stats(sport, player_id)             → dict (JSON)
get_schedule(sport, days_ahead=7)              → dict (JSON)
```

### OddsFetcher
```
get_odds(sport, markets='h2h,spreads,totals') → list (JSON)
get_upcoming_odds(sport)                       → list (JSON)
find_value_bets(odds_data)                     → list (bets)
```

### GameAnalyzer
```
analyze_scoreboard(scoreboard_data)            → dict {games, highlights}
analyze_standings(standings_data)              → dict {teams, trends}
find_must_watch_matchups(schedule, standings)  → list (matchups)
_analyze_game(event)                           → dict (game_model)
_detect_upset(h_team, a_team, h_score, a_score) → bool
```

### PlayerAnalyzer
```
extract_standout_players(scoreboard, sport)    → list (players)
analyze_injuries(news_data)                    → list (injuries)
analyze_roster_changes(news_data)              → list (roster_changes)
get_player_summary(player_data)                → dict (summary)
_is_standout_performance(stat_name, val, sport) → bool
```

### SlackFormatter
```
format_full_report(all_sports_data)            → str (markdown)
format_sport_quick_update(sport, data)         → str (markdown)
_format_sport_section(sport, data, config)     → str (markdown)
_format_trends(trends)                         → str (markdown)
_format_recent_games(games)                    → str (markdown)
_format_standout_players(players)              → str (markdown)
_format_betting_insights(betting_data)         → str (markdown)
_format_must_watch(matchups)                   → str (markdown)
```

### ReportScheduler
```
morning_report()                               → None (posts/saves)
evening_report()                               → None (posts/saves)
quick_update(sport)                            → None (posts)
post_to_slack(report)                          → bool
run()                                          → None (infinite loop)
```

---

## EMOJI REFERENCE

| Emoji | Use | Method |
|-------|-----|--------|
| 🔥 | Hot streak | `_format_trends()` |
| ❄️ | Cold streak | `_format_trends()` |
| ⚠️ | Upset / Warning | `_format_recent_games()` |
| 👀 | Close game / Must-watch | `_format_recent_games()` |
| ⭐ | Standout performance | `_format_standout_players()` |
| 💰 | Betting insights | `_format_betting_insights()` |
| 📈 | Trends | `_format_trends()` |
| 📅 | Recent results | `_format_recent_games()` |
| 🏥 | Injury | `_format_injury_roster_updates()` |
| 🆕 | New/Roster move | `_format_injury_roster_updates()` |

---

## CONFIGURATION POINTS

### To Add a New Sport:
1. **config.py** - Add to `SPORTS_CONFIG`
2. **data_fetchers/espn_fetcher.py** - ESPN league code
3. **data_fetchers/odds_fetcher.py** - Odds sport key mapping
4. **analyzers/player_analyzer.py** - Performance thresholds
5. **formatters/slack_formatter.py** - Emoji mapping (optional)

### To Change Schedule:
Edit `scheduler.py`:
```python
schedule.every().day.at("08:00").do(self.morning_report)  # Time format: "HH:MM"
schedule.every().day.at("18:00").do(self.evening_report)
schedule.every().sunday.at("13:00").do(lambda: self.quick_update('nfl'))
```

### To Adjust Thresholds:
- **Streaks:** `GameAnalyzer.__init__()` - `hot_streak_threshold`, `cold_streak_threshold`
- **Game classification:** `GameAnalyzer._analyze_game()` - close_game (≤7), blowout (≥21)
- **Player thresholds:** `PlayerAnalyzer.performance_thresholds` by sport
- **Injury keywords:** `PlayerAnalyzer.analyze_injuries()` - `injury_keywords` list
- **Roster keywords:** `PlayerAnalyzer.analyze_roster_changes()` - `roster_keywords` list

---

## COMMON CUSTOMIZATIONS

### Custom Report Output
```python
# Replace SlackFormatter with HTMLFormatter
from formatters.html_formatter import HTMLFormatter

class HTMLFormatter:
    def format_full_report(self, all_sports_data):
        # Generate HTML instead of markdown
        pass
```

### Custom Data Processing
```python
# Extend GameAnalyzer
class CustomGameAnalyzer(GameAnalyzer):
    def analyze_team_momentum(self, standings_data):
        # Custom analysis logic
        pass
```

### Custom Sports Configuration
```python
# In config.py, add to SPORTS_CONFIG:
'cricket': {
    'espn_league': 'cricket/international',
    'display_name': 'International Cricket',
    'emoji': '🏏',
    'season_active': True
}
```

### Add More Analysis
```python
# In report_generator.py _generate_sport_data():
# Add new analysis method call:
advanced_stats = self.game_analyzer.analyze_team_momentum(standings)
sport_data['momentum'] = advanced_stats
```

---

## TROUBLESHOOTING

### ESPN API 403 Errors
- API is rate-limited or ESPN blocked requests
- Solution: Wait 15-30 minutes, try again during off-peak hours
- Fallback: Use `python demo_report.py` to see format with sample data

### No Betting Data
- ODDS_API_KEY not configured
- Solution: Sign up at https://the-odds-api.com/ (free tier: 500/month)
- Add key to .env file

### Slack Not Posting
- SLACK_WEBHOOK_URL not configured or invalid
- Solution: Create webhook at https://api.slack.com/messaging/webhooks
- Add to .env, verify format

### Missing Data in Reports
- Some APIs may be down or returning partial data
- Solution: Reports gracefully degrade, showing whatever data is available
- Check individual API endpoints for status

---

## PERFORMANCE NOTES

- **API Calls:** 0.5s delay between requests (rate limiting)
- **Report Generation:** ~5-15s for full multi-sport report
- **Scheduler:** Checks for pending jobs every 60 seconds
- **Memory:** Minimal (no caching, processes data on-demand)

---

## EXTENSION OPPORTUNITIES FOR DASHBOARD

### 1. Real-time Updates
- WebSocket connection to ESPN API
- Streaming game updates
- Live score notifications

### 2. Historical Data
- Database storage (SQLite/PostgreSQL)
- Historical trends and analytics
- Year-over-year comparisons

### 3. Personalization
- User preferences/favorite teams
- Custom report templates
- Notification preferences

### 4. Interactive UI
- Web dashboard (Flask/Django)
- Command palette interface
- Story/narrative templates
- Team/player comparison tools

### 5. Advanced Analysis
- Predictive models
- Advanced statistics
- Fantasy sports integration
- Automated highlight generation

---

## DEPENDENCIES

```
requests==2.31.0           # HTTP client
beautifulsoup4==4.12.3     # HTML parsing
python-dateutil==2.8.2     # Date utilities
pytz==2024.1              # Timezone support
schedule==1.2.0           # Job scheduling
python-dotenv==1.0.1      # Environment variables
```

---

**Ready to implement dashboard, command palette, story templates, and UX features!**
