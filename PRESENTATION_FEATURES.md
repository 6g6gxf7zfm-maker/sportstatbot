# SportStatBot - Creative & Presentation Features

This document describes the comprehensive creative and presentation enhancement features available in SportStatBot.

## Table of Contents

1. [Overview](#overview)
2. [Emoji & Tone Calibration](#emoji--tone-calibration)
3. [Style Themes](#style-themes)
4. [Dynamic Color Coding](#dynamic-color-coding)
5. [Randomized Story Openers](#randomized-story-openers)
6. [Graphic Header Generator](#graphic-header-generator)
7. [Chart Generation System](#chart-generation-system)
8. [Section Divider Templates](#section-divider-templates)
9. [Auto-Image Fetcher](#auto-image-fetcher)
10. [Timeline Visualizations](#timeline-visualizations)
11. [Storybook View](#storybook-view)
12. [PDF Generation](#pdf-generation)
13. [Auto-Credits System](#auto-credits-system)
14. [Usage Examples](#usage-examples)

---

## Overview

SportStatBot now includes advanced presentation features that allow you to customize the look, feel, and format of your sports reports. From professional business reports to engaging fan-focused articles, you can tailor the output to match your audience and platform.

## Emoji & Tone Calibration

Control the level of emojis and tone from professional to fun.

### Tone Levels

- **Professional**: Minimal to no emojis, formal language
- **Balanced**: Moderate emoji use, professional yet engaging (default)
- **Engaging**: Enhanced emoji use, conversational tone
- **Fun**: Maximum emojis, enthusiastic language

### Usage

```bash
# Professional tone
python cli.py --sports nba --tone professional

# Fun tone
python cli.py --sports nfl --tone fun

# Balanced (default)
python cli.py --sports mlb --tone balanced
```

### Example Output

**Professional**:
```
Key Trends
* Lakers won their last 5 games
```

**Fun**:
```
🔥🔥🔥 Key Trends
• Lakers won their last 5 games 🏆🏆🏆
```

---

## Style Themes

Four distinct presentation styles inspired by major sports media outlets.

### Available Themes

#### ESPN Style
- Bold, authoritative, highlight-focused coverage
- Emphasis on scores and top performances
- Energetic, action-oriented language
- Bright color scheme in PDFs

```bash
python cli.py --sports nba --theme espn
```

#### The Athletic Style
- Analytical, narrative-driven content
- Deeper insights and context
- Elegant, sophisticated formatting
- Muted color scheme in PDFs

```bash
python cli.py --sports nfl --theme athletic
```

#### FiveThirtyEight Style
- Data-driven, statistical analysis
- Probability and trend-focused
- Numbers and metrics emphasized
- Cool, analytical color scheme

```bash
python cli.py --sports mlb --theme 538
```

#### Bleacher Report Style
- Energetic, fan-focused content
- Social media friendly
- Exciting, bold headlines
- Vibrant color scheme

```bash
python cli.py --sports nba --theme bleacher
```

---

## Dynamic Color Coding

Terminal color coding for team streaks and performance indicators.

### Color Scheme

- **Hot Green** (🟢): Teams on 5+ win streaks
- **Warm Yellow** (🟡): Teams on 3-4 win streaks
- **Cold Blue** (🔵): Teams on 3-4 loss streaks
- **Freezing Red** (🔴): Teams on 5+ loss streaks

### Usage

```bash
python cli.py --sports nba --colors
```

### Example

When enabled, team streaks will be color-coded in terminal output:
```
🟢 Lakers have won their last 5 games
🔴 Spurs have lost their last 6 games
```

---

## Randomized Story Openers

Fresh, dynamic introductions for each sport report.

### Features

- Sport-specific opening lines
- Randomized selection for variety
- Contextual emotion words
- Weekly/seasonal awareness

### Examples

**NFL**:
- "Week 10 brought fireworks to the NFL..."
- "The gridiron delivered drama this week..."
- "Sunday's slate had it all..."

**NBA**:
- "The NBA continues to amaze..."
- "Hardwood highlights dominated the night..."
- "Another thrilling night in the Association..."

### Disable Openers

```bash
python cli.py --sports nfl --no-openers
```

---

## Graphic Header Generator

Customizable header styles for reports.

### Header Styles

#### Standard (Default)
```
╔══════════════════════════════════════════════════════════════╗
║  🏀  NBA Report - November 9, 2025  🏀
╚══════════════════════════════════════════════════════════════╝
```

#### Compact
```
🏀 NBA | November 9, 2025
```

#### Bold
```
█████████████████████████████████████████████████████████████
   🏀  NBA REPORT - NOVEMBER 9, 2025
█████████████████████████████████████████████████████████████
```

#### Minimal
```
🏀 NBA — November 9, 2025
```

### Usage

```bash
python cli.py --sports nba --header-style bold
python cli.py --sports nfl --header-style minimal
```

---

## Chart Generation System

Automated statistical visualizations using matplotlib.

### Chart Types

1. **Streak Charts**: Win/loss visualization for teams
2. **Standings Charts**: Conference/division standings
3. **Player Performance Charts**: Individual stat breakdowns
4. **Score Progression Charts**: Quarter-by-quarter game flow
5. **Team Comparison Charts**: Head-to-head stat comparisons
6. **Betting Odds Charts**: Spread and line visualizations

### Usage

```bash
# Generate charts for a report
python cli.py --sports nba --charts

# Charts + PDF
python cli.py --sports nfl --charts --pdf
```

### Features

- Automatic chart generation based on report data
- Charts embedded in markdown output
- High-resolution PNG exports (150 DPI)
- Color-coded visualizations
- Saved to `reports/charts/` directory

### Example

```python
from visualizers.chart_generator import ChartGenerator

chart_gen = ChartGenerator()

# Generate standings chart
chart_path = chart_gen.generate_standings_chart(
    standings_data,
    sport="NBA",
    division="Eastern Conference"
)

# Embed in markdown
markdown = chart_gen.embed_chart_in_markdown(chart_path, "NBA East Standings")
```

---

## Section Divider Templates

Theme-specific section separators for enhanced readability.

### Divider Styles (by Theme)

- **ESPN**: `═` (60 chars)
- **The Athletic**: `─` (60 chars)
- **FiveThirtyEight**: `─` (60 chars)
- **Bleacher Report**: `▬` (60 chars)

Dividers automatically match your selected theme.

---

## Auto-Image Fetcher

Automatically fetch and embed team logos and player images.

### Features

- Team logo fetching from ESPN CDN
- Player headshot support
- Local caching for performance
- Markdown image embedding
- HTML support for size control

### Usage

```python
from visualizers.image_fetcher import ImageFetcher

fetcher = ImageFetcher()

# Fetch team logo
logo_path = fetcher.get_team_logo("Los Angeles Lakers", "nba")

# Create game header with logos
header = fetcher.create_team_header_with_logos(
    "Los Angeles Lakers",
    "Boston Celtics",
    "nba",
    "7:30 PM ET"
)
```

### Cache Management

```python
# Check cache size
size = fetcher.get_cache_size()

# Clear cache
fetcher.clear_cache()
```

Images are cached in `reports/images/` directory.

---

## Timeline Visualizations

Create visual timelines for storylines and events.

### Timeline Types

1. **Season Timeline**: Major events throughout a season
2. **Game Flow Timeline**: Key moments in a game
3. **Streak Timeline**: Team's recent results
4. **Player Career Timeline**: Career milestones
5. **Playoff Bracket Timeline**: Tournament progression
6. **Injury Timeline**: Player injury history
7. **Trade Deadline Timeline**: Roster moves

### Usage

```python
from visualizers.timeline_generator import TimelineGenerator

timeline_gen = TimelineGenerator()

# Generate streak timeline
timeline = timeline_gen.generate_streak_timeline(
    "Los Angeles Lakers",
    recent_games,
    limit=10
)

# Generate season timeline
timeline = timeline_gen.generate_season_timeline(
    season_events,
    title="2024-25 NBA Season"
)
```

### Example Output

```
Nov 1   ✅ vs Phoenix Suns      (115-105)
Nov 3   ✅ vs Sacramento Kings  (120-107)
Nov 5   ❌ vs Denver Nuggets    (102-110)
Nov 7   ✅ vs Portland Blazers  (134-110)
```

---

## Storybook View

Render all sports stories in sequence as one cohesive feature article.

### Features

- Cover page with title and date
- Table of contents
- Narrative chapter structure
- Themed formatting
- Sequential storytelling
- Epilogue/conclusion

### Usage

```bash
# Generate storybook view
python cli.py --all --storybook

# Storybook with specific theme
python cli.py --sports nfl nba mlb --storybook --theme athletic

# Storybook as PDF
python cli.py --all --storybook --pdf
```

### Structure

1. **Cover Page**: Professional title page
2. **Table of Contents**: Chapter listing by sport
3. **Chapters**: Each sport as a narrative chapter
   - Opening
   - Key storylines
   - Player spotlights
   - Looking ahead
4. **Epilogue**: Summary and conclusion
5. **Credits**: Agent contributions (if enabled)

---

## PDF Generation

Create professional PDF reports with custom styling.

### Features

- High-quality PDF output
- Theme-specific styling
- Custom fonts and colors
- Page numbers and headers
- Cover pages
- Table support
- Image embedding

### Usage

```bash
# Generate PDF
python cli.py --sports nba --pdf

# PDF with specific theme
python cli.py --sports nfl --pdf --theme athletic

# PDF + Markdown output
python cli.py --all --pdf --output weekly_report.md
```

### PDF Styling

PDFs automatically apply theme-specific colors:
- **ESPN**: Red accents (#c8102e)
- **The Athletic**: Black/grey minimalist
- **FiveThirtyEight**: Clean black text
- **Bleacher Report**: Orange accents (#ff6c00)

### Weekly Booklets

```python
from formatters.pdf_generator import PDFGenerator
from datetime import datetime, timedelta

pdf_gen = PDFGenerator()

# Generate weekly booklet
booklet_path = pdf_gen.generate_weekly_booklet(
    daily_reports,
    week_start=datetime.now() - timedelta(days=7),
    week_end=datetime.now(),
    theme='espn'
)
```

PDFs are saved to `reports/pdf/` directory.

---

## Auto-Credits System

Track which agents/modules contributed to each section.

### Features

- Automatic credit tracking
- Module attribution
- Section-by-section credits
- Optional credits display

### Usage

```bash
# Enable credits
python cli.py --sports nba --credits
```

### Example Output

```markdown
## Report Credits

This report was generated by the following agents:

- 📡 Data Collection: Full Report Generation
- 🎮 Game Analysis: NBA Analysis
- 👤 Player Analysis: Standout Players
- 💰 Betting Analysis: Betting Insights
- 📝 Report Formatting: Full Report Generation
```

### Programmatic Usage

```python
from presentation_config import PresentationConfig

config = PresentationConfig(track_credits=True)

# Add credits during processing
config.add_credit('game_analyzer', 'NBA Game Analysis')
config.add_credit('player_analyzer', 'Top Performers')

# Get credits section
credits_md = config.get_credits_section()
```

---

## Usage Examples

### Example 1: Professional Business Report

```bash
python cli.py --sports nfl nba \
  --tone professional \
  --theme 538 \
  --no-openers \
  --header-style minimal \
  --pdf \
  --output weekly_analysis.md
```

Creates a data-driven, professional PDF suitable for business stakeholders.

### Example 2: Fan-Focused Social Media Content

```bash
python cli.py --sports nba \
  --tone fun \
  --theme bleacher \
  --colors \
  --charts \
  --output fan_update.md
```

Generates energetic, visual content perfect for social media sharing.

### Example 3: Comprehensive Weekly Digest

```bash
python cli.py --all \
  --tone balanced \
  --theme athletic \
  --storybook \
  --charts \
  --credits \
  --pdf \
  --output digest.md
```

Creates a complete narrative-style weekly digest with all features enabled.

### Example 4: Quick Game Day Update

```bash
python cli.py --sports nfl \
  --quick \
  --tone engaging \
  --theme espn \
  --colors
```

Generates a quick, colorful update for game day.

### Example 5: Statistical Deep Dive

```bash
python cli.py --sports nba \
  --tone professional \
  --theme 538 \
  --charts \
  --timeline \
  --pdf
```

Creates an analytical report with extensive visualizations.

---

## Advanced Configuration

### Programmatic Usage

```python
from presentation_config import PresentationConfig, ToneLevel, StyleTheme
from formatters.enhanced_formatter import EnhancedFormatter
from report_generator import SportsReportGenerator

# Configure presentation
config = PresentationConfig(
    tone=ToneLevel.ENGAGING,
    theme=StyleTheme.ESPN,
    use_colors=True,
    use_random_openers=True,
    header_template='bold',
    track_credits=True
)

# Generate report
generator = SportsReportGenerator()
formatter = EnhancedFormatter(config)

# Get data and format
data = generator._generate_sport_data('nba')
report = formatter.format_full_report({'nba': data})

print(report)
```

### Custom Themes

You can extend the theme system by modifying `presentation_config.py`:

```python
STYLE_THEMES['custom'] = {
    'name': 'Custom Style',
    'description': 'Your custom description',
    'header_style': 'bold',
    'use_scores_heavily': True,
    'emphasize_highlights': True,
    'tone_words': ['custom', 'words'],
    'section_divider': '━' * 60,
    'use_numbers': True,
    'color_scheme': 'custom'
}
```

---

## File Structure

```
sportstatbot/
├── presentation_config.py          # Presentation configuration
├── formatters/
│   ├── enhanced_formatter.py       # Enhanced markdown formatter
│   ├── storybook_formatter.py      # Storybook/narrative formatter
│   └── pdf_generator.py            # PDF generation
├── visualizers/
│   ├── chart_generator.py          # Chart/graph generation
│   ├── image_fetcher.py            # Team logos & images
│   └── timeline_generator.py       # Timeline visualizations
└── reports/
    ├── charts/                     # Generated charts
    ├── images/                     # Cached images
    └── pdf/                        # PDF outputs
```

---

## Requirements

All presentation features require these dependencies:

```
matplotlib>=3.7.0       # Chart generation
numpy>=1.24.0          # Numerical operations
pillow>=10.0.0         # Image handling
markdown>=3.5.0        # Markdown processing
weasyprint>=60.0       # PDF generation
pypdf2>=3.0.0          # PDF manipulation
colorama>=0.4.6        # Terminal colors
```

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Best Practices

1. **Choose the right theme**: Match your audience (ESPN for broad appeal, Athletic for analysis, etc.)
2. **Balance tone with audience**: Professional for business, engaging/fun for fans
3. **Use colors wisely**: Enable for terminal viewing, but note they won't appear in PDFs
4. **Generate charts for key insights**: Don't overuse - focus on impactful visualizations
5. **Enable credits for transparency**: Especially useful for automated reports
6. **Use storybook view for summaries**: Great for weekly/monthly digests
7. **PDF for distribution**: Use markdown for archives, PDF for sharing

---

## Troubleshooting

### Charts not generating

Ensure matplotlib is properly installed:
```bash
pip install matplotlib numpy
```

### PDF generation fails

Check weasyprint dependencies:
```bash
pip install weasyprint
# On macOS: brew install cairo pango gdk-pixbuf libffi
# On Ubuntu: apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

### Images not fetching

Check internet connection and ESPN CDN availability. Images are cached locally after first fetch.

### Colors not showing in terminal

Ensure your terminal supports ANSI color codes. Most modern terminals do.

---

## Future Enhancements

Planned features for future releases:

- Interactive HTML reports
- Video highlight embedding
- Social media auto-posting
- Custom logo/branding support
- Multi-language support
- Real-time game tracking
- Mobile-optimized formats
- Email newsletter templates

---

## Support

For issues or feature requests, please visit:
https://github.com/yourusername/sportstatbot/issues

---

**Happy Reporting!** 🏆
