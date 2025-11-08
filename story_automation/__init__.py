"""
Story Automation Module for SportStatBot

Provides comprehensive story creation and writing automation features including:
- Export to Google Docs and Apple Notes
- AI-powered content generation
- Multiple writing styles and perspectives
- Story analysis and rating
- Narrative continuity and context management
"""

from .generators.story_generator import StoryGenerator
from .generators.title_generator import TitleGenerator
from .generators.summary_generator import SummaryGenerator
from .generators.sidebar_generator import SidebarGenerator
from .generators.pullquote_generator import PullQuoteGenerator
from .generators.trivia_generator import TriviaGenerator
from .generators.timeline_generator import TimelineGenerator

from .formatters.markdown_converter import MarkdownConverter
from .formatters.stat_highlighter import StatHighlighter
from .formatters.footnote_inserter import FootnoteInserter

from .exporters.google_docs_exporter import GoogleDocsExporter
from .exporters.apple_notes_syncer import AppleNotesSyncer

from .analyzers.story_rater import StoryRater
from .analyzers.diff_analyzer import DiffAnalyzer
from .analyzers.context_manager import ContextManager

__all__ = [
    'StoryGenerator',
    'TitleGenerator',
    'SummaryGenerator',
    'SidebarGenerator',
    'PullQuoteGenerator',
    'TriviaGenerator',
    'TimelineGenerator',
    'MarkdownConverter',
    'StatHighlighter',
    'FootnoteInserter',
    'GoogleDocsExporter',
    'AppleNotesSyncer',
    'StoryRater',
    'DiffAnalyzer',
    'ContextManager',
]
