"""
Document Manager - CRUD operations for sports content documents
"""

import uuid
import re
from datetime import datetime
from typing import List, Optional, Dict, Set
from pathlib import Path

from .models import (
    Document, DocumentMetadata, DocumentType, DocumentVersion,
    League, Revision
)
from .database_handler import DatabaseHandler


class DocumentManager:
    """Manages sports content documents"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db",
                 storage_path: str = "knowledge_manager/storage"):
        self.db = DatabaseHandler(db_path)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_document(
        self,
        title: str,
        content: str,
        league: League,
        document_type: DocumentType,
        folder_path: str,
        authors: List[str],
        tags: Set[str] = None,
        season: Optional[str] = None,
        week: Optional[int] = None
    ) -> Document:
        """Create a new document"""
        doc_id = str(uuid.uuid4())
        now = datetime.now()

        # Extract entities from content
        teams = self._extract_teams(content, league)
        players = self._extract_players(content)
        stats_mentioned = self._extract_stats(content)

        metadata = DocumentMetadata(
            league=league,
            date=now,
            authors=authors,
            tags=tags or set(),
            data_timestamp=now,
            document_type=document_type,
            version=DocumentVersion.DRAFT.value,
            season=season,
            week=week,
            teams=teams,
            players=players,
            stats_mentioned=stats_mentioned
        )

        doc = Document(
            doc_id=doc_id,
            title=title,
            content=content,
            metadata=metadata,
            folder_path=folder_path,
            created_at=now,
            updated_at=now
        )

        # Save to database
        self.db.save_document(doc.to_dict())

        # Add tags
        for tag in (tags or set()):
            self.db.add_tag(doc_id, tag)

        # Index mentions
        self._index_mentions(doc)

        # Index stats
        self._index_stats(doc)

        # Save content to file
        self._save_content_file(doc)

        return doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        data = self.db.get_document(doc_id)
        if data:
            return Document.from_dict(data)
        return None

    def update_document(
        self,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        version: Optional[str] = None,
        author: str = "system"
    ) -> Optional[Document]:
        """Update an existing document"""
        doc = self.get_document(doc_id)
        if not doc:
            return None

        # Create revision before updating
        self._create_revision(doc, author)

        # Update fields
        if title:
            doc.title = title
        if content:
            doc.content = content
            # Re-extract entities and stats
            doc.metadata.teams = self._extract_teams(content, doc.metadata.league)
            doc.metadata.players = self._extract_players(content)
            doc.metadata.stats_mentioned = self._extract_stats(content)
        if tags:
            doc.metadata.tags = tags
            # Update tag associations
            for tag in tags:
                self.db.add_tag(doc_id, tag)
        if version:
            doc.metadata.version = version

        doc.updated_at = datetime.now()
        doc.revision_count += 1

        # Save updates
        self.db.save_document(doc.to_dict())
        self._save_content_file(doc)

        # Re-index if content changed
        if content:
            self._index_mentions(doc)
            self._index_stats(doc)

        return doc

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        doc = self.get_document(doc_id)
        if not doc:
            return False

        # Delete from database
        self.db.delete_document(doc_id)

        # Delete content file
        file_path = self._get_content_file_path(doc_id)
        if file_path.exists():
            file_path.unlink()

        return True

    def list_documents(
        self,
        folder_path: Optional[str] = None,
        league: Optional[League] = None,
        document_type: Optional[DocumentType] = None,
        tags: Optional[Set[str]] = None,
        limit: int = 100
    ) -> List[Document]:
        """List documents with filters"""
        # TODO: Implement more sophisticated filtering
        # For now, do basic search
        query = ""
        if folder_path:
            # Get documents in this folder
            folder_data = self.db.get_folder(folder_path)
            if folder_data:
                doc_ids = folder_data.get('document_ids', [])
                return [self.get_document(doc_id) for doc_id in doc_ids
                       if self.get_document(doc_id)]
        return []

    def publish_document(self, doc_id: str, author: str = "system") -> Optional[Document]:
        """Publish a document (change version to Published)"""
        return self.update_document(
            doc_id,
            version=DocumentVersion.PUBLISHED.value,
            author=author
        )

    def archive_document(self, doc_id: str, author: str = "system") -> Optional[Document]:
        """Archive a document"""
        return self.update_document(
            doc_id,
            version=DocumentVersion.ARCHIVED.value,
            author=author
        )

    def add_comment(self, doc_id: str, author: str, comment: str) -> bool:
        """Add a comment to a document"""
        doc = self.get_document(doc_id)
        if not doc:
            return False

        doc.comments.append({
            'author': author,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        })

        self.db.save_document(doc.to_dict())
        return True

    def get_revisions(self, doc_id: str) -> List[Revision]:
        """Get revision history for a document"""
        revisions_data = self.db.get_revisions(doc_id)
        return [self._dict_to_revision(data) for data in revisions_data]

    def _create_revision(self, doc: Document, author: str, change_summary: str = ""):
        """Create a revision snapshot"""
        revision = Revision(
            revision_id=str(uuid.uuid4()),
            doc_id=doc.doc_id,
            version=doc.metadata.version,
            content=doc.content,
            metadata=doc.metadata.to_dict(),
            author=author,
            timestamp=datetime.now(),
            change_summary=change_summary
        )
        self.db.save_revision(revision.to_dict())

    def _save_content_file(self, doc: Document):
        """Save document content to file"""
        file_path = self._get_content_file_path(doc.doc_id)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create header with metadata
        header = self._generate_header(doc)
        full_content = f"{header}\n\n{doc.content}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

    def _get_content_file_path(self, doc_id: str) -> Path:
        """Get file path for document content"""
        return self.storage_path / f"{doc_id}.md"

    def _generate_header(self, doc: Document) -> str:
        """Generate metadata header for document"""
        metadata = doc.metadata
        header = f"""---
# Document Metadata
League: {metadata.league.value.upper()}
Date: {metadata.date.strftime('%Y-%m-%d')}
Authors: {', '.join(metadata.authors)}
Tags: {', '.join(f'#{tag}' for tag in metadata.tags)}
Type: {metadata.document_type.value}
Version: {metadata.version}
Data Timestamp: {metadata.data_timestamp.isoformat()}
{'Season: ' + metadata.season if metadata.season else ''}
{'Week: ' + str(metadata.week) if metadata.week else ''}
---"""
        return header

    def _extract_teams(self, content: str, league: League) -> List[str]:
        """Extract team names from content"""
        # Common team name patterns
        teams = set()

        # NFL teams
        nfl_teams = [
            "Chiefs", "Bills", "49ers", "Eagles", "Cowboys", "Giants", "Patriots",
            "Packers", "Steelers", "Ravens", "Browns", "Bengals", "Dolphins",
            "Jets", "Colts", "Texans", "Titans", "Jaguars", "Broncos", "Raiders",
            "Chargers", "Rams", "Cardinals", "Seahawks", "Vikings", "Bears",
            "Lions", "Saints", "Buccaneers", "Panthers", "Falcons", "Commanders"
        ]

        # NBA teams
        nba_teams = [
            "Lakers", "Celtics", "Warriors", "Nets", "Bucks", "Suns", "Heat",
            "76ers", "Nuggets", "Clippers", "Mavericks", "Knicks", "Bulls",
            "Cavaliers", "Raptors", "Grizzlies", "Hawks", "Timberwolves",
            "Pelicans", "Kings", "Trail Blazers", "Jazz", "Thunder", "Spurs",
            "Magic", "Wizards", "Hornets", "Pistons", "Pacers", "Rockets"
        ]

        # Use appropriate list based on league
        team_list = []
        if league == League.NFL:
            team_list = nfl_teams
        elif league == League.NBA:
            team_list = nba_teams

        for team in team_list:
            if re.search(r'\b' + team + r'\b', content, re.IGNORECASE):
                teams.add(team)

        return sorted(list(teams))

    def _extract_players(self, content: str) -> List[str]:
        """Extract player names from content"""
        # Look for patterns like "FirstName LastName" or "F. LastName"
        # This is a simplified version - could be enhanced with NER
        players = set()

        # Pattern for names (capitalized words)
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        matches = re.findall(pattern, content)

        # Filter out common false positives
        exclude = {'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where'}
        for match in matches:
            if not any(word in match for word in exclude):
                players.add(match)

        return sorted(list(players))[:20]  # Limit to top 20

    def _extract_stats(self, content: str) -> Dict[str, float]:
        """Extract statistical mentions from content"""
        stats = {}

        # Common stat patterns
        patterns = {
            'points': r'(\d+(?:\.\d+)?)\s*(?:points?|pts)',
            'yards': r'(\d+)\s*(?:yards?|yds)',
            'touchdowns': r'(\d+)\s*(?:touchdowns?|TDs?)',
            'assists': r'(\d+)\s*(?:assists?)',
            'rebounds': r'(\d+)\s*(?:rebounds?)',
            'goals': r'(\d+)\s*(?:goals?)',
            'xG': r'xG[:\s]*(\d+(?:\.\d+)?)',
            'EPA': r'EPA[/\s]*play[:\s]*(-?\d+(?:\.\d+)?)',
        }

        for stat_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Take the maximum value found
                values = [float(m) if isinstance(m, str) else float(m) for m in matches]
                stats[stat_name] = max(values)

        return stats

    def _index_mentions(self, doc: Document):
        """Index entity mentions for quick recall"""
        # Index teams
        for team in doc.metadata.teams:
            self.db.add_mention(
                doc.doc_id,
                entity_type="team",
                entity_name=team,
                context=doc.title
            )

        # Index players
        for player in doc.metadata.players:
            self.db.add_mention(
                doc.doc_id,
                entity_type="player",
                entity_name=player,
                context=doc.title
            )

    def _index_stats(self, doc: Document):
        """Index statistical mentions"""
        for stat_name, stat_value in doc.metadata.stats_mentioned.items():
            self.db.add_stat_mention(
                doc.doc_id,
                stat_name=stat_name,
                stat_value=stat_value,
                context=doc.title
            )

    def _dict_to_revision(self, data: Dict) -> Revision:
        """Convert dictionary to Revision object"""
        return Revision(
            revision_id=data['revision_id'],
            doc_id=data['doc_id'],
            version=data['version'],
            content=data['content'],
            metadata=data['metadata'],
            author=data['author'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            change_summary=data.get('change_summary', '')
        )
