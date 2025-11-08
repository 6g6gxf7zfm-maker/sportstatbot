"""
Story Memory Map - Cross-linking and relationship visualization
Shows connections between related stories
"""

from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, Counter
import json

from .database_handler import DatabaseHandler
from .models import StoryLink


class StoryMemoryMap:
    """Manages cross-linking and relationships between stories"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)

    def auto_link_documents(self, doc_id: str) -> int:
        """
        Automatically create links between this document and related documents
        Returns the number of links created
        """
        doc = self.db.get_document(doc_id)
        if not doc:
            return 0

        links_created = 0
        metadata = doc.get('metadata', {})

        # Link by teams
        teams = metadata.get('teams', [])
        for team in teams:
            related_docs = self._find_docs_mentioning(team, exclude_doc_id=doc_id)
            for related_doc in related_docs[:10]:  # Limit to top 10
                self._create_link(
                    doc_id,
                    related_doc['doc_id'],
                    link_type='same_team',
                    strength=self._calculate_team_link_strength(doc, related_doc)
                )
                links_created += 1

        # Link by players
        players = metadata.get('players', [])
        for player in players:
            related_docs = self._find_docs_mentioning(player, exclude_doc_id=doc_id)
            for related_doc in related_docs[:10]:
                self._create_link(
                    doc_id,
                    related_doc['doc_id'],
                    link_type='same_player',
                    strength=self._calculate_player_link_strength(doc, related_doc)
                )
                links_created += 1

        # Link by tags
        tags = metadata.get('tags', [])
        if tags:
            for tag in tags:
                related_docs = self.db.get_documents_by_tag(tag)
                for related_doc in related_docs[:5]:  # Limit to top 5 per tag
                    if related_doc['doc_id'] != doc_id:
                        self._create_link(
                            doc_id,
                            related_doc['doc_id'],
                            link_type='same_tag',
                            strength=0.5
                        )
                        links_created += 1

        # Link by matchup (documents mentioning same team pair)
        if len(teams) >= 2:
            matchup_docs = self._find_matchup_docs(teams[0], teams[1], exclude_doc_id=doc_id)
            for matchup_doc in matchup_docs[:5]:
                self._create_link(
                    doc_id,
                    matchup_doc['doc_id'],
                    link_type='same_matchup',
                    strength=0.9
                )
                links_created += 1

        return links_created

    def get_story_map(self, doc_id: str, depth: int = 2) -> Dict:
        """
        Get the story memory map for a document
        Shows all connected stories up to a certain depth
        """
        visited = set()
        story_map = {
            'root': doc_id,
            'nodes': [],
            'edges': []
        }

        def explore(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return

            visited.add(current_id)
            doc = self.db.get_document(current_id)

            if doc:
                story_map['nodes'].append({
                    'doc_id': current_id,
                    'title': doc['title'],
                    'depth': current_depth,
                    'metadata': doc.get('metadata', {})
                })

                # Get linked documents
                linked = self.db.get_linked_documents(current_id)
                for linked_doc in linked:
                    edge = {
                        'from': current_id,
                        'to': linked_doc['doc_id'],
                        'link_type': linked_doc.get('link_type', 'unknown'),
                        'strength': linked_doc.get('strength', 1.0)
                    }
                    story_map['edges'].append(edge)

                    # Recursively explore
                    explore(linked_doc['doc_id'], current_depth + 1)

        explore(doc_id, 0)
        return story_map

    def find_story_clusters(self, min_cluster_size: int = 3) -> List[Dict]:
        """
        Find clusters of highly connected stories
        Useful for identifying story arcs or related coverage
        """
        # Get all links
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source_doc_id, target_doc_id, strength
                FROM story_links
                WHERE strength >= 0.7
            """)
            links = cursor.fetchall()

        # Build adjacency graph
        graph = defaultdict(set)
        for link in links:
            graph[link['source_doc_id']].add(link['target_doc_id'])
            graph[link['target_doc_id']].add(link['source_doc_id'])

        # Find connected components (simple DFS)
        visited = set()
        clusters = []

        def dfs(node: str, cluster: Set[str]):
            if node in visited:
                return
            visited.add(node)
            cluster.add(node)
            for neighbor in graph[node]:
                dfs(neighbor, cluster)

        for doc_id in graph:
            if doc_id not in visited:
                cluster = set()
                dfs(doc_id, cluster)
                if len(cluster) >= min_cluster_size:
                    clusters.append(self._cluster_to_dict(cluster))

        return clusters

    def get_story_correlation_matrix(self, team_name: str) -> Dict:
        """
        Which teams appear together most often in stories?
        Useful for identifying rivalries, divisions, etc.
        """
        # Find all documents mentioning this team
        mentions = self.db.find_mentions(team_name, limit=1000)
        doc_ids = [m['doc_id'] for m in mentions]

        # For each document, find other teams mentioned
        co_occurrences = Counter()

        for doc_id in doc_ids:
            doc = self.db.get_document(doc_id)
            if doc:
                teams = doc.get('metadata', {}).get('teams', [])
                for team in teams:
                    if team != team_name:
                        co_occurrences[team] += 1

        return {
            'team': team_name,
            'total_mentions': len(doc_ids),
            'co_occurrences': dict(co_occurrences.most_common(20))
        }

    def get_link_statistics(self) -> Dict:
        """Get statistics about story links"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Total links
            cursor.execute("SELECT COUNT(*) as count FROM story_links")
            total_links = cursor.fetchone()['count']

            # Links by type
            cursor.execute("""
                SELECT link_type, COUNT(*) as count
                FROM story_links
                GROUP BY link_type
                ORDER BY count DESC
            """)
            links_by_type = {row['link_type']: row['count'] for row in cursor.fetchall()}

            # Most linked document
            cursor.execute("""
                SELECT source_doc_id as doc_id, COUNT(*) as link_count
                FROM story_links
                GROUP BY source_doc_id
                ORDER BY link_count DESC
                LIMIT 1
            """)
            most_linked = cursor.fetchone()

            return {
                'total_links': total_links,
                'links_by_type': links_by_type,
                'most_linked_doc': most_linked['doc_id'] if most_linked else None,
                'most_linked_count': most_linked['link_count'] if most_linked else 0
            }

    def suggest_related_stories(self, doc_id: str, limit: int = 5) -> List[Dict]:
        """Suggest related stories for a document"""
        linked = self.db.get_linked_documents(doc_id)

        # Sort by strength
        linked.sort(key=lambda x: x.get('strength', 0), reverse=True)

        suggestions = []
        for doc in linked[:limit]:
            suggestions.append({
                'doc_id': doc['doc_id'],
                'title': doc['title'],
                'link_type': doc.get('link_type'),
                'strength': doc.get('strength'),
                'reason': self._explain_link(doc.get('link_type'))
            })

        return suggestions

    def _create_link(self, source_id: str, target_id: str, link_type: str,
                    strength: float = 1.0):
        """Create a link between two documents"""
        # Avoid duplicate links
        existing = self.db.get_linked_documents(source_id)
        if any(doc['doc_id'] == target_id for doc in existing):
            return

        link = StoryLink(
            source_doc_id=source_id,
            target_doc_id=target_id,
            link_type=link_type,
            strength=strength,
            auto_detected=True
        )

        self.db.add_story_link(link.to_dict())

    def _find_docs_mentioning(self, entity: str, exclude_doc_id: str = None) -> List[Dict]:
        """Find documents mentioning an entity"""
        mentions = self.db.find_mentions(entity, limit=50)
        docs = []

        for mention in mentions:
            if mention['doc_id'] != exclude_doc_id:
                doc = self.db.get_document(mention['doc_id'])
                if doc:
                    docs.append(doc)

        return docs

    def _find_matchup_docs(self, team1: str, team2: str, exclude_doc_id: str = None) -> List[Dict]:
        """Find documents mentioning both teams (matchup coverage)"""
        team1_docs = {m['doc_id'] for m in self.db.find_mentions(team1, limit=100)}
        team2_docs = {m['doc_id'] for m in self.db.find_mentions(team2, limit=100)}

        matchup_doc_ids = team1_docs.intersection(team2_docs)
        if exclude_doc_id:
            matchup_doc_ids.discard(exclude_doc_id)

        return [self.db.get_document(doc_id) for doc_id in matchup_doc_ids]

    def _calculate_team_link_strength(self, doc1: Dict, doc2: Dict) -> float:
        """Calculate link strength based on team overlap"""
        teams1 = set(doc1.get('metadata', {}).get('teams', []))
        teams2 = set(doc2.get('metadata', {}).get('teams', []))

        if not teams1 or not teams2:
            return 0.5

        overlap = len(teams1.intersection(teams2))
        total = len(teams1.union(teams2))

        return overlap / total if total > 0 else 0.5

    def _calculate_player_link_strength(self, doc1: Dict, doc2: Dict) -> float:
        """Calculate link strength based on player overlap"""
        players1 = set(doc1.get('metadata', {}).get('players', []))
        players2 = set(doc2.get('metadata', {}).get('players', []))

        if not players1 or not players2:
            return 0.5

        overlap = len(players1.intersection(players2))
        total = len(players1.union(players2))

        return overlap / total if total > 0 else 0.5

    def _cluster_to_dict(self, cluster: Set[str]) -> Dict:
        """Convert cluster to dictionary with details"""
        docs = [self.db.get_document(doc_id) for doc_id in cluster]
        docs = [d for d in docs if d]  # Filter None

        # Find common themes
        all_teams = []
        all_tags = []
        for doc in docs:
            metadata = doc.get('metadata', {})
            all_teams.extend(metadata.get('teams', []))
            all_tags.extend(metadata.get('tags', []))

        return {
            'size': len(cluster),
            'doc_ids': list(cluster),
            'common_teams': [team for team, count in Counter(all_teams).most_common(3)],
            'common_tags': [tag for tag, count in Counter(all_tags).most_common(3)]
        }

    def _explain_link(self, link_type: str) -> str:
        """Explain why documents are linked"""
        explanations = {
            'same_team': "Both stories cover the same team",
            'same_player': "Both stories mention the same player",
            'same_tag': "Both stories share a topic tag",
            'same_matchup': "Both stories cover the same matchup",
            'related_game': "Stories about related games",
        }
        return explanations.get(link_type, "Related content")
