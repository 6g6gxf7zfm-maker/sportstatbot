# SportStatBot Search & Query Engine

Natural language search and query system for sports statistics and reports.

## Features

### 1. Natural Language Question Engine
Ask questions in plain English and get intelligent answers:
```bash
python search_cli.py query "Which teams have the best net rating since March?"
python search_cli.py query "Show me Patrick Mahomes stats from last week"
python search_cli.py query "What is the Celtics win streak?"
```

### 2. "Ask the Story" - Semantic Search
Search through past reports and digests using semantic understanding:
```bash
python search_cli.py search "Celtics injuries"
python search_cli.py search "MVP candidates" --limit 10
python search_cli.py search "playoff race eastern conference"
```

### 3. Stats-to-Story Generator
Convert raw statistics into engaging narratives:
```bash
python search_cli.py story player=Mahomes passing_yards=350 touchdowns=4
python search_cli.py story team=Chiefs result=won score="31-28"
```

### 4. Keyword Search (Fuzzy and Semantic)
Intelligent search across all indexed content with typo tolerance.

### 5. Context Recall
Find historical occurrences of events:
```bash
python search_cli.py history "lost 3 straight" --team Celtics
python search_cli.py history "triple double" --player "LeBron James"
```

### 6. Comparative Search
Compare players, teams, or time periods:
```bash
python search_cli.py compare "Patrick Mahomes" "Josh Allen" --aspect passing
python search_cli.py compare Chiefs Ravens --aspect offense
```

### 7. "Explain the Stat" Glossary
Comprehensive glossary of sports statistics:
```bash
python search_cli.py explain EPA
python search_cli.py explain "TS%"
python search_cli.py explain wRC+

# Browse glossary
python search_cli.py glossary --sport nfl
python search_cli.py glossary --search efficiency
python search_cli.py glossary --list-all
```

### 8. Drill Down Agent
Click on any bullet point to see full underlying data (API feature).

### 9. Auto Cross-Check
Automatically verify stat consistency across multiple sources (API feature).

### 10. Search Filters
Filter searches by:
- Player name
- Team name
- League/Sport
- Time window (last 7 days, this month, since March, etc.)
- Story type (injury, trade, game, analysis)
- Result (win/loss)
- Statistical thresholds

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The search engine will automatically initialize on first use.

## Usage

### Command Line Interface

#### Query (Natural Language)
```bash
python search_cli.py query "Which teams have the best offense?"
python search_cli.py query "Who leads the NBA in scoring?"
python search_cli.py query "What is EPA in football?"
```

#### Search (Semantic Search)
```bash
python search_cli.py search "injuries this week"
python search_cli.py search "trade deadline moves"
```

#### Explain Stats
```bash
python search_cli.py explain EPA
python search_cli.py explain PER
python search_cli.py explain xG
```

#### Compare
```bash
python search_cli.py compare "Player A" "Player B"
python search_cli.py compare TeamA TeamB --aspect defense
```

#### Context Recall
```bash
python search_cli.py history "championship win" --team Lakers
```

#### Generate Story
```bash
python search_cli.py story player=Curry points=45 threes=8 team=Warriors
```

#### Browse Glossary
```bash
# List all stats
python search_cli.py glossary --list-all

# Search glossary
python search_cli.py glossary --search "shooting"

# View stats for a sport
python search_cli.py glossary --sport nba
```

#### View Statistics
```bash
python search_cli.py stats
```

### Python API

```python
from search_engine import SportStatSearchEngine
from data_fetchers.espn_fetcher import ESPNFetcher

# Initialize
fetcher = ESPNFetcher()
engine = SportStatSearchEngine(data_fetcher=fetcher)

# Query
result = engine.query("Which teams have the best net rating?")

# Search past reports
results = engine.ask_the_story("Celtics injuries", top_k=5)

# Explain a stat
explanation = engine.explain_stat("EPA")

# Compare entities
comparison = engine.compare("Patrick Mahomes", "Josh Allen")

# Context recall
last_time = engine.find_last_occurrence("lost 3 straight", team="Celtics")

# Generate story
story = engine.stats_to_story({
    'player': 'Patrick Mahomes',
    'stats': {'passing_yards': 350, 'touchdowns': 4},
    'team': 'Chiefs'
})

# Index a report for searchability
engine.index_report({
    'id': 'report_123',
    'sport': 'nfl',
    'date': '2025-11-08',
    'content': 'Report content here...',
    'teams': ['Chiefs', 'Raiders'],
    'players': ['Patrick Mahomes']
})

# Cross-check a stat
verification = engine.cross_check_stat(
    stat_name='passing_yards',
    value=350,
    entity='Patrick Mahomes',
    context={'date': '2025-11-08'}
)
```

## Stats Glossary

The search engine includes comprehensive definitions for:

### NFL Stats
- **EPA** - Expected Points Added
- **CPOE** - Completion Percentage Over Expected
- **DVOA** - Defense-adjusted Value Over Average
- **QBR** - Total Quarterback Rating

### NBA Stats
- **TS%** - True Shooting Percentage
- **PER** - Player Efficiency Rating
- **BPM** - Box Plus-Minus
- **USG%** - Usage Rate
- **NetRtg** - Net Rating

### MLB Stats
- **wRC+** - Weighted Runs Created Plus
- **WAR** - Wins Above Replacement
- **FIP** - Fielding Independent Pitching
- **OPS+** - On-base Plus Slugging Plus
- **BABIP** - Batting Average on Balls In Play

### NHL Stats
- **xGF%** - Expected Goals For Percentage
- **Corsi** - Corsi For Percentage
- **Fenwick** - Fenwick For Percentage
- **PDO** - Team Luck Indicator
- **GAR** - Goals Above Replacement

### Soccer Stats
- **xG** - Expected Goals
- **xA** - Expected Assists
- **PPDA** - Passes Per Defensive Action

## Architecture

The search engine is composed of several specialized components:

1. **QueryParser** - Parses natural language into structured queries
2. **SemanticSearchEngine** - Vector-based semantic search using embeddings
3. **StatsGlossary** - Comprehensive stats definitions
4. **SearchFilters** - Powerful filtering system
5. **ContextRecall** - Historical event lookup
6. **ComparativeSearch** - Entity comparison engine
7. **StoryGenerator** - Stats-to-narrative conversion
8. **DrillDownAgent** - Detailed data exploration
9. **CrossCheckVerifier** - Multi-source stat verification
10. **ReportStorage** - Persistent storage and indexing

## Data Storage

Reports and search indices are stored in:
- `./search_data/` - Vector embeddings and indices
- `./reports_db/` - TinyDB database with reports

To export/import data:
```python
# Export
engine.report_storage.export_to_file('backup.json')

# Import
engine.report_storage.import_from_file('backup.json')
```

## Advanced Features

### Custom Filters

```python
from search_engine import FilterBuilder

# Build custom filter pipeline
pipeline = FilterBuilder.build_custom(
    sport='nfl',
    teams=['Chiefs', 'Ravens'],
    last_n_days=7
)

# Apply to data
filtered = pipeline.apply(data)
```

### Indexing Reports

```python
# Index a complete report
engine.index_report({
    'id': 'nfl_week10_2025',
    'sport': 'nfl',
    'date': '2025-11-08',
    'content': 'Full report text...',
    'sections': [
        {
            'title': 'Key Trends',
            'content': 'Section content...',
            'type': 'trends'
        }
    ],
    'teams': ['Chiefs', 'Bills', 'Ravens'],
    'players': ['Patrick Mahomes', 'Josh Allen']
})
```

### Drill Down

```python
# Drill down into a bullet point
details = engine.drill_down_bullet(
    "Patrick Mahomes - 368 passing yards",
    context={'sport': 'nfl', 'date': '2025-11-08'}
)
```

### Smart Completion

```python
# Get writing suggestions
completions = engine.complete_prompt(
    "Patrick Mahomes has been on fire lately,",
    context={'player': 'Patrick Mahomes', 'team': 'Chiefs'}
)
```

## Configuration

The search engine can be configured via initialization:

```python
engine = SportStatSearchEngine(
    data_fetcher=my_fetcher,
    storage_path='./custom_storage'
)
```

## Performance

- Semantic search uses lightweight `all-MiniLM-L6-v2` model
- ChromaDB for efficient vector storage
- TinyDB for lightweight report storage
- Supports thousands of indexed reports

## Examples

### Example 1: Finding Team Trends
```bash
python search_cli.py query "Which NBA teams are on winning streaks?"
```

### Example 2: Player Comparison
```bash
python search_cli.py compare "Stephen Curry" "Damian Lillard" --aspect "three point shooting"
```

### Example 3: Historical Context
```bash
python search_cli.py history "30 point game" --player "Kevin Durant"
```

### Example 4: Stat Explanation
```bash
python search_cli.py explain "TS%"
```

Output:
```
**True Shooting Percentage (TS%)**

*NBA | Advanced*

**Definition:** Shooting efficiency that accounts for 2-pointers, 3-pointers, and free throws

**Formula:** PTS / (2 × (FGA + 0.44 × FTA))

**Typical Range:** 40% to 70%

**Context:** Better than FG% because it values 3-pointers and free throws appropriately

**Example:** 60% TS means very efficient scoring

**Good Value:** > 58% is above average
```

### Example 5: Generate Story
```bash
python search_cli.py story player="Patrick Mahomes" passing_yards=368 touchdowns=3 team=Chiefs context=positive
```

Output:
```
Patrick Mahomes put on a show with 368.0 passing yards and 3.0 touchdowns,
showcasing elite-level play.
```

## Troubleshooting

### Missing Dependencies
If you see errors about missing packages:
```bash
pip install sentence-transformers chromadb tinydb rapidfuzz
```

### No Indexed Data
The search engine needs indexed reports to search. Index reports using:
```python
engine.index_report(report_data)
```

### Slow First Query
The first query may be slow as the embedding model loads. Subsequent queries will be fast.

## Contributing

The search engine is modular and extensible:

- Add new stat definitions to `search_engine/stats_glossary.py`
- Extend query patterns in `search_engine/query_parser.py`
- Add custom filters in `search_engine/search_filters.py`
- Implement new story templates in `search_engine/story_generator.py`

## License

Part of SportStatBot project.
