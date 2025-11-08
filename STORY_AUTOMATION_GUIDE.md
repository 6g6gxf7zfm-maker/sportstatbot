## Story Creation & Writing Automation Guide

Complete guide to SportStatBot's story automation features for automated sports content generation, formatting, and distribution.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Detailed Features](#detailed-features)
5. [Export & Sync](#export--sync)
6. [Writing Styles & Perspectives](#writing-styles--perspectives)
7. [Analysis & Rating](#analysis--rating)
8. [Advanced Features](#advanced-features)
9. [Configuration](#configuration)
10. [API Reference](#api-reference)

---

## Overview

The Story Automation module transforms SportStatBot from a data aggregator into a full-featured sports journalism automation platform. It generates narrative-driven stories with multiple writing styles, automatic exports, and comprehensive analysis.

### Key Capabilities

- **AI-Powered Narratives**: Generate compelling stories from raw sports data
- **Multiple Writing Styles**: Analytical, storytelling, fan voice, and more
- **Automatic Organization**: Export to Google Docs and Apple Notes with smart folder structure
- **Content Enhancement**: Sidebars, pull quotes, trivia, and timelines
- **Quality Control**: Automated story rating (A-F grading system)
- **Narrative Continuity**: Maintain context across stories with "Narrative Bridge"

---

## Features

### Content Generation

#### 1. Auto-Title Generator (SEO Optimized)
Generate compelling, search-optimized titles automatically.

```bash
python story_cli.py --sports nfl --headline-tone bold
```

**Tone Options:**
- `neutral`: Objective, factual reporting
- `bold`: Strong, assertive statements
- `tabloid`: Sensational, attention-grabbing
- `poetic`: Lyrical, metaphorical language
- `data_driven`: Numbers-first, statistically focused

**Example Output:**
```
Data-driven: "NFL Stats & Analysis: Week 12 Performance Breakdown"
Bold: "Chiefs Unstoppable: AFC Power Rankings Shift Dramatically"
Tabloid: "SHOCKING UPSETS: You Won't Believe What Happened!"
```

#### 2. Story Summary Generator (TL;DR)
Auto-generate concise summaries at the top of every story.

**Formats:**
- **Bullets**: Key points in bullet format
- **Paragraph**: Narrative summary
- **Numbers**: Numbered list of highlights

```python
from story_automation.generators.summary_generator import SummaryGenerator

summary_gen = SummaryGenerator()
summary = summary_gen.generate_summary(context, sport='nfl', style='bullets')
```

#### 3. Dynamic Sidebars
Automatically generate contextual sidebars:

- **3 Numbers That Matter**: Top 3 statistical highlights
- **By the Data**: Trend analysis with stats
- **Key Stats**: Quick facts and figures
- **Players to Watch**: Featured player performances
- **Betting Corner**: Value bets and insights

#### 4. Pull Quote Auto-Suggester
Extract impactful quotes automatically based on:
- Impact markers (unprecedented, historic, remarkable)
- Statistical significance
- Emotional language
- Superlatives

#### 5. Trivia Injection
Add fun facts and historical context:

```python
from story_automation.generators.trivia_generator import TriviaGenerator

trivia_gen = TriviaGenerator()
trivia = trivia_gen.get_trivia(sport='nba', context=story_context)
```

#### 6. Event Timeline Builder
Generate chronological timelines of events:

**Formats:**
- **Vertical**: Traditional timeline view
- **Horizontal**: Compact horizontal layout
- **Compact**: List format with timestamps

---

## Export & Sync

### Google Docs Exporter

Automatically export stories to Google Docs with organized folder structure.

**Folder Organization:**
```
SportStatBot/
  ├── NFL/
  │   ├── 2024/
  │   │   ├── 11-November/
  │   │   │   ├── digests/
  │   │   │   ├── features/
  │   │   │   ├── previews/
  │   │   │   └── betting_insights/
```

**Setup:**
```bash
# Set environment variables
export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
export GOOGLE_ROOT_FOLDER_ID=your_folder_id

# Export story
python story_cli.py --sports nfl --export google_docs
```

**Features:**
- Preserves markdown formatting (bold, italic, headings)
- Maintains emoji formatting
- Auto-generates document titles
- Creates folder structure automatically
- Batch export support

### Apple Notes Syncer

Sync stories to Apple Notes with automatic organization.

**Folder Structure:**
```
SportStatBot/
  ├── NFL/
  │   ├── Daily Digests/
  │   ├── Feature Stories/
  │   ├── Game Previews/
  │   └── Betting Insights/
```

**Usage:**
```bash
python story_cli.py --sports nba --export apple_notes
```

**Features:**
- macOS native integration
- iCloud sync across devices
- Rich text formatting
- HTML content support

### Markdown-to-Google Docs Converter

Preserves formatting when converting to Google Docs:

- **Bold** text (`**bold**` or `__bold__`)
- _Italic_ text (`*italic*` or `_italic_`)
- [Links](url) - `[text](url)`
- Headings (# H1, ## H2, etc.)
- Bullet lists
- Emojis 🎯

---

## Writing Styles & Perspectives

### Base Styles

#### 1. Analytical (Default)
Data-driven, objective analysis with statistical insights.

```bash
python story_cli.py --sports nfl --style analytical
```

**Characteristics:**
- Emphasis on statistics and trends
- Objective tone
- Detailed performance metrics
- Comparative analysis

#### 2. Storytelling
Narrative-focused with dramatic arcs and character development.

```bash
python story_cli.py --sports nba --style storytelling
```

**Characteristics:**
- Narrative structure
- Emotional engagement
- Character development
- Story arcs

#### 3. Fan Voice
Passionate, enthusiastic fan perspective with emotional engagement.

```bash
python story_cli.py --sports nfl --style fan_voice
```

**Characteristics:**
- Enthusiastic tone
- Emotional language
- Fan-centric perspective
- Engaging and exciting

### Perspective Overlays

#### 1. Coach Lens
Tactical and strategic emphasis, X's and O's focus.

```bash
python story_cli.py --sports nfl --perspective coach_lens
```

**Emphasis:**
- Game planning and strategy
- Tactical execution
- Player positioning
- Scheme analysis

#### 2. Casual Fan
Simplified explanations, jargon-free, accessible language.

```bash
python story_cli.py --sports nba --perspective casual_fan
```

**Features:**
- Simple, clear language
- Jargon explained inline
- Context provided for stats
- Accessible to newcomers

#### 3. Academic Mode
Scholarly analysis with references and deep tactical breakdowns.

```bash
python story_cli.py --sports nfl --perspective academic
```

**Features:**
- Deep tactical analysis
- Statistical methodology
- Historical context
- Referenced insights

### Recast Mode

Rewrite the same story in multiple styles simultaneously.

```bash
python story_cli.py --sports nfl --recast analytical storytelling fan_voice
```

**Output:**
Generates 3 complete versions of the same story, each with a different style.

---

## Analysis & Rating

### Editor Rating System

Automated A-F grading on:
- **Clarity** (30%): Readability and comprehension
- **Insight** (35%): Analysis depth and value
- **Structure** (25%): Organization and flow
- **Engagement** (10%): Reader interest and appeal

**Grade Scale:**
- **A (90-100)**: Excellent - publication ready
- **B (80-89)**: Good - minor improvements needed
- **C (70-79)**: Fair - significant improvements needed
- **D (60-69)**: Poor - major revision required
- **F (0-59)**: Failing - complete rewrite needed

```bash
python story_cli.py --sports nfl --rate
```

**Example Output:**
```
📊 STORY RATING: B (84.5/100)

Score Breakdown:
  Clarity: 88.0
  Insight: 82.5
  Structure: 85.0
  Engagement: 83.0

Feedback:
  • Strong analytical depth and insights
  • Well-structured with strong organization
  • Consider adding more dynamic language for engagement
```

### Auto-Compare (Diff View)

Track changes between story versions.

**Usage:**
```python
from story_automation.analyzers.diff_analyzer import DiffAnalyzer

diff_analyzer = DiffAnalyzer()

# Save versions
v1 = diff_analyzer.save_version(story_v1, 'nfl', 'morning')
v2 = diff_analyzer.save_version(story_v2, 'nfl', 'evening')

# Compare
comparison = diff_analyzer.compare_versions(v1, v2, 'nfl')

# Generate diff view
diff_view = diff_analyzer.generate_diff_view(comparison, 'markdown')
```

**Features:**
- Line-by-line comparison
- Change statistics (added, removed, modified)
- Multiple output formats (markdown, HTML, unified diff)
- Version history tracking

---

## Advanced Features

### Narrative Bridge

Maintain context and continuity across stories.

**Features:**
- Track team storylines over time
- Monitor player performance trends
- Identify continuing narratives
- Generate contextual introductions

**Usage:**
```python
from story_automation.analyzers.context_manager import ContextManager

context_mgr = ContextManager()

# Get narrative bridge
bridge = context_mgr.get_narrative_bridge('nfl', lookback_days=7)

# Get team storyline
storyline = context_mgr.get_team_storyline('Kansas City Chiefs', 'nfl')
```

### Section Shuffler

Reorganize content sections for optimal narrative flow.

**Strategies:**
- Importance-based (most significant first)
- Chronological (time-ordered events)
- Thematic (grouped by topic)
- Engagement-based (most compelling first)

### Data Footnote Inserter

Add source citations and timestamps automatically.

```python
from story_automation.formatters.footnote_inserter import FootnoteInserter

footnote = FootnoteInserter()

# Add footnote to stat
stat_with_footnote = footnote.add_stat_footnote(
    "Patrick Mahomes threw for 350 yards",
    source="ESPN API"
)
```

**Output:**
```
Patrick Mahomes threw for 350 yards[^1]

[^1]: Source: ESPN API - Data as of 2024-11-08 14:30 EST
```

### Inline Stat Highlighting

Auto-colorize and emphasize statistics.

**Features:**
- Color-coded highs/lows
- Emoji indicators (📈📉🔥❄️)
- Bold emphasis for key numbers
- Percentage highlighting

```python
from story_automation.formatters.stat_highlighter import StatHighlighter

highlighter = StatHighlighter()

# Highlight stats in text
highlighted = highlighter.highlight_stats(
    text="The Chiefs scored 42 points with 87% completion rate",
    format_type='markdown'
)
```

**Output:**
```
The Chiefs scored **42** points with 📊 **87%** completion rate
```

### Auto-Subhead Generation

Generate subheadings for longform content automatically.

**Logic:**
- Break content into logical sections
- Generate descriptive subheads
- Maintain parallel structure
- SEO-friendly formatting

---

## Configuration

### Environment Variables

```bash
# Google API Configuration
export GOOGLE_CREDENTIALS_PATH=/path/to/google-credentials.json
export GOOGLE_ROOT_FOLDER_ID=your_google_drive_folder_id

# Claude API (for AI narrative generation)
export ANTHROPIC_API_KEY=your_anthropic_api_key

# Story Preferences
export STORY_DEFAULT_STYLE=analytical
export STORY_DEFAULT_TONE=neutral
export INCLUDE_SIDEBARS=true
export INCLUDE_TRIVIA=false
```

### Configuration File

Create `story_config.json`:

```json
{
  "default_style": "analytical",
  "default_tone": "neutral",
  "features": {
    "sidebars": true,
    "pullquotes": true,
    "trivia": false,
    "footnotes": true,
    "timeline": false
  },
  "export": {
    "default_format": "local",
    "google_docs": {
      "auto_export": false,
      "folder_structure": "sport/year/month/type"
    },
    "apple_notes": {
      "auto_sync": false
    }
  },
  "rating": {
    "auto_rate": true,
    "min_passing_grade": 70
  }
}
```

---

## API Reference

### StoryGenerator

```python
from story_automation.generators.story_generator import StoryGenerator

story_gen = StoryGenerator(api_key='your_api_key')

story = story_gen.generate_story(
    sport_data=data,
    sport_name='nfl',
    style='analytical',           # analytical, storytelling, fan_voice
    perspective='coach_lens',      # None, coach_lens, casual_fan, academic
    headline_tone='bold',          # neutral, bold, tabloid, poetic, data_driven
    include_sidebar=True,
    include_pullquotes=True,
    include_trivia=False
)

# Recast into multiple styles
recast_versions = story_gen.recast_story(
    story,
    target_styles=['analytical', 'storytelling', 'fan_voice']
)
```

### GoogleDocsExporter

```python
from story_automation.exporters.google_docs_exporter import GoogleDocsExporter

exporter = GoogleDocsExporter(
    credentials_path='/path/to/creds.json',
    root_folder_id='folder_id'
)

# Export single story
result = exporter.export_story(
    story=story,
    sport='nfl',
    story_type='digests',    # digests, features, previews, betting_insights
    title='Custom Title'     # Optional
)

# Batch export
results = exporter.batch_export(stories, sport='nfl')

# List exported docs
docs = exporter.list_exported_docs(sport='nfl', story_type='digests')
```

### StoryRater

```python
from story_automation.analyzers.story_rater import StoryRater

rater = StoryRater()

# Rate single story
rating = rater.rate_story(story, context=sport_data)

# Access results
print(f"Grade: {rating['letter_grade']}")
print(f"Score: {rating['overall_score']}")
print(f"Clarity: {rating['scores']['clarity']}")
print(f"Insight: {rating['scores']['insight']}")
print(f"Feedback: {rating['feedback']}")

# Batch rate
ratings = rater.batch_rate(stories)

# Generate report
report = rater.generate_report(ratings)
print(report)
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Generate analytical story with all features
python story_cli.py \
  --sports nfl nba \
  --style analytical \
  --headline-tone data_driven \
  --sidebars \
  --pullquotes \
  --trivia \
  --rate \
  --export google_docs

# 2. Generate fan-friendly story with casual perspective
python story_cli.py \
  --sports nba \
  --style fan_voice \
  --perspective casual_fan \
  --headline-tone bold \
  --export apple_notes

# 3. Generate professional analysis with coach perspective
python story_cli.py \
  --sports nfl \
  --style analytical \
  --perspective coach_lens \
  --headline-tone neutral \
  --sidebars \
  --rate

# 4. Recast story into all styles
python story_cli.py \
  --sports nfl \
  --recast analytical storytelling fan_voice coach_lens casual_fan academic

# 5. Save to custom file
python story_cli.py \
  --sports nba \
  --style storytelling \
  --output nba_story.json
```

### Python API Example

```python
from story_cli import StoryAutomationCLI

# Initialize CLI
cli = StoryAutomationCLI()

# Generate story
stories = cli.generate_story(
    sports=['nfl', 'nba'],
    style='analytical',
    perspective='coach_lens',
    headline_tone='bold',
    include_sidebars=True,
    include_pullquotes=True,
    include_trivia=True,
    export_format='google_docs',
    rate_story=True
)

# Print results
for sport, story in stories.items():
    print(f"\n{sport.upper()} Story:")
    cli.print_story(story)

    if story.get('rating'):
        rating = story['rating']
        print(f"Rating: {rating['letter_grade']} ({rating['overall_score']}/100)")
```

---

## Troubleshooting

### Google Docs Export Issues

**Problem**: "Google credentials not configured"
**Solution**: Set `GOOGLE_CREDENTIALS_PATH` environment variable

**Problem**: "Permission denied"
**Solution**: Ensure service account has access to target folder

### Apple Notes Sync Issues

**Problem**: "Apple Notes not available"
**Solution**: Only works on macOS with Notes.app installed

**Problem**: "Folder creation failed"
**Solution**: Check Notes.app permissions in System Preferences

### Story Generation Issues

**Problem**: Low story ratings
**Solution**:
- Ensure sufficient source data is available
- Try different writing styles
- Enable sidebars and pull quotes for better structure

**Problem**: Missing context/continuity
**Solution**: Ensure Context Manager is properly saving context between runs

---

## Best Practices

1. **Use appropriate styles for audience**:
   - Analytical for professional readers
   - Fan Voice for casual audiences
   - Storytelling for narrative-driven content

2. **Enable sidebars for data-heavy stories**: Improves clarity scores

3. **Rate stories before publishing**: Ensures quality standards

4. **Maintain narrative continuity**: Use Context Manager for ongoing storylines

5. **Organize exports systematically**: Use Google Docs folder structure

6. **Recast important stories**: Generate multiple versions for different platforms

---

## Future Enhancements

- AI-powered narrative generation with Claude API
- Multi-language support
- Video script generation
- Social media auto-posting
- Email newsletter formatting
- WordPress integration
- Real-time story updates
- Collaborative editing features

---

For more information, see the main [README.md](README.md) or [USAGE_GUIDE.md](USAGE_GUIDE.md).
