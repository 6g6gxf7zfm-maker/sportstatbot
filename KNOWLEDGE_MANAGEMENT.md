
# Sports Knowledge Management System

Comprehensive organization and retrieval system for sports content, designed for professional sports journalism and analysis teams.

## 🎯 Features Overview

### 📁 Hierarchical Organization
- **Google Drive-style folder structure**
  - `/NFL/Weekly Digests/YYYY-MM-DD`
  - `/NBA/Features/Stars/LeBron`
  - `/Betting Insights/{Date}`
  - `/Injuries/Current Week`
- Automatic folder creation for leagues, dates, and players
- Nested folder support with unlimited depth

### 🏷️ Tagging & Metadata
- Apple Notes-style tagging: `#injury`, `#feature`, `#preview`
- Auto-tag suggestions based on content analysis
- Document metadata headers with league, date, authors, tags
- Tag correlation and relationship mapping
- Popular tags tracking

### 🔍 Advanced Search
- Full-text search across all documents
- **Search by statistics**: Find stories with xG>2, EPA/play>0.25, etc.
- Filter by league, type, tags, date range
- Player and team mention searches
- Matchup searches (find stories about Team A vs Team B)
- Fuzzy search with similarity matching

### ⚡ Quick Recall Agent
- Type player/team name → instantly find last 5 mentions
- Entity timeline views
- Cross-entity comparisons
- Statistics about entity coverage
- Batch recall for multiple entities

### 🗺️ Story Memory Map
- Auto-linking of related stories
- Visual story connection graphs
- Story clusters detection
- Correlation matrix (which teams appear together)
- Link strength calculation
- Relationship explanations

### 📚 Auto-Indexing
- Table of contents by week, sport, story type
- Team-specific indexes
- Player-specific indexes
- Master index generation
- Archive summaries ("This Week in Sports Intelligence")

### 🗄️ Archive Management
- Auto-archive documents after 30 days
- Organized archive by year-month
- Archive statistics and reports
- Restore archived documents
- Revision history cleanup
- Scheduled cleanup routines

### 📝 Version Control
- Revision history tracking
- Version labels: v1.0=Draft, v1.1=Edited, v2.0=Published
- Snapshot on every edit
- Change summary tracking
- Author tracking per revision

### 👥 Editor Dashboard
- Task management system
- Pending stories view
- Beat deadlines tracking
- Team workload distribution
- Weekly activity summaries
- Priority and status tracking

### 📤 Export Tools
- PDF export for offline briefings
- Markdown export with metadata
- JSON export for integrations
- Weekly briefing generator
- Player/team report generation
- Batch export capabilities

### 🔗 Cross-Sport Features
- Compare trends across leagues
- Multi-league indexes
- Cross-sport tagging
- League correlation analysis

## 🚀 Quick Start

### Installation

```bash
# System is already integrated into SportStatBot
# No additional installation needed
```

### Create Your First Document

```bash
python knowledge_cli.py create "Chiefs Dominate Bills in Thriller" \
  --league nfl \
  --type recap \
  --folder "/NFL/Weekly Digests/2025-11-08" \
  --author "John Doe" \
  --tags "chiefs,bills,playoff-implications" \
  --auto-tag \
  --auto-link
```

### Search for Content

```bash
# Text search
python knowledge_cli.py search "Patrick Mahomes" --league nfl --limit 10

# Search by stat
python knowledge_cli.py search "" --stat "xG>2" --league mls

# Search with filters
python knowledge_cli.py search "injury" \
  --league nba \
  --type injury_report \
  --tags "injury,roster-moves"
```

### Quick Recall

```bash
# Find mentions of a player
python knowledge_cli.py recall "LeBron James" --limit 5 --timeline

# Find mentions of a team
python knowledge_cli.py recall "Chiefs" --limit 10
```

### View Editor Dashboard

```bash
# Full dashboard
python knowledge_cli.py dashboard --weekly

# Filter by assignee
python knowledge_cli.py dashboard --assignee "John Doe"
```

## 📖 Usage Guide

### Creating Documents

#### Basic Document Creation

```python
from knowledge_manager import DocumentManager
from knowledge_manager.models import League, DocumentType
from datetime import datetime

dm = DocumentManager()

doc = dm.create_document(
    title="Lakers Extend Win Streak to 7",
    content="""The Lakers defeated the Celtics 115-110...""",
    league=League.NBA,
    document_type=DocumentType.RECAP,
    folder_path="/NBA/Weekly Digests/2025-11-08",
    authors=["John Doe"],
    tags={"lakers", "celtics", "win-streak"},
    season="2024-25"
)

print(f"Created document: {doc.doc_id}")
```

#### Auto-Tagging

```python
from knowledge_manager import MetadataManager

mm = MetadataManager()

content = "LeBron James suffered a minor ankle injury..."
title = "Lakers Star Questionable for Next Game"

suggested_tags = mm.auto_tag_document(content, title)
# Returns: {'injury', 'lakers', 'roster-moves'}
```

### Searching Documents

#### Text Search

```python
from knowledge_manager import SearchEngine
from knowledge_manager.models import League

se = SearchEngine()

# Simple search
results = se.search("touchdown pass")

# Advanced search
results = se.search(
    query="playoff implications",
    league=League.NFL,
    tags={"preview", "analysis"},
    date_from=datetime(2025, 11, 1),
    date_to=datetime(2025, 11, 8)
)
```

#### Search by Statistics

```python
# Find all stories mentioning xG > 2
results = se.search_by_stat(
    stat_name="xG",
    operator=">",
    value=2.0,
    league=League.MLS
)

# Find EPA/play mentions
results = se.search_by_stat("EPA", ">", 0.25)
```

#### Player/Team Search

```python
# Find all stories about a player
results = se.search_by_player("Patrick Mahomes", limit=20)

# Find matchup coverage
results = se.search_by_matchup("Chiefs", "Bills")
```

### Quick Recall

```python
from knowledge_manager import QuickRecallAgent

qr = QuickRecallAgent()

# Recall player mentions
result = qr.recall_player("LeBron James", limit=5)

print(result['summary'])
# "LeBron James mentioned in 5 recent documents. Latest: 'Lakers Win Again' (2025-11-08)"

for mention in result['mentions']:
    print(f"- {mention['title']} ({mention['date']})")

# Get entity timeline
timeline = qr.get_entity_timeline("Chiefs", limit=20)

# Compare two entities
comparison = qr.compare_entities("Mahomes", "Allen")
print(f"Common coverage: {comparison['common_mentions']} documents")
```

### Story Memory Map

```python
from knowledge_manager import StoryMemoryMap

smm = StoryMemoryMap()

# Auto-link a document
doc_id = "abc123..."
links_created = smm.auto_link_documents(doc_id)
print(f"Created {links_created} automatic links")

# View story map
story_map = smm.get_story_map(doc_id, depth=2)
print(f"Connected stories: {len(story_map['nodes'])}")

# Find correlation
matrix = smm.get_story_correlation_matrix("Chiefs")
print("Teams appearing with Chiefs:")
for team, count in matrix['co_occurrences'].items():
    print(f"  {team}: {count} times")

# Find story clusters
clusters = smm.find_story_clusters(min_cluster_size=3)
for cluster in clusters:
    print(f"Cluster: {cluster['size']} stories")
    print(f"  Teams: {cluster['common_teams']}")
    print(f"  Tags: {cluster['common_tags']}")
```

### Indexing

```python
from knowledge_manager.indexer import AutoIndexer

indexer = AutoIndexer()

# Weekly index
weekly_index = indexer.build_weekly_index(
    league=League.NFL,
    weeks_back=4
)

# Sport index
sport_index = indexer.build_sport_index()

# Story type index
type_index = indexer.build_story_type_index(league=League.NBA)

# Team index
team_index = indexer.build_team_index("Chiefs")

# Player index
player_index = indexer.build_player_index("LeBron James")

# Generate TOC
toc = indexer.generate_table_of_contents(
    league=League.NFL,
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 8)
)
print(toc)

# Archive summary
summary = indexer.generate_archive_summary(days_back=7)
print(summary)  # "This Week in Sports Intelligence"
```

### Archive Management

```python
from knowledge_manager import ArchiveManager

archiver = ArchiveManager()

# Auto-archive old documents
result = archiver.auto_archive(days_old=30, dry_run=False)
print(f"Archived {result['archived']} documents")

# Get archive stats
stats = archiver.get_archive_stats()
print(f"Total archived: {stats['total_archived']}")
print(f"Archive size: {stats['archive_size_mb']} MB")

# List archived docs
archived = archiver.list_archived_documents(year_month="2025-10")

# Restore document
success = archiver.restore_document(doc_id)

# Cleanup routines
cleanup_result = archiver.schedule_cleanup()
```

### Editor Dashboard

```python
from knowledge_manager import EditorDashboard
from datetime import datetime, timedelta

dashboard = EditorDashboard()

# Create task
task = dashboard.create_task(
    title="Review Chiefs-Bills recap",
    description="Fact-check stats and quotes",
    doc_id="abc123...",
    assignee="John Doe",
    priority="high",
    deadline=datetime.now() + timedelta(days=2)
)

# Get dashboard view
view = dashboard.get_dashboard_view(assignee="John Doe")

print(f"Pending tasks: {view['tasks']['total_pending']}")
print(f"Overdue: {view['tasks']['overdue']}")
print(f"Drafts: {view['documents']['drafts']}")

# Update task status
dashboard.update_task_status(task.task_id, "completed")

# Get weekly summary
summary = dashboard.get_weekly_summary(assignee="John Doe")
print(f"Completion rate: {summary['completion_rate']}%")

# Get team workload
workload = dashboard.get_team_workload()
for assignee, stats in workload.items():
    print(f"{assignee}: {stats['pending']} pending, {stats['completed']} completed")
```

### Exporting

```python
from knowledge_manager import DocumentExporter
from datetime import datetime, timedelta

exporter = DocumentExporter()

# Export single document to markdown
md_path = exporter.export_to_markdown(doc_id)

# Export to PDF-ready markdown
pdf_path = exporter.export_to_pdf_markdown(doc_id)
# Then convert: pandoc {pdf_path} -o output.pdf

# Export weekly briefing
briefing_path = exporter.export_weekly_briefing(
    league="nfl",
    week_start=datetime.now() - timedelta(days=7),
    week_end=datetime.now()
)

# Export search results
results = se.search("playoff")
export_path = exporter.export_search_results(results, "playoff_stories.md")

# Export player report
mentions = qr.recall_player("LeBron James", limit=50)
report_path = exporter.export_player_report("LeBron James", mentions['mentions'])

# List all exports
exports = exporter.list_exports()
for export in exports:
    print(f"{export['filename']} - {export['size_kb']} KB")
```

## 🗂️ Folder Structure

```
knowledge_manager/
├── database/              # SQLite database
│   └── sports_knowledge.db
├── storage/               # Document content files
│   ├── {doc_id}.md
│   └── ...
├── archive/               # Archived documents
│   ├── 2025-10/
│   │   ├── {doc_id}.md
│   │   └── {doc_id}_metadata.json
│   └── 2025-11/
└── exports/               # Exported files
    ├── briefings/
    ├── reports/
    └── ...
```

## 📊 Data Models

### Document Metadata

```python
{
    "league": "nfl",
    "date": "2025-11-08T10:30:00",
    "authors": ["John Doe"],
    "tags": ["chiefs", "bills", "playoff"],
    "data_timestamp": "2025-11-08T10:30:00",
    "document_type": "recap",
    "version": "2.0",  # Draft=1.0, Edited=1.1, Published=2.0
    "season": "2024-25",
    "week": 10,
    "teams": ["Chiefs", "Bills"],
    "players": ["Patrick Mahomes", "Josh Allen"],
    "stats_mentioned": {
        "yards": 368,
        "touchdowns": 3,
        "EPA": 0.28
    }
}
```

## 🔧 Advanced Features

### Custom Search Filters

```python
from knowledge_manager import SearchEngine

se = SearchEngine()

# Complex advanced search
results = se.advanced_search({
    'text': 'playoff implications',
    'league': League.NFL,
    'tags': {'preview', 'analysis'},
    'teams': ['Chiefs', 'Bills'],
    'players': ['Mahomes'],
    'stats': {
        'EPA': ('>', 0.25),
        'yards': ('>', 300)
    },
    'date_range': (datetime(2025, 11, 1), datetime(2025, 11, 8)),
    'version': '2.0'  # Published only
})
```

### Trending Topics

```python
# Get trending topics from last 7 days
trending = se.get_trending_topics(days=7, limit=10)

for topic in trending:
    print(f"{topic['entity']} ({topic['type']}): {topic['mentions']} mentions")
```

### Tag Management

```python
from knowledge_manager import MetadataManager

mm = MetadataManager()

# Get popular tags
popular = mm.get_popular_tags(limit=20)

# Get related tags
related = mm.get_related_tags('injury', limit=10)
# Tags that often appear with 'injury'

# Merge tags (rename)
mm.merge_tags('injuries', 'injury')

# Get tag statistics
stats = mm.get_tag_stats()
print(f"Total tags: {stats['total_tags']}")
print(f"Most used: {stats['most_used_tag']} ({stats['most_used_count']} uses)")
```

## 📝 Best Practices

### Document Organization

1. **Use consistent folder paths**
   ```
   /{League}/{Category}/{Subcategory}
   /NFL/Weekly Digests/2025-11-08
   /NBA/Features/Stars/LeBron James
   ```

2. **Tag appropriately**
   - Use specific tags: `#chiefs-offense` not just `#chiefs`
   - Include type tags: `#preview`, `#recap`, `#injury`
   - Add contextual tags: `#playoff-implications`, `#mvp-race`

3. **Auto-tag first, then refine**
   ```python
   tags = mm.auto_tag_document(content, title)
   tags.add('custom-tag')  # Add your own
   ```

### Search Optimization

1. **Start broad, then narrow**
   ```python
   results = se.search("touchdown")  # Broad
   results = se.search("touchdown", league=League.NFL, tags={'red-zone'})  # Narrow
   ```

2. **Use entity searches for people/teams**
   ```python
   # Better than text search
   results = se.search_by_player("Mahomes")
   ```

3. **Leverage stats search**
   ```python
   # Find exceptional performances
   results = se.search_by_stat("yards", ">", 400)
   ```

### Workflow

1. **Draft → Edit → Publish**
   ```python
   # Create as draft (v1.0)
   doc = dm.create_document(...)

   # Edit
   dm.update_document(doc.doc_id, content=new_content)

   # Publish
   dm.publish_document(doc.doc_id)
   ```

2. **Use tasks for collaboration**
   ```python
   dashboard.create_document_task(
       doc_id,
       task_type="review",
       assignee="editor@example.com"
   )
   ```

3. **Archive regularly**
   ```python
   # Schedule monthly
   archiver.auto_archive(days_old=30)
   archiver.cleanup_old_revisions(keep_recent=10)
   ```

## 🎨 CLI Examples

### Complete Workflows

```bash
# Morning workflow: Create game recap
python knowledge_cli.py create "Chiefs Top Bills in Thriller" \
  --league nfl \
  --type recap \
  --folder "/NFL/Weekly Digests/2025-11-08" \
  --file game_recap.txt \
  --author "Sports Desk" \
  --auto-tag \
  --auto-link

# Find recent Chiefs coverage
python knowledge_cli.py recall "Chiefs" --limit 10 --timeline

# Check dashboard before deadline
python knowledge_cli.py dashboard --assignee "editor@example.com" --weekly

# Export weekly briefing
python knowledge_cli.py export --weekly --league nfl

# Generate archive summary
python knowledge_cli.py index archive --days 7

# Monthly cleanup
python knowledge_cli.py archive cleanup
```

## 🔍 Troubleshooting

### Database Issues

```python
# Reset database (careful!)
from knowledge_manager.database_handler import DatabaseHandler
db = DatabaseHandler()
# Database will auto-initialize on first use
```

### Search Not Finding Results

- Check date ranges
- Try broader queries
- Verify league/type filters
- Check if documents are archived

### Link Creation

```python
# Manually create link
from knowledge_manager import StoryMemoryMap
smm = StoryMemoryMap()
smm._create_link(doc1_id, doc2_id, "related_game", strength=0.8)
```

## 📚 API Reference

See inline documentation in each module:

- `DocumentManager` - knowledge_manager/document_manager.py
- `SearchEngine` - knowledge_manager/search_engine.py
- `QuickRecallAgent` - knowledge_manager/quick_recall.py
- `StoryMemoryMap` - knowledge_manager/story_memory_map.py
- `ArchiveManager` - knowledge_manager/archive_manager.py
- `EditorDashboard` - knowledge_manager/dashboard.py
- `DocumentExporter` - knowledge_manager/exporter.py

## 🚀 Integration with SportStatBot

The knowledge management system integrates seamlessly with SportStatBot's report generation:

```python
from report_generator import ReportGenerator
from knowledge_manager import DocumentManager, FolderManager
from knowledge_manager.models import League, DocumentType
from datetime import datetime

# Generate report
generator = ReportGenerator()
report = generator.generate_full_report(['nfl'])

# Save to knowledge base
dm = DocumentManager()
fm = FolderManager()

# Create folder
folder = fm.create_date_folder("/NFL/Weekly Digests", datetime.now())

# Save report as document
doc = dm.create_document(
    title=f"NFL Report - {datetime.now().strftime('%Y-%m-%d')}",
    content=report,
    league=League.NFL,
    document_type=DocumentType.WEEKLY_DIGEST,
    folder_path=folder.path,
    authors=["SportStatBot"],
    tags={"automated", "weekly-digest"}
)

# Auto-link
from knowledge_manager import StoryMemoryMap
smm = StoryMemoryMap()
smm.auto_link_documents(doc.doc_id)
```

---

**Built for professional sports journalism teams** 🏆

For questions or issues, see the main SportStatBot README.
