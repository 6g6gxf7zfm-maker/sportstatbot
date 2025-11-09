"""
Travel Fatigue Model

Quantifies performance impact from travel schedules, accounting for:
- Flight distance
- Timezone changes
- Rest days between games
- Back-to-back games
"""

import math
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class TravelFatigueModel:
    """
    Models the impact of travel on team performance

    Factors considered:
    1. Distance traveled (flight miles)
    2. Timezone difference (jet lag effect)
    3. Rest days (recovery time)
    4. Back-to-back games
    5. Travel direction (east vs west for timezone)
    """

    # City coordinates for distance calculations (latitude, longitude)
    CITY_COORDS = {
        # NBA Cities
        'atlanta': (33.7490, -84.3880),
        'boston': (42.3601, -71.0589),
        'brooklyn': (40.6782, -73.9442),
        'charlotte': (35.2271, -80.8431),
        'chicago': (41.8781, -87.6298),
        'cleveland': (41.4993, -81.6944),
        'dallas': (32.7767, -96.7970),
        'denver': (39.7392, -104.9903),
        'detroit': (42.3314, -83.0458),
        'golden_state': (37.7749, -122.4194),  # SF/Oakland
        'houston': (29.7604, -95.3698),
        'indiana': (39.7684, -86.1581),  # Indianapolis
        'la_clippers': (34.0522, -118.2437),
        'la_lakes': (34.0522, -118.2437),
        'memphis': (35.1495, -90.0490),
        'miami': (25.7617, -80.1918),
        'milwaukee': (43.0389, -87.9065),
        'minnesota': (44.9778, -93.2650),  # Minneapolis
        'new_orleans': (29.9511, -90.0715),
        'new_york': (40.7128, -74.0060),
        'oklahoma_city': (35.4676, -97.5164),
        'orlando': (28.5383, -81.3792),
        'philadelphia': (39.9526, -75.1652),
        'phoenix': (33.4484, -112.0740),
        'portland': (45.5152, -122.6784),
        'sacramento': (38.5816, -121.4944),
        'san_antonio': (29.4241, -98.4936),
        'toronto': (43.6532, -79.3832),
        'utah': (40.7608, -111.8910),  # Salt Lake City
        'washington': (38.9072, -77.0369),
        # NFL Cities (subset - add more as needed)
        'green_bay': (44.5133, -88.0133),
        'kansas_city': (39.0997, -94.5786),
        'las_vegas': (36.1699, -115.1398),
        'seattle': (47.6062, -122.3321),
        'tampa': (27.9506, -82.4572),
    }

    # Timezone offsets (from UTC)
    TIMEZONES = {
        'ET': -5,  # Eastern
        'CT': -6,  # Central
        'MT': -7,  # Mountain
        'PT': -8,  # Pacific
    }

    def __init__(self):
        """Initialize the travel fatigue model"""
        # Coefficient weights (can be tuned based on data)
        self.distance_weight = 0.001  # Impact per mile
        self.timezone_weight = 2.0    # Impact per hour difference
        self.rest_bonus = 0.5         # Bonus per rest day
        self.back_to_back_penalty = 5.0  # Extra penalty for B2B

    def calculate_distance(
        self,
        from_city: str,
        to_city: str
    ) -> float:
        """
        Calculate great circle distance between cities (in miles)

        Args:
            from_city: Origin city name
            to_city: Destination city name

        Returns:
            Distance in miles
        """
        from_city = from_city.lower().replace(' ', '_')
        to_city = to_city.lower().replace(' ', '_')

        if from_city not in self.CITY_COORDS or to_city not in self.CITY_COORDS:
            # Default estimate if city not in database
            return 1000.0

        lat1, lon1 = self.CITY_COORDS[from_city]
        lat2, lon2 = self.CITY_COORDS[to_city]

        # Haversine formula
        R = 3959  # Earth's radius in miles

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return round(distance, 2)

    def get_timezone_delta(
        self,
        from_city: str,
        to_city: str
    ) -> int:
        """
        Calculate timezone difference (simplified)

        Args:
            from_city: Origin city
            to_city: Destination city

        Returns:
            Hours difference (positive = traveling east)
        """
        # Simplified timezone mapping by longitude
        from_city = from_city.lower().replace(' ', '_')
        to_city = to_city.lower().replace(' ', '_')

        if from_city not in self.CITY_COORDS or to_city not in self.CITY_COORDS:
            return 0

        _, from_lon = self.CITY_COORDS[from_city]
        _, to_lon = self.CITY_COORDS[to_city]

        # Rough estimate: 15 degrees longitude ≈ 1 hour
        delta = int(round((from_lon - to_lon) / 15))
        return delta

    def calculate_fatigue_score(
        self,
        from_city: str,
        to_city: str,
        rest_days: int,
        previous_games_in_days: int = 7
    ) -> Dict[str, float]:
        """
        Calculate comprehensive fatigue score

        Args:
            from_city: Origin city (previous game location or home)
            to_city: Away game location
            rest_days: Days of rest before this game
            previous_games_in_days: Number of games in last N days

        Returns:
            Dict with fatigue metrics
        """
        # Calculate components
        distance = self.calculate_distance(from_city, to_city)
        timezone_delta = abs(self.get_timezone_delta(from_city, to_city))

        # Base fatigue from distance and timezone
        distance_fatigue = distance * self.distance_weight
        timezone_fatigue = timezone_delta * self.timezone_weight

        # Rest day adjustment (more rest = less fatigue)
        rest_adjustment = rest_days * self.rest_bonus

        # Back-to-back penalty
        b2b_penalty = self.back_to_back_penalty if rest_days == 0 else 0

        # Recent game density penalty
        density_penalty = max(0, (previous_games_in_days - 3) * 0.5)

        # Total fatigue score
        total_fatigue = (
            distance_fatigue +
            timezone_fatigue +
            density_penalty +
            b2b_penalty -
            rest_adjustment
        )

        # Ensure non-negative
        total_fatigue = max(0, total_fatigue)

        # Convert to performance impact (percentage)
        # Each point of fatigue ≈ -0.5% performance
        performance_impact = -0.5 * total_fatigue

        return {
            'fatigue_score': round(total_fatigue, 2),
            'distance_miles': distance,
            'timezone_delta': timezone_delta,
            'rest_days': rest_days,
            'back_to_back': rest_days == 0,
            'performance_impact_pct': round(performance_impact, 2),
            'components': {
                'distance_fatigue': round(distance_fatigue, 2),
                'timezone_fatigue': round(timezone_fatigue, 2),
                'rest_adjustment': round(-rest_adjustment, 2),
                'b2b_penalty': b2b_penalty,
                'density_penalty': round(density_penalty, 2)
            }
        }

    def adjust_prediction(
        self,
        base_prediction: float,
        fatigue_score: float
    ) -> float:
        """
        Adjust a performance prediction based on fatigue

        Args:
            base_prediction: Original prediction (points, spread, etc.)
            fatigue_score: Fatigue score from calculate_fatigue_score

        Returns:
            Adjusted prediction
        """
        impact_pct = -0.5 * fatigue_score / 100
        adjusted = base_prediction * (1 + impact_pct)
        return round(adjusted, 2)

    def compare_scenarios(
        self,
        scenarios: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        Compare fatigue across multiple game scenarios

        Args:
            scenarios: Dict mapping scenario names to params

        Returns:
            Dict with fatigue comparisons

        Example:
            >>> scenarios = {
            ...     'Home Game': {'from': 'boston', 'to': 'boston', 'rest': 2},
            ...     'West Coast Trip': {'from': 'boston', 'to': 'portland', 'rest': 1}
            ... }
            >>> model.compare_scenarios(scenarios)
        """
        results = {}

        for name, params in scenarios.items():
            fatigue = self.calculate_fatigue_score(
                params['from'],
                params['to'],
                params['rest'],
                params.get('games_in_7days', 3)
            )
            results[name] = fatigue

        return results

    def generate_report(
        self,
        team_name: str,
        from_city: str,
        to_city: str,
        rest_days: int
    ) -> str:
        """
        Generate a human-readable fatigue report

        Args:
            team_name: Team name
            from_city: Previous location
            to_city: Game location
            rest_days: Rest days

        Returns:
            Formatted report
        """
        result = self.calculate_fatigue_score(from_city, to_city, rest_days)

        report = f"""
✈️ **Travel Fatigue Report: {team_name}**

**Trip Details:**
• Route: {from_city.title()} → {to_city.title()}
• Distance: {result['distance_miles']:,.0f} miles
• Timezone Change: {result['timezone_delta']} hour(s)
• Rest Days: {result['rest_days']}
• Back-to-Back: {"Yes ⚠️" if result['back_to_back'] else "No"}

**Fatigue Analysis:**
• Fatigue Score: {result['fatigue_score']:.1f}
• Expected Performance Impact: {result['performance_impact_pct']:+.1f}%

**Breakdown:**
• Distance Factor: {result['components']['distance_fatigue']:.2f}
• Timezone Factor: {result['components']['timezone_fatigue']:.2f}
• Rest Adjustment: {result['components']['rest_adjustment']:.2f}
"""
        if result['back_to_back']:
            report += f"• Back-to-Back Penalty: {result['components']['b2b_penalty']:.2f}\n"

        # Interpretation
        report += "\n**Impact Assessment:**\n"
        if result['fatigue_score'] < 3:
            report += "✅ Minimal travel impact expected. Normal performance likely.\n"
        elif result['fatigue_score'] < 6:
            report += "⚠️ Moderate travel fatigue. Slight performance dip possible.\n"
        elif result['fatigue_score'] < 10:
            report += "⚠️ Significant travel fatigue. Performance could be noticeably affected.\n"
        else:
            report += "🚨 Severe travel fatigue. Major performance impact likely.\n"

        return report.strip()


# Example usage
if __name__ == "__main__":
    model = TravelFatigueModel()

    print("=" * 70)
    print("TRAVEL FATIGUE MODEL - Examples")
    print("=" * 70)

    # Scenario 1: Home game (no travel)
    print("\n" + model.generate_report("Boston Celtics", "boston", "boston", 2))

    print("\n" + "=" * 70)

    # Scenario 2: East coast road trip
    print("\n" + model.generate_report("Boston Celtics", "boston", "miami", 1))

    print("\n" + "=" * 70)

    # Scenario 3: Cross-country back-to-back
    print("\n" + model.generate_report("Boston Celtics", "portland", "miami", 0))

    print("\n" + "=" * 70)

    # Scenario 4: West coast swing
    print("\n" + model.generate_report("New York Knicks", "new_york", "golden_state", 2))

    print("\n" + "=" * 70)

    # Compare scenarios
    scenarios = {
        'Home Game': {'from': 'boston', 'to': 'boston', 'rest': 2},
        'Short Road Trip': {'from': 'boston', 'to': 'philadelphia', 'rest': 1},
        'West Coast Trip': {'from': 'boston', 'to': 'portland', 'rest': 1},
        'Cross-Country B2B': {'from': 'golden_state', 'to': 'miami', 'rest': 0}
    }

    comparison = model.compare_scenarios(scenarios)

    print("\n📊 Scenario Comparison:")
    for scenario, data in sorted(comparison.items(), key=lambda x: x[1]['fatigue_score']):
        print(f"• {scenario}: Fatigue Score = {data['fatigue_score']:.1f} "
              f"({data['performance_impact_pct']:+.1f}% impact)")
