"""Travel miles penalty calculator for team fatigue factor."""
from typing import Dict, Tuple
import math


class TravelPenaltyCalculator:
    """
    Calculates performance penalty based on travel distance.

    Teams traveling long distances often experience fatigue and
    performance decreases, especially across time zones.
    """

    def __init__(self):
        """Initialize travel penalty calculator."""
        self.city_coordinates = self._get_city_coordinates()
        self.time_zones = self._get_time_zones()

    def calculate_travel_penalty(
        self,
        origin_city: str,
        destination_city: str,
        sport: str,
        travel_date: str = None,
        back_to_back: bool = False
    ) -> Dict:
        """
        Calculate travel penalty for a trip.

        Args:
            origin_city: Starting city
            destination_city: Destination city
            sport: Sport type
            travel_date: Date of travel (optional)
            back_to_back: Whether this is back-to-back travel

        Returns:
            Dictionary with travel impact analysis
        """
        # Calculate distance
        distance = self._calculate_distance(origin_city, destination_city)

        # Calculate time zone change
        tz_change = self._calculate_timezone_change(origin_city, destination_city)

        # Determine direction (East or West)
        direction = self._determine_direction(origin_city, destination_city)

        # Calculate base penalty
        distance_penalty = self._distance_to_penalty(distance, sport)
        timezone_penalty = self._timezone_to_penalty(tz_change, direction)

        # Back-to-back multiplier
        if back_to_back:
            total_penalty = (distance_penalty + timezone_penalty) * 1.5
        else:
            total_penalty = distance_penalty + timezone_penalty

        # Convert to performance impact
        performance_impact = self._penalty_to_performance_impact(total_penalty, sport)

        return {
            'origin': origin_city,
            'destination': destination_city,
            'distance_miles': round(distance, 0),
            'timezone_change': tz_change,
            'direction': direction,
            'distance_penalty': round(distance_penalty, 2),
            'timezone_penalty': round(timezone_penalty, 2),
            'total_penalty': round(total_penalty, 2),
            'performance_impact': performance_impact,
            'severity': self._rate_travel_severity(total_penalty),
            'recommendation': self._generate_travel_recommendation(
                total_penalty, tz_change, direction
            ),
            'sport': sport
        }

    def calculate_road_trip_fatigue(
        self,
        trip_schedule: List[Tuple[str, str]],
        sport: str
    ) -> Dict:
        """
        Calculate cumulative fatigue over a road trip.

        Args:
            trip_schedule: List of (origin, destination) tuples
            sport: Sport type

        Returns:
            Cumulative road trip analysis
        """
        if not trip_schedule:
            return {'total_fatigue': 0, 'note': 'No travel'}

        total_distance = 0
        total_penalty = 0
        max_tz_change = 0

        for i, (origin, destination) in enumerate(trip_schedule):
            distance = self._calculate_distance(origin, destination)
            tz_change = abs(self._calculate_timezone_change(origin, destination))

            total_distance += distance
            penalty_calc = self.calculate_travel_penalty(
                origin, destination, sport,
                back_to_back=(i > 0 and trip_schedule[i-1][1] == origin)
            )
            total_penalty += penalty_calc['total_penalty']
            max_tz_change = max(max_tz_change, tz_change)

        return {
            'total_cities': len(trip_schedule),
            'total_miles': round(total_distance, 0),
            'max_timezone_change': max_tz_change,
            'cumulative_penalty': round(total_penalty, 2),
            'trip_difficulty': self._rate_trip_difficulty(total_penalty),
            'expected_win_pct_impact': round(total_penalty * 0.02, 3),
            'sport': sport
        }

    def _calculate_distance(self, city1: str, city2: str) -> float:
        """Calculate distance between two cities in miles."""
        coords1 = self.city_coordinates.get(city1.lower())
        coords2 = self.city_coordinates.get(city2.lower())

        if not coords1 or not coords2:
            # Default assumption for unknown cities
            return 1000.0

        # Haversine formula
        lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
        lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in miles
        radius = 3959

        return radius * c

    def _calculate_timezone_change(self, city1: str, city2: str) -> int:
        """Calculate time zone change (negative = west, positive = east)."""
        tz1 = self.time_zones.get(city1.lower(), 0)
        tz2 = self.time_zones.get(city2.lower(), 0)

        return tz2 - tz1

    def _determine_direction(self, city1: str, city2: str) -> str:
        """Determine travel direction."""
        tz_change = self._calculate_timezone_change(city1, city2)

        if tz_change > 0:
            return "EAST"
        elif tz_change < 0:
            return "WEST"
        else:
            coords1 = self.city_coordinates.get(city1.lower())
            coords2 = self.city_coordinates.get(city2.lower())

            if coords1 and coords2:
                if coords2[1] > coords1[1]:
                    return "EAST"
                else:
                    return "WEST"

            return "NEUTRAL"

    def _distance_to_penalty(self, distance: float, sport: str) -> float:
        """Convert travel distance to performance penalty."""
        # Base penalty increases with distance
        if distance < 500:
            return 0.5
        elif distance < 1000:
            return 1.0
        elif distance < 1500:
            return 1.5
        elif distance < 2500:
            return 2.5
        else:
            return 3.5

    def _timezone_to_penalty(self, tz_change: int, direction: str) -> float:
        """Convert timezone change to performance penalty."""
        abs_change = abs(tz_change)

        # Eastward travel is typically harder (body clock issues)
        if direction == "EAST":
            multiplier = 1.3
        else:
            multiplier = 1.0

        base_penalty = abs_change * 0.8 * multiplier

        return base_penalty

    def _penalty_to_performance_impact(self, penalty: float, sport: str) -> Dict:
        """Convert penalty score to performance metrics."""
        # Sport-specific conversions
        if sport == 'nba':
            point_impact = penalty * 0.6
            win_prob_impact = penalty * 0.015
        elif sport == 'nfl':
            point_impact = penalty * 0.4
            win_prob_impact = penalty * 0.02
        elif sport in ['nhl', 'mls', 'soccer']:
            point_impact = penalty * 0.15
            win_prob_impact = penalty * 0.02
        else:
            point_impact = penalty * 0.5
            win_prob_impact = penalty * 0.018

        return {
            'expected_scoring_decrease': round(point_impact, 1),
            'win_probability_decrease': round(win_prob_impact, 3),
            'fatigue_rating': round(penalty / 5 * 100, 0)  # 0-100 scale
        }

    def _rate_travel_severity(self, penalty: float) -> str:
        """Rate travel severity."""
        if penalty >= 6:
            return "EXTREME"
        elif penalty >= 4:
            return "HIGH"
        elif penalty >= 2:
            return "MODERATE"
        elif penalty >= 1:
            return "LOW"
        else:
            return "MINIMAL"

    def _rate_trip_difficulty(self, cumulative_penalty: float) -> str:
        """Rate overall road trip difficulty."""
        if cumulative_penalty >= 15:
            return "BRUTAL"
        elif cumulative_penalty >= 10:
            return "VERY_DIFFICULT"
        elif cumulative_penalty >= 6:
            return "DIFFICULT"
        elif cumulative_penalty >= 3:
            return "MODERATE"
        else:
            return "MANAGEABLE"

    def _generate_travel_recommendation(
        self,
        penalty: float,
        tz_change: int,
        direction: str
    ) -> str:
        """Generate recommendation based on travel impact."""
        if penalty >= 5:
            return f"Significant travel disadvantage - expect {penalty:.1f}pt impact"
        elif penalty >= 3:
            return f"Moderate travel impact - team may struggle early"
        elif abs(tz_change) >= 2 and direction == "EAST":
            return "Eastward time zone change - circadian rhythm disruption likely"
        elif penalty >= 1:
            return "Minor travel fatigue expected"
        else:
            return "Minimal travel impact"

    def _get_city_coordinates(self) -> Dict[str, Tuple[float, float]]:
        """Get coordinates for major sports cities (lat, lon)."""
        return {
            # NBA/NHL cities
            'boston': (42.36, -71.06),
            'new york': (40.71, -74.01),
            'philadelphia': (39.95, -75.17),
            'brooklyn': (40.68, -73.94),
            'toronto': (43.65, -79.38),
            'miami': (25.76, -80.19),
            'orlando': (28.54, -81.38),
            'charlotte': (35.23, -80.84),
            'atlanta': (33.75, -84.39),
            'washington': (38.91, -77.04),
            'cleveland': (41.50, -81.69),
            'detroit': (42.33, -83.05),
            'chicago': (41.88, -87.63),
            'indianapolis': (39.77, -86.16),
            'milwaukee': (43.04, -87.91),
            'memphis': (35.15, -90.05),
            'new orleans': (29.95, -90.07),
            'dallas': (32.78, -96.80),
            'houston': (29.76, -95.37),
            'san antonio': (29.42, -98.49),
            'oklahoma city': (35.47, -97.52),
            'denver': (39.74, -104.99),
            'utah': (40.76, -111.89),
            'salt lake city': (40.76, -111.89),
            'phoenix': (33.45, -112.07),
            'los angeles': (34.05, -118.24),
            'sacramento': (38.58, -121.49),
            'san francisco': (37.77, -122.42),
            'portland': (45.52, -122.68),
            'seattle': (47.61, -122.33),
            'minneapolis': (44.98, -93.27),
            'las vegas': (36.17, -115.14),
            # NFL cities
            'green bay': (44.52, -88.02),
            'kansas city': (39.10, -94.58),
            'pittsburgh': (40.44, -79.99),
            'baltimore': (39.29, -76.61),
            'cincinnati': (39.10, -84.51),
            'jacksonville': (30.33, -81.66),
            'tampa': (27.95, -82.46),
            'nashville': (36.16, -86.78),
            # MLB additions
            'st louis': (38.63, -90.20),
            'oakland': (37.80, -122.27),
            'san diego': (32.72, -117.16),
            'arizona': (33.45, -112.07)
        }

    def _get_time_zones(self) -> Dict[str, int]:
        """Get time zones for cities (hours from UTC-5/EST)."""
        return {
            # Eastern (0)
            'boston': 0, 'new york': 0, 'philadelphia': 0, 'brooklyn': 0,
            'toronto': 0, 'miami': 0, 'orlando': 0, 'charlotte': 0,
            'atlanta': 0, 'washington': 0, 'cleveland': 0, 'detroit': 0,
            'pittsburgh': 0, 'baltimore': 0, 'jacksonville': 0, 'tampa': 0,
            # Central (-1)
            'chicago': -1, 'indianapolis': -1, 'milwaukee': -1, 'memphis': -1,
            'new orleans': -1, 'dallas': -1, 'houston': -1, 'san antonio': -1,
            'oklahoma city': -1, 'minneapolis': -1, 'kansas city': -1,
            'green bay': -1, 'cincinnati': -1, 'nashville': -1, 'st louis': -1,
            # Mountain (-2)
            'denver': -2, 'utah': -2, 'salt lake city': -2, 'phoenix': -2, 'arizona': -2,
            # Pacific (-3)
            'los angeles': -3, 'sacramento': -3, 'san francisco': -3,
            'portland': -3, 'seattle': -3, 'las vegas': -3,
            'oakland': -3, 'san diego': -3
        }
