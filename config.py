"""
Configuration for Instagram Reel Automation
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio for Reels
VIDEO_FPS = 30
VIDEO_DURATION_MIN = 15  # seconds
VIDEO_DURATION_MAX = 30  # seconds

# Font Settings
FONT_PATH = None  # Will use default if None
TITLE_FONT_SIZE = 80
SUBTITLE_FONT_SIZE = 60
CAPTION_FONT_SIZE = 50

# Colors (RGB)
PRIMARY_COLOR = (255, 255, 255)  # White
ACCENT_COLOR = (255, 215, 0)  # Gold
BACKGROUND_COLOR = (20, 20, 30)  # Dark blue/black

# Text Animation
TEXT_ANIMATION_DURATION = 0.5  # seconds

# Output
OUTPUT_DIR = 'output'
MUSIC_DIR = 'assets/music'
IMAGES_DIR = 'assets/images'

# Content Categories
SPORTS_CATEGORIES = [
    'NBA',
    'NFL',
    'MLB',
    'NHL',
    'Soccer',
    'Tennis',
    'Boxing/MMA',
    'Olympics',
    'College Sports',
    'General Sports Facts'
]

# Viral Video Templates
VIDEO_TEMPLATES = [
    'stat_reveal',
    'prediction',
    'fact_drop',
    'highlight_moment',
    'vs_comparison',
    'top_5_list',
    'did_you_know'
]
