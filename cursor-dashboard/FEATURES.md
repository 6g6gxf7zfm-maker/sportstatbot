# SportStatBot Cursor Dashboard - Feature Documentation

Complete feature breakdown and usage guide for the Cursor Dashboard.

## Table of Contents
1. [Custom Dashboard](#custom-dashboard)
2. [Command Palette](#command-palette)
3. [Story Templates](#story-templates)
4. [Advanced Editor](#advanced-editor)
5. [AI Co-Author](#ai-co-author)
6. [Writing Feedback](#writing-feedback)
7. [Real-time Proofreading](#real-time-proofreading)
8. [Fact Checking](#fact-checking)
9. [Agent Logs](#agent-logs)
10. [Writing History](#writing-history)
11. [Export System](#export-system)

---

## Custom Dashboard

### League Tabs
**Location**: Top header bar

**Supported Leagues**:
- NFL (National Football League)
- NBA (National Basketball Association)
- MLB (Major League Baseball)
- NHL (National Hockey League)
- MLS (Major League Soccer)
- Soccer (International)
- Golf (PGA Tour)

**Usage**:
1. Click any league tab to switch context
2. All data, stories, and suggestions auto-update
3. Story queue filters to selected league
4. Color-coded by league for visual organization

**Features**:
- Instant switching (no page reload)
- Persistent selection across sessions
- Real-time data updates per league
- Independent story queues per league

---

## Command Palette

**Shortcut**: `⌘K` (Mac) or `Ctrl+K` (Windows/Linux)

### Available Commands

#### Generate Category
| Command | Shortcut | Description |
|---------|----------|-------------|
| Generate Digest | `⌘G D` | Create comprehensive sports digest |
| Generate Preview | `⌘G P` | Create game preview |
| Generate Betting | `⌘G B` | Create betting insights |

#### Export Category
| Command | Shortcut | Description |
|---------|----------|-------------|
| Export to Google Docs | `⌘G` | Export current story to Google Docs |
| Export as Markdown | - | Download story as .md file |

#### Data Category
| Command | Shortcut | Description |
|---------|----------|-------------|
| Run Simulation | `⌘R` | Simulate game outcomes |
| Refresh Data | `⌘⇧R` | Fetch latest stats and scores |

#### Settings Category
| Command | Shortcut | Description |
|---------|----------|-------------|
| Open Settings | - | Configure preferences |

### Usage Tips
1. **Fuzzy search**: Type partial words (e.g., "gen dig" for "Generate Digest")
2. **Arrow keys**: Navigate through commands
3. **Enter**: Execute selected command
4. **Escape**: Close palette

---

## Story Templates

### Available Templates

#### 1. Daily Digest
**Length**: 800-1200 words
**Purpose**: Comprehensive overview of all games, trends, and performances

**Includes**:
- Game recaps with scores
- Standout player performances
- Team trends (hot/cold streaks)
- Injury updates
- Must-watch matchups

**Best For**: Morning roundups, daily newsletters

---

#### 2. Game Preview
**Length**: 400-600 words
**Purpose**: Detailed preview of upcoming matchups

**Includes**:
- Team matchup analysis
- Key player comparisons
- Recent form and trends
- Betting odds context
- What to watch for

**Best For**: Pre-game articles, preview shows

---

#### 3. Feature Story
**Length**: 600-900 words
**Purpose**: In-depth analysis of trends, players, or teams

**Includes**:
- Deep statistical analysis
- Historical context
- Expert insights
- Data visualizations (suggested)
- Future implications

**Best For**: Weekend features, analysis pieces

---

#### 4. Betting Snapshot
**Length**: 300-500 words
**Purpose**: Quick betting insights and recommendations

**Includes**:
- Current odds analysis
- Value picks
- Trend-based recommendations
- Risk assessment
- Expert picks

**Best For**: Betting newsletters, quick picks

---

## Advanced Editor

### Color-Coded Data States

#### 🟡 Yellow - Missing Data
**Meaning**: Stat or data point mentioned but not yet added
**Action**: Add the missing data or remove reference
**Example**: "scored points" (how many?)

#### 🔵 Blue - Verified Data
**Meaning**: Data confirmed from official source
**Action**: None - data is good to go
**Example**: "scored 27 points" (verified via ESPN)

#### 🔴 Red - Stale Data
**Meaning**: Data is outdated or needs refresh
**Action**: Update with latest information
**Example**: "leading scorer" (was last week, not now)

### Inline Features

#### Hover to Expand
1. Hover over any stat
2. See full context in tooltip:
   - Data source
   - Time window
   - Verification status
   - Last updated

#### Auto-Paragraph Expander
**Shortcut**: `⌘E` or `Ctrl+E`

**How It Works**:
1. Place cursor in paragraph
2. Press `⌘E`
3. AI expands with:
   - Additional context
   - Supporting statistics
   - Relevant quotes
   - Data-backed analysis

**Settings**:
- Expansion length (short/medium/long)
- Tone (neutral/analytical/casual)
- Data density (light/moderate/heavy)

### Word Count Tools

#### Limiter Mode
**Purpose**: Keep stories within target length

**Settings**:
- Hard limit (stops at X words)
- Soft limit (warning at X words)
- No limit

**Available Limits**: 300, 500, 800, 1200 words

#### Expander Mode
**Purpose**: Reach minimum word count

**Features**:
- Suggests areas to expand
- Shows progress to target
- AI-powered expansion suggestions

---

## AI Co-Author

**Location**: Right sidebar (toggle with "Show/Hide AI Co-Author")

### Features

#### 1. Paragraph Suggestions
**Real-time**: Updates as you write

**Each Suggestion Includes**:
- Full paragraph draft
- Reasoning/context
- Data points used
- Confidence score (0-100%)

**Actions**:
- ✅ Accept: Insert into editor
- ❌ Reject: Remove suggestion
- 🔄 Refresh: Get new suggestions

#### 2. Next Paragraph Generator
**Location**: Bottom of sidebar

**How It Works**:
1. Click "Generate Next Paragraph"
2. AI analyzes:
   - Current content
   - Available data
   - Story flow
   - Missing elements
3. Provides 1-3 options
4. One-click insertion

#### 3. Confidence Scoring
**How It's Calculated**:
- Data availability (40%)
- Context relevance (30%)
- Flow/coherence (20%)
- Style match (10%)

**Interpretation**:
- 90-100%: High confidence, likely accurate
- 75-89%: Good suggestion, minor edits may be needed
- 60-74%: Moderate confidence, review carefully
- <60%: Low confidence, use as inspiration only

---

## Writing Feedback

**Location**: Right panel (toggle with "Show/Hide Feedback")

### Feedback Types

#### 1. Sentence Length
**Triggers**: Sentences > 35 words
**Severity**: Warning ⚠️

**Example**:
```
❌ "The Lakers won their third straight game on Tuesday night..."
   (45 words - too long)

✅ "The Lakers won their third straight game on Tuesday night.
    Anthony Davis led with 28 points..."
   (Two shorter sentences)
```

#### 2. Missing Data Window
**Triggers**: Stats without time context
**Severity**: Error ❌

**Example**:
```
❌ "averaging 25 points" (when?)
✅ "averaging 25 points per game this season"
✅ "averaging 25 points over his last 5 games"
```

#### 3. Grammar Issues
**Triggers**: Various grammar rules
**Severity**: Error ❌

**Checks**:
- Subject-verb agreement
- Tense consistency
- Pronoun clarity
- Modifier placement

#### 4. Structure Problems
**Triggers**: Flow and organization issues
**Severity**: Warning ⚠️

**Checks**:
- Paragraph length
- Topic transitions
- Logical flow
- Redundancy

#### 5. House Style Violations
**Triggers**: Style guide mismatches
**Severity**: Info ℹ️

**Customizable**:
- AP Style
- Chicago Manual
- Custom style guide
- Sport-specific conventions

---

## Real-time Proofreading

**Location**: Separate panel (optional)

### Features

#### Auto-Check
- Activates after 2 seconds of no typing
- Checks entire document
- Updates in real-time

#### Issue Categories

**Grammar** 🔴
- Verb tenses
- Agreement errors
- Syntax problems

**Spelling** 🟡
- Typos
- Name misspellings
- Contextual errors

**Style** 🔵
- Passive voice
- Wordiness
- Clarity issues

**Clarity** 🟣
- Ambiguous references
- Jargon overuse
- Complex phrasing

#### Apply Suggestions
1. Review suggestion
2. See original vs. suggested
3. Click "Apply" to replace
4. Or edit manually

---

## Fact Checking

### Inline Fact-Check Tooltips

**How It Works**:
1. Data points auto-tagged during writing
2. Hover over any stat
3. See verification tooltip:
   - ✅ Verified or ⚠️ Unverified
   - Data source
   - Source link (clickable)
   - Last checked timestamp

**Example**:
```
"Anthony Davis scored 28 points"
     [hover]
     ✅ Verified Fact
     ESPN Box Score
     🔗 https://espn.com/nba/game...
     ⏰ Checked: Jan 15, 2:30 PM
```

### Manual Fact Check
1. Select text
2. Right-click → "Fact Check"
3. System verifies against:
   - ESPN API
   - Official team stats
   - The Odds API (for betting)
4. Returns verification status

### Source Links
- All facts link to original source
- One-click to verify independently
- Cached for quick re-checking

---

## Agent Logs

**Location**: "Agent Logs" tab in main dashboard

### What Gets Logged

#### Data Fetcher Agent 🔵
- API calls to ESPN
- Data refresh operations
- Cache hits/misses
- Error handling

#### Analyzer Agent 🟢
- Trend detection
- Statistical analysis
- Pattern recognition
- Outlier identification

#### Formatter Agent 🟡
- Content structuring
- Template application
- Style formatting
- Output generation

#### Writer Agent 🟣
- AI content generation
- Paragraph expansion
- Suggestion creation
- Story composition

### Log Details
Each log entry shows:
- **Timestamp**: When action occurred
- **Agent**: Which component acted
- **Action**: What was done
- **Details**: Specific information
- **Data** (expandable): Full payload

### Filtering
- Filter by agent type
- Search log content
- Date range selection
- Export logs

---

## Writing History

**Location**: "Writing History" tab

### Metrics Tracked

#### Daily Stats
- Stories written
- Total words
- Average words per story
- Time spent writing

#### Weekly/Monthly Views
- Productivity trends
- Peak writing times
- Most written templates
- Favorite leagues

### Visual Charts

#### Story Count Chart
- Bar chart by day
- 7-day or 30-day view
- Hover for details

#### Word Count Trends
- Line chart over time
- Moving average
- Goal tracking

#### Template Distribution
- Pie chart of template usage
- Most/least used
- Optimization suggestions

### Recent Activity
- Last 10 stories
- Quick stats per story
- One-click to reopen

---

## Export System

### Preview Modal

**Access**: Click "Preview" before exporting

**Features**:
- Full markdown rendering
- Formatted view
- Metadata display:
  - Word count
  - Template type
  - Sport/league
  - Last updated
- Export options

### Export to Google Docs

**Shortcut**: `⌘G` or `Ctrl+G`

**Process**:
1. Click "Export to Google Docs"
2. Story uploads to your Google Drive
3. Opens in new tab
4. Preserves formatting:
   - Headings
   - Lists
   - Bold/italic
   - Links

**Requirements**:
- Google account
- Google Docs API credentials
- Authorization (first time only)

### Download as Markdown

**Process**:
1. Click "Markdown" in preview
2. Downloads `.md` file
3. Filename auto-generated from title

**Format**:
```markdown
# Story Title

Story content with **formatting**
preserved including:
- Lists
- **Bold**
- *Italic*
- [Links](url)
```

### Copy to Clipboard

**Process**:
1. Click "Copy" button
2. Content copied to clipboard
3. Paste anywhere

**Formats Available**:
- Plain text
- Markdown
- HTML (for CMS)

---

## Keyboard Shortcuts Reference

### Global
| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open command palette |
| `⌘S` / `Ctrl+S` | Save story |
| `Esc` | Close modals/panels |

### Writing
| Shortcut | Action |
|----------|--------|
| `⌘E` / `Ctrl+E` | Expand paragraph |
| `⌘B` / `Ctrl+B` | Bold text |
| `⌘I` / `Ctrl+I` | Italic text |

### Export
| Shortcut | Action |
|----------|--------|
| `⌘G` / `Ctrl+G` | Export to Google Docs |
| `⌘⇧E` / `Ctrl+Shift+E` | Export as Markdown |
| `⌘⇧C` / `Ctrl+Shift+C` | Copy to clipboard |

### Data
| Shortcut | Action |
|----------|--------|
| `⌘R` / `Ctrl+R` | Run simulation |
| `⌘⇧R` / `Ctrl+Shift+R` | Refresh data |

---

## Best Practices

### For Best Results

1. **Start with Template**: Choose appropriate template for your goal
2. **Review AI Suggestions**: Don't blindly accept - edit for your voice
3. **Verify Data**: Always check fact tooltips before publishing
4. **Use Feedback**: Address all errors, consider warnings
5. **Check History**: Learn from your patterns to improve

### Workflow Tips

1. **Morning Routine**:
   - Check overnight games
   - Generate daily digest
   - Review and edit

2. **Pre-Game**:
   - Create game preview
   - Add betting insights
   - Schedule publication

3. **Post-Game**:
   - Update with final scores
   - Add standout performances
   - Export quickly

4. **Weekly Feature**:
   - Analyze week's data
   - Create feature story
   - Deep dive with AI co-author

---

## Troubleshooting

### Common Issues

**Issue**: AI suggestions not appearing
**Fix**: Ensure you've written at least 100 words

**Issue**: Data showing as stale
**Fix**: Click "Refresh Data" in command palette

**Issue**: Export failing
**Fix**: Check API credentials in settings

**Issue**: Fact check not working
**Fix**: Verify ESPN API key is valid

---

## Advanced Configuration

### Custom Templates
Create your own templates by modifying `src/components/TemplateModal.tsx`

### Style Guide Import
Upload your custom style guide for feedback alignment

### API Integration
Connect to additional data sources via backend API

### Hotkey Customization
Modify shortcuts in `src/App.tsx` and component files

---

*For more information, see the main README.md or visit [docs.sportstatbot.com]*
