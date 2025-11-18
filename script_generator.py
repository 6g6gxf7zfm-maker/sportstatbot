"""
AI Script Generator for Viral Sports Reels
"""
import openai
import random
from config import OPENAI_API_KEY, SPORTS_CATEGORIES, VIDEO_TEMPLATES


class ScriptGenerator:
    def __init__(self):
        self.client = None
        if OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                print("Will use fallback scripts.")

    def generate_script(self, category=None, template=None, custom_prompt=None):
        """
        Generate a viral sports script for Instagram Reels

        Args:
            category: Sports category (NBA, NFL, etc.) or None for random
            template: Video template type or None for random
            custom_prompt: Custom prompt to override template

        Returns:
            dict with 'hook', 'content', 'cta', 'hashtags', 'voiceover'
        """
        if not category:
            category = random.choice(SPORTS_CATEGORIES)

        if not template:
            template = random.choice(VIDEO_TEMPLATES)

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._build_prompt(category, template)

        # Check if OpenAI client is available
        if not self.client:
            print("⚠️  OpenAI API key not configured. Using fallback script.")
            return self._get_fallback_script(category, template)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a viral Instagram Reels content creator specializing in sports.
Create engaging, short-form content optimized for 15-30 second videos.
Use attention-grabbing hooks, surprising facts, and strong calls-to-action.
Keep language casual, energetic, and Gen-Z friendly."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,
                max_tokens=500
            )

            content = response.choices[0].message.content
            parsed = self._parse_response(content)
            parsed['category'] = category
            parsed['template'] = template

            return parsed

        except Exception as e:
            print(f"Error generating script: {e}")
            return self._get_fallback_script(category, template)

    def _build_prompt(self, category, template):
        """Build prompt based on category and template"""
        template_prompts = {
            'stat_reveal': f"""Create a mind-blowing {category} stat reveal for Instagram Reels.
Format:
HOOK: (One shocking question or statement - 5-8 words)
CONTENT: (2-3 lines revealing the stat with context)
CTA: (Call to action - encourage engagement)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)""",

            'prediction': f"""Create a bold {category} prediction for Instagram Reels.
Format:
HOOK: (Controversial prediction - 5-8 words)
CONTENT: (2-3 lines with reasoning)
CTA: (Ask viewers to agree/disagree)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)""",

            'fact_drop': f"""Create a surprising {category} fact for Instagram Reels.
Format:
HOOK: (Intriguing question - 5-8 words)
CONTENT: (2-3 lines revealing the fact)
CTA: (Encourage likes/follows)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)""",

            'vs_comparison': f"""Create a {category} player/team comparison for Instagram Reels.
Format:
HOOK: (X vs Y - who wins? - 5-8 words)
CONTENT: (2-3 lines comparing stats/achievements)
CTA: (Ask viewers to pick a side)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)""",

            'top_5_list': f"""Create a top 5 {category} list for Instagram Reels.
Format:
HOOK: (Top 5 announcement - 5-8 words)
CONTENT: (List 5 items with brief descriptions)
CTA: (Ask what they missed)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 20-25 seconds when read)""",

            'did_you_know': f"""Create a 'Did You Know' {category} fact for Instagram Reels.
Format:
HOOK: (Did you know... - 5-8 words)
CONTENT: (2-3 lines with the fact and context)
CTA: (Encourage sharing/tagging)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)""",

            'highlight_moment': f"""Create content about an iconic {category} moment for Instagram Reels.
Format:
HOOK: (Describe the moment - 5-8 words)
CONTENT: (2-3 lines with details and impact)
CTA: (Ask if they remember it)
HASHTAGS: (10-15 trending hashtags)
VOICEOVER: (Full script for text-to-speech, 15-25 seconds when read)"""
        }

        return template_prompts.get(template, template_prompts['stat_reveal'])

    def _parse_response(self, content):
        """Parse AI response into structured format"""
        lines = content.strip().split('\n')
        parsed = {
            'hook': '',
            'content': '',
            'cta': '',
            'hashtags': [],
            'voiceover': ''
        }

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            if line.upper().startswith('HOOK:'):
                current_section = 'hook'
                parsed['hook'] = line.split(':', 1)[1].strip()
            elif line.upper().startswith('CONTENT:'):
                current_section = 'content'
                parsed['content'] = line.split(':', 1)[1].strip()
            elif line.upper().startswith('CTA:'):
                current_section = 'cta'
                parsed['cta'] = line.split(':', 1)[1].strip()
            elif line.upper().startswith('HASHTAGS:'):
                current_section = 'hashtags'
                hashtag_line = line.split(':', 1)[1].strip()
                parsed['hashtags'] = [tag.strip() for tag in hashtag_line.split() if tag.startswith('#')]
            elif line.upper().startswith('VOICEOVER:'):
                current_section = 'voiceover'
                parsed['voiceover'] = line.split(':', 1)[1].strip()
            else:
                # Continue adding to current section
                if current_section == 'content':
                    parsed['content'] += ' ' + line
                elif current_section == 'voiceover':
                    parsed['voiceover'] += ' ' + line
                elif current_section == 'hashtags' and line.startswith('#'):
                    parsed['hashtags'].extend([tag.strip() for tag in line.split() if tag.startswith('#')])

        # Clean up
        parsed['hook'] = parsed['hook'].strip()
        parsed['content'] = parsed['content'].strip()
        parsed['cta'] = parsed['cta'].strip()
        parsed['voiceover'] = parsed['voiceover'].strip()

        # Ensure we have hashtags
        if not parsed['hashtags']:
            parsed['hashtags'] = self._generate_default_hashtags(parsed.get('category', 'Sports'))

        return parsed

    def _generate_default_hashtags(self, category):
        """Generate default hashtags if AI doesn't provide them"""
        base_tags = ['#sports', '#viral', '#fyp', '#reels', '#instagram', '#trending']
        category_tags = {
            'NBA': ['#nba', '#basketball', '#hoops', '#nbabasketball', '#ballers'],
            'NFL': ['#nfl', '#football', '#nflfootball', '#gridiron', '#touchdown'],
            'MLB': ['#mlb', '#baseball', '#homerun', '#mlbbaseball', '#baseballlife'],
            'Soccer': ['#soccer', '#football', '#futbol', '#goal', '#worldcup'],
        }

        specific = category_tags.get(category, ['#sports', '#athlete', '#game'])
        return base_tags + specific

    def _get_fallback_script(self, category, template):
        """Fallback script if API fails"""
        return {
            'hook': f'Crazy {category} Stat Alert! 🚨',
            'content': 'This is a placeholder script. Please add your OpenAI API key to generate AI content.',
            'cta': 'Follow for more sports content!',
            'hashtags': ['#sports', '#viral', '#fyp', '#reels', '#trending'],
            'voiceover': 'This is a placeholder script. Please add your OpenAI API key to .env file to generate AI-powered content.',
            'category': category,
            'template': template
        }

    def generate_batch(self, count=5, category=None):
        """Generate multiple scripts at once"""
        scripts = []
        for i in range(count):
            print(f"Generating script {i+1}/{count}...")
            script = self.generate_script(category=category)
            scripts.append(script)
        return scripts


if __name__ == "__main__":
    # Test script generation
    generator = ScriptGenerator()

    print("=" * 60)
    print("TESTING SCRIPT GENERATOR")
    print("=" * 60)

    script = generator.generate_script(category='NBA', template='stat_reveal')

    print(f"\nCategory: {script['category']}")
    print(f"Template: {script['template']}")
    print(f"\nHOOK: {script['hook']}")
    print(f"\nCONTENT: {script['content']}")
    print(f"\nCTA: {script['cta']}")
    print(f"\nHASHTAGS: {' '.join(script['hashtags'])}")
    print(f"\nVOICEOVER: {script['voiceover']}")
