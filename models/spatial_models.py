"""
Spatial and Tactical Analysis Models

3. Spatial pressure-map regression for defensive coverage
17. Tactical similarity scoring between teams
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.spatial.distance import euclidean, cosine
from scipy.stats import gaussian_kde


class SpatialPressureMapRegression:
    """
    Spatial pressure-map regression for defensive coverage.

    Models defensive pressure as a heat map across the playing surface,
    identifying zones of high/low coverage and predicting offensive success rates.
    """

    def __init__(
        self,
        field_dimensions: Tuple[int, int] = (100, 50),
        grid_resolution: int = 10
    ):
        """
        Initialize spatial pressure map.

        Args:
            field_dimensions: (length, width) of field in yards/meters
            grid_resolution: Number of grid cells per dimension
        """
        self.field_length = field_dimensions[0]
        self.field_width = field_dimensions[1]
        self.grid_res = grid_resolution

        # Create grid
        self.x_bins = np.linspace(0, self.field_length, grid_resolution)
        self.y_bins = np.linspace(0, self.field_width, grid_resolution)

        self.pressure_maps: Dict[str, np.ndarray] = {}

    def build_pressure_map(
        self,
        team_id: str,
        defensive_positions: List[Tuple[float, float]],
        event_outcomes: List[Dict]
    ) -> np.ndarray:
        """
        Build pressure map from defensive positions and outcomes.

        Args:
            team_id: Team identifier
            defensive_positions: List of (x, y) defender positions
            event_outcomes: List of events with 'location', 'success', 'event_type'

        Returns:
            Pressure map array (grid_res x grid_res)
        """
        # Initialize pressure map
        pressure_map = np.zeros((self.grid_res, self.grid_res))

        if not defensive_positions or not event_outcomes:
            self.pressure_maps[team_id] = pressure_map
            return pressure_map

        # Calculate pressure at each grid point
        for i, x in enumerate(self.x_bins):
            for j, y in enumerate(self.y_bins):
                pressure_map[i, j] = self._calculate_local_pressure(
                    (x, y),
                    defensive_positions,
                    event_outcomes
                )

        self.pressure_maps[team_id] = pressure_map
        return pressure_map

    def _calculate_local_pressure(
        self,
        location: Tuple[float, float],
        defender_positions: List[Tuple[float, float]],
        events: List[Dict]
    ) -> float:
        """
        Calculate defensive pressure at a specific location.

        Args:
            location: (x, y) position to evaluate
            defender_positions: Defender locations
            events: Event outcomes near this location

        Returns:
            Pressure value (0 to 1, higher = more pressure)
        """
        # Calculate distance-weighted defender influence
        pressure = 0.0

        for def_pos in defender_positions:
            distance = euclidean(location, def_pos)
            # Pressure decays with distance (inverse square law)
            influence = 1.0 / (1.0 + distance ** 2 / 100.0)
            pressure += influence

        # Normalize by number of defenders
        pressure /= max(len(defender_positions), 1)

        # Adjust based on actual event outcomes in this zone
        nearby_events = [
            e for e in events
            if euclidean(location, e.get('location', (0, 0))) < 5
        ]

        if nearby_events:
            success_rate = sum(
                1 for e in nearby_events if not e.get('success', False)
            ) / len(nearby_events)
            # High success rate for defense = high pressure
            pressure = 0.7 * pressure + 0.3 * success_rate

        return np.clip(pressure, 0, 1)

    def predict_success_probability(
        self,
        team_id: str,
        attack_location: Tuple[float, float],
        event_type: str
    ) -> float:
        """
        Predict offensive success probability at a location.

        Args:
            team_id: Defending team identifier
            attack_location: (x, y) position of attack
            event_type: Type of offensive event

        Returns:
            Success probability (0 to 1)
        """
        if team_id not in self.pressure_maps:
            return 0.5

        pressure_map = self.pressure_maps[team_id]

        # Find grid cell for attack location
        x_idx = np.searchsorted(self.x_bins, attack_location[0]) - 1
        y_idx = np.searchsorted(self.y_bins, attack_location[1]) - 1

        x_idx = np.clip(x_idx, 0, self.grid_res - 1)
        y_idx = np.clip(y_idx, 0, self.grid_res - 1)

        pressure = pressure_map[x_idx, y_idx]

        # Base success rate (varies by event type)
        base_rates = {
            'pass': 0.65,
            'shot': 0.35,
            'dribble': 0.55,
            'run': 0.70
        }
        base_rate = base_rates.get(event_type, 0.5)

        # Pressure reduces success probability
        success_prob = base_rate * (1 - 0.6 * pressure)

        return np.clip(success_prob, 0, 1)

    def identify_coverage_gaps(
        self,
        team_id: str,
        threshold: float = 0.3
    ) -> List[Tuple[float, float]]:
        """
        Identify areas with weak defensive coverage.

        Args:
            team_id: Team identifier
            threshold: Pressure threshold below which is considered a gap

        Returns:
            List of (x, y) positions with coverage gaps
        """
        if team_id not in self.pressure_maps:
            return []

        pressure_map = self.pressure_maps[team_id]
        gaps = []

        for i, x in enumerate(self.x_bins):
            for j, y in enumerate(self.y_bins):
                if pressure_map[i, j] < threshold:
                    gaps.append((x, y))

        return gaps


class TacticalSimilarityScoring:
    """
    Tactical similarity scoring between teams.

    Quantifies how similar two teams' playing styles are based on
    multiple tactical dimensions.
    """

    def __init__(self):
        """Initialize tactical similarity scorer."""
        self.team_profiles: Dict[str, Dict[str, float]] = {}

    def build_tactical_profile(
        self,
        team_id: str,
        stats: Dict[str, float]
    ):
        """
        Build tactical profile for a team.

        Args:
            team_id: Team identifier
            stats: Tactical statistics dict with keys:
                - possession_pct
                - pass_completion_pct
                - passes_per_game
                - long_pass_pct
                - shots_per_game
                - shot_distance_avg
                - defensive_line_height
                - pressing_intensity
                - counter_attack_freq
                - set_piece_frequency
        """
        # Normalize stats to 0-1 scale for comparison
        normalized_profile = {
            'possession': stats.get('possession_pct', 50) / 100,
            'pass_completion': stats.get('pass_completion_pct', 75) / 100,
            'pass_volume': min(stats.get('passes_per_game', 400) / 800, 1.0),
            'long_ball': stats.get('long_pass_pct', 15) / 50,
            'shot_volume': min(stats.get('shots_per_game', 15) / 30, 1.0),
            'shot_distance': min(stats.get('shot_distance_avg', 18) / 30, 1.0),
            'defensive_line': stats.get('defensive_line_height', 50) / 100,
            'pressing': min(stats.get('pressing_intensity', 100) / 200, 1.0),
            'counter_attack': min(stats.get('counter_attack_freq', 5) / 15, 1.0),
            'set_pieces': min(stats.get('set_piece_frequency', 20) / 40, 1.0)
        }

        self.team_profiles[team_id] = normalized_profile

    def calculate_similarity(
        self,
        team_a_id: str,
        team_b_id: str,
        method: str = 'euclidean'
    ) -> float:
        """
        Calculate tactical similarity between two teams.

        Args:
            team_a_id: First team identifier
            team_b_id: Second team identifier
            method: Similarity method ('euclidean', 'cosine', 'manhattan')

        Returns:
            Similarity score (0 to 1, where 1 = identical tactics)
        """
        if team_a_id not in self.team_profiles or team_b_id not in self.team_profiles:
            return 0.5

        profile_a = self.team_profiles[team_a_id]
        profile_b = self.team_profiles[team_b_id]

        # Convert to vectors
        keys = sorted(profile_a.keys())
        vec_a = np.array([profile_a[k] for k in keys])
        vec_b = np.array([profile_b[k] for k in keys])

        if method == 'euclidean':
            # Euclidean distance (normalize to 0-1)
            distance = np.linalg.norm(vec_a - vec_b)
            max_distance = np.sqrt(len(keys))
            similarity = 1 - (distance / max_distance)
        elif method == 'cosine':
            # Cosine similarity
            similarity = 1 - cosine(vec_a, vec_b)
        elif method == 'manhattan':
            # Manhattan distance
            distance = np.sum(np.abs(vec_a - vec_b))
            max_distance = len(keys)
            similarity = 1 - (distance / max_distance)
        else:
            similarity = 0.5

        return np.clip(similarity, 0, 1)

    def get_tactical_archetype(
        self,
        team_id: str
    ) -> str:
        """
        Classify team into tactical archetype.

        Args:
            team_id: Team identifier

        Returns:
            Archetype description
        """
        if team_id not in self.team_profiles:
            return "Unknown"

        profile = self.team_profiles[team_id]

        # Define archetypes based on key metrics
        possession = profile['possession']
        pressing = profile['pressing']
        long_ball = profile['long_ball']
        counter_attack = profile['counter_attack']

        if possession > 0.6 and pressing > 0.6:
            return "Possession-based pressing (Tiki-taka)"
        elif possession > 0.55 and profile['pass_completion'] > 0.8:
            return "Possession-based patient buildup"
        elif counter_attack > 0.6 and possession < 0.45:
            return "Counter-attacking"
        elif pressing > 0.7:
            return "High-intensity pressing"
        elif long_ball > 0.5:
            return "Direct/Long-ball"
        elif profile['defensive_line'] < 0.4:
            return "Low-block defensive"
        else:
            return "Balanced/Pragmatic"

    def find_similar_teams(
        self,
        team_id: str,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find teams with most similar tactics.

        Args:
            team_id: Team identifier
            top_n: Number of similar teams to return

        Returns:
            List of (team_id, similarity_score) tuples
        """
        if team_id not in self.team_profiles:
            return []

        similarities = []

        for other_team_id in self.team_profiles:
            if other_team_id != team_id:
                similarity = self.calculate_similarity(team_id, other_team_id)
                similarities.append((other_team_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_n]

    def get_tactical_mismatch_score(
        self,
        team_a_id: str,
        team_b_id: str
    ) -> Dict:
        """
        Analyze tactical matchup between teams.

        Args:
            team_a_id: First team identifier
            team_b_id: Second team identifier

        Returns:
            Mismatch analysis with advantages
        """
        if team_a_id not in self.team_profiles or team_b_id not in self.team_profiles:
            return {'mismatch_score': 0.5, 'advantages': []}

        profile_a = self.team_profiles[team_a_id]
        profile_b = self.team_profiles[team_b_id]

        advantages = []

        # Pressing vs possession mismatch
        if profile_a['pressing'] > 0.6 and profile_b['possession'] > 0.6:
            advantages.append({
                'team': team_a_id,
                'advantage': 'Pressing vs possession-heavy opponent',
                'magnitude': profile_a['pressing'] * profile_b['possession']
            })

        # Counter-attack vs high defensive line
        if profile_a['counter_attack'] > 0.6 and profile_b['defensive_line'] > 0.6:
            advantages.append({
                'team': team_a_id,
                'advantage': 'Counter-attacks vs high defensive line',
                'magnitude': profile_a['counter_attack'] * profile_b['defensive_line']
            })

        # Similar for team B
        if profile_b['pressing'] > 0.6 and profile_a['possession'] > 0.6:
            advantages.append({
                'team': team_b_id,
                'advantage': 'Pressing vs possession-heavy opponent',
                'magnitude': profile_b['pressing'] * profile_a['possession']
            })

        if profile_b['counter_attack'] > 0.6 and profile_a['defensive_line'] > 0.6:
            advantages.append({
                'team': team_b_id,
                'advantage': 'Counter-attacks vs high defensive line',
                'magnitude': profile_b['counter_attack'] * profile_a['defensive_line']
            })

        # Overall mismatch score (higher = more mismatched styles)
        similarity = self.calculate_similarity(team_a_id, team_b_id)
        mismatch_score = 1 - similarity

        return {
            'mismatch_score': mismatch_score,
            'advantages': sorted(advantages, key=lambda x: x['magnitude'], reverse=True)
        }
