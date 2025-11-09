"""Workflow archive system with version notes for SportStatBot."""
import json
import os
import shutil
from typing import Dict, List, Optional
from datetime import datetime


class WorkflowArchive:
    """Manage archival and versioning of workflows."""

    def __init__(self, archive_dir: str = 'archive'):
        """
        Initialize workflow archive.

        Args:
            archive_dir: Directory for archived workflows
        """
        self.archive_dir = archive_dir
        os.makedirs(archive_dir, exist_ok=True)
        self.versions_file = os.path.join(archive_dir, 'versions.json')
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict:
        """Load version index."""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'workflows': {}, 'version_count': 0}
        return {'workflows': {}, 'version_count': 0}

    def _save_versions(self) -> bool:
        """Save version index."""
        try:
            with open(self.versions_file, 'w') as f:
                json.dump(self.versions, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving versions: {e}")
            return False

    def archive_workflow(
        self,
        workflow_name: str,
        workflow_data: Dict,
        version_notes: str,
        author: Optional[str] = None
    ) -> str:
        """
        Archive a workflow with version notes.

        Args:
            workflow_name: Name of the workflow
            workflow_data: Workflow configuration and data
            version_notes: Notes about this version
            author: Optional author name

        Returns:
            Version ID
        """
        # Generate version ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.versions['version_count'] += 1
        version_number = self.versions['version_count']
        version_id = f"v{version_number}_{timestamp}"

        # Initialize workflow in versions if needed
        if workflow_name not in self.versions['workflows']:
            self.versions['workflows'][workflow_name] = {
                'name': workflow_name,
                'created_at': datetime.now().isoformat(),
                'versions': [],
                'active_version': None
            }

        # Create version entry
        version_entry = {
            'version_id': version_id,
            'version_number': version_number,
            'timestamp': datetime.now().isoformat(),
            'author': author or 'system',
            'notes': version_notes,
            'archived': False
        }

        # Save workflow data
        workflow_dir = os.path.join(self.archive_dir, workflow_name)
        os.makedirs(workflow_dir, exist_ok=True)

        version_file = os.path.join(workflow_dir, f"{version_id}.json")
        with open(version_file, 'w') as f:
            json.dump({
                'version_info': version_entry,
                'workflow_data': workflow_data
            }, f, indent=2)

        # Update version index
        self.versions['workflows'][workflow_name]['versions'].append(version_entry)
        self.versions['workflows'][workflow_name]['active_version'] = version_id
        self._save_versions()

        return version_id

    def get_workflow_versions(self, workflow_name: str) -> List[Dict]:
        """
        Get all versions of a workflow.

        Args:
            workflow_name: Workflow name

        Returns:
            List of version entries
        """
        if workflow_name not in self.versions['workflows']:
            return []

        return self.versions['workflows'][workflow_name]['versions']

    def load_workflow_version(
        self,
        workflow_name: str,
        version_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Load a specific version of a workflow.

        Args:
            workflow_name: Workflow name
            version_id: Version ID (None for active version)

        Returns:
            Workflow data or None
        """
        if workflow_name not in self.versions['workflows']:
            print(f"Workflow '{workflow_name}' not found")
            return None

        # Get version ID
        if version_id is None:
            version_id = self.versions['workflows'][workflow_name]['active_version']

        if not version_id:
            print(f"No active version for workflow '{workflow_name}'")
            return None

        # Load workflow file
        version_file = os.path.join(
            self.archive_dir,
            workflow_name,
            f"{version_id}.json"
        )

        if not os.path.exists(version_file):
            print(f"Version file not found: {version_file}")
            return None

        try:
            with open(version_file, 'r') as f:
                data = json.load(f)
                return data['workflow_data']
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return None

    def set_active_version(
        self,
        workflow_name: str,
        version_id: str
    ) -> bool:
        """
        Set the active version of a workflow.

        Args:
            workflow_name: Workflow name
            version_id: Version ID to activate

        Returns:
            True if successful
        """
        if workflow_name not in self.versions['workflows']:
            print(f"Workflow '{workflow_name}' not found")
            return False

        # Verify version exists
        versions = self.get_workflow_versions(workflow_name)
        if not any(v['version_id'] == version_id for v in versions):
            print(f"Version '{version_id}' not found")
            return False

        self.versions['workflows'][workflow_name]['active_version'] = version_id
        return self._save_versions()

    def archive_old_version(
        self,
        workflow_name: str,
        version_id: str
    ) -> bool:
        """
        Mark a version as archived (no longer active).

        Args:
            workflow_name: Workflow name
            version_id: Version ID to archive

        Returns:
            True if successful
        """
        if workflow_name not in self.versions['workflows']:
            return False

        # Find and update version
        for version in self.versions['workflows'][workflow_name]['versions']:
            if version['version_id'] == version_id:
                version['archived'] = True
                return self._save_versions()

        return False

    def get_version_notes(
        self,
        workflow_name: str,
        version_id: Optional[str] = None
    ) -> str:
        """
        Get version notes for a workflow.

        Args:
            workflow_name: Workflow name
            version_id: Version ID (None for all versions)

        Returns:
            Formatted version notes
        """
        if workflow_name not in self.versions['workflows']:
            return f"Workflow '{workflow_name}' not found"

        versions = self.get_workflow_versions(workflow_name)

        if version_id:
            # Get specific version
            version = next(
                (v for v in versions if v['version_id'] == version_id),
                None
            )
            if not version:
                return f"Version '{version_id}' not found"

            output = []
            output.append(f"\nVersion: {version['version_id']}")
            output.append(f"Date: {version['timestamp'][:19]}")
            output.append(f"Author: {version['author']}")
            output.append(f"\nNotes:\n{version['notes']}")
            return "\n".join(output)
        else:
            # Get all versions
            output = []
            output.append(f"\n📚 VERSION HISTORY: {workflow_name}")
            output.append("="*70)

            for version in reversed(versions):
                status = "🗄️  ARCHIVED" if version.get('archived') else "✅ ACTIVE"
                output.append(f"\n{version['version_id']} - {status}")
                output.append(f"  Date: {version['timestamp'][:19]}")
                output.append(f"  Author: {version['author']}")
                output.append(f"  Notes: {version['notes']}")

            return "\n".join(output)

    def list_workflows(self) -> List[str]:
        """
        List all archived workflows.

        Returns:
            List of workflow names
        """
        return list(self.versions['workflows'].keys())

    def delete_workflow_version(
        self,
        workflow_name: str,
        version_id: str
    ) -> bool:
        """
        Delete a specific workflow version.

        Args:
            workflow_name: Workflow name
            version_id: Version ID to delete

        Returns:
            True if successful
        """
        if workflow_name not in self.versions['workflows']:
            return False

        # Don't delete if it's the active version
        if self.versions['workflows'][workflow_name]['active_version'] == version_id:
            print("Cannot delete active version")
            return False

        # Delete file
        version_file = os.path.join(
            self.archive_dir,
            workflow_name,
            f"{version_id}.json"
        )

        try:
            if os.path.exists(version_file):
                os.remove(version_file)

            # Remove from index
            versions = self.versions['workflows'][workflow_name]['versions']
            self.versions['workflows'][workflow_name]['versions'] = [
                v for v in versions if v['version_id'] != version_id
            ]

            return self._save_versions()
        except Exception as e:
            print(f"Error deleting version: {e}")
            return False

    def export_workflow(
        self,
        workflow_name: str,
        version_id: Optional[str] = None,
        export_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Export a workflow to a file.

        Args:
            workflow_name: Workflow name
            version_id: Version ID (None for active)
            export_path: Export file path (None for auto-generate)

        Returns:
            Export file path or None
        """
        workflow_data = self.load_workflow_version(workflow_name, version_id)
        if not workflow_data:
            return None

        if not export_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = f"exports/{workflow_name}_{timestamp}.json"

        try:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            return export_path
        except Exception as e:
            print(f"Error exporting workflow: {e}")
            return None

    def import_workflow(
        self,
        import_path: str,
        workflow_name: str,
        version_notes: str
    ) -> Optional[str]:
        """
        Import a workflow from a file.

        Args:
            import_path: Path to import file
            workflow_name: Name for imported workflow
            version_notes: Notes for this import

        Returns:
            Version ID or None
        """
        try:
            with open(import_path, 'r') as f:
                workflow_data = json.load(f)

            return self.archive_workflow(
                workflow_name=workflow_name,
                workflow_data=workflow_data,
                version_notes=version_notes,
                author='imported'
            )
        except Exception as e:
            print(f"Error importing workflow: {e}")
            return None
