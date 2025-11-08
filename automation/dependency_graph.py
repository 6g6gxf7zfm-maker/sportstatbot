"""Dependency graph builder and visualizer for workflow pipelines."""
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the dependency graph."""
    name: str
    type: str  # 'harvest', 'beat', 'copy', 'export', etc.
    dependencies: List[str]
    metadata: Dict

    def to_dict(self) -> Dict:
        """Convert node to dictionary."""
        return {
            'name': self.name,
            'type': self.type,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }


class DependencyGraph:
    """
    Build and visualize task dependency graphs.

    Features:
    - Topological sorting for execution order
    - Cycle detection
    - Visual graph generation (Mermaid, GraphViz)
    - Critical path analysis
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[Tuple[str, str]] = []

    def add_node(
        self,
        name: str,
        node_type: str,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add a node to the graph.

        Args:
            name: Node name
            node_type: Type of node (harvest, beat, copy, export)
            dependencies: List of node names this node depends on
            metadata: Additional node metadata
        """
        dependencies = dependencies or []
        node = GraphNode(
            name=name,
            type=node_type,
            dependencies=dependencies,
            metadata=metadata or {}
        )

        self.nodes[name] = node

        # Add edges for dependencies
        for dep in dependencies:
            self.edges.append((dep, name))

        logger.info(f"Added node: {name} (type: {node_type}, dependencies: {dependencies})")

    def get_topological_order(self) -> List[str]:
        """
        Get topological sort of the graph (execution order).

        Returns:
            List of node names in execution order

        Raises:
            ValueError: If graph contains cycles
        """
        # Detect cycles first
        if self.has_cycles():
            raise ValueError("Graph contains cycles, cannot create topological order")

        visited = set()
        order = []

        def visit(node_name: str):
            if node_name in visited:
                return

            node = self.nodes.get(node_name)
            if not node:
                return

            # Visit dependencies first
            for dep in node.dependencies:
                visit(dep)

            visited.add(node_name)
            order.append(node_name)

        # Visit all nodes
        for node_name in self.nodes:
            visit(node_name)

        return order

    def has_cycles(self) -> bool:
        """
        Check if the graph contains cycles.

        Returns:
            True if cycles exist, False otherwise
        """
        visited = set()
        rec_stack = set()

        def visit(node_name: str) -> bool:
            visited.add(node_name)
            rec_stack.add(node_name)

            node = self.nodes.get(node_name)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if visit(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(node_name)
            return False

        for node_name in self.nodes:
            if node_name not in visited:
                if visit(node_name):
                    return True

        return False

    def get_levels(self) -> Dict[int, List[str]]:
        """
        Get nodes grouped by execution level (for parallel execution).

        Returns:
            Dictionary mapping level number to list of node names
        """
        levels = {}
        node_levels = {}

        def get_level(node_name: str) -> int:
            if node_name in node_levels:
                return node_levels[node_name]

            node = self.nodes.get(node_name)
            if not node or not node.dependencies:
                node_levels[node_name] = 0
                return 0

            # Level is max of dependency levels + 1
            max_dep_level = max(get_level(dep) for dep in node.dependencies)
            level = max_dep_level + 1
            node_levels[node_name] = level
            return level

        # Calculate levels for all nodes
        for node_name in self.nodes:
            level = get_level(node_name)
            if level not in levels:
                levels[level] = []
            levels[level].append(node_name)

        return levels

    def get_critical_path(self) -> List[str]:
        """
        Find the critical path (longest path) through the graph.

        Returns:
            List of node names representing the critical path
        """
        # Calculate longest path to each node
        distances = {name: 0 for name in self.nodes}
        predecessors = {name: None for name in self.nodes}

        for node_name in self.get_topological_order():
            node = self.nodes[node_name]

            for dep in node.dependencies:
                if distances[dep] + 1 > distances[node_name]:
                    distances[node_name] = distances[dep] + 1
                    predecessors[node_name] = dep

        # Find node with maximum distance
        max_node = max(distances, key=distances.get)

        # Reconstruct path
        path = []
        current = max_node
        while current is not None:
            path.append(current)
            current = predecessors[current]

        path.reverse()
        return path

    def to_mermaid(self) -> str:
        """
        Generate Mermaid diagram syntax for visualization.

        Returns:
            Mermaid diagram as string
        """
        lines = ["graph TD"]

        # Add nodes with styling based on type
        node_styles = {
            'harvest': '([{name}])',
            'beat': '[{name}]',
            'copy': '{{{{name}}}}',
            'export': '({name})'
        }

        for name, node in self.nodes.items():
            style = node_styles.get(node.type, '[{name}]')
            lines.append(f"    {name}{style.format(name=name)}")

        # Add edges
        for source, target in self.edges:
            lines.append(f"    {source} --> {target}")

        # Add styling
        lines.append("")
        lines.append("    classDef harvest fill:#e1f5e1,stroke:#4caf50")
        lines.append("    classDef beat fill:#e3f2fd,stroke:#2196f3")
        lines.append("    classDef copy fill:#fff3e0,stroke:#ff9800")
        lines.append("    classDef export fill:#f3e5f5,stroke:#9c27b0")

        for name, node in self.nodes.items():
            lines.append(f"    class {name} {node.type}")

        return "\n".join(lines)

    def to_graphviz(self) -> str:
        """
        Generate GraphViz DOT syntax for visualization.

        Returns:
            DOT diagram as string
        """
        lines = ["digraph DependencyGraph {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box, style=rounded];")

        # Node colors by type
        colors = {
            'harvest': '#e1f5e1',
            'beat': '#e3f2fd',
            'copy': '#fff3e0',
            'export': '#f3e5f5'
        }

        # Add nodes
        for name, node in self.nodes.items():
            color = colors.get(node.type, '#ffffff')
            lines.append(f'    "{name}" [fillcolor="{color}", style="filled,rounded"];')

        # Add edges
        for source, target in self.edges:
            lines.append(f'    "{source}" -> "{target}";')

        lines.append("}")
        return "\n".join(lines)

    def to_ascii(self) -> str:
        """
        Generate simple ASCII visualization.

        Returns:
            ASCII diagram as string
        """
        levels = self.get_levels()
        lines = []

        lines.append("Pipeline Flow:")
        lines.append("=" * 60)

        for level in sorted(levels.keys()):
            nodes = levels[level]
            level_str = f"Level {level}: "

            node_strs = []
            for node_name in nodes:
                node = self.nodes[node_name]
                node_strs.append(f"{node_name} ({node.type})")

            lines.append(level_str + " | ".join(node_strs))

            # Add arrows to next level
            if level < max(levels.keys()):
                lines.append("    ↓")

        lines.append("=" * 60)

        # Add critical path
        critical_path = self.get_critical_path()
        lines.append(f"\nCritical Path: {' → '.join(critical_path)}")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """
        Convert graph to dictionary for serialization.

        Returns:
            Dictionary representation of graph
        """
        return {
            'nodes': {name: node.to_dict() for name, node in self.nodes.items()},
            'edges': self.edges,
            'execution_order': self.get_topological_order(),
            'levels': self.get_levels(),
            'critical_path': self.get_critical_path()
        }

    def to_json(self) -> str:
        """
        Convert graph to JSON.

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_workflow(cls, workflow) -> 'DependencyGraph':
        """
        Create dependency graph from a Workflow object.

        Args:
            workflow: Workflow instance

        Returns:
            DependencyGraph instance
        """
        graph = cls()

        for step_name, step in workflow.steps.items():
            graph.add_node(
                name=step_name,
                node_type=step.metadata.get('type', 'step'),
                dependencies=step.dependencies,
                metadata=step.metadata
            )

        return graph
