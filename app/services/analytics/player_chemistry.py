"""Player chemistry and synergy analytics"""

import numpy as np
from typing import List, Dict
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sklearn.cluster import KMeans

from app.models import Player, PlayerChemistry, PlayerMetrics, Game, PlayByPlay


class PlayerChemistryAnalyzer:
    """Analyze player chemistry and lineup synergies"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_chemistry(
        self,
        player_id: int,
        teammate_id: int,
        season: str
    ) -> PlayerChemistry:
        """Calculate chemistry score between two players"""

        # Get shared minutes and performance data
        shared_data = await self._get_shared_playing_time(
            player_id, teammate_id, season
        )

        if not shared_data["games_together"]:
            raise ValueError("Players have not played together")

        # Calculate chemistry components
        chemistry_score = self._calculate_chemistry_score(shared_data)
        offensive_synergy = self._calculate_offensive_synergy(shared_data)
        defensive_synergy = self._calculate_defensive_synergy(shared_data)
        synergy_rating = (offensive_synergy + defensive_synergy) / 2

        chemistry = PlayerChemistry(
            player_id=player_id,
            teammate_id=teammate_id,
            season=season,
            chemistry_score=chemistry_score,
            shared_minutes=shared_data["total_minutes"],
            plus_minus_together=shared_data["plus_minus"],
            offensive_synergy=offensive_synergy,
            defensive_synergy=defensive_synergy,
            games_together=shared_data["games_together"],
            assist_connection=shared_data.get("assist_connection", 0),
            synergy_rating=synergy_rating,
        )

        self.db.add(chemistry)
        await self.db.commit()
        return chemistry

    async def find_best_lineups(
        self,
        team_id: int,
        lineup_size: int = 5,
        min_minutes: int = 50
    ) -> List[Dict]:
        """
        Find best performing lineup combinations

        Args:
            team_id: Team to analyze
            lineup_size: Number of players in lineup
            min_minutes: Minimum minutes played together

        Returns:
            List of lineups with their performance metrics
        """

        # This would analyze actual lineup data
        # Placeholder implementation
        return [
            {
                "players": [1, 2, 3, 4, 5],
                "plus_minus": 12.5,
                "offensive_rating": 118.5,
                "defensive_rating": 105.2,
                "net_rating": 13.3,
                "minutes": 150
            }
        ]

    async def calculate_similarity_clusters(
        self,
        league: str,
        n_clusters: int = 10
    ) -> Dict[int, List[int]]:
        """
        Cluster players by playing style and stats

        Returns:
            dict mapping cluster_id to list of player_ids
        """

        # Get player stats for clustering
        result = await self.db.execute(
            select(Player, PlayerMetrics)
            .join(PlayerMetrics, Player.id == PlayerMetrics.player_id)
            .where(Player.is_active == True)
        )

        # This would extract features and cluster
        # Placeholder implementation
        return {
            0: [1, 2, 3],  # "Playmakers"
            1: [4, 5, 6],  # "3-and-D wings"
            2: [7, 8, 9],  # "Rim protectors"
        }

    async def _get_shared_playing_time(
        self,
        player_id: int,
        teammate_id: int,
        season: str
    ) -> Dict:
        """Get shared playing time and performance data"""

        # This would query actual game logs and lineup data
        # Placeholder implementation
        return {
            "games_together": 45,
            "total_minutes": 850.0,
            "plus_minus": 8.5,
            "points_together": 1250,
            "assists_together": 320,
            "assist_connection": 45,  # Assists from one to the other
        }

    def _calculate_chemistry_score(self, shared_data: Dict) -> float:
        """
        Calculate overall chemistry score (0-100)

        Based on:
        - Plus/minus when playing together
        - Time on court together
        - Assist connections
        """

        # Normalize plus/minus (assume -20 to +20 range)
        pm_score = (shared_data["plus_minus"] + 20) / 40 * 50

        # Minutes together score (more time = more chemistry)
        minutes_score = min(shared_data["total_minutes"] / 1000, 1.0) * 30

        # Assist connection score
        assist_score = min(shared_data.get("assist_connection", 0) / 50, 1.0) * 20

        chemistry = pm_score + minutes_score + assist_score

        return np.clip(chemistry, 0, 100)

    def _calculate_offensive_synergy(self, shared_data: Dict) -> float:
        """Calculate offensive synergy score (0-100)"""

        # Based on points scored and assists when playing together
        points_per_game = shared_data["points_together"] / max(shared_data["games_together"], 1)
        assists_per_game = shared_data["assists_together"] / max(shared_data["games_together"], 1)

        # Normalize (assuming 25 ppg and 7 apg as good)
        points_score = min(points_per_game / 25, 1.0) * 60
        assist_score = min(assists_per_game / 7, 1.0) * 40

        return np.clip(points_score + assist_score, 0, 100)

    def _calculate_defensive_synergy(self, shared_data: Dict) -> float:
        """Calculate defensive synergy score (0-100)"""

        # Would analyze defensive stats when playing together
        # Placeholder
        return 72.0

    async def get_player_similarity(
        self,
        player_id: int,
        n_similar: int = 10
    ) -> List[Dict]:
        """
        Find most similar players based on stats and style

        Returns:
            List of similar players with similarity scores
        """

        # Would use cosine similarity on stat vectors
        # Placeholder
        return [
            {"player_id": 123, "similarity_score": 0.92, "name": "Similar Player 1"},
            {"player_id": 456, "similarity_score": 0.88, "name": "Similar Player 2"},
        ]
