"""
Pull Quote Generator - Auto-suggest impactful pull quotes
"""

import re
from typing import List, Dict, Any


class PullQuoteGenerator:
    """Generate and suggest pull quotes from story text"""

    # Markers for impactful statements
    IMPACT_MARKERS = [
        'unprecedented', 'historic', 'remarkable', 'stunning', 'explosive',
        'dominant', 'record-breaking', 'phenomenal', 'incredible', 'extraordinary',
        'never before', 'first time', 'best ever', 'worst ever', 'all-time'
    ]

    def __init__(self, min_length: int = 30, max_length: int = 120):
        """
        Initialize pull quote generator

        Args:
            min_length: Minimum character length for pull quote
            max_length: Maximum character length for pull quote
        """
        self.min_length = min_length
        self.max_length = max_length

    def extract_pullquotes(
        self,
        text: str,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Extract pull quotes from text

        Args:
            text: Story text to analyze
            count: Number of pull quotes to extract

        Returns:
            List of pull quote dictionaries with text and metadata
        """
        # Split into sentences
        sentences = self._split_sentences(text)

        # Score each sentence
        scored_sentences = []
        for sentence in sentences:
            score = self._score_sentence(sentence)
            if score > 0:
                scored_sentences.append({
                    'text': sentence,
                    'score': score,
                    'length': len(sentence)
                })

        # Sort by score
        scored_sentences.sort(key=lambda x: x['score'], reverse=True)

        # Filter by length and take top N
        pullquotes = []
        for item in scored_sentences:
            if (self.min_length <= item['length'] <= self.max_length and
                len(pullquotes) < count):
                pullquotes.append({
                    'text': self._clean_quote(item['text']),
                    'score': item['score'],
                    'type': self._classify_quote(item['text'])
                })

        return pullquotes

    def generate_from_context(
        self,
        context: Dict[str, Any],
        count: int = 3
    ) -> List[str]:
        """
        Generate pull quotes from story context

        Args:
            context: Story context data
            count: Number of quotes to generate

        Returns:
            List of pull quote strings
        """
        quotes = []

        # Generate from trends
        trends = context.get('trends', [])
        for trend in trends[:2]:
            if trend.get('type') == 'hot_streak':
                quote = f"{trend.get('team', 'Team')} continues their remarkable run"
                quotes.append(quote)

        # Generate from player performances
        players = context.get('standout_players', [])
        for player in players[:2]:
            if len(quotes) < count:
                quote = f"{player.get('player', 'Player')} putting up historic numbers"
                quotes.append(quote)

        return quotes[:count]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Remove markdown formatting
        text = re.sub(r'\*\*|__|\*|_', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)

        # Clean and filter
        cleaned = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                cleaned.append(sentence)

        return cleaned

    def _score_sentence(self, sentence: str) -> float:
        """Score a sentence for pull quote potential"""
        score = 0.0
        lower_sentence = sentence.lower()

        # Check for impact markers
        for marker in self.IMPACT_MARKERS:
            if marker in lower_sentence:
                score += 10.0

        # Check for quotes (already quoted text is good)
        if '"' in sentence or '"' in sentence or '"' in sentence:
            score += 5.0

        # Check for numbers/stats
        if re.search(r'\d+', sentence):
            score += 3.0

        # Check for superlatives
        superlatives = ['best', 'worst', 'most', 'least', 'greatest', 'top', 'bottom']
        for sup in superlatives:
            if f' {sup} ' in f' {lower_sentence} ':
                score += 5.0

        # Bonus for exclamation points
        if '!' in sentence:
            score += 2.0

        # Penalty for being too long or too short
        length = len(sentence)
        if length < self.min_length or length > self.max_length:
            score *= 0.3

        return score

    def _clean_quote(self, text: str) -> str:
        """Clean quote text for display"""
        # Remove leading/trailing punctuation
        text = text.strip('.,;:- ')

        # Ensure it ends with punctuation
        if not text[-1] in '.!?':
            text += '.'

        return text

    def _classify_quote(self, text: str) -> str:
        """Classify the type of quote"""
        lower_text = text.lower()

        if any(marker in lower_text for marker in ['record', 'best', 'worst', 'first']):
            return 'record'
        elif any(marker in lower_text for marker in ['win', 'victory', 'dominate']):
            return 'performance'
        elif any(marker in lower_text for marker in ['injury', 'hurt', 'out']):
            return 'injury'
        elif re.search(r'\d+', text):
            return 'statistical'
        else:
            return 'general'
