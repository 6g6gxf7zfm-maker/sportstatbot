"""Stats glossary with explanations for common sports statistics."""
from typing import Dict, List, Optional


class StatsGlossary:
    """
    Comprehensive glossary of sports statistics across multiple leagues.
    Provides definitions, formulas, and context for common stats.
    """

    def __init__(self):
        self.glossary = self._build_glossary()

    def _build_glossary(self) -> Dict[str, Dict]:
        """Build comprehensive stats glossary across all sports."""
        return {
            # NFL Stats
            'EPA': {
                'name': 'Expected Points Added',
                'sport': 'NFL',
                'category': 'Advanced',
                'definition': 'Measures the value of a play by comparing the expected points before and after the play',
                'formula': 'EP After - EP Before',
                'range': 'Typically -3.0 to +7.0 per play',
                'context': 'Positive EPA means the play increased scoring probability. Accounts for down, distance, and field position.',
                'example': 'A 3rd down conversion adds ~2.0 EPA, while a sack might be -1.5 EPA',
                'good_value': '> 0.10 per play is elite',
                'aliases': ['expected points added', 'ep added']
            },
            'CPOE': {
                'name': 'Completion Percentage Over Expected',
                'sport': 'NFL',
                'category': 'Advanced',
                'definition': 'How much better/worse a QB completes passes compared to expectation based on throw difficulty',
                'formula': 'Actual Completion % - Expected Completion %',
                'range': '-10% to +10%',
                'context': 'Accounts for throw distance, pressure, receiver separation, and other factors',
                'example': '+5% CPOE means completing 5% more passes than expected given difficulty',
                'good_value': '> +3% is very good',
                'aliases': ['completion over expected']
            },
            'DVOA': {
                'name': 'Defense-adjusted Value Over Average',
                'sport': 'NFL',
                'category': 'Advanced',
                'definition': 'Measures team efficiency by comparing success on every play to league average based on situation',
                'formula': 'Complex - adjusts for down, distance, field position, and opponent quality',
                'range': '-30% to +30%',
                'context': 'Positive DVOA is good for offense, negative is good for defense',
                'example': '+15% offensive DVOA means 15% better than average offense',
                'good_value': '> +10% offense, < -10% defense',
                'aliases': ['defense adjusted value']
            },
            'QBR': {
                'name': 'Total Quarterback Rating',
                'sport': 'NFL',
                'category': 'Advanced',
                'definition': 'ESPN metric evaluating QB performance on all plays including clutch-weighting',
                'formula': 'Proprietary - includes EPA, clutch factor, and context',
                'range': '0 to 100',
                'context': 'Weighted for game situation and accounts for team context',
                'example': '70+ QBR is Pro Bowl level performance',
                'good_value': '> 65 is excellent',
                'aliases': ['total qbr', 'quarterback rating']
            },

            # NBA Stats
            'TS%': {
                'name': 'True Shooting Percentage',
                'sport': 'NBA',
                'category': 'Advanced',
                'definition': 'Shooting efficiency that accounts for 2-pointers, 3-pointers, and free throws',
                'formula': 'PTS / (2 × (FGA + 0.44 × FTA))',
                'range': '40% to 70%',
                'context': 'Better than FG% because it values 3-pointers and free throws appropriately',
                'example': '60% TS means very efficient scoring',
                'good_value': '> 58% is above average',
                'aliases': ['true shooting', 'ts percentage', 'ts pct']
            },
            'PER': {
                'name': 'Player Efficiency Rating',
                'sport': 'NBA',
                'category': 'Advanced',
                'definition': 'Overall rating of per-minute productivity, adjusted for pace',
                'formula': 'Complex formula summing positive contributions minus negative ones',
                'range': '0 to 35+',
                'context': 'League average PER is always 15.0',
                'example': 'PER of 25+ is MVP-caliber',
                'good_value': '> 20 is All-Star level',
                'aliases': ['player efficiency', 'efficiency rating']
            },
            'BPM': {
                'name': 'Box Plus-Minus',
                'sport': 'NBA',
                'category': 'Advanced',
                'definition': 'Estimates player contribution per 100 possessions relative to league average',
                'formula': 'Regression based on box score stats',
                'range': '-10 to +12',
                'context': '0.0 is league average, measured per 100 possessions',
                'example': '+5 BPM means team outscores opponents by 5 points per 100 possessions',
                'good_value': '> +3 is All-Star level',
                'aliases': ['box plus minus', 'plus minus']
            },
            'USG%': {
                'name': 'Usage Rate',
                'sport': 'NBA',
                'category': 'Advanced',
                'definition': 'Percentage of team plays used by a player while on court',
                'formula': '100 × ((FGA + 0.44 × FTA + TOV) × (Tm MP / 5)) / (MP × (Tm FGA + 0.44 × Tm FTA + Tm TOV))',
                'range': '10% to 40%',
                'context': 'Higher usage means player handles the ball more and takes more shots',
                'example': '30%+ usage is a primary offensive option',
                'good_value': '> 28% for stars',
                'aliases': ['usage rate', 'usage percentage']
            },
            'NetRtg': {
                'name': 'Net Rating',
                'sport': 'NBA',
                'category': 'Advanced',
                'definition': 'Point differential per 100 possessions',
                'formula': 'Offensive Rating - Defensive Rating',
                'range': '-20 to +20',
                'context': 'Positive means team/player scores more than they allow',
                'example': '+10 Net Rating is championship-level',
                'good_value': '> +5 is excellent',
                'aliases': ['net rating', 'point differential']
            },

            # MLB Stats
            'wRC+': {
                'name': 'Weighted Runs Created Plus',
                'sport': 'MLB',
                'category': 'Advanced',
                'definition': 'Offensive productivity adjusted for park and league, where 100 is average',
                'formula': '(wRC / PA) / (League wRC / League PA) × 100',
                'range': '0 to 200+',
                'context': 'Accounts for all offensive events weighted by run value',
                'example': '150 wRC+ means 50% better than league average hitter',
                'good_value': '> 120 is All-Star level',
                'aliases': ['weighted runs created', 'wrc plus']
            },
            'WAR': {
                'name': 'Wins Above Replacement',
                'sport': 'MLB',
                'category': 'Advanced',
                'definition': 'Total player value in wins compared to replacement-level player',
                'formula': 'Complex - combines hitting, fielding, baserunning, positional adjustment',
                'range': '-2 to 12',
                'context': 'Measures total contribution to team wins. Different versions: fWAR, bWAR',
                'example': '5+ WAR in a season is All-Star level',
                'good_value': '> 6 is MVP candidate',
                'aliases': ['wins above replacement', 'fwar', 'bwar']
            },
            'FIP': {
                'name': 'Fielding Independent Pitching',
                'sport': 'MLB',
                'category': 'Advanced',
                'definition': 'Pitcher ERA estimator based only on strikeouts, walks, HBP, and home runs',
                'formula': '((13×HR)+(3×(BB+HBP))-(2×K))/IP + constant',
                'range': '2.00 to 6.00',
                'context': 'Removes defense and luck, focuses on what pitcher controls',
                'example': 'FIP of 3.00 is excellent, below ERA suggests regression',
                'good_value': '< 3.50 is very good',
                'aliases': ['fielding independent pitching', 'fip era']
            },
            'OPS+': {
                'name': 'On-base Plus Slugging Plus',
                'sport': 'MLB',
                'category': 'Advanced',
                'definition': 'OPS adjusted for park and league, where 100 is average',
                'formula': '100 × (OBP/lgOBP + SLG/lgSLG - 1)',
                'range': '0 to 200+',
                'context': 'Park and league adjusted measure of hitting ability',
                'example': '130 OPS+ means 30% better than league average',
                'good_value': '> 120 is excellent',
                'aliases': ['ops plus', 'adjusted ops']
            },
            'BABIP': {
                'name': 'Batting Average on Balls In Play',
                'sport': 'MLB',
                'category': 'Advanced',
                'definition': 'Batting average on balls that are put in play (excludes HRs, Ks)',
                'formula': '(H - HR) / (AB - K - HR + SF)',
                'range': '.250 to .350',
                'context': 'League average ~.300. Extreme values often regress to mean',
                'example': '.350 BABIP often indicates luck, likely to decline',
                'good_value': '.300-.320 is normal',
                'aliases': ['babip', 'batting average balls in play']
            },

            # NHL Stats
            'xGF%': {
                'name': 'Expected Goals For Percentage',
                'sport': 'NHL',
                'category': 'Advanced',
                'definition': 'Percentage of expected goals for vs total expected goals (for + against)',
                'formula': 'xGF / (xGF + xGA)',
                'range': '35% to 65%',
                'context': 'Measures territorial dominance and shot quality',
                'example': '55% xGF means team generates more dangerous chances',
                'good_value': '> 52% is strong',
                'aliases': ['expected goals for', 'xgf percent']
            },
            'Corsi': {
                'name': 'Corsi For Percentage',
                'sport': 'NHL',
                'category': 'Advanced',
                'definition': 'Shot attempt differential (shots + blocks + misses)',
                'formula': 'CF / (CF + CA)',
                'range': '40% to 60%',
                'context': 'Proxy for puck possession. More attempts = more offensive zone time',
                'example': '55% Corsi means controlling 55% of shot attempts',
                'good_value': '> 52% is good',
                'aliases': ['corsi for', 'cf%']
            },
            'Fenwick': {
                'name': 'Fenwick For Percentage',
                'sport': 'NHL',
                'category': 'Advanced',
                'definition': 'Unblocked shot attempt differential (Corsi minus blocks)',
                'formula': 'FF / (FF + FA)',
                'range': '40% to 60%',
                'context': 'Like Corsi but excludes blocked shots for better shot quality measure',
                'example': '54% Fenwick indicates strong possession',
                'good_value': '> 52% is good',
                'aliases': ['fenwick for', 'ff%']
            },
            'PDO': {
                'name': 'PDO',
                'sport': 'NHL',
                'category': 'Advanced',
                'definition': 'Sum of shooting percentage and save percentage (luck indicator)',
                'formula': 'Shooting % + Save %',
                'range': '96.0 to 104.0',
                'context': '100.0 is average. Extremes suggest luck, regression expected',
                'example': 'PDO of 103 suggests team is getting lucky',
                'good_value': '98.5-101.5 is normal',
                'aliases': ['pdo', 'team luck']
            },
            'GAR': {
                'name': 'Goals Above Replacement',
                'sport': 'NHL',
                'category': 'Advanced',
                'definition': 'Total player value in goals above replacement-level player',
                'formula': 'Complex - includes offense, defense, and special teams contributions',
                'range': '-10 to +30',
                'context': 'All-in-one metric for player value',
                'example': '+20 GAR is Hart Trophy caliber',
                'good_value': '> +10 is All-Star level',
                'aliases': ['goals above replacement']
            },

            # Soccer Stats
            'xG': {
                'name': 'Expected Goals',
                'sport': 'Soccer',
                'category': 'Advanced',
                'definition': 'Probability a shot results in a goal based on shot quality factors',
                'formula': 'Model-based on shot location, angle, body part, assist type, etc.',
                'range': '0.0 to 1.0 per shot',
                'context': 'Sum across all shots for total xG. Compares to actual goals',
                'example': '1.8 xG but 0 goals = unlucky finishing',
                'good_value': 'Outperforming xG long-term is elite',
                'aliases': ['expected goals', 'xgoals']
            },
            'xA': {
                'name': 'Expected Assists',
                'sport': 'Soccer',
                'category': 'Advanced',
                'definition': 'Probability that a pass becomes an assist based on shot quality it creates',
                'formula': 'Sum of xG from shots resulting from player passes',
                'range': '0.0 to 15+ per season',
                'context': 'Measures chance creation quality, not just raw assists',
                'example': '8 xA with 3 assists = teammates finishing poorly',
                'good_value': '> 0.3 xA per 90 is creative',
                'aliases': ['expected assists', 'xassists']
            },
            'PPDA': {
                'name': 'Passes Per Defensive Action',
                'sport': 'Soccer',
                'category': 'Advanced',
                'definition': 'Measure of pressing intensity (opponent passes allowed before defensive action)',
                'formula': 'Opponent Passes / Defensive Actions',
                'range': '5 to 20',
                'context': 'Lower = more aggressive press. Only counts passes in final 60% of pitch',
                'example': 'PPDA of 7 = very high press, 15 = low press',
                'good_value': '< 10 is aggressive pressing',
                'aliases': ['passes per defensive action', 'pressing intensity']
            },

            # General Stats
            'Pace': {
                'name': 'Pace',
                'sport': 'Multiple',
                'category': 'Context',
                'definition': 'Speed of play, measured differently per sport',
                'formula': 'NBA: Possessions per 48 min | NFL: Plays per game',
                'range': 'Varies by sport',
                'context': 'Important context for rate stats. Higher pace = more opportunities',
                'example': 'NBA: 100 pace = 100 possessions per 48 minutes',
                'good_value': 'Neutral - depends on strategy',
                'aliases': ['pace of play', 'tempo']
            }
        }

    def get_stat_info(self, stat_key: str) -> Optional[Dict]:
        """
        Get information about a specific stat.

        Args:
            stat_key: Stat abbreviation (case-insensitive)

        Returns:
            Dictionary with stat information or None if not found
        """
        stat_upper = stat_key.upper()

        # Direct lookup
        if stat_upper in self.glossary:
            return self.glossary[stat_upper]

        # Check aliases
        for key, info in self.glossary.items():
            aliases = [a.upper() for a in info.get('aliases', [])]
            if stat_upper in aliases or stat_key.lower() in info.get('aliases', []):
                return info

        return None

    def search_stats(self, query: str, sport: Optional[str] = None) -> List[Dict]:
        """
        Search for stats matching a query.

        Args:
            query: Search query (name or description)
            sport: Filter by sport (optional)

        Returns:
            List of matching stat dictionaries
        """
        from rapidfuzz import fuzz

        query_lower = query.lower()
        results = []

        for key, info in self.glossary.items():
            # Filter by sport if specified
            if sport and info.get('sport', '').upper() != sport.upper() and info.get('sport') != 'Multiple':
                continue

            # Check if query matches key, name, or definition
            score = 0
            if query_lower in key.lower():
                score = 100
            elif query_lower in info['name'].lower():
                score = 90
            elif query_lower in info['definition'].lower():
                score = 70
            else:
                # Fuzzy match on name
                score = fuzz.partial_ratio(query_lower, info['name'].lower())

            if score >= 60:
                results.append({
                    'key': key,
                    'score': score,
                    **info
                })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def get_stats_by_sport(self, sport: str) -> List[Dict]:
        """
        Get all stats for a specific sport.

        Args:
            sport: Sport name

        Returns:
            List of stat dictionaries for that sport
        """
        sport_upper = sport.upper()
        results = []

        for key, info in self.glossary.items():
            if info.get('sport', '').upper() == sport_upper or info.get('sport') == 'Multiple':
                results.append({
                    'key': key,
                    **info
                })

        return results

    def format_stat_explanation(self, stat_key: str) -> str:
        """
        Format a comprehensive explanation of a stat.

        Args:
            stat_key: Stat abbreviation

        Returns:
            Formatted explanation string
        """
        info = self.get_stat_info(stat_key)

        if not info:
            return f"Stat '{stat_key}' not found in glossary."

        explanation = f"**{info['name']} ({stat_key.upper()})**\n\n"
        explanation += f"*{info['sport']} | {info['category']}*\n\n"
        explanation += f"**Definition:** {info['definition']}\n\n"
        explanation += f"**Formula:** {info['formula']}\n\n"
        explanation += f"**Typical Range:** {info['range']}\n\n"
        explanation += f"**Context:** {info['context']}\n\n"
        explanation += f"**Example:** {info['example']}\n\n"
        explanation += f"**Good Value:** {info['good_value']}\n"

        return explanation

    def get_all_stats_list(self) -> List[str]:
        """Get list of all stat abbreviations in glossary."""
        return list(self.glossary.keys())
