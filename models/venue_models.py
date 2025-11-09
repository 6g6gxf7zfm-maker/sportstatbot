"""
Venue and Environmental Models

9. Home-field variance decomposition separating altitude vs crowd
11. Weather-normalized shot quality for open-air venues
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class HomeFieldVarianceDecomposition:
    """
    Home-field variance decomposition separating altitude vs crowd.

    Decomposes home-field advantage into constituent factors:
    altitude, crowd noise, travel, familiarity, etc.
    """

    def __init__(self):
        """Initialize home-field decomposition model."""
        self.venue_factors = {}

    def decompose_home_advantage(
        self,
        venue_id: str,
        altitude_ft: float,
        capacity: int,
        avg_attendance_pct: float,
        team_home_win_pct: float,
        league_avg_home_win_pct: float = 0.56
    ) -> Dict:
        """
        Decompose home-field advantage into factors.

        Args:
            venue_id: Venue identifier
            altitude_ft: Altitude in feet
            capacity: Stadium capacity
            avg_attendance_pct: Average attendance as % of capacity
            team_home_win_pct: Team's home win percentage
            league_avg_home_win_pct: League average home win %

        Returns:
            Decomposed factors and their contributions
        """
        # Calculate total home advantage
        total_advantage = team_home_win_pct - league_avg_home_win_pct

        # Altitude factor
        altitude_impact = self._calculate_altitude_impact(altitude_ft)

        # Crowd factor
        crowd_impact = self._calculate_crowd_impact(capacity, avg_attendance_pct)

        # Travel factor (assuming average)
        travel_impact = 0.02  # ~2% baseline travel advantage

        # Familiarity factor
        familiarity_impact = 0.01  # ~1% from knowing venue

        # Residual (coaching, specific venue quirks, etc.)
        explained_impact = altitude_impact + crowd_impact + travel_impact + familiarity_impact
        residual = total_advantage - explained_impact

        # Calculate contribution percentages
        total_absolute = sum([
            abs(altitude_impact),
            abs(crowd_impact),
            abs(travel_impact),
            abs(familiarity_impact),
            abs(residual)
        ])

        contributions = {
            'altitude': {
                'impact': altitude_impact,
                'contribution_pct': (abs(altitude_impact) / total_absolute * 100) if total_absolute > 0 else 0
            },
            'crowd': {
                'impact': crowd_impact,
                'contribution_pct': (abs(crowd_impact) / total_absolute * 100) if total_absolute > 0 else 0
            },
            'travel': {
                'impact': travel_impact,
                'contribution_pct': (abs(travel_impact) / total_absolute * 100) if total_absolute > 0 else 0
            },
            'familiarity': {
                'impact': familiarity_impact,
                'contribution_pct': (abs(familiarity_impact) / total_absolute * 100) if total_absolute > 0 else 0
            },
            'residual': {
                'impact': residual,
                'contribution_pct': (abs(residual) / total_absolute * 100) if total_absolute > 0 else 0
            }
        }

        self.venue_factors[venue_id] = contributions

        return {
            'total_home_advantage': total_advantage,
            'factors': contributions,
            'primary_factor': max(contributions.items(), key=lambda x: abs(x[1]['impact']))[0]
        }

    def _calculate_altitude_impact(self, altitude_ft: float) -> float:
        """
        Calculate impact of altitude on home advantage.

        Args:
            altitude_ft: Altitude in feet

        Returns:
            Win percentage impact
        """
        # Altitude starts having noticeable effect above 3000 ft
        if altitude_ft < 3000:
            return 0.0

        # Denver (5280 ft) has ~3-4% altitude advantage
        # Mexico City (7350 ft) has ~5-6% advantage
        base_impact = (altitude_ft - 3000) / 2000 * 0.03

        return min(base_impact, 0.06)  # Cap at 6%

    def _calculate_crowd_impact(
        self,
        capacity: int,
        attendance_pct: float
    ) -> float:
        """
        Calculate impact of crowd on home advantage.

        Args:
            capacity: Stadium capacity
            attendance_pct: Average attendance as % of capacity

        Returns:
            Win percentage impact
        """
        # Larger crowds have more impact
        # Full capacity provides ~2-3% advantage
        # Low attendance reduces advantage

        # Size factor
        if capacity > 70000:
            size_factor = 1.2
        elif capacity > 50000:
            size_factor = 1.1
        elif capacity > 30000:
            size_factor = 1.0
        elif capacity > 15000:
            size_factor = 0.9
        else:
            size_factor = 0.8

        # Attendance factor
        attendance_factor = attendance_pct

        # Base crowd advantage
        base_crowd_impact = 0.03  # 3% at full capacity for avg stadium

        impact = base_crowd_impact * size_factor * attendance_factor

        return impact

    def predict_advantage_for_matchup(
        self,
        venue_id: str,
        visiting_team_altitude: float = 0.0
    ) -> float:
        """
        Predict home advantage for specific matchup.

        Args:
            venue_id: Home venue identifier
            visiting_team_altitude: Visiting team's home altitude

        Returns:
            Predicted home advantage for this matchup
        """
        if venue_id not in self.venue_factors:
            return 0.056  # League average

        factors = self.venue_factors[venue_id]

        # Base advantage from all factors
        base_advantage = sum(f['impact'] for f in factors.values())

        # Adjust altitude advantage based on visitor's altitude acclimation
        altitude_impact = factors['altitude']['impact']

        if visiting_team_altitude > 3000:
            # Visitor is acclimated to altitude
            altitude_reduction = (visiting_team_altitude / 5280) * altitude_impact
            base_advantage -= altitude_reduction * 0.5

        return base_advantage


class WeatherNormalizedShotQuality:
    """
    Weather-normalized shot quality for open-air venues.

    Adjusts shot quality metrics based on weather conditions in outdoor sports.
    """

    def __init__(self, sport: str = 'football'):
        """
        Initialize weather normalization model.

        Args:
            sport: Sport type (affects weather impact)
        """
        self.sport = sport

    def normalize_shot_quality(
        self,
        observed_quality: float,
        weather_conditions: Dict
    ) -> Dict:
        """
        Normalize shot quality for weather conditions.

        Args:
            observed_quality: Observed completion/accuracy rate
            weather_conditions: Dict with 'temp', 'wind_speed', 'precipitation', 'humidity'

        Returns:
            Weather-normalized metrics
        """
        # Extract conditions
        temp = weather_conditions.get('temp_f', 70)
        wind_speed = weather_conditions.get('wind_mph', 0)
        precipitation = weather_conditions.get('precipitation', 'none')
        humidity = weather_conditions.get('humidity_pct', 50)

        # Calculate weather impact
        temp_impact = self._temperature_impact(temp)
        wind_impact = self._wind_impact(wind_speed)
        precip_impact = self._precipitation_impact(precipitation)
        humidity_impact = self._humidity_impact(humidity)

        # Total weather adjustment
        total_adjustment = temp_impact + wind_impact + precip_impact + humidity_impact

        # Normalized quality (what quality would be in neutral conditions)
        normalized_quality = observed_quality / (1 + total_adjustment)

        return {
            'observed_quality': observed_quality,
            'normalized_quality': normalized_quality,
            'weather_impact_pct': total_adjustment * 100,
            'factors': {
                'temperature': temp_impact,
                'wind': wind_impact,
                'precipitation': precip_impact,
                'humidity': humidity_impact
            },
            'difficulty_rating': self._conditions_to_difficulty(weather_conditions)
        }

    def _temperature_impact(self, temp_f: float) -> float:
        """Calculate temperature impact on shot quality."""
        # Ideal temperature: 60-75°F
        if 60 <= temp_f <= 75:
            return 0.0
        elif temp_f < 32:
            # Extreme cold
            return -0.10
        elif temp_f < 45:
            # Cold
            return -0.05
        elif temp_f < 60:
            # Cool
            return -0.02
        elif temp_f > 95:
            # Extreme heat
            return -0.08
        elif temp_f > 85:
            # Hot
            return -0.04
        else:
            return -0.01

    def _wind_impact(self, wind_mph: float) -> float:
        """Calculate wind impact on shot quality."""
        # Wind affects passing/kicking significantly
        if wind_mph < 5:
            return 0.0
        elif wind_mph < 10:
            return -0.02
        elif wind_mph < 15:
            return -0.05
        elif wind_mph < 20:
            return -0.10
        else:
            return -0.15  # Extreme wind

    def _precipitation_impact(self, precipitation: str) -> float:
        """Calculate precipitation impact."""
        precip_impacts = {
            'none': 0.0,
            'light_rain': -0.03,
            'rain': -0.07,
            'heavy_rain': -0.12,
            'snow': -0.10,
            'heavy_snow': -0.18
        }

        return precip_impacts.get(precipitation.lower(), 0.0)

    def _humidity_impact(self, humidity_pct: float) -> float:
        """Calculate humidity impact."""
        # Extreme humidity affects ball handling
        if humidity_pct > 80:
            return -0.03
        elif humidity_pct < 20:
            return -0.01
        else:
            return 0.0

    def _conditions_to_difficulty(self, conditions: Dict) -> str:
        """Convert conditions to difficulty rating."""
        total_negative_impact = (
            abs(self._temperature_impact(conditions.get('temp_f', 70))) +
            abs(self._wind_impact(conditions.get('wind_mph', 0))) +
            abs(self._precipitation_impact(conditions.get('precipitation', 'none'))) +
            abs(self._humidity_impact(conditions.get('humidity_pct', 50)))
        )

        if total_negative_impact < 0.05:
            return "Ideal"
        elif total_negative_impact < 0.10:
            return "Good"
        elif total_negative_impact < 0.15:
            return "Challenging"
        else:
            return "Severe"

    def predict_performance_in_conditions(
        self,
        player_neutral_stats: Dict[str, float],
        weather_conditions: Dict
    ) -> Dict[str, float]:
        """
        Predict player performance in specific weather.

        Args:
            player_neutral_stats: Player stats in neutral conditions
            weather_conditions: Weather condition dict

        Returns:
            Predicted stats in these conditions
        """
        normalization = self.normalize_shot_quality(1.0, weather_conditions)
        weather_multiplier = 1.0 + normalization['weather_impact_pct'] / 100

        predicted_stats = {}
        for stat, value in player_neutral_stats.items():
            # Different stats affected differently by weather
            if stat in ['completion_pct', 'fg_pct', 'accuracy']:
                predicted_stats[stat] = value * weather_multiplier
            elif stat in ['yards', 'distance']:
                # Distance stats affected more by wind
                wind_mult = 1.0 + (normalization['factors']['wind'] * 1.5)
                predicted_stats[stat] = value * wind_mult
            else:
                # Other stats less affected
                predicted_stats[stat] = value * (1.0 + normalization['weather_impact_pct'] / 200)

        return predicted_stats
