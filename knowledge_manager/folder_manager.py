"""
Folder Manager - Hierarchical folder organization system
Implements Google Drive-style folder structure for sports content
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path

from .models import FolderNode
from .database_handler import DatabaseHandler


class FolderManager:
    """Manages hierarchical folder structure for sports content"""

    def __init__(self, db_path: str = "knowledge_manager/database/sports_knowledge.db"):
        self.db = DatabaseHandler(db_path)
        self._ensure_root_folders()

    def _ensure_root_folders(self):
        """Ensure standard root folders exist"""
        root_structure = {
            "/NFL": ["Weekly Digests", "Features", "Betting Insights", "Injuries"],
            "/NBA": ["Weekly Digests", "Features", "Betting Insights", "Injuries"],
            "/MLB": ["Weekly Digests", "Features", "Betting Insights", "Injuries"],
            "/NHL": ["Weekly Digests", "Features", "Betting Insights", "Injuries"],
            "/MLS": ["Weekly Digests", "Features", "Betting Insights", "Injuries"],
            "/Soccer": ["Premier League", "International", "Features"],
            "/Golf": ["PGA Tour", "Features"],
        }

        for root, subfolders in root_structure.items():
            self.create_folder(root, root.lstrip('/'))
            for subfolder in subfolders:
                self.create_folder(f"{root}/{subfolder}", subfolder, parent_path=root)

    def create_folder(
        self,
        path: str,
        name: str,
        parent_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> FolderNode:
        """Create a new folder"""
        # Check if folder already exists
        existing = self.db.get_folder(path)
        if existing:
            return FolderNode.from_dict(existing)

        folder = FolderNode(
            path=path,
            name=name,
            parent_path=parent_path,
            metadata=metadata or {},
            created_at=datetime.now()
        )

        self.db.save_folder(folder.to_dict())

        # Update parent's children list
        if parent_path:
            parent = self.db.get_folder(parent_path)
            if parent:
                children = parent.get('children', [])
                if path not in children:
                    children.append(path)
                    parent['children'] = children
                    self.db.save_folder(parent)

        return folder

    def get_folder(self, path: str) -> Optional[FolderNode]:
        """Get a folder by path"""
        data = self.db.get_folder(path)
        if data:
            return FolderNode.from_dict(data)
        return None

    def add_document_to_folder(self, folder_path: str, doc_id: str) -> bool:
        """Add a document to a folder"""
        folder_data = self.db.get_folder(folder_path)
        if not folder_data:
            return False

        doc_ids = folder_data.get('document_ids', [])
        if doc_id not in doc_ids:
            doc_ids.append(doc_id)
            folder_data['document_ids'] = doc_ids
            self.db.save_folder(folder_data)

        return True

    def remove_document_from_folder(self, folder_path: str, doc_id: str) -> bool:
        """Remove a document from a folder"""
        folder_data = self.db.get_folder(folder_path)
        if not folder_data:
            return False

        doc_ids = folder_data.get('document_ids', [])
        if doc_id in doc_ids:
            doc_ids.remove(doc_id)
            folder_data['document_ids'] = doc_ids
            self.db.save_folder(folder_data)
            return True

        return False

    def list_folder_contents(self, path: str) -> Dict:
        """List all contents of a folder (subfolders and documents)"""
        folder = self.get_folder(path)
        if not folder:
            return {'folders': [], 'documents': []}

        subfolders = []
        for child_path in folder.children:
            child = self.get_folder(child_path)
            if child:
                subfolders.append({
                    'path': child.path,
                    'name': child.name,
                    'doc_count': len(child.document_ids)
                })

        return {
            'folders': subfolders,
            'documents': folder.document_ids
        }

    def get_folder_tree(self, root_path: str = "/", max_depth: int = 3) -> Dict:
        """Get hierarchical tree structure"""
        def build_tree(path: str, current_depth: int = 0) -> Optional[Dict]:
            if current_depth > max_depth:
                return None

            folder = self.get_folder(path)
            if not folder:
                return None

            tree = {
                'path': folder.path,
                'name': folder.name,
                'doc_count': len(folder.document_ids),
                'children': []
            }

            for child_path in folder.children:
                child_tree = build_tree(child_path, current_depth + 1)
                if child_tree:
                    tree['children'].append(child_tree)

            return tree

        return build_tree(root_path) or {}

    def create_date_folder(
        self,
        base_path: str,
        date: datetime,
        format: str = "YYYY-MM-DD"
    ) -> FolderNode:
        """Create a date-based folder (e.g., /NFL/Weekly Digests/2025-11-08)"""
        date_str = date.strftime("%Y-%m-%d")
        folder_path = f"{base_path}/{date_str}"
        folder_name = date_str

        return self.create_folder(folder_path, folder_name, parent_path=base_path)

    def create_player_folder(
        self,
        league_path: str,
        player_name: str
    ) -> FolderNode:
        """Create a player-specific folder (e.g., /NBA/Features/Stars/LeBron)"""
        features_path = f"{league_path}/Features"
        stars_path = f"{features_path}/Stars"

        # Ensure parent folders exist
        self.create_folder(features_path, "Features", parent_path=league_path)
        self.create_folder(stars_path, "Stars", parent_path=features_path)

        # Create player folder
        player_path = f"{stars_path}/{player_name}"
        return self.create_folder(player_path, player_name, parent_path=stars_path)

    def search_folders(self, query: str) -> List[Dict]:
        """Search for folders by name or path"""
        # Simple implementation - could be enhanced
        all_folders = []
        roots = ["/NFL", "/NBA", "/MLB", "/NHL", "/MLS", "/Soccer", "/Golf"]

        for root in roots:
            tree = self.get_folder_tree(root, max_depth=10)
            if tree:
                all_folders.extend(self._flatten_tree(tree, query))

        return all_folders

    def _flatten_tree(self, tree: Dict, query: str = "") -> List[Dict]:
        """Flatten folder tree and filter by query"""
        results = []

        if not query or query.lower() in tree['name'].lower() or query.lower() in tree['path'].lower():
            results.append({
                'path': tree['path'],
                'name': tree['name'],
                'doc_count': tree['doc_count']
            })

        for child in tree.get('children', []):
            results.extend(self._flatten_tree(child, query))

        return results

    def get_recent_folders(self, limit: int = 10) -> List[Dict]:
        """Get most recently created folders"""
        # This would require a more sophisticated query
        # For now, return a simple implementation
        roots = ["/NFL", "/NBA", "/MLB", "/NHL", "/MLS", "/Soccer", "/Golf"]
        folders = []

        for root in roots:
            tree = self.get_folder_tree(root, max_depth=2)
            if tree:
                folders.extend(self._flatten_tree(tree))

        return folders[:limit]
