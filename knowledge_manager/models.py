"""
Data models for the knowledge management system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum


class DocumentType(Enum):
    """Types of sports documents"""
    WEEKLY_DIGEST = "weekly_digest"
    FEATURE = "feature"
    PREVIEW = "preview"
    RECAP = "recap"
    INJURY_REPORT = "injury_report"
    BETTING_INSIGHT = "betting_insight"
    PLAYER_PROFILE = "player_profile"
    TEAM_ANALYSIS = "team_analysis"
    STAT_BREAKDOWN = "stat_breakdown"


class DocumentVersion(Enum):
    """Document version stages"""
    DRAFT = "1.0"
    EDITED = "1.1"
    PUBLISHED = "2.0"
    ARCHIVED = "3.0"


class League(Enum):
    """Supported sports leagues"""
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    MLS = "mls"
    PREMIER_LEAGUE = "premier_league"
    PGA = "pga"


@dataclass
class DocumentMetadata:
    """Metadata for a sports document"""
    league: League
    date: datetime
    authors: List[str]
    tags: Set[str]
    data_timestamp: datetime
    document_type: DocumentType
    version: str = DocumentVersion.DRAFT.value
    season: Optional[str] = None
    week: Optional[int] = None
    teams: List[str] = field(default_factory=list)
    players: List[str] = field(default_factory=list)
    stats_mentioned: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert metadata to dictionary"""
        return {
            'league': self.league.value,
            'date': self.date.isoformat(),
            'authors': self.authors,
            'tags': list(self.tags),
            'data_timestamp': self.data_timestamp.isoformat(),
            'document_type': self.document_type.value,
            'version': self.version,
            'season': self.season,
            'week': self.week,
            'teams': self.teams,
            'players': self.players,
            'stats_mentioned': self.stats_mentioned,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentMetadata':
        """Create metadata from dictionary"""
        return cls(
            league=League(data['league']),
            date=datetime.fromisoformat(data['date']),
            authors=data['authors'],
            tags=set(data['tags']),
            data_timestamp=datetime.fromisoformat(data['data_timestamp']),
            document_type=DocumentType(data['document_type']),
            version=data.get('version', DocumentVersion.DRAFT.value),
            season=data.get('season'),
            week=data.get('week'),
            teams=data.get('teams', []),
            players=data.get('players', []),
            stats_mentioned=data.get('stats_mentioned', {}),
        )


@dataclass
class Document:
    """A sports content document"""
    doc_id: str
    title: str
    content: str
    metadata: DocumentMetadata
    folder_path: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    revision_count: int = 0
    linked_docs: List[str] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert document to dictionary"""
        return {
            'doc_id': self.doc_id,
            'title': self.title,
            'content': self.content,
            'metadata': self.metadata.to_dict(),
            'folder_path': self.folder_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'revision_count': self.revision_count,
            'linked_docs': self.linked_docs,
            'comments': self.comments,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Document':
        """Create document from dictionary"""
        return cls(
            doc_id=data['doc_id'],
            title=data['title'],
            content=data['content'],
            metadata=DocumentMetadata.from_dict(data['metadata']),
            folder_path=data['folder_path'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            revision_count=data.get('revision_count', 0),
            linked_docs=data.get('linked_docs', []),
            comments=data.get('comments', []),
        )


@dataclass
class FolderNode:
    """Hierarchical folder structure node"""
    path: str
    name: str
    parent_path: Optional[str] = None
    children: List[str] = field(default_factory=list)
    document_ids: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert folder to dictionary"""
        return {
            'path': self.path,
            'name': self.name,
            'parent_path': self.parent_path,
            'children': self.children,
            'document_ids': self.document_ids,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FolderNode':
        """Create folder from dictionary"""
        return cls(
            path=data['path'],
            name=data['name'],
            parent_path=data.get('parent_path'),
            children=data.get('children', []),
            document_ids=data.get('document_ids', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']),
        )


@dataclass
class Revision:
    """Document revision history entry"""
    revision_id: str
    doc_id: str
    version: str
    content: str
    metadata: Dict
    author: str
    timestamp: datetime = field(default_factory=datetime.now)
    change_summary: str = ""

    def to_dict(self) -> Dict:
        """Convert revision to dictionary"""
        return {
            'revision_id': self.revision_id,
            'doc_id': self.doc_id,
            'version': self.version,
            'content': self.content,
            'metadata': self.metadata,
            'author': self.author,
            'timestamp': self.timestamp.isoformat(),
            'change_summary': self.change_summary,
        }


@dataclass
class StoryLink:
    """Link between related stories"""
    source_doc_id: str
    target_doc_id: str
    link_type: str  # "mentions_player", "same_team", "related_game", etc.
    strength: float = 1.0  # Link strength/relevance
    auto_detected: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert link to dictionary"""
        return {
            'source_doc_id': self.source_doc_id,
            'target_doc_id': self.target_doc_id,
            'link_type': self.link_type,
            'strength': self.strength,
            'auto_detected': self.auto_detected,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class EditorTask:
    """Task for editor dashboard"""
    task_id: str
    doc_id: Optional[str]
    title: str
    description: str
    assignee: Optional[str]
    status: str  # "pending", "in_progress", "completed"
    priority: str  # "low", "medium", "high", "urgent"
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'doc_id': self.doc_id,
            'title': self.title,
            'description': self.description,
            'assignee': self.assignee,
            'status': self.status,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
