"""
Travel Miles Penalty Calculator.

Calculates fatigue penalty based on travel distance.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class TravelImpact:
    """Travel impact assessment."""
    team: str
    miles_traveled: float
    time_zones_crossed: int
    fatigue_penalty: float  # Rating points
    performance_impact: float  # Percentage
    jet_lag_factor: float
    recovery_days_needed: int


class TravelPenaltyCalculator:
    """Calculates team fatigue from travel."""

    # Major city coordinates (approximate)
    CITY_COORDS = {
        'New York': (40.7, -74.0),
        'Los Angeles': (34.0, -118.2),
        'Chicago': (41.9, -87.6),
        'Houston': (29.8, -95.4),
        'Phoenix': (33.4, -112.1),
        'Philadelphia': (40.0, -75.2),
        'San Antonio': (29.4, -98.5),
        'San Diego': (32.7, -117.2),
        'Dallas': (32.8, -96.8),
        'Miami': (25.8, -80.2),
        'Boston': (42.4, -71.1),
        'Seattle': (47.6, -122.3),
        'Denver': (39.7, -105.0),
        'Atlanta': (33.7, -84.4),
    }

    def __init__(self):
        """Initialize travel penalty calculator."""
        pass

    def calculate_travel_impact(
        self,
        team: str,
        origin_city: str,
        destination_city: str,
        days_since_travel: int = 0
    ) -> TravelImpact:
        """
        Calculate travel impact on team performance.

        Args:
            team: Team name
            origin_city: Origin city
            destination_city: Destination city
            days_since_travel: Days since travel occurred

        Returns:
            TravelImpact with penalty details
        """
        # Calculate distance
        miles = self._calculate_distance(origin_city, destination_city)

        # Time zones crossed
        origin_tz = self._get_timezone_offset(origin_city)
        dest_tz = self._get_timezone_offset(destination_city)
        tz_crossed = abs(origin_tz - dest_tz)

        # Base fatigue from distance
        # Short trips (<500 mi) = minimal impact
        # Medium trips (500-1500 mi) = moderate impact
        # Long trips (>1500 mi) = significant impact
        if miles < 500:
            base_fatigue = 0.5
        elif miles < 1500:
            base_fatigue = 1.5
        else:
            base_fatigue = 3.0

        # Time zone penalty
        tz_penalty = tz_crossed * 1.5

        # Total fatigue penalty (in rating points)
        total_fatigue = base_fatigue + tz_penalty

        # Recovery factor
        if days_since_travel >= 2:
            recovery = 0.7  # Mostly recovered
        elif days_since_travel == 1:
            recovery = 0.4  # Partial recovery
        else:
            recovery = 0  # Just arrived

        adjusted_fatigue = total_fatigue * (1 - recovery)

        # Performance impact (percentage)
        performance_impact = adjusted_fatigue * 0.02  # 2% per rating point

        # Jet lag factor
        jet_lag = min(1.0, tz_crossed * 0.25)

        # Recovery days needed
        recovery_days = math.ceil(tz_crossed / 2) if tz_crossed > 0 else 1

        return TravelImpact(
            team=team,
            miles_traveled=round(miles, 1),
            time_zones_crossed=tz_crossed,
            fatigue_penalty=round(adjusted_fatigue, 2),
            performance_impact=round(performance_impact * 100, 1),
            jet_lag_factor=round(jet_lag, 2),
            recovery_days_needed=recovery_days
        )

    def _calculate_distance(self, city1: str, city2: str) -> float:
        """Calculate distance between cities in miles."""
        coords1 = self.CITY_COORDS.get(city1, (0, 0))
        coords2 = self.CITY_COORDS.get(city2, (0, 0))

        lat1, lon1 = coords1
        lat2, lon2 = coords2

        # Haversine formula
        R = 3959  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat/2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) ** 2)

        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def _get_timezone_offset(self, city: str) -> int:
        """Get approximate timezone offset for city."""
        # Simplified timezone mapping
        eastern = ['New York', 'Philadelphia', 'Boston', 'Miami', 'Atlanta']
        central = ['Chicago', 'Houston', 'San Antonio', 'Dallas']
        mountain = ['Denver', 'Phoenix']
        pacific = ['Los Angeles', 'San Diego', 'Seattle']

        if city in eastern:
            return -5
        elif city in central:
            return -6
        elif city in mountain:
            return -7
        elif city in pacific:
            return -8
        else:
            return -6  # Default to central


