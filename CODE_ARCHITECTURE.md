# SportStatBot - Code Architecture & Class Relationships

## CLASS HIERARCHY & RELATIONSHIPS

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                    SportsReportGenerator                           │
│                   (report_generator.py)                            │
│                                                                     │
│  • generate_full_report(sports)                                    │
│  • generate_sport_report(sport, quick)                             │
│  • _generate_sport_data(sport)                                     │
│  • _analyze_betting_data(odds)                                     │
│  • generate_custom_analysis(sport, team)                           │
│  • save_report(report, filename)                                   │
│                                                                     │
└─────────────┬───────────────┬─────────────────┬────────────────────┘
              │               │                 │
              ▼               ▼                 ▼
     ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐
     │  ESPNFetcher     │  │  OddsFetcher    │  │ GameAnalyzer     │
     │                  │  │                 │  │                  │
     │ • scoreboard()   │  │ • get_odds()    │  │ • analyze_board()│
     │ • standings()    │  │ • find_value()  │  │ • analyze_stand()│
     │ • team_info()    │  │                 │  │ • find_must_w()  │
     │ • news()         │  │                 │  │                  │
     │ • player_stats() │  │                 │  │                  │
     │ • schedule()     │  │                 │  │                  │
     └──────────────────┘  └─────────────────┘  └──────────────────┘
                                                          │
                                                          ▼
                                                ┌──────────────────┐
                                                │ PlayerAnalyzer   │
                                                │                  │
                                                │ • standouts()    │
                                                │ • injuries()     │
                                                │ • roster_chgs()  │
                                                └──────────────────┘

              │                                           │
              ├───────────────────────┬───────────────────┤
              │                       │                   │
              ▼                       ▼                   ▼
        ┌────────────────────────────────────────────────────┐
        │           SlackFormatter                           │
        │                                                    │
        │ • format_full_report(all_sports_data)             │
        │ • _format_sport_section(sport, data)              │
        │ • _format_trends(trends)                          │
        │ • _format_recent_games(games)                     │
        │ • _format_standout_players(players)               │
        │ • _format_betting_insights(betting)               │
        │ • _format_must_watch(matchups)                    │
        │ • format_sport_quick_update(sport, data)          │
        └────────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────┐
        │           Formatted Report (Markdown)          │
        │     Ready for Console/File/Slack               │
        └────────────────────────────────────────────────┘
```

---

## KEY CLASS IMPLEMENTATIONS

### 1. SportsReportGenerator
**File:** `report_generator.py`

```python
class SportsReportGenerator:
    def __init__(self):
        self.espn_fetcher = ESPNFetcher()
        self.odds_fetcher = OddsFetcher()
        self.game_analyzer = GameAnalyzer()
        self.player_analyzer = PlayerAnalyzer()
        self.slack_formatter = SlackFormatter()
    
    def generate_full_report(self, sports=None):
        # Orchestrates entire report generation
        all_sports_data = {}
        
        for sport in sports:
            sport_data = self._generate_sport_data(sport)
            all_sports_data[sport] = sport_data
        
        report = self.slack_formatter.format_full_report(all_sports_data)
        return report
    
    def _generate_sport_data(self, sport):
        # Aggregates all data for a single sport
        sport_data = {
            'trends': [],
            'recent_games': [],
            'standout_players': [],
            'injuries': [],
            'roster_changes': [],
            'betting_insights': {},
            'must_watch': []
        }
        
        # Fetch and analyze
        scoreboard = self.espn_fetcher.get_scoreboard(sport)
        game_analysis = self.game_analyzer.analyze_scoreboard(scoreboard)
        sport_data['recent_games'] = game_analysis['games']
        
        # ... more data collection ...
        
        return sport_data
```

### 2. Data Fetchers

#### ESPNFetcher
```python
class ESPNFetcher:
    def __init__(self):
        self.base_url = config.ESPN_API_BASE
        self.session = requests.Session()
        # Set User-Agent to avoid blocks
    
    def get_scoreboard(self, sport, limit=20):
        # Fetch recent games/scores
        league = config.SPORTS_CONFIG[sport]['espn_league']
        url = f"{self.base_url}/{league}/scoreboard"
        response = self.session.get(url, params={'limit': limit})
        return response.json()
    
    def get_standings(self, sport):
        # Fetch team standings and records
        league = config.SPORTS_CONFIG[sport]['espn_league']
        url = f"{self.base_url}/{league}/standings"
        response = self.session.get(url)
        return response.json()
    
    def get_news(self, sport, limit=10):
        # Fetch latest news articles
        league = config.SPORTS_CONFIG[sport]['espn_league']
        url = f"{self.base_url}/{league}/news"
        response = self.session.get(url, params={'limit': limit})
        return response.json()
```

#### OddsFetcher
```python
class OddsFetcher:
    def __init__(self):
        self.api_key = config.ODDS_API_KEY
        self.sport_keys = {
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            # ...
        }
    
    def get_odds(self, sport, markets='h2h,spreads,totals'):
        # Fetch betting odds
        if not self.api_key:
            return None
        
        sport_key = self.sport_keys.get(sport)
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': markets,
            'oddsFormat': 'american'
        }
        response = self.session.get(url, params=params)
        return response.json()
    
    def find_value_bets(self, odds_data):
        # Analyze odds across bookmakers
        value_bets = []
        
        for game in odds_data:
            for bookmaker in game['bookmakers']:
                for market in bookmaker['markets']:
                    if market['key'] == 'spreads':
                        # Analyze spreads for value
                        pass
        
        return value_bets
```

### 3. Analyzers

#### GameAnalyzer
```python
class GameAnalyzer:
    def __init__(self):
        self.hot_streak_threshold = 3
        self.cold_streak_threshold = 3
    
    def analyze_scoreboard(self, scoreboard_data):
        # Process game events
        analyzed_games = []
        
        for event in scoreboard_data['events']:
            game_info = self._analyze_game(event)
            analyzed_games.append(game_info)
        
        return {'games': analyzed_games}
    
    def _analyze_game(self, event):
        # Extract and classify single game
        competition = event['competitions'][0]
        competitors = competition['competitors']
        
        home_team = [c for c in competitors if c['homeAway'] == 'home'][0]
        away_team = [c for c in competitors if c['homeAway'] == 'away'][0]
        
        game_info = {
            'home_team': home_team['team']['displayName'],
            'away_team': away_team['team']['displayName'],
            'home_score': int(home_team['score']),
            'away_score': int(away_team['score']),
            'is_close': abs(home_team['score'] - away_team['score']) <= 7,
            'is_blowout': abs(home_team['score'] - away_team['score']) >= 21,
            'is_upset': self._detect_upset(home_team, away_team, 
                                          home_team['score'], away_team['score'])
        }
        
        return game_info
    
    def analyze_standings(self, standings_data):
        # Extract trends from standings
        trends = []
        
        for standings in standings_data['children'][0]['standings']['entries']:
            team = standings['team']['displayName']
            streak = self._extract_streak(standings['stats'])
            
            if 'W' in streak and int(streak[0]) >= self.hot_streak_threshold:
                trends.append({
                    'type': 'hot_streak',
                    'team': team,
                    'description': f"{team} on {streak[0]}-game win streak 🔥"
                })
        
        return {'trends': trends}
```

#### PlayerAnalyzer
```python
class PlayerAnalyzer:
    def __init__(self):
        self.performance_thresholds = {
            'nfl': {
                'passing_yards': 300,
                'rushing_yards': 100,
                'receiving_yards': 100,
                'touchdowns': 3
            },
            # ... other sports ...
        }
    
    def extract_standout_players(self, scoreboard_data, sport):
        # Find top performances
        standouts = []
        
        for event in scoreboard_data['events']:
            competition = event['competitions'][0]
            
            for leader_category in competition.get('leaders', []):
                for leader in leader_category.get('leaders', []):
                    athlete = leader['athlete']
                    value = leader['displayValue']
                    
                    if self._is_standout_performance(
                        leader_category['name'], value, sport
                    ):
                        standouts.append({
                            'player': athlete['displayName'],
                            'team': leader['team']['displayName'],
                            'stat_category': leader_category['name'],
                            'value': value
                        })
        
        return standouts
    
    def analyze_injuries(self, news_data):
        # Extract injury-related news
        injuries = []
        injury_keywords = ['injury', 'injured', 'hurt', 'out', 'doubtful',
                          'questionable', 'ir', 'concussion']
        
        for article in news_data['articles']:
            headline = article['headline'].lower()
            
            if any(kw in headline for kw in injury_keywords):
                injuries.append({
                    'headline': article['headline'],
                    'description': article['description'],
                    'type': 'injury_update'
                })
        
        return injuries
```

### 4. Formatters

#### SlackFormatter
```python
class SlackFormatter:
    def __init__(self):
        self.emoji = {
            'fire': '🔥',
            'cold': '❄️',
            'warning': '⚠️',
            'star': '⭐',
            'moneybag': '💰',
            'eyes': '👀'
        }
    
    def format_full_report(self, all_sports_data):
        # Create complete report
        report_sections = [
            f"# 🏆 SPORTS UPDATE - {datetime.now().strftime('%B %d, %Y')}\n"
        ]
        
        for sport, data in all_sports_data.items():
            sport_config = config.SPORTS_CONFIG[sport]
            section = self._format_sport_section(sport, data, sport_config)
            report_sections.append(section)
        
        return "\n---\n".join(report_sections)
    
    def _format_sport_section(self, sport, data, sport_config):
        emoji = sport_config['emoji']
        display_name = sport_config['display_name']
        
        sections = [f"\n## {emoji} {display_name} UPDATE\n"]
        
        if data.get('trends'):
            sections.append(self._format_trends(data['trends']))
        
        if data.get('recent_games'):
            sections.append(self._format_recent_games(data['recent_games']))
        
        if data.get('standout_players'):
            sections.append(self._format_standout_players(
                data['standout_players']
            ))
        
        return "\n".join(sections)
    
    def _format_trends(self, trends):
        lines = [f"### {self.emoji['fire']} KEY TRENDS\n"]
        
        hot_streaks = [t for t in trends if t['type'] == 'hot_streak']
        
        for trend in hot_streaks:
            lines.append(f"• **{trend['team']}** - {trend['description']}")
        
        return "\n".join(lines)
    
    def _format_recent_games(self, games):
        lines = [f"### 📅 RECENT RESULTS\n"]
        
        for game in games[:5]:
            winner = game['winner']
            loser = game['loser']
            w_score = game['winner_score']
            l_score = game['loser_score']
            
            lines.append(f"• **{winner}** {w_score}, {loser} {l_score}")
        
        return "\n".join(lines)
```

---

## DATA FLOW EXAMPLES

### Example 1: Fetching and Analyzing NFL Data

```python
# In SportsReportGenerator._generate_sport_data('nfl')

# 1. Fetch scoreboard
scoreboard = espn_fetcher.get_scoreboard('nfl', limit=15)
# Returns: { 'events': [ {...game data...}, ... ] }

# 2. Analyze games
game_analysis = game_analyzer.analyze_scoreboard(scoreboard)
# Returns: { 'games': [GameModel], 'highlights': [...] }
sport_data['recent_games'] = game_analysis['games']

# 3. Extract standouts
standouts = player_analyzer.extract_standout_players(scoreboard, 'nfl')
# Returns: [PlayerModel] filtered by performance thresholds
sport_data['standout_players'] = standouts

# 4. Fetch standings
standings = espn_fetcher.get_standings('nfl')
# Returns: { 'children': [{ 'standings': { 'entries': [...] } }] }

# 5. Analyze standings for trends
standings_analysis = game_analyzer.analyze_standings(standings)
# Returns: { 'trends': [TrendModel], ... }
sport_data['trends'] = standings_analysis['trends']

# 6. Fetch news
news = espn_fetcher.get_news('nfl', limit=20)
# Returns: { 'articles': [{...}, ...] }

# 7. Analyze for injuries/roster
injuries = player_analyzer.analyze_injuries(news)
roster_changes = player_analyzer.analyze_roster_changes(news)
sport_data['injuries'] = injuries
sport_data['roster_changes'] = roster_changes

# Final sport_data structure:
{
    'enabled': True,
    'trends': [TrendModel, ...],
    'recent_games': [GameModel, ...],
    'standout_players': [PlayerModel, ...],
    'injuries': [InjuryModel, ...],
    'roster_changes': [RosterModel, ...],
    'betting_insights': {...},
    'must_watch': [MatchupModel, ...]
}
```

### Example 2: Formatting for Output

```python
# In SlackFormatter.format_full_report(all_sports_data)

# Input: { 'nfl': {...}, 'nba': {...}, ... }

# 1. Create header
report = "# 🏆 SPORTS UPDATE - November 8, 2025"

# 2. For each sport
for sport, data in all_sports_data.items():
    # 2a. Format trends section
    trends_section = """### 📈 KEY TRENDS

**🔥 Hot Teams:**
• Kansas City Chiefs - 5-game win streak 🔥
• San Francisco 49ers - 4-game win streak 🔥

**❄️ Cold Teams:**
• New York Giants - 4-game losing streak ❄️"""
    
    # 2b. Format recent games
    games_section = """### 📅 RECENT RESULTS

**Notable Games:**
• Kansas City Chiefs 31, Buffalo Bills 28 👀
  _Mahomes: 368 YDS, 3 TD | Allen: 342 YDS, 2 TD_"""
    
    # 2c. Format standout players
    players_section = """### ⭐ STANDOUT PERFORMANCES

• **Patrick Mahomes** (Chiefs) - 368 passing yards
• **Christian McCaffrey** (49ers) - 145 rushing yards"""
    
    # Combine sections
    report += trends_section + games_section + players_section

# 3. Add footer with timestamp
report += f"\n_Report generated at {datetime.now().strftime('%I:%M %p ET')}_"

# Output ready for console/file/Slack
```

---

## CONFIGURATION & DEPENDENCY FLOW

```
.env file
  │
  ├─► ODDS_API_KEY ────────────┐
  │                             │
  ├─► SLACK_WEBHOOK_URL ──┐    │
  │                       │    │
  └─► REPORT_TIMEZONE     │    │
                          │    │
                          ▼    ▼
              ┌─────────────────────────┐
              │   config.py             │
              │                         │
              │  SPORTS_CONFIG          │
              │  API_ENDPOINTS          │
              │  TIMEZONE               │
              └─────────────────────────┘
                    │           │
        ┌───────────┼───────────┼──────────┬─────────────┐
        │           │           │          │             │
        ▼           ▼           ▼          ▼             ▼
    ESPNFetcher OddsFetcher GameAnalyzer PlayerAnalyzer SlackFormatter
        │           │           │          │             │
        └───────────┴───────────┴──────────┴─────────────┘
                    │
                    ▼
           SportsReportGenerator
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    Console    File Save    Slack Post
```

---

## EXTENSION HOOKS FOR DASHBOARD

### Hook 1: Data Access
```python
# In a new web dashboard module
from report_generator import SportsReportGenerator

generator = SportsReportGenerator()
sport_data = generator._generate_sport_data('nfl')

# Now you have structured data:
# - sport_data['recent_games'] → Use for game display
# - sport_data['trends'] → Use for team stats
# - sport_data['standout_players'] → Use for player cards
# - sport_data['must_watch'] → Use for featured games widget
```

### Hook 2: Custom Formatting
```python
# In formatters/html_formatter.py
class HTMLFormatter:
    def format_full_report(self, all_sports_data):
        # Generate HTML instead of Slack markdown
        html = "<div class='sports-report'>"
        
        for sport, data in all_sports_data.items():
            html += self._format_sport_card(sport, data)
        
        html += "</div>"
        return html
    
    def _format_sport_card(self, sport, data):
        # Create HTML card for each sport
        return f"<div class='sport-card'>{sport}</div>"
```

### Hook 3: Custom Analysis
```python
# Extend GameAnalyzer
class EnhancedGameAnalyzer(GameAnalyzer):
    def analyze_team_momentum(self, standings_data, lookback_days=7):
        # Custom analysis: team momentum/trajectory
        momentum = []
        
        for team in standings_data['children'][0]['standings']['entries']:
            # Calculate recent form (W/L last N games)
            recent_record = self._calculate_recent_record(team, lookback_days)
            momentum.append({
                'team': team['team']['displayName'],
                'recent_record': recent_record
            })
        
        return momentum
```

---

**This code architecture shows the layered design and extension points available for building the dashboard and UX features.**
