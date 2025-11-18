# Usage Examples 📚

Real-world examples of using the Instagram Reel Automation tool.

## Basic Examples

### 1. Create Random Sports Reel
```bash
python main.py
```
- Generates random category + template
- Includes voiceover
- Outputs to `output/` folder

### 2. Create NBA Content
```bash
python main.py --category NBA
```
- NBA-focused content
- Random template
- Perfect for basketball content creators

### 3. Create Specific Template
```bash
python main.py --category NFL --template prediction
```
- NFL predictions
- Great for engagement
- Controversial predictions drive comments

### 4. Batch Generation
```bash
python main.py --batch 10
```
- Creates 10 reels at once
- Random categories and templates
- Perfect for weekly content planning

### 5. Fast Generation (No Voiceover)
```bash
python main.py --category Soccer --no-voiceover
```
- Faster creation
- Silent video with text only
- Add music manually later

## Content Strategy Examples

### Monday Motivation
```bash
# Create inspiring sports moments
python main.py --category "General Sports Facts" --template highlight_moment
```

Post on Monday morning with #MondayMotivation

### Throwback Thursday
```bash
# Create historical facts
python main.py --category NBA --template did_you_know
```

Use with #ThrowbackThursday #TBT

### Weekend Predictions
```bash
# Create bold predictions for weekend games
python main.py --category NFL --template prediction
python main.py --category NBA --template prediction
```

Post Friday evening for weekend engagement

### Weekly Batch
```bash
# Create full week of content
python main.py --batch 7 --category NBA
```

Generate once, post daily

## Advanced Examples

### Soccer World Cup Content
```bash
# Generate 5 soccer reels
for i in {1..5}; do
  python main.py --category Soccer --template fact_drop
done
```

### Multi-Sport Coverage
```bash
# Create one reel for each major sport
python main.py --category NBA
python main.py --category NFL
python main.py --category MLB
python main.py --category Soccer
python main.py --category NHL
```

### Engagement-Focused Content
```bash
# VS comparisons drive comments
python main.py --category NBA --template vs_comparison
python main.py --category NFL --template vs_comparison
```

### Top Lists Series
```bash
# Create a series of top 5 lists
python main.py --category NBA --template top_5_list
python main.py --category NFL --template top_5_list
python main.py --category Soccer --template top_5_list
```

## Posting Schedule Example

### Daily Posting Schedule
```bash
# Monday - Motivation
python main.py --category "General Sports Facts" --template highlight_moment

# Tuesday - NBA Stats
python main.py --category NBA --template stat_reveal

# Wednesday - NFL Facts
python main.py --category NFL --template fact_drop

# Thursday - Throwback
python main.py --category NBA --template did_you_know

# Friday - Weekend Predictions
python main.py --category NFL --template prediction

# Saturday - Soccer Content
python main.py --category Soccer --template stat_reveal

# Sunday - Top Lists
python main.py --category NBA --template top_5_list
```

### Peak Times (US Eastern)
- **12:00 PM** - Lunch break
- **5:00 PM** - After work
- **9:00 PM** - Evening scroll

## Expected Output

### Terminal Output
```
============================================================
🎬 INSTAGRAM REEL AUTOMATION
============================================================

📝 Step 1: Generating AI script...

✅ Script generated!
   Category: NBA
   Template: stat_reveal
   Hook: 🚨 LeBron's INSANE Career Record! 🚨

🏷️  Step 2: Generating hashtags...
✅ Generated 30 hashtags

🎥 Step 3: Creating video...
🎙️  Generating voiceover...
✅ Voiceover generated: output/temp/voiceover_1234.mp3
📹 Rendering video: nba_stat_reveal_20240118_143022.mp4
✅ Video created: output/nba_stat_reveal_20240118_143022.mp4

💾 Step 4: Saving metadata...
✅ Metadata saved: output/nba_stat_reveal_20240118_143022_metadata.json

============================================================
✅ REEL READY FOR MANUAL POSTING!
============================================================

📹 Video: output/nba_stat_reveal_20240118_143022.mp4

📝 CAPTION:
------------------------------------------------------------
🚨 LeBron's INSANE Career Record! 🚨

LeBron James has played against 35% of all players in NBA
history. That's over 1,200 different players across 21
seasons. Absolutely mind-blowing longevity!

Follow for more crazy NBA stats! 👆

💡 TIP: Post hashtags in FIRST COMMENT for better reach!

🏷️  HASHTAGS (copy to first comment):
------------------------------------------------------------
#viral #fyp #foryou #trending #explore
#sports #sportsnews #espn #gameday #sportslife
#nba #basketball #hoops #nbahighlights #nbabasketball
#bball #ballers #stats #sportsstats #mindblown
#insane #crazy #mondaymotivation
------------------------------------------------------------
```

### Files Created
```
output/
├── nba_stat_reveal_20240118_143022.mp4
└── nba_stat_reveal_20240118_143022_metadata.json
```

### Metadata File Content
```json
{
  "video_file": "nba_stat_reveal_20240118_143022.mp4",
  "video_path": "output/nba_stat_reveal_20240118_143022.mp4",
  "created_at": "2024-01-18T14:30:22.123456",
  "category": "NBA",
  "template": "stat_reveal",
  "hook": "🚨 LeBron's INSANE Career Record! 🚨",
  "content": "LeBron James has played against 35%...",
  "cta": "Follow for more crazy NBA stats! 👆",
  "voiceover": "Did you know LeBron James...",
  "hashtags": ["#viral", "#fyp", ...],
  "caption": "🚨 LeBron's INSANE Career Record! 🚨\n\n..."
}
```

## Performance Metrics

### Expected Generation Times
- **With voiceover:** 45-90 seconds per reel
- **Without voiceover:** 20-40 seconds per reel
- **Batch of 10:** 8-15 minutes total

### API Costs (Approximate)
- **Per reel:** $0.02-0.05 (GPT-4)
- **Batch of 10:** $0.20-0.50
- **Monthly (30 reels):** $0.60-1.50

## Pro Tips

### 1. Test First
```bash
# Create 3 test reels to check quality
python main.py --batch 3
```

### 2. Find Your Niche
```bash
# If you focus on NBA, create only NBA content
python main.py --category NBA --batch 7
```

### 3. Template Rotation
```bash
# Rotate templates for variety
python main.py --category NBA --template stat_reveal
python main.py --category NBA --template prediction
python main.py --category NBA --template vs_comparison
```

### 4. Weekend Preparation
```bash
# Friday: Generate content for weekend
python main.py --batch 6

# Schedule posts:
# Sat 12pm, 5pm, 9pm
# Sun 12pm, 5pm, 9pm
```

### 5. Trend Riding
When big sports news breaks:
```bash
# Quickly create relevant content
python main.py --category NBA --template fact_drop
python main.py --category NBA --template prediction
```

## Workflow Example

### Weekly Content Creation Workflow

**Friday Morning:**
```bash
# Generate week's content
python main.py --category NBA --batch 7
```

**Friday Afternoon:**
- Review all 7 videos
- Delete any you don't like
- Re-generate if needed

**Weekend:**
- Plan posting schedule
- Prepare captions and hashtags
- Schedule in your calendar

**During Week:**
- Post daily at peak times
- Copy-paste caption and video
- Add hashtags in first comment
- Engage with comments immediately

---

Ready to dominate Instagram Reels! 🔥
