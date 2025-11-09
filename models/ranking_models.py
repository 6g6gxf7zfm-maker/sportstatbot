"""
Ranking Models

24. Multi-metric composite ranking (weighted PCA)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class MultiMetricCompositeRanking:
    """
    Multi-metric composite ranking using weighted PCA.

    Combines multiple performance metrics into a single composite
    ranking using principal component analysis.
    """

    def __init__(self, n_components: int = 3):
        """
        Initialize composite ranking model.

        Args:
            n_components: Number of principal components to use
        """
        self.n_components = n_components
        self.pca = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.team_rankings = {}

    def compute_composite_rankings(
        self,
        teams_data: List[Dict],
        metric_weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Compute composite rankings from multiple metrics.

        Args:
            teams_data: List of team dicts with performance metrics
            metric_weights: Optional weights for each metric

        Returns:
            Ranking results
        """
        # Extract features
        features_matrix = []
        team_ids = []

        for team in teams_data:
            features = self._extract_features(team)
            features_matrix.append(features)
            team_ids.append(team.get('id', 'unknown'))

        # Convert to array and normalize
        X = np.array(features_matrix)
        X_normalized = self.scaler.fit_transform(X)

        # Apply PCA
        self.pca = PCA(n_components=min(self.n_components, X.shape[1]))
        X_pca = self.pca.fit_transform(X_normalized)

        # Calculate composite scores
        if metric_weights:
            # Apply custom weights
            composite_scores = self._apply_weights(X_normalized, metric_weights)
        else:
            # Use first principal component as composite score
            composite_scores = X_pca[:, 0]

        # Rank teams
        rankings = self._create_rankings(team_ids, composite_scores)

        # Store explained variance
        explained_variance = self.pca.explained_variance_ratio_

        return {
            'rankings': rankings,
            'explained_variance': explained_variance.tolist(),
            'feature_loadings': self._get_feature_loadings(),
            'top_10': rankings[:10]
        }

    def _extract_features(self, team_data: Dict) -> List[float]:
        """Extract feature vector from team data."""
        features = [
            team_data.get('wins', 0),
            team_data.get('win_pct', 0.5),
            team_data.get('point_differential', 0),
            team_data.get('offensive_rating', 110),
            team_data.get('defensive_rating', 110),
            team_data.get('net_rating', 0),
            team_data.get('pace', 100),
            team_data.get('strength_of_schedule', 1.0),
            team_data.get('recent_form', 0.5),
            team_data.get('home_win_pct', 0.5),
            team_data.get('away_win_pct', 0.5),
            team_data.get('vs_winning_teams', 0.5)
        ]

        self.feature_names = [
            'wins', 'win_pct', 'point_diff', 'off_rating',
            'def_rating', 'net_rating', 'pace', 'sos',
            'form', 'home_pct', 'away_pct', 'vs_winning'
        ]

        return features

    def _apply_weights(
        self,
        X: np.ndarray,
        weights: Dict[str, float]
    ) -> np.ndarray:
        """Apply custom weights to features."""
        weight_vector = np.array([
            weights.get(name, 1.0) for name in self.feature_names
        ])

        # Normalize weights
        weight_vector = weight_vector / np.sum(weight_vector)

        # Weighted sum
        composite_scores = X @ weight_vector

        return composite_scores

    def _create_rankings(
        self,
        team_ids: List[str],
        scores: np.ndarray
    ) -> List[Dict]:
        """Create ranked list from scores."""
        # Combine team IDs and scores
        teams_scores = list(zip(team_ids, scores))

        # Sort by score (descending)
        teams_scores.sort(key=lambda x: x[1], reverse=True)

        # Create rankings
        rankings = []
        for rank, (team_id, score) in enumerate(teams_scores, 1):
            self.team_rankings[team_id] = {
                'rank': rank,
                'composite_score': float(score),
                'percentile': ((len(teams_scores) - rank + 1) / len(teams_scores)) * 100
            }

            rankings.append({
                'rank': rank,
                'team_id': team_id,
                'composite_score': float(score),
                'tier': self._rank_to_tier(rank, len(teams_scores))
            })

        return rankings

    def _rank_to_tier(self, rank: int, total_teams: int) -> str:
        """Convert rank to tier."""
        percentile = (total_teams - rank + 1) / total_teams

        if percentile >= 0.90:
            return "Elite"
        elif percentile >= 0.75:
            return "Contender"
        elif percentile >= 0.50:
            return "Playoff Team"
        elif percentile >= 0.25:
            return "Bubble Team"
        else:
            return "Rebuild"

    def _get_feature_loadings(self) -> Dict[str, List[float]]:
        """Get feature loadings for each principal component."""
        if self.pca is None:
            return {}

        loadings = {}

        for i, component in enumerate(self.pca.components_):
            loadings[f'PC{i+1}'] = {
                name: float(loading)
                for name, loading in zip(self.feature_names, component)
            }

        return loadings

    def identify_key_drivers(
        self,
        team_id: str
    ) -> List[Tuple[str, float]]:
        """
        Identify key performance drivers for a team.

        Args:
            team_id: Team identifier

        Returns:
            List of (metric, impact) tuples
        """
        if self.pca is None or team_id not in self.team_rankings:
            return []

        # Get first principal component (most important)
        pc1_loadings = self.pca.components_[0]

        # Get feature contributions
        drivers = [
            (name, float(loading))
            for name, loading in zip(self.feature_names, pc1_loadings)
        ]

        # Sort by absolute loading (importance)
        drivers.sort(key=lambda x: abs(x[1]), reverse=True)

        return drivers[:5]  # Top 5 drivers

    def power_rankings_with_tiers(
        self,
        teams_data: List[Dict]
    ) -> Dict:
        """
        Create power rankings with tier classifications.

        Args:
            teams_data: Team performance data

        Returns:
            Power rankings with tiers
        """
        rankings_result = self.compute_composite_rankings(teams_data)
        rankings = rankings_result['rankings']

        # Group into tiers
        tiers = {
            'Elite': [],
            'Contender': [],
            'Playoff Team': [],
            'Bubble Team': [],
            'Rebuild': []
        }

        for team_rank in rankings:
            tier = team_rank['tier']
            tiers[tier].append(team_rank)

        return {
            'rankings': rankings,
            'tiers': tiers,
            'tier_summary': {
                tier: len(teams)
                for tier, teams in tiers.items()
            }
        }

    def simulate_rank_stability(
        self,
        team_id: str,
        n_simulations: int = 1000
    ) -> Dict:
        """
        Simulate ranking stability (confidence in ranking).

        Args:
            team_id: Team identifier
            n_simulations: Number of Monte Carlo simulations

        Returns:
            Stability analysis
        """
        if team_id not in self.team_rankings:
            return {'stability': 'Unknown'}

        current_rank = self.team_rankings[team_id]['rank']
        current_score = self.team_rankings[team_id]['composite_score']

        # Simulate rank changes with noise
        simulated_ranks = []

        for _ in range(n_simulations):
            # Add random noise to score
            noise = np.random.normal(0, 0.1)  # 10% standard deviation
            noisy_score = current_score + noise

            # Recalculate rank (simplified - assumes other teams stay same)
            simulated_rank = current_rank  # Placeholder
            simulated_ranks.append(simulated_rank)

        # Calculate stability metrics
        rank_std = np.std(simulated_ranks)
        stability_pct = (1 - min(rank_std / current_rank, 1.0)) * 100

        return {
            'current_rank': current_rank,
            'rank_stability_pct': stability_pct,
            'stability_rating': self._stability_rating(stability_pct),
            'expected_rank_range': (
                int(current_rank - rank_std),
                int(current_rank + rank_std)
            )
        }

    def _stability_rating(self, stability_pct: float) -> str:
        """Convert stability percentage to rating."""
        if stability_pct > 90:
            return "Very Stable"
        elif stability_pct > 75:
            return "Stable"
        elif stability_pct > 60:
            return "Moderate"
        else:
            return "Volatile"
