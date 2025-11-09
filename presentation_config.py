"""
Presentation Configuration for SportStatBot
Manages themes, tone settings, and styling options for report generation
"""

from typing import Dict, List, Tuple
import random


class ToneLevel:
    """Emoji and tone calibration levels"""
    PROFESSIONAL = "professional"
    BALANCED = "balanced"
    ENGAGING = "engaging"
    FUN = "fun"


class StyleTheme:
    """Available presentation style themes"""
    ESPN = "espn"
    THE_ATHLETIC = "athletic"
    FIVETHIRTYEIGHT = "538"
    BLEACHER_REPORT = "bleacher"


# Emoji sets based on tone level
EMOJI_SETS = {
    ToneLevel.PROFESSIONAL: {
        'fire': '',
        'cold': '',
        'warning': '!',
        'trophy': '',
        'chart_up': '↑',
        'chart_down': '↓',
        'star': '*',
        'moneybag': '$',
        'eyes': '>',
        'calendar': '',
        'injury': 'INJ',
        'new': 'NEW',
        'rocket': '^',
        'boom': '!',
        'thinking': '?',
        'checkmark': '✓',
        'x': '✗'
    },
    ToneLevel.BALANCED: {
        'fire': '🔥',
        'cold': '❄️',
        'warning': '⚠️',
        'trophy': '🏆',
        'chart_up': '📈',
        'chart_down': '📉',
        'star': '⭐',
        'moneybag': '💰',
        'eyes': '👀',
        'calendar': '📅',
        'injury': '🏥',
        'new': '🆕',
        'rocket': '🚀',
        'boom': '💥',
        'thinking': '🤔',
        'checkmark': '✅',
        'x': '❌'
    },
    ToneLevel.ENGAGING: {
        'fire': '🔥🔥',
        'cold': '🥶❄️',
        'warning': '⚠️⚠️',
        'trophy': '🏆✨',
        'chart_up': '📈🚀',
        'chart_down': '📉💔',
        'star': '⭐⭐',
        'moneybag': '💰💰',
        'eyes': '👀👀',
        'calendar': '📅🗓️',
        'injury': '🏥😷',
        'new': '🆕✨',
        'rocket': '🚀💨',
        'boom': '💥💥',
        'thinking': '🤔💭',
        'checkmark': '✅💯',
        'x': '❌⛔'
    },
    ToneLevel.FUN: {
        'fire': '🔥🔥🔥',
        'cold': '🥶🧊❄️',
        'warning': '🚨⚠️🚨',
        'trophy': '🏆🏆🏆',
        'chart_up': '📈🚀🌙',
        'chart_down': '📉💀☠️',
        'star': '⭐🌟✨',
        'moneybag': '💰💵💸',
        'eyes': '👀👁️👁️',
        'calendar': '📅🗓️📆',
        'injury': '🏥😷🤕',
        'new': '🆕✨🎉',
        'rocket': '🚀🚀💨',
        'boom': '💥💥💥',
        'thinking': '🤔🤔💭',
        'checkmark': '✅💯🎯',
        'x': '❌⛔🚫'
    }
}


# Style theme configurations
STYLE_THEMES = {
    StyleTheme.ESPN: {
        'name': 'ESPN Style',
        'description': 'Bold, authoritative, highlight-focused coverage',
        'header_style': 'bold_caps',
        'use_scores_heavily': True,
        'emphasize_highlights': True,
        'tone_words': ['dominates', 'explosive', 'stellar', 'clutch', 'breakout'],
        'section_divider': '═' * 60,
        'use_numbers': True,  # Rankings, stats front and center
        'color_scheme': 'bright'
    },
    StyleTheme.THE_ATHLETIC: {
        'name': 'The Athletic Style',
        'description': 'Analytical, narrative-driven, deeper insights',
        'header_style': 'elegant',
        'use_scores_heavily': False,
        'emphasize_highlights': False,
        'tone_words': ['indicates', 'suggests', 'reveals', 'demonstrates', 'reflects'],
        'section_divider': '─' * 60,
        'use_numbers': True,  # But woven into narrative
        'color_scheme': 'muted'
    },
    StyleTheme.FIVETHIRTYEIGHT: {
        'name': 'FiveThirtyEight Style',
        'description': 'Data-driven, statistical, probability-focused',
        'header_style': 'data_focused',
        'use_scores_heavily': True,
        'emphasize_highlights': False,
        'tone_words': ['probability', 'expected', 'statistical', 'correlation', 'trend'],
        'section_divider': '─' * 60,
        'use_numbers': True,  # Heavy stats emphasis
        'color_scheme': 'cool'
    },
    StyleTheme.BLEACHER_REPORT: {
        'name': 'Bleacher Report Style',
        'description': 'Energetic, fan-focused, social media friendly',
        'header_style': 'exciting',
        'use_scores_heavily': True,
        'emphasize_highlights': True,
        'tone_words': ['unbelievable', 'insane', 'wild', 'incredible', 'jaw-dropping'],
        'section_divider': '▬' * 60,
        'use_numbers': True,
        'color_scheme': 'vibrant'
    }
}


# Terminal color codes for streak visualization
class Colors:
    """ANSI color codes for terminal output"""
    # Streak colors
    HOT_GREEN = '\033[92m'      # Bright green
    WARM_YELLOW = '\033[93m'    # Yellow
    COLD_BLUE = '\033[94m'      # Blue
    ICY_CYAN = '\033[96m'       # Cyan
    FREEZING_RED = '\033[91m'   # Red for very cold

    # Emphasis colors
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Reset
    RESET = '\033[0m'

    # Background colors
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'

    @staticmethod
    def get_streak_color(wins: int, losses: int) -> str:
        """Get color based on team streak"""
        if wins >= 5:
            return Colors.HOT_GREEN
        elif wins >= 3:
            return Colors.WARM_YELLOW
        elif losses >= 5:
            return Colors.FREEZING_RED
        elif losses >= 3:
            return Colors.COLD_BLUE
        else:
            return Colors.RESET

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Wrap text in color codes"""
        return f"{color}{text}{Colors.RESET}"


# Randomized story openers by sport
STORY_OPENERS = {
    'nfl': [
        "Week {week} brought fireworks to the NFL...",
        "The gridiron delivered drama this week...",
        "NFL fans witnessed {emotion} action...",
        "Sunday's slate had it all...",
        "The NFL landscape shifted this week...",
        "From coast to coast, the NFL delivered...",
        "Another week, another set of surprises...",
        "The playoff race heated up this week...",
    ],
    'nba': [
        "The NBA continues to amaze...",
        "Hardwood highlights dominated the night...",
        "Another {emotion} night in the Association...",
        "The NBA's best put on a show...",
        "From tip-off to final buzzer, drama unfolded...",
        "The league's stars shined bright...",
        "Basketball fans were treated to {emotion} performances...",
        "The NBA never disappoints...",
    ],
    'mlb': [
        "Baseball delivered {emotion} moments...",
        "The diamond was full of drama...",
        "Another day, another set of heroics...",
        "MLB's finest showcased their skills...",
        "From first pitch to final out...",
        "The pennant race continues to tighten...",
        "America's pastime produced thrills...",
        "The MLB storyline gets more interesting...",
    ],
    'nhl': [
        "The ice was on fire this week...",
        "Hockey fans witnessed {emotion} action...",
        "Another {emotion} night on the ice...",
        "The NHL continues to deliver...",
        "From puck drop to final horn...",
        "The playoff push intensifies...",
        "Hockey's best brought their A-game...",
        "The frozen battlefield produced drama...",
    ],
    'soccer': [
        "The beautiful game lived up to its name...",
        "Football fans witnessed {emotion} action...",
        "From the pitch to the stands, drama unfolded...",
        "The soccer world continues to evolve...",
        "Another matchday, another set of stories...",
        "Goals, saves, and everything in between...",
        "The global game delivered excellence...",
        "Clubs across the leagues competed fiercely...",
    ],
    'ncaaf': [
        "College football brought the chaos...",
        "Saturday's slate delivered {emotion} moments...",
        "The college football landscape shifted...",
        "From conference play to rivalry games...",
        "Another week of upsets and highlights...",
        "The road to the playoff continues...",
        "College football fans were treated to drama...",
        "Campus stadiums rocked with excitement...",
    ],
    'ncaab': [
        "College hoops delivered excitement...",
        "The hardwood was full of young talent...",
        "March may be far away, but the drama is here...",
        "College basketball showcased future stars...",
        "From coast to coast, the arenas erupted...",
        "Another night of college basketball magic...",
        "The tournament picture begins to form...",
        "Campus gymnasiums came alive...",
    ],
    'default': [
        "Sports fans were treated to {emotion} action...",
        "The competition was fierce...",
        "Athletes delivered memorable moments...",
        "From start to finish, drama unfolded...",
        "Another day of sporting excellence...",
    ]
}

# Emotion words for story openers
OPENER_EMOTIONS = [
    'thrilling', 'incredible', 'dramatic', 'outstanding', 'memorable',
    'spectacular', 'intense', 'exciting', 'remarkable', 'compelling'
]


def get_random_opener(sport: str, **kwargs) -> str:
    """Get a randomized story opener for a sport"""
    openers = STORY_OPENERS.get(sport.lower(), STORY_OPENERS['default'])
    opener = random.choice(openers)

    # Replace placeholders
    if '{emotion}' in opener:
        opener = opener.replace('{emotion}', random.choice(OPENER_EMOTIONS))
    if '{week}' in opener and 'week' in kwargs:
        opener = opener.replace('{week}', str(kwargs['week']))

    return opener


# Graphic header templates
HEADER_TEMPLATES = {
    'standard': """
╔══════════════════════════════════════════════════════════════╗
║  {sport_emoji}  {sport_name} Report - {date}  {sport_emoji}
╚══════════════════════════════════════════════════════════════╝
""",
    'compact': "{sport_emoji} {sport_name} | {date}",
    'bold': """
█████████████████████████████████████████████████████████████
   {sport_emoji}  {sport_name} REPORT - {date}
█████████████████████████████████████████████████████████████
""",
    'minimal': "{sport_emoji} {sport_name} — {date}",
}


# Section divider templates
SECTION_DIVIDERS = {
    'standard': "\n{'═' * 60}\n",
    'bold': "\n{'█' * 60}\n",
    'light': "\n{'─' * 60}\n",
    'double': "\n{'═' * 60}\n",
    'wave': "\n{'~' * 60}\n",
    'star': "\n{'*' * 60}\n",
}


# Auto-credits agent tags
AGENT_CREDITS = {
    'data_fetcher': '📡 Data Collection',
    'game_analyzer': '🎮 Game Analysis',
    'player_analyzer': '👤 Player Analysis',
    'odds_analyzer': '💰 Betting Analysis',
    'formatter': '📝 Report Formatting',
    'scheduler': '⏰ Scheduling',
}


class PresentationConfig:
    """Main presentation configuration class"""

    def __init__(
        self,
        tone: str = ToneLevel.BALANCED,
        theme: str = StyleTheme.ESPN,
        use_colors: bool = False,
        use_random_openers: bool = True,
        header_template: str = 'standard',
        track_credits: bool = False
    ):
        self.tone = tone
        self.theme = theme
        self.use_colors = use_colors
        self.use_random_openers = use_random_openers
        self.header_template = header_template
        self.track_credits = track_credits

        # Load configurations
        self.emoji = EMOJI_SETS.get(tone, EMOJI_SETS[ToneLevel.BALANCED])
        self.style = STYLE_THEMES.get(theme, STYLE_THEMES[StyleTheme.ESPN])
        self.credits = [] if track_credits else None

    def get_emoji(self, name: str) -> str:
        """Get emoji based on current tone setting"""
        return self.emoji.get(name, '')

    def get_opener(self, sport: str, **kwargs) -> str:
        """Get story opener"""
        if self.use_random_openers:
            return get_random_opener(sport, **kwargs)
        return ""

    def get_header_template(self) -> str:
        """Get header template"""
        return HEADER_TEMPLATES.get(self.header_template, HEADER_TEMPLATES['standard'])

    def add_credit(self, agent: str, section: str):
        """Add agent credit for a section"""
        if self.track_credits and self.credits is not None:
            self.credits.append({
                'agent': agent,
                'section': section,
                'label': AGENT_CREDITS.get(agent, agent)
            })

    def get_credits_section(self) -> str:
        """Generate credits section"""
        if not self.track_credits or not self.credits:
            return ""

        credits_text = "\n\n## Report Credits\n\n"
        credits_text += "This report was generated by the following agents:\n\n"

        for credit in self.credits:
            credits_text += f"- {credit['label']}: {credit['section']}\n"

        return credits_text

    def colorize_streak(self, text: str, wins: int, losses: int) -> str:
        """Apply color to streak text"""
        if not self.use_colors:
            return text

        color = Colors.get_streak_color(wins, losses)
        return Colors.colorize(text, color)


# Default configuration
DEFAULT_CONFIG = PresentationConfig()
