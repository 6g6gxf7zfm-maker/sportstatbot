"""
Story Rater - Editor rating system for stories (A-F grading)
"""

from typing import Dict, List, Any, Tuple
import re


class StoryRater:
    """
    Rate stories on clarity, insight, and structure

    Grading scale:
    - A (90-100): Excellent - publication ready
    - B (80-89): Good - minor improvements needed
    - C (70-79): Fair - significant improvements needed
    - D (60-69): Poor - major revision required
    - F (0-59): Failing - complete rewrite needed
    """

    # Scoring criteria weights
    WEIGHTS = {
        'clarity': 0.30,
        'insight': 0.35,
        'structure': 0.25,
        'engagement': 0.10
    }

    def __init__(self):
        pass

    def rate_story(
        self,
        story: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rate a story comprehensively

        Args:
            story: Story dictionary
            context: Optional context for insight evaluation

        Returns:
            Dictionary with rating details
        """
        # Calculate individual scores
        clarity_score = self._rate_clarity(story)
        insight_score = self._rate_insight(story, context)
        structure_score = self._rate_structure(story)
        engagement_score = self._rate_engagement(story)

        # Calculate weighted total
        total_score = (
            clarity_score * self.WEIGHTS['clarity'] +
            insight_score * self.WEIGHTS['insight'] +
            structure_score * self.WEIGHTS['structure'] +
            engagement_score * self.WEIGHTS['engagement']
        )

        # Determine letter grade
        letter_grade = self._score_to_grade(total_score)

        # Generate feedback
        feedback = self._generate_feedback(
            clarity_score,
            insight_score,
            structure_score,
            engagement_score,
            story
        )

        return {
            'overall_score': round(total_score, 1),
            'letter_grade': letter_grade,
            'scores': {
                'clarity': round(clarity_score, 1),
                'insight': round(insight_score, 1),
                'structure': round(structure_score, 1),
                'engagement': round(engagement_score, 1)
            },
            'feedback': feedback,
            'strengths': self._identify_strengths(story),
            'improvements': self._suggest_improvements(story, total_score)
        }

    def _rate_clarity(self, story: Dict[str, Any]) -> float:
        """Rate story clarity (0-100)"""
        score = 50.0  # Base score

        body = story.get('body', '')

        # Check readability metrics
        if body:
            # Sentence length (shorter is clearer)
            sentences = re.split(r'[.!?]+', body)
            sentences = [s.strip() for s in sentences if s.strip()]

            if sentences:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

                if avg_sentence_length < 20:
                    score += 20
                elif avg_sentence_length < 30:
                    score += 10

            # Jargon check (fewer complex words is clearer)
            complex_words = len(re.findall(r'\b\w{12,}\b', body))
            total_words = len(body.split())

            if total_words > 0:
                jargon_ratio = complex_words / total_words
                if jargon_ratio < 0.05:
                    score += 15
                elif jargon_ratio < 0.10:
                    score += 8

            # Formatting (headings, bullets help clarity)
            if '##' in body or '###' in body:
                score += 10

            if re.search(r'^\s*[-*•]\s+', body, re.MULTILINE):
                score += 5

        # TL;DR presence (helps clarity)
        if story.get('tldr'):
            score += 10

        return min(score, 100.0)

    def _rate_insight(
        self,
        story: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Rate story insight (0-100)"""
        score = 50.0  # Base score

        body = story.get('body', '')

        # Check for analysis depth
        analysis_markers = [
            'because', 'therefore', 'as a result', 'this means',
            'indicates', 'suggests', 'reveals', 'demonstrates'
        ]

        analysis_count = sum(1 for marker in analysis_markers if marker in body.lower())
        score += min(analysis_count * 5, 20)

        # Check for data-driven insights
        if re.search(r'\d+%|\d+\.\d+', body):
            score += 10

        # Check for comparisons
        comparison_markers = ['compared to', 'versus', 'while', 'whereas', 'more than', 'less than']
        comparison_count = sum(1 for marker in comparison_markers if marker in body.lower())
        score += min(comparison_count * 3, 15)

        # Context utilization
        if context:
            # Check if story uses multiple data sources
            if story.get('metadata', {}).get('data_sources'):
                score += 10

        # Unique perspective
        if story.get('perspective') and story['perspective'] != 'neutral':
            score += 5

        return min(score, 100.0)

    def _rate_structure(self, story: Dict[str, Any]) -> float:
        """Rate story structure (0-100)"""
        score = 50.0  # Base score

        # Has headline
        if story.get('headline'):
            score += 15

        # Has subhead
        if story.get('subhead'):
            score += 10

        # Has TL;DR
        if story.get('tldr'):
            score += 10

        # Has body
        if story.get('body'):
            body = story['body']

            # Body length (not too short, not too long)
            word_count = len(body.split())
            if 200 <= word_count <= 1000:
                score += 15
            elif 100 <= word_count <= 1500:
                score += 10

            # Paragraph structure
            paragraphs = [p for p in body.split('\n\n') if p.strip()]
            if 3 <= len(paragraphs) <= 10:
                score += 10

        # Has conclusion
        if story.get('conclusion'):
            score += 5

        # Has supporting elements
        if story.get('sidebars'):
            score += 5

        return min(score, 100.0)

    def _rate_engagement(self, story: Dict[str, Any]) -> float:
        """Rate story engagement (0-100)"""
        score = 50.0  # Base score

        body = story.get('body', '')

        # Emotional language
        emotion_words = [
            'stunning', 'incredible', 'remarkable', 'dramatic', 'thrilling',
            'exciting', 'shocking', 'amazing', 'phenomenal', 'explosive'
        ]

        emotion_count = sum(1 for word in emotion_words if word in body.lower())
        score += min(emotion_count * 4, 16)

        # Questions (engage reader)
        question_count = body.count('?')
        score += min(question_count * 5, 15)

        # Pull quotes (highly engaging)
        if story.get('pullquotes'):
            score += 10

        # Trivia (adds interest)
        if story.get('trivia'):
            score += 5

        # Emojis (visual engagement)
        emoji_count = len(re.findall(r'[\U0001F000-\U0001F9FF]', body))
        score += min(emoji_count * 2, 10)

        # Active voice (more engaging)
        passive_markers = ['was', 'were', 'been', 'being']
        passive_count = sum(1 for marker in passive_markers if f' {marker} ' in body.lower())
        total_words = len(body.split())

        if total_words > 0:
            passive_ratio = passive_count / total_words
            if passive_ratio < 0.05:
                score += 10
            elif passive_ratio < 0.10:
                score += 5

        return min(score, 100.0)

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_feedback(
        self,
        clarity: float,
        insight: float,
        structure: float,
        engagement: float,
        story: Dict[str, Any]
    ) -> List[str]:
        """Generate specific feedback points"""
        feedback = []

        # Clarity feedback
        if clarity < 70:
            feedback.append("Consider simplifying sentence structure for better clarity")
        elif clarity >= 90:
            feedback.append("Excellent clarity - easy to understand")

        # Insight feedback
        if insight < 70:
            feedback.append("Add more analysis and data-driven insights")
        elif insight >= 90:
            feedback.append("Strong analytical depth and insights")

        # Structure feedback
        if structure < 70:
            feedback.append("Improve structure with clearer sections and organization")
        elif structure >= 90:
            feedback.append("Well-structured with strong organization")

        # Engagement feedback
        if engagement < 70:
            feedback.append("Increase engagement with more dynamic language")
        elif engagement >= 90:
            feedback.append("Highly engaging and compelling narrative")

        return feedback

    def _identify_strengths(self, story: Dict[str, Any]) -> List[str]:
        """Identify story strengths"""
        strengths = []

        if story.get('headline'):
            strengths.append("Strong headline")

        if story.get('tldr'):
            strengths.append("Clear TL;DR summary")

        if story.get('sidebars'):
            strengths.append("Effective use of sidebars")

        if story.get('pullquotes'):
            strengths.append("Impactful pull quotes")

        body = story.get('body', '')
        word_count = len(body.split())
        if word_count > 300:
            strengths.append("Comprehensive coverage")

        return strengths

    def _suggest_improvements(
        self,
        story: Dict[str, Any],
        score: float
    ) -> List[str]:
        """Suggest specific improvements"""
        improvements = []

        # Missing elements
        if not story.get('tldr'):
            improvements.append("Add TL;DR summary for quick scanning")

        if not story.get('subhead'):
            improvements.append("Add subhead to clarify focus")

        if not story.get('sidebars'):
            improvements.append("Consider adding sidebar with key stats")

        if not story.get('pullquotes'):
            improvements.append("Extract 1-2 compelling pull quotes")

        # Content improvements based on score
        if score < 70:
            improvements.append("Major revision recommended - focus on structure and clarity")

        body = story.get('body', '')
        if body:
            word_count = len(body.split())
            if word_count < 200:
                improvements.append("Expand content with more detail and analysis")
            elif word_count > 1500:
                improvements.append("Consider condensing to improve readability")

        return improvements

    def batch_rate(
        self,
        stories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rate multiple stories

        Args:
            stories: List of story dictionaries

        Returns:
            List of rating results
        """
        return [self.rate_story(story) for story in stories]

    def generate_report(
        self,
        ratings: List[Dict[str, Any]]
    ) -> str:
        """
        Generate summary report of ratings

        Args:
            ratings: List of rating results

        Returns:
            Formatted report string
        """
        report = "# Story Ratings Report\n\n"

        # Overall statistics
        if ratings:
            avg_score = sum(r['overall_score'] for r in ratings) / len(ratings)
            grade_distribution = {}

            for rating in ratings:
                grade = rating['letter_grade']
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

            report += f"**Average Score:** {avg_score:.1f}\n\n"
            report += "**Grade Distribution:**\n"
            for grade in ['A', 'B', 'C', 'D', 'F']:
                count = grade_distribution.get(grade, 0)
                report += f"- {grade}: {count} stories\n"

            report += "\n## Individual Ratings\n\n"

            # List each rating
            for i, rating in enumerate(ratings, 1):
                report += f"### Story #{i}: Grade {rating['letter_grade']} ({rating['overall_score']:.1f})\n\n"

                # Scores breakdown
                report += "**Scores:**\n"
                for metric, score in rating['scores'].items():
                    report += f"- {metric.capitalize()}: {score:.1f}\n"

                # Feedback
                if rating['feedback']:
                    report += "\n**Feedback:**\n"
                    for item in rating['feedback']:
                        report += f"- {item}\n"

                report += "\n"

        return report
