# Instagram Reel Automation 🎬

AI-powered automation tool for creating **viral sports videos** for Instagram Reels. Generate engaging 15-30 second videos with AI scripts, voiceovers, and trending hashtags - ready for manual posting!

## Features ✨

- 🤖 **AI Script Generation** - GPT-4 powered sports content
- 🎥 **Automatic Video Creation** - Professional 9:16 Reels format
- 🎙️ **AI Voiceover** - Text-to-speech narration
- ✍️ **Animated Text Overlays** - Eye-catching captions
- 🏷️ **Trending Hashtags** - Auto-generated viral hashtag sets
- 🎨 **Custom Templates** - Multiple viral video formats
- ⚡ **Batch Creation** - Generate multiple reels at once
- 📝 **Manual Posting Workflow** - Full control over when to post

## Sports Categories 🏀

- NBA Basketball
- NFL Football
- MLB Baseball
- NHL Hockey
- Soccer/Football
- Tennis
- Boxing/MMA
- Olympics
- College Sports
- General Sports Facts

## Video Templates 🎬

1. **Stat Reveal** - Mind-blowing statistics
2. **Prediction** - Bold sports predictions
3. **Fact Drop** - Surprising facts
4. **VS Comparison** - Player/team comparisons
5. **Top 5 List** - Rankings and lists
6. **Did You Know** - Trivia format
7. **Highlight Moment** - Iconic moments

## Quick Start 🚀

### Prerequisites

- Python 3.8+
- OpenAI API key
- ImageMagick (for text rendering)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd sportstatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install ImageMagick** (required for moviepy)

**macOS:**
```bash
brew install imagemagick
```

**Ubuntu/Debian:**
```bash
sudo apt-get install imagemagick
```

**Windows:**
Download from https://imagemagick.org/script/download.php

4. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Usage

**Create a single reel (random category):**
```bash
python main.py
```

**Create NBA reel:**
```bash
python main.py --category NBA
```

**Create NFL prediction reel:**
```bash
python main.py --category NFL --template prediction
```

**Create 5 reels in batch:**
```bash
python main.py --batch 5
```

**Create without voiceover:**
```bash
python main.py --category Soccer --no-voiceover
```

**List all options:**
```bash
python main.py --list
```

## Output 📹

Each reel generation creates:

- **Video file** (.mp4) - Ready to upload to Instagram
- **Metadata file** (.json) - Script, hashtags, and caption
- **Posting instructions** - Displayed in terminal

Example output:
```
output/
  ├── nba_stat_reveal_20240118_143022.mp4
  ├── nba_stat_reveal_20240118_143022_metadata.json
  └── batch_summary.json
```

## Manual Posting Workflow 📱

1. **Run the automation** to generate your reel
2. **Review the video** in the output folder
3. **Copy the caption** from terminal or metadata file
4. **Upload to Instagram** manually
5. **Post hashtags** in the first comment (better reach!)

## Project Structure 📁

```
sportstatbot/
├── main.py                 # CLI interface
├── script_generator.py     # AI script generation
├── video_generator.py      # Video creation engine
├── hashtag_generator.py    # Hashtag generation
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── output/               # Generated videos
└── assets/               # Media assets (optional)
    ├── music/           # Background music
    └── images/          # Background images
```

## Configuration ⚙️

Edit `config.py` to customize:

- Video dimensions (default: 1080x1920)
- Font sizes and colors
- Animation durations
- Video length (15-30 seconds)
- Output directories

## Advanced Usage 🔧

### Custom Script Generation

```python
from script_generator import ScriptGenerator

generator = ScriptGenerator()
script = generator.generate_script(
    category='NBA',
    template='stat_reveal'
)
print(script)
```

### Create Video from Custom Script

```python
from video_generator import VideoGenerator

video_gen = VideoGenerator()
custom_script = {
    'hook': 'Your hook here',
    'content': 'Your content here',
    'cta': 'Your call-to-action',
    'voiceover': 'Full voiceover script',
    'category': 'NBA'
}

video_gen.create_reel(custom_script)
```

### Generate Hashtags

```python
from hashtag_generator import HashtagGenerator

hashtag_gen = HashtagGenerator()
tags = hashtag_gen.generate(category='NFL', template='prediction')
print(hashtag_gen.format_for_comment(tags))
```

## Tips for Viral Content 🔥

1. **Post consistently** - 1-2 reels per day
2. **Post at peak times** - 12pm, 5pm, 9pm in your timezone
3. **Use first comment for hashtags** - Better algorithm performance
4. **Engage quickly** - Respond to comments in first hour
5. **Mix content types** - Rotate through different templates
6. **Follow trends** - Use time-based hashtags (#MondayMotivation)
7. **Test different categories** - See what resonates with your audience

## Troubleshooting 🔧

**"ModuleNotFoundError: No module named 'moviepy'"**
- Run: `pip install -r requirements.txt`

**"ImageMagick not found"**
- Install ImageMagick (see installation section)
- On Windows, add to PATH

**"OpenAI API error"**
- Check your API key in `.env` file
- Ensure you have API credits

**Video rendering slow**
- Reduce video quality in `video_generator.py`
- Use `--no-voiceover` flag for faster generation

**Text not appearing in video**
- Install ImageMagick
- Check font availability on your system

## Limitations ⚠️

- Requires OpenAI API key (costs apply)
- Manual posting only (no direct Instagram API)
- Basic video templates (can be extended)
- Text-to-speech voice is robotic (upgrade to ElevenLabs for premium voice)

## Future Enhancements 🚀

- [ ] Background music integration
- [ ] Stock footage/image overlays
- [ ] More video templates
- [ ] Premium AI voices (ElevenLabs)
- [ ] Trending topic scraping
- [ ] Analytics tracking
- [ ] Custom font support
- [ ] Video preview GUI

## Contributing 🤝

Pull requests welcome! Please test thoroughly before submitting.

## License 📄

MIT License - see LICENSE file for details

## Disclaimer ⚖️

This tool is for content creation only. You are responsible for:
- Posting content manually
- Following Instagram's terms of service
- Ensuring content accuracy
- Respecting copyright/licensing

## Support 💬

Issues? Questions? Open a GitHub issue!

---

**Made with ❤️ for sports content creators**

Happy creating! 🎬🏀🏈⚽
