#!/usr/bin/env python3
"""
Viral Engineer v1.0 - Transform any topic into viral-ready Instagram Reel creative packages.

This module generates viral hooks, high-retention scripts, captions, hashtags, and scoring
for Instagram Reels optimized for maximum engagement and virality.
"""

import json
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class Hook:
    """Represents a viral hook with scoring metrics."""
    text: str
    curiosity: int
    controversy: int
    clarity: int

    @property
    def engagement_score(self) -> float:
        """Calculate engagement score: (curiosity + controversy) / 2"""
        return (self.curiosity + self.controversy) / 2


@dataclass
class ScriptSegment:
    """Represents a timed segment of the reel script."""
    time: str
    text: str


class ViralEngineer:
    """
    Main class for generating viral Instagram Reel content packages.

    Transforms topics into complete viral-ready creative packages including:
    - 5 scored viral hooks with auto-selected best hook
    - 12-second high-retention script with viral structure
    - Engagement-optimized caption
    - 15 viral hashtags
    - Comprehensive viral scoring breakdown
    """

    VERSION = "ViralEngineer-MVP-v1"

    # Viral trigger words for different tones
    TRIGGER_WORDS = {
        'energetic': [
            'insane', 'explosive', 'unstoppable', 'dominating', 'crushing',
            'beast mode', 'legendary', 'unreal', 'crazy', 'fire'
        ],
        'analytical': [
            'proves', 'data shows', 'analytics reveal', 'numbers confirm',
            'stats expose', 'metrics indicate', 'science says', 'breakdown'
        ],
        'emotional': [
            'heartbreaking', 'inspiring', 'shocking', 'devastating',
            'incredible', 'unbelievable', 'powerful', 'moving', 'raw'
        ],
        'comedic': [
            'nobody talks about', 'awkward truth', 'weird fact', 'plot twist',
            'wait for it', 'bet you didn\'t know', 'funny thing is', 'irony'
        ]
    }

    # Viral hook patterns
    HOOK_PATTERNS = {
        'question': [
            "Why does nobody talk about {topic}?",
            "What if I told you {topic}?",
            "Who decided {topic}?"
        ],
        'statement': [
            "{topic} and it's not even close",
            "{topic} is actually insane",
            "The truth about {topic}"
        ],
        'command': [
            "Stop sleeping on {topic}",
            "Watch what happens with {topic}",
            "Name a better {topic}"
        ],
        'controversy': [
            "{topic} is overrated and I'll prove it",
            "Everyone's wrong about {topic}",
            "{topic} changed everything"
        ]
    }

    # Debate-inducing caption templates
    CAPTION_TEMPLATES = [
        "Agree or nah?",
        "Be honest...",
        "Who agrees?",
        "Hot take or facts?",
        "Thoughts?",
        "Am I wrong though?",
        "Change my mind",
        "Who else?",
        "Debate me",
        "Facts or cap?"
    ]

    # Viral hashtag categories (sports-focused but adaptable)
    HASHTAG_CATEGORIES = {
        'broad': [
            'viral', 'fyp', 'foryou', 'trending', 'explorepage',
            'reels', 'reelsinstagram', 'instareels', 'instagood'
        ],
        'sports_broad': [
            'sports', 'sportsnews', 'athlete', 'goat', 'mvp',
            'sportsedits', 'sportstalk', 'sportsdebate'
        ],
        'engagement': [
            'debate', 'facts', 'truth', 'hottake', 'controversial',
            'real', 'thoughts', 'opinion'
        ]
    }

    def __init__(self):
        """Initialize the Viral Engineer."""
        self.version = self.VERSION

    def generate_hooks(self, topic: str, tone: str = 'energetic', count: int = 5) -> List[Hook]:
        """
        Generate viral hooks for the given topic.

        Args:
            topic: The topic to create hooks about
            tone: The tone to use (energetic, analytical, emotional, comedic)
            count: Number of hooks to generate

        Returns:
            List of Hook objects with scoring
        """
        hooks = []
        patterns = []

        # Select patterns based on tone
        if tone == 'energetic':
            patterns = [
                f"This {topic} stat will blow your mind",
                f"{topic} just changed the game forever",
                f"Nobody's talking about this {topic} fact",
                f"The {topic} debate is finally over",
                f"Wait till you see this {topic} play"
            ]
        elif tone == 'analytical':
            patterns = [
                f"The data on {topic} is shocking",
                f"{topic} by the numbers is insane",
                f"This {topic} stat proves everything",
                f"Analytics reveal the truth about {topic}",
                f"The science behind {topic} is wild"
            ]
        elif tone == 'emotional':
            patterns = [
                f"This {topic} moment broke me",
                f"The real story behind {topic}",
                f"{topic} hits different now",
                f"Why {topic} means everything",
                f"The {topic} truth nobody tells you"
            ]
        elif tone == 'comedic':
            patterns = [
                f"Nobody told me {topic} was this funny",
                f"The awkward truth about {topic}",
                f"{topic} but make it weird",
                f"Plot twist with {topic}",
                f"The {topic} paradox is hilarious"
            ]
        else:
            # Default energetic
            patterns = [
                f"{topic} is absolutely insane",
                f"This {topic} fact will shock you",
                f"Everyone's wrong about {topic}",
                f"The {topic} debate just ended",
                f"{topic} changed everything"
            ]

        # Generate hooks with scoring
        for i, pattern in enumerate(patterns[:count]):
            # Score each hook
            curiosity = self._score_curiosity(pattern)
            controversy = self._score_controversy(pattern)
            clarity = self._score_clarity(pattern)

            hooks.append(Hook(
                text=pattern,
                curiosity=curiosity,
                controversy=controversy,
                clarity=clarity
            ))

        return hooks

    def _score_curiosity(self, text: str) -> int:
        """Score hook curiosity (1-10) based on mystery/open loop triggers."""
        score = 5  # Base score

        curiosity_triggers = [
            'why', 'what if', 'nobody', 'secret', 'truth', 'reveal',
            'shocking', 'wait', 'you won\'t believe', 'never', 'hidden'
        ]

        text_lower = text.lower()
        for trigger in curiosity_triggers:
            if trigger in text_lower:
                score += 1

        # Questions get bonus
        if '?' in text:
            score += 1

        return min(score, 10)

    def _score_controversy(self, text: str) -> int:
        """Score controversy (1-10) based on debate-inducing language."""
        score = 4  # Base score

        controversy_triggers = [
            'wrong', 'overrated', 'underrated', 'best', 'worst', 'never',
            'always', 'everyone', 'nobody', 'changed', 'proves', 'debate'
        ]

        text_lower = text.lower()
        for trigger in controversy_triggers:
            if trigger in text_lower:
                score += 1

        # Absolute statements get bonus
        if any(word in text_lower for word in ['is', 'are', 'will', 'must']):
            score += 1

        return min(score, 10)

    def _score_clarity(self, text: str) -> int:
        """Score clarity (1-10) - how clear and understandable the hook is."""
        score = 8  # Start high

        # Penalize if too long
        word_count = len(text.split())
        if word_count > 12:
            score -= 2
        elif word_count > 10:
            score -= 1

        # Penalize complex words
        complex_words = ['nevertheless', 'furthermore', 'consequently', 'notwithstanding']
        for word in complex_words:
            if word in text.lower():
                score -= 1

        return max(min(score, 10), 1)

    def select_best_hook(self, hooks: List[Hook]) -> Hook:
        """
        Select the best hook based on engagement score.

        Formula: (curiosity + controversy) / 2
        """
        return max(hooks, key=lambda h: h.engagement_score)

    def generate_script(self, topic: str, hook: str, tone: str = 'energetic') -> List[ScriptSegment]:
        """
        Generate a 12-second high-retention script.

        Structure:
        - 0-1.5s: Hook
        - 1.5-3s: Surprise twist/insight
        - 3-6s: Quick proof/stat
        - 6-10s: Punchy conclusion
        - 10-12s: Loop closer

        Args:
            topic: The main topic
            hook: The selected hook
            tone: The tone to use

        Returns:
            List of ScriptSegment objects
        """
        segments = []

        # Segment 1: Hook (0-1.5s)
        segments.append(ScriptSegment("0-1.5", hook))

        # Segment 2: Twist (1.5-3s)
        if tone == 'energetic':
            twist = f"Here's what makes {topic} absolutely insane."
        elif tone == 'analytical':
            twist = f"The numbers behind {topic} tell a different story."
        elif tone == 'emotional':
            twist = f"But the truth about {topic} hits different."
        else:  # comedic
            twist = f"But wait, the {topic} plot thickens."

        segments.append(ScriptSegment("1.5-3", twist))

        # Segment 3: Proof/Stat (3-6s)
        if tone == 'energetic':
            proof = f"In the last season alone, {topic} broke 3 records that stood for decades."
        elif tone == 'analytical':
            proof = f"Stats show {topic} has a 47% higher impact than anything we've seen."
        elif tone == 'emotional':
            proof = f"This changed how we see {topic} forever."
        else:  # comedic
            proof = f"Turns out {topic} is actually a 200 IQ move disguised as chaos."

        segments.append(ScriptSegment("3-6", proof))

        # Segment 4: Conclusion (6-10s)
        if tone == 'energetic':
            conclusion = f"That's why {topic} is the most underrated story of the year."
        elif tone == 'analytical':
            conclusion = f"The data doesn't lie - {topic} is elite tier."
        elif tone == 'emotional':
            conclusion = f"And that's why {topic} means everything."
        else:  # comedic
            conclusion = f"So yeah, {topic} is simultaneously genius and ridiculous."

        segments.append(ScriptSegment("6-10", conclusion))

        # Segment 5: Loop closer (10-12s)
        loop = f"Still think {topic} is just hype?"
        segments.append(ScriptSegment("10-12", loop))

        return segments

    def generate_caption(self, topic: str, hook: str) -> str:
        """
        Generate a caption that invites comments and debate.

        Under 15 words, includes debate trigger.
        """
        # Extract key phrase from hook
        import random
        debate_trigger = random.choice(self.CAPTION_TEMPLATES)

        # Create short caption with debate trigger
        caption = f"{debate_trigger}"

        return caption

    def generate_hashtags(self, topic: str, count: int = 15) -> List[str]:
        """
        Generate viral hashtags mixing broad and niche tags.

        Args:
            topic: The main topic
            count: Number of hashtags (default 15)

        Returns:
            List of lowercase hashtags
        """
        hashtags = []

        # Add broad viral tags (5)
        hashtags.extend(self.HASHTAG_CATEGORIES['broad'][:5])

        # Add sports broad tags (4)
        hashtags.extend(self.HASHTAG_CATEGORIES['sports_broad'][:4])

        # Add engagement tags (3)
        hashtags.extend(self.HASHTAG_CATEGORIES['engagement'][:3])

        # Add topic-specific tags (3)
        topic_lower = topic.lower().replace(' ', '')
        hashtags.append(topic_lower)
        hashtags.append(f"{topic_lower}2024")
        hashtags.append(f"{topic_lower}edits")

        # Ensure all lowercase and unique
        hashtags = [tag.lower() for tag in hashtags[:count]]

        return hashtags

    def calculate_viral_score(self, script: List[ScriptSegment], hook: Hook) -> Dict[str, int]:
        """
        Calculate viral scoring across 4 pillars.

        Pillars:
        1. Curiosity Score (open loops, mystery)
        2. Emotional Trigger Score (shock, passion, hype)
        3. Controversy/Debate Score (disagreement potential)
        4. Replayability Score (loop structure)

        Returns:
            Dict with individual scores and total
        """
        # Combine all script text
        full_script = " ".join([seg.text for seg in script])

        # 1. Curiosity Score
        curiosity = hook.curiosity

        # 2. Emotional Trigger Score
        emotional_triggers = [
            'insane', 'shocking', 'incredible', 'unbelievable', 'broke',
            'changed', 'forever', 'truth', 'everything', 'wild'
        ]
        emotion_score = 5
        for trigger in emotional_triggers:
            if trigger in full_script.lower():
                emotion_score += 1
        emotion_score = min(emotion_score, 10)

        # 3. Debate/Controversy Score
        debate_score = hook.controversy

        # 4. Replayability Score (check for loop structure)
        replay_score = 7  # Base score for having structure

        # Check if loop closer references hook
        if script[-1].text and any(word in script[0].text.lower() for word in script[-1].text.lower().split()[:3]):
            replay_score += 2

        # Check for question at end
        if '?' in script[-1].text:
            replay_score += 1

        replay_score = min(replay_score, 10)

        total = curiosity + emotion_score + debate_score + replay_score

        return {
            'curiosity': curiosity,
            'emotion': emotion_score,
            'debate': debate_score,
            'replayability': replay_score,
            'total': total
        }

    def generate(self, topic: str, tone: str = 'energetic') -> Dict[str, Any]:
        """
        Generate complete viral reel package.

        Args:
            topic: The topic to create content about
            tone: Tone (energetic, analytical, emotional, comedic)

        Returns:
            Complete viral package as dictionary
        """
        # Validate tone
        valid_tones = ['energetic', 'analytical', 'emotional', 'comedic']
        if tone not in valid_tones:
            tone = 'energetic'

        # Generate 5 hooks
        hooks = self.generate_hooks(topic, tone, count=5)

        # Select best hook
        best_hook = self.select_best_hook(hooks)

        # Generate script
        script = self.generate_script(topic, best_hook.text, tone)

        # Generate caption
        caption = self.generate_caption(topic, best_hook.text)

        # Generate hashtags
        hashtags = self.generate_hashtags(topic, count=15)

        # Calculate scores
        scores = self.calculate_viral_score(script, best_hook)

        # Build output package
        package = {
            'topic': topic,
            'best_hook': best_hook.text,
            'all_hooks': [
                {
                    'text': h.text,
                    'curiosity': h.curiosity,
                    'controversy': h.controversy,
                    'clarity': h.clarity
                }
                for h in hooks
            ],
            'script': [
                {
                    'time': seg.time,
                    'text': seg.text
                }
                for seg in script
            ],
            'caption': caption,
            'hashtags': hashtags,
            'scores': scores,
            'version': self.VERSION
        }

        return package

    def generate_json(self, topic: str, tone: str = 'energetic') -> str:
        """
        Generate viral package and return as JSON string.

        Args:
            topic: The topic
            tone: The tone

        Returns:
            JSON string of the package
        """
        package = self.generate(topic, tone)
        return json.dumps(package, indent=2, ensure_ascii=False)


def main():
    """CLI demo for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python viral_reel_generator.py <topic> [tone]")
        print("Tones: energetic, analytical, emotional, comedic")
        sys.exit(1)

    topic = sys.argv[1]
    tone = sys.argv[2] if len(sys.argv) > 2 else 'energetic'

    engineer = ViralEngineer()
    result = engineer.generate_json(topic, tone)

    print(result)


if __name__ == '__main__':
    main()
