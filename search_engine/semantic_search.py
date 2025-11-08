"""Semantic search engine for sports reports and data."""
import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class SemanticSearchEngine:
    """
    Semantic search engine for finding relevant sports information.
    Uses embeddings to enable "Ask the Story" functionality.
    """

    def __init__(self, storage_path: str = './search_data'):
        """
        Initialize semantic search engine.

        Args:
            storage_path: Directory for storing embeddings and index
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

        # Initialize embedding model
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                # Use a lightweight model optimized for semantic search
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")

        # Initialize vector database
        self.db = None
        if CHROMADB_AVAILABLE:
            try:
                self.db = chromadb.PersistentClient(
                    path=os.path.join(storage_path, 'chroma_db')
                )
                # Get or create collection
                self.collection = self.db.get_or_create_collection(
                    name="sports_reports",
                    metadata={"description": "Sports reports and digests"}
                )
            except Exception as e:
                print(f"Warning: Could not initialize vector database: {e}")

        # Fallback to simple in-memory storage
        self.documents = []
        self.embeddings = []
        self._load_fallback_index()

    def index_report(self, report_id: str, content: str, metadata: Dict) -> bool:
        """
        Index a report for semantic search.

        Args:
            report_id: Unique identifier for the report
            content: Report text content
            metadata: Report metadata (sport, date, teams, etc.)

        Returns:
            True if successful
        """
        if not self.model:
            print("Warning: Embedding model not available")
            return False

        try:
            # Generate embedding
            embedding = self.model.encode(content, convert_to_numpy=True)

            # Store in vector database if available
            if self.db and self.collection:
                self.collection.add(
                    ids=[report_id],
                    embeddings=[embedding.tolist()],
                    documents=[content],
                    metadatas=[metadata]
                )
            else:
                # Fallback to in-memory storage
                self.documents.append({
                    'id': report_id,
                    'content': content,
                    'metadata': metadata
                })
                self.embeddings.append(embedding)
                self._save_fallback_index()

            return True

        except Exception as e:
            print(f"Error indexing report: {e}")
            return False

    def index_report_sections(self, report_id: str, sections: List[Dict]) -> bool:
        """
        Index individual sections of a report separately for better granularity.

        Args:
            report_id: Base report ID
            sections: List of section dictionaries with 'title', 'content', and metadata

        Returns:
            True if successful
        """
        success_count = 0

        for i, section in enumerate(sections):
            section_id = f"{report_id}_section_{i}"
            section_text = f"{section.get('title', '')}\n\n{section.get('content', '')}"

            metadata = section.get('metadata', {})
            metadata['report_id'] = report_id
            metadata['section_index'] = i
            metadata['section_title'] = section.get('title', '')

            if self.index_report(section_id, section_text, metadata):
                success_count += 1

        return success_count > 0

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Semantic search across indexed reports.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters (sport, date_range, etc.)

        Returns:
            List of search results with content and metadata
        """
        if not self.model:
            return self._fallback_keyword_search(query, top_k, filters)

        try:
            # Generate query embedding
            query_embedding = self.model.encode(query, convert_to_numpy=True)

            # Search in vector database if available
            if self.db and self.collection:
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=top_k,
                    where=self._build_filter_query(filters) if filters else None
                )

                return self._format_chromadb_results(results)
            else:
                # Fallback to in-memory cosine similarity
                return self._fallback_similarity_search(query_embedding, top_k, filters)

        except Exception as e:
            print(f"Error during semantic search: {e}")
            return self._fallback_keyword_search(query, top_k, filters)

    def search_by_topic(self, topic: str, top_k: int = 5) -> List[Dict]:
        """
        Search for content related to a specific topic.

        Args:
            topic: Topic to search for (e.g., "injuries", "trades", "winning streaks")
            top_k: Number of results

        Returns:
            List of relevant results
        """
        # Expand topic into a more detailed query
        topic_queries = {
            'injuries': 'injury reports, players injured, return timeline, injury updates',
            'trades': 'roster changes, trades, player acquisitions, signings',
            'streaks': 'winning streaks, losing streaks, hot teams, cold teams, momentum',
            'playoffs': 'playoff implications, playoff picture, postseason, standings',
            'performances': 'standout performances, top players, career highs, records',
        }

        query = topic_queries.get(topic.lower(), topic)
        return self.search(query, top_k)

    def find_similar_reports(self, report_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find reports similar to a given report.

        Args:
            report_id: ID of the source report
            top_k: Number of similar reports to return

        Returns:
            List of similar reports
        """
        if not self.db or not self.collection:
            return []

        try:
            # Get the source report
            source = self.collection.get(ids=[report_id])
            if not source['embeddings']:
                return []

            # Search for similar items
            results = self.collection.query(
                query_embeddings=source['embeddings'],
                n_results=top_k + 1  # +1 to exclude self
            )

            # Format and filter out the source report
            formatted = self._format_chromadb_results(results)
            return [r for r in formatted if r['id'] != report_id][:top_k]

        except Exception as e:
            print(f"Error finding similar reports: {e}")
            return []

    def _build_filter_query(self, filters: Dict) -> Dict:
        """Build ChromaDB filter query from filter dictionary."""
        where = {}

        if 'sport' in filters:
            where['sport'] = filters['sport']

        if 'team' in filters:
            where['team'] = filters['team']

        if 'date_after' in filters:
            where['date'] = {'$gte': filters['date_after'].isoformat()}

        if 'date_before' in filters:
            where['date'] = {'$lte': filters['date_before'].isoformat()}

        return where if where else None

    def _format_chromadb_results(self, results: Dict) -> List[Dict]:
        """Format ChromaDB results into standard format."""
        formatted = []

        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted

    def _fallback_similarity_search(self, query_embedding: np.ndarray, top_k: int,
                                   filters: Optional[Dict]) -> List[Dict]:
        """Fallback cosine similarity search using in-memory data."""
        if not self.embeddings:
            return []

        # Calculate cosine similarities
        embeddings_matrix = np.array(self.embeddings)
        similarities = np.dot(embeddings_matrix, query_embedding) / (
            np.linalg.norm(embeddings_matrix, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = self.documents[idx]

            # Apply filters if provided
            if filters and not self._matches_filters(doc['metadata'], filters):
                continue

            results.append({
                'id': doc['id'],
                'content': doc['content'],
                'metadata': doc['metadata'],
                'similarity': float(similarities[idx])
            })

        return results

    def _fallback_keyword_search(self, query: str, top_k: int,
                                 filters: Optional[Dict]) -> List[Dict]:
        """Simple keyword-based search fallback."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        results = []

        for doc in self.documents:
            # Apply filters
            if filters and not self._matches_filters(doc['metadata'], filters):
                continue

            # Calculate simple keyword overlap score
            content_lower = doc['content'].lower()
            content_words = set(content_lower.split())

            overlap = len(query_words & content_words)
            if overlap > 0:
                # Boost score if query is substring
                score = overlap
                if query_lower in content_lower:
                    score += 5

                results.append({
                    'id': doc['id'],
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': score
                })

        # Sort by score and return top-k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if document metadata matches filter criteria."""
        if 'sport' in filters and metadata.get('sport') != filters['sport']:
            return False

        if 'team' in filters and filters['team'] not in metadata.get('teams', []):
            return False

        if 'date_after' in filters:
            doc_date = datetime.fromisoformat(metadata.get('date', ''))
            if doc_date < filters['date_after']:
                return False

        if 'date_before' in filters:
            doc_date = datetime.fromisoformat(metadata.get('date', ''))
            if doc_date > filters['date_before']:
                return False

        return True

    def _save_fallback_index(self):
        """Save fallback index to disk."""
        index_path = os.path.join(self.storage_path, 'fallback_index.json')

        data = {
            'documents': self.documents,
            'embeddings': [emb.tolist() for emb in self.embeddings]
        }

        with open(index_path, 'w') as f:
            json.dump(data, f)

    def _load_fallback_index(self):
        """Load fallback index from disk."""
        index_path = os.path.join(self.storage_path, 'fallback_index.json')

        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    data = json.load(f)

                self.documents = data.get('documents', [])
                self.embeddings = [np.array(emb) for emb in data.get('embeddings', [])]
            except Exception as e:
                print(f"Error loading fallback index: {e}")

    def get_stats(self) -> Dict:
        """Get search engine statistics."""
        if self.db and self.collection:
            count = self.collection.count()
        else:
            count = len(self.documents)

        return {
            'total_documents': count,
            'embedding_model': 'all-MiniLM-L6-v2' if self.model else None,
            'vector_db_enabled': self.db is not None,
            'storage_path': self.storage_path
        }
