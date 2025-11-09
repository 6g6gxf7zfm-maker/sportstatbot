"""
Clustering Models

14. Opponent style clustering using unsupervised learning
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class OpponentStyleClustering:
    """
    Opponent style clustering using unsupervised learning.

    Groups opponents into tactical/stylistic clusters to identify
    patterns and predict matchup dynamics.
    """

    def __init__(self, n_clusters: int = 5):
        """
        Initialize opponent style clustering.

        Args:
            n_clusters: Number of style clusters
        """
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.feature_names = []
        self.team_styles = {}

    def fit_clusters(
        self,
        teams_data: List[Dict]
    ) -> Dict:
        """
        Fit clustering model to team data.

        Args:
            teams_data: List of team dicts with tactical stats

        Returns:
            Clustering results
        """
        # Extract features
        features_list = []
        team_ids = []

        for team in teams_data:
            features = self._extract_features(team)
            features_list.append(features)
            team_ids.append(team.get('id', 'unknown'))

        # Convert to array and normalize
        X = np.array(features_list)
        X_normalized = self.scaler.fit_transform(X)

        # Fit K-means
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X_normalized)

        # Store results
        for team_id, label in zip(team_ids, cluster_labels):
            self.team_styles[team_id] = label

        # Characterize clusters
        cluster_profiles = self._characterize_clusters(X, cluster_labels)

        return {
            'n_clusters': self.n_clusters,
            'cluster_assignments': {tid: int(label) for tid, label in zip(team_ids, cluster_labels)},
            'cluster_profiles': cluster_profiles,
            'feature_names': self.feature_names
        }

    def _extract_features(self, team_data: Dict) -> List[float]:
        """Extract feature vector from team data."""
        features = [
            team_data.get('pace', 100),
            team_data.get('offensive_rating', 110),
            team_data.get('defensive_rating', 110),
            team_data.get('three_point_rate', 0.35),
            team_data.get('assist_rate', 0.60),
            team_data.get('turnover_rate', 0.14),
            team_data.get('offensive_rebound_rate', 0.25),
            team_data.get('free_throw_rate', 0.25),
            team_data.get('true_shooting_pct', 0.56),
            team_data.get('effective_fg_pct', 0.52)
        ]

        self.feature_names = [
            'pace', 'off_rating', 'def_rating', '3pt_rate',
            'ast_rate', 'tov_rate', 'oreb_rate', 'ft_rate',
            'ts_pct', 'efg_pct'
        ]

        return features

    def _characterize_clusters(
        self,
        X: np.ndarray,
        labels: np.ndarray
    ) -> Dict:
        """Characterize each cluster's playing style."""
        profiles = {}

        for cluster_id in range(self.n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = X[cluster_mask]

            if len(cluster_data) == 0:
                continue

            # Calculate cluster centroid
            centroid = np.mean(cluster_data, axis=0)

            # Assign archetype based on characteristics
            archetype = self._assign_archetype(centroid)

            profiles[cluster_id] = {
                'archetype': archetype,
                'size': int(np.sum(cluster_mask)),
                'avg_features': {
                    name: float(value)
                    for name, value in zip(self.feature_names, centroid)
                },
                'key_characteristics': self._identify_key_characteristics(centroid)
            }

        return profiles

    def _assign_archetype(self, centroid: np.ndarray) -> str:
        """Assign playing style archetype based on centroid."""
        # Extract key features (assuming order from _extract_features)
        pace = centroid[0]
        off_rating = centroid[1]
        def_rating = centroid[2]
        three_pt_rate = centroid[3]

        # Define archetypes
        if pace > 102:
            if off_rating > 115:
                return "Fast-paced, high-powered offense"
            else:
                return "Fast-paced, transition-focused"
        elif pace < 98:
            if def_rating < 108:
                return "Slow-paced, defensive grind"
            else:
                return "Slow-paced, half-court offense"
        else:
            if three_pt_rate > 0.40:
                return "Modern three-point heavy"
            elif off_rating > 112 and def_rating > 112:
                return "Balanced, high-scoring"
            elif def_rating < 108:
                return "Defense-first, balanced pace"
            else:
                return "Traditional, balanced approach"

    def _identify_key_characteristics(self, centroid: np.ndarray) -> List[str]:
        """Identify key distinguishing characteristics."""
        characteristics = []

        pace, off_rtg, def_rtg, three_rate, ast_rate, tov_rate, oreb_rate, ft_rate, ts_pct, efg_pct = centroid

        # Pace
        if pace > 103:
            characteristics.append("Very high pace")
        elif pace < 97:
            characteristics.append("Very low pace")

        # Offense
        if off_rtg > 115:
            characteristics.append("Elite offense")
        elif off_rtg < 108:
            characteristics.append("Weak offense")

        # Defense
        if def_rtg < 108:
            characteristics.append("Elite defense")
        elif def_rtg > 115:
            characteristics.append("Weak defense")

        # Three-point shooting
        if three_rate > 0.42:
            characteristics.append("Three-point heavy")
        elif three_rate < 0.30:
            characteristics.append("Inside-focused")

        # Ball movement
        if ast_rate > 0.65:
            characteristics.append("Excellent ball movement")

        # Rebounding
        if oreb_rate > 0.30:
            characteristics.append("Strong offensive rebounding")

        return characteristics

    def predict_cluster(
        self,
        team_data: Dict
    ) -> int:
        """
        Predict cluster for a new team.

        Args:
            team_data: Team statistics

        Returns:
            Cluster ID
        """
        if self.kmeans is None:
            return -1

        features = self._extract_features(team_data)
        features_normalized = self.scaler.transform([features])

        cluster_id = self.kmeans.predict(features_normalized)[0]

        return int(cluster_id)

    def find_similar_opponents(
        self,
        team_id: str,
        top_n: int = 5
    ) -> List[Tuple[str, int]]:
        """
        Find opponents with similar playing style.

        Args:
            team_id: Team identifier
            top_n: Number of similar teams to return

        Returns:
            List of (team_id, cluster_id) tuples
        """
        if team_id not in self.team_styles:
            return []

        target_cluster = self.team_styles[team_id]

        similar_teams = [
            (tid, cluster)
            for tid, cluster in self.team_styles.items()
            if cluster == target_cluster and tid != team_id
        ]

        return similar_teams[:top_n]

    def matchup_analysis(
        self,
        team_a_id: str,
        team_b_id: str,
        cluster_profiles: Dict
    ) -> Dict:
        """
        Analyze matchup between two teams based on clusters.

        Args:
            team_a_id: First team
            team_b_id: Second team
            cluster_profiles: Cluster profile information

        Returns:
            Matchup analysis
        """
        if team_a_id not in self.team_styles or team_b_id not in self.team_styles:
            return {'error': 'One or both teams not clustered'}

        cluster_a = self.team_styles[team_a_id]
        cluster_b = self.team_styles[team_b_id]

        profile_a = cluster_profiles.get(cluster_a, {})
        profile_b = cluster_profiles.get(cluster_b, {})

        # Determine stylistic matchup
        if cluster_a == cluster_b:
            matchup_type = "Mirror matchup - similar styles"
        else:
            matchup_type = "Contrasting styles"

        return {
            'team_a_cluster': cluster_a,
            'team_b_cluster': cluster_b,
            'team_a_archetype': profile_a.get('archetype', 'Unknown'),
            'team_b_archetype': profile_b.get('archetype', 'Unknown'),
            'matchup_type': matchup_type,
            'team_a_characteristics': profile_a.get('key_characteristics', []),
            'team_b_characteristics': profile_b.get('key_characteristics', [])
        }
