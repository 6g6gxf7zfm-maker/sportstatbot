"""Base plugin class for SportStatBot extensions."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class PluginCategory(Enum):
    """Categories for plugin classification."""
    ANALYTICS = "analytics"
    PREDICTOR = "predictor"
    GENERATOR = "generator"
    VISUALIZER = "visualizer"
    VALIDATOR = "validator"
    EXPORTER = "exporter"


class PluginPriority(Enum):
    """Priority levels for plugin execution."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class BasePlugin(ABC):
    """
    Abstract base class for all SportStatBot plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self):
        """Initialize the plugin."""
        self.enabled = True
        self.config = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what the plugin does."""
        pass

    @property
    @abstractmethod
    def category(self) -> PluginCategory:
        """Return the plugin category."""
        pass

    @property
    def priority(self) -> PluginPriority:
        """Return the plugin priority (default: MEDIUM)."""
        return PluginPriority.MEDIUM

    @property
    def dependencies(self) -> List[str]:
        """
        Return list of required plugin names that must be loaded first.
        Override if plugin has dependencies.
        """
        return []

    @property
    def required_data_sources(self) -> List[str]:
        """
        Return list of required data sources (APIs, etc.).
        Override if plugin requires specific data sources.
        """
        return []

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with custom settings.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.enabled = config.get('enabled', True)

    def validate(self) -> bool:
        """
        Validate that the plugin can run properly.
        Override to add custom validation logic.

        Returns:
            True if plugin is properly configured and can run
        """
        return self.enabled

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin's main functionality.

        Args:
            data: Input data dictionary containing:
                - sport: Sport key (nfl, nba, etc.)
                - sport_data: Current sport data
                - scoreboard: Recent games data
                - standings: Current standings
                - news: Recent news articles
                - Any other relevant data

        Returns:
            Dictionary with plugin results to be merged into sport data
        """
        pass

    def on_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors during plugin execution.
        Override to add custom error handling.

        Args:
            error: The exception that occurred

        Returns:
            Dictionary with error information or fallback data
        """
        return {
            'error': str(error),
            'plugin': self.name,
            'status': 'failed'
        }

    def cleanup(self) -> None:
        """
        Clean up resources after plugin execution.
        Override if plugin needs cleanup.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata for documentation and debugging.

        Returns:
            Dictionary with plugin information
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority.value,
            'enabled': self.enabled,
            'dependencies': self.dependencies,
            'required_data_sources': self.required_data_sources
        }

    def __str__(self) -> str:
        """String representation of the plugin."""
        return f"{self.name} v{self.version} ({self.category.value})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Plugin: {self.name} v{self.version} category={self.category.value} enabled={self.enabled}>"
