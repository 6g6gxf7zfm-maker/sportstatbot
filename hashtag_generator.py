"""
Hashtag Generator for Viral Instagram Reels
"""
import random
from datetime import datetime


class HashtagGenerator:
    """Generate trending and relevant hashtags for sports content"""

    # Base viral hashtags
    VIRAL_TAGS = [
        '#viral', '#fyp', '#foryou', '#trending', '#explore',
        '#reels', '#reelsinstagram', '#instareels', '#explorepage',
        '#instagood', '#instagram', '#instaviral'
    ]

    # Sports general hashtags
    SPORTS_GENERAL = [
        '#sports', '#sportsnews', '#sportshighlights', '#athlete',
        '#espn', '#sportscenter', '#sportsedits', '#sportsfan',
        '#gameday', '#sportlife', '#athletics', '#competition'
    ]

    # Category-specific hashtags
    CATEGORY_TAGS = {
        'NBA': [
            '#nba', '#basketball', '#hoops', '#nbahighlights',
            '#nbabasketball', '#bball', '#ballers', '#nbaplayoffs',
            '#nbamemes', '#nbafinals', '#nbadraft', '#nbateams',
            '#basketballneverstops', '#basketballislife', '#dunks'
        ],
        'NFL': [
            '#nfl', '#football', '#nflfootball', '#nflnews',
            '#americanfootball', '#touchdown', '#nflhighlights',
            '#nflplayoffs', '#superbowl', '#nfldraft', '#gridiron',
            '#footballseason', '#nflmemes', '#quarterback', '#nflteams'
        ],
        'MLB': [
            '#mlb', '#baseball', '#baseballlife', '#mlbbaseball',
            '#homerun', '#mlbnews', '#worldseries', '#mlbplayoffs',
            '#baseballseason', '#pitcher', '#mlbhighlights',
            '#baseballfan', '#mlbdraft', '#majorleaguebaseball'
        ],
        'NHL': [
            '#nhl', '#hockey', '#hockeygram', '#hockeylife',
            '#icehockey', '#nhlhockey', '#hockeyfan', '#stanleycup',
            '#nhlplayoffs', '#hockeyhighlights', '#puck', '#nhlnews'
        ],
        'Soccer': [
            '#soccer', '#football', '#futbol', '#goal', '#fifa',
            '#soccerlife', '#soccerskills', '#worldcup', '#ucl',
            '#premierleague', '#championsleague', '#messi', '#ronaldo',
            '#soccerhighlights', '#footballskills', '#soccerplayer'
        ],
        'Tennis': [
            '#tennis', '#tennislife', '#tennisplayer', '#atp', '#wta',
            '#grandslam', '#wimbledon', '#usopen', '#rolandgarros',
            '#australianopen', '#tennislove', '#tenniscourt'
        ],
        'Boxing/MMA': [
            '#boxing', '#mma', '#ufc', '#fight', '#knockout',
            '#boxingtraining', '#mmafighter', '#boxinglife',
            '#ufcfighter', '#combatsports', '#boxingnews', '#mmahighlights'
        ],
        'Olympics': [
            '#olympics', '#olympicgames', '#teamusa', '#olympian',
            '#olympicathletes', '#olympicspirit', '#goldmedal',
            '#olympicsports', '#olympichistory'
        ],
        'College Sports': [
            '#collegesports', '#ncaa', '#collegefootball', '#collegebasketball',
            '#marchmadness', '#ncaafootball', '#ncaabasketball',
            '#collegeathlete', '#ncaasports', '#d1sports'
        ],
        'General Sports Facts': [
            '#sportsfacts', '#didyouknow', '#sportshistory',
            '#sportstrivia', '#sportstrivia', '#sportsknowledge',
            '#sportsfan', '#sportslife', '#sportsnews'
        ]
    }

    # Template-specific hashtags
    TEMPLATE_TAGS = {
        'stat_reveal': ['#stats', '#sportsstats', '#mindblown', '#insane', '#crazy'],
        'prediction': ['#prediction', '#hottake', '#bold', '#controversial'],
        'fact_drop': ['#facts', '#didyouknow', '#funfact', '#sportsfacts'],
        'vs_comparison': ['#versus', '#debate', '#whosbetter', '#goat'],
        'top_5_list': ['#top5', '#ranking', '#best', '#alltime'],
        'did_you_know': ['#didyouknow', '#trivia', '#funfacts', '#learn'],
        'highlight_moment': ['#highlights', '#epic', '#iconic', '#legendary']
    }

    # Time-based hashtags
    def _get_time_tags(self):
        """Get hashtags based on current time/day"""
        now = datetime.now()
        day = now.strftime('%A').lower()
        month = now.strftime('%B').lower()

        time_tags = []

        # Day-specific
        day_tags = {
            'monday': ['#mondaymotivation', '#motivationmonday'],
            'tuesday': ['#transformationtuesday', '#tuesdaythoughts'],
            'wednesday': ['#wednesdaywisdom', '#wisdomwednesday'],
            'thursday': ['#throwbackthursday', '#tbt', '#thursdayvibes'],
            'friday': ['#fridayfeeling', '#friyay', '#fridayvibes'],
            'saturday': ['#saturdayvibes', '#weekend', '#saturdaynight'],
            'sunday': ['#sundayfunday', '#sundayvibes', '#sundaynight']
        }

        if day in day_tags:
            time_tags.extend(day_tags[day][:1])  # Add one day tag

        return time_tags

    def generate(self, category='Sports', template=None, count=30):
        """
        Generate hashtag set for a post

        Args:
            category: Sports category
            template: Video template type
            count: Number of hashtags to generate (Instagram limit is 30)

        Returns:
            List of hashtags
        """
        hashtags = set()

        # Add viral tags (4-5)
        hashtags.update(random.sample(self.VIRAL_TAGS, min(5, len(self.VIRAL_TAGS))))

        # Add general sports tags (3-4)
        hashtags.update(random.sample(self.SPORTS_GENERAL, min(4, len(self.SPORTS_GENERAL))))

        # Add category-specific tags (10-12)
        if category in self.CATEGORY_TAGS:
            category_tags = self.CATEGORY_TAGS[category]
            hashtags.update(random.sample(category_tags, min(12, len(category_tags))))

        # Add template tags (2-3)
        if template and template in self.TEMPLATE_TAGS:
            hashtags.update(self.TEMPLATE_TAGS[template])

        # Add time-based tags (1-2)
        hashtags.update(self._get_time_tags())

        # Convert to list and limit to count
        hashtag_list = list(hashtags)[:count]

        # Sort by popularity (viral first, then specific)
        def sort_key(tag):
            if tag in self.VIRAL_TAGS:
                return 0
            elif tag in self.SPORTS_GENERAL:
                return 1
            else:
                return 2

        hashtag_list.sort(key=sort_key)

        return hashtag_list

    def format_for_caption(self, hashtags):
        """Format hashtags for Instagram caption"""
        return ' '.join(hashtags)

    def format_for_comment(self, hashtags):
        """Format hashtags as comment (recommended for better reach)"""
        # Split into groups of 5 for readability
        groups = [hashtags[i:i+5] for i in range(0, len(hashtags), 5)]
        return '\n'.join([' '.join(group) for group in groups])


if __name__ == "__main__":
    # Test hashtag generation
    generator = HashtagGenerator()

    print("=" * 60)
    print("TESTING HASHTAG GENERATOR")
    print("=" * 60)

    categories = ['NBA', 'NFL', 'Soccer']

    for category in categories:
        print(f"\n{category} Hashtags:")
        hashtags = generator.generate(category=category, template='stat_reveal', count=30)
        print(f"Generated {len(hashtags)} hashtags")
        print(generator.format_for_comment(hashtags))
        print()
