# Setup Guide 🚀

Complete guide to get your Instagram Reel Automation up and running.

## Step-by-Step Setup

### 1. System Requirements

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **ImageMagick** (for text rendering)
- **OpenAI API key** (for AI generation)

### 2. Check Python Version

```bash
python --version
# or
python3 --version
```

Should show Python 3.8 or higher.

### 3. Install ImageMagick

ImageMagick is required for rendering text in videos.

#### macOS
```bash
brew install imagemagick
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install imagemagick
```

#### Windows
1. Download from: https://imagemagick.org/script/download.php#windows
2. Run the installer
3. **Important:** Check "Add to PATH" during installation
4. Restart your terminal

#### Verify Installation
```bash
convert --version
```

Should display ImageMagick version info.

### 4. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or if using Python 3:
pip3 install -r requirements.txt
```

This installs:
- `openai` - AI script generation
- `moviepy` - Video creation
- `pillow` - Image processing
- `gtts` - Text-to-speech
- `python-dotenv` - Environment variables
- `requests` - HTTP requests
- `pydub` - Audio processing
- `numpy` - Numerical operations

### 5. Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Note:** OpenAI charges per API call. Check pricing at https://openai.com/pricing

### 6. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Save and exit.

### 7. Test Installation

Run a simple test:

```bash
python main.py --list
```

Should display available categories and templates.

### 8. Create Your First Reel

```bash
python main.py --category NBA
```

This will:
1. Generate an AI script
2. Create a video with text overlays
3. Add AI voiceover
4. Generate hashtags
5. Save everything to `output/` folder

### 9. Check Output

```bash
ls output/
```

You should see:
- `.mp4` video file
- `_metadata.json` file with caption and hashtags

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "ImageMagick not found"

**Solution:**
- Make sure ImageMagick is installed
- On Windows: Add to system PATH
- Restart terminal after installation

### Issue: "OpenAI API error: Authentication"

**Solution:**
- Check API key in `.env` file
- Ensure key starts with `sk-`
- No quotes around the key in `.env`

### Issue: "OpenAI API error: Insufficient credits"

**Solution:**
- Add credits to your OpenAI account
- Check usage at https://platform.openai.com/usage

### Issue: Video rendering is very slow

**Solutions:**
- First video is always slower (loading libraries)
- Use `--no-voiceover` for faster generation
- Close other applications
- Use batch mode to generate multiple at once

### Issue: "Permission denied" on macOS/Linux

**Solution:**
```bash
chmod +x main.py
```

### Issue: Text not showing in video

**Solution:**
- Verify ImageMagick is installed
- Try installing additional fonts:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ttf-mscorefonts-installer

  # macOS
  brew install --cask font-arial
  ```

## Testing Your Setup

Run all tests:

```bash
# Test script generation
python script_generator.py

# Test hashtag generation
python hashtag_generator.py

# Test video generation (creates test reel)
python video_generator.py
```

## Optimization Tips

### Reduce API Costs

1. Use `template` parameter to control script length
2. Generate batch reels to reuse API context
3. Edit and reuse good scripts manually

### Speed Up Video Generation

1. Use `--no-voiceover` when testing
2. Reduce video quality in `config.py`
3. Generate in batch mode

### Better Video Quality

1. Add custom fonts to `assets/` folder
2. Use stock images in `assets/images/`
3. Add background music to `assets/music/`

## Next Steps

1. ✅ Generate 3-5 test reels
2. ✅ Review video quality
3. ✅ Adjust settings in `config.py` if needed
4. ✅ Create a batch of reels for the week
5. ✅ Schedule manual posting times
6. ✅ Track which content performs best

## Getting Help

- **Documentation:** See README.md
- **Issues:** Check GitHub issues
- **API Issues:** https://platform.openai.com/docs

---

Ready to create viral content! 🎬
