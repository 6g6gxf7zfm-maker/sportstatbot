"""Plugin manager for loading and executing SportStatBot plugins."""
import importlib
import inspect
import os
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from .base_plugin import BasePlugin, PluginCategory, PluginPriority


class PluginManager:
    """
    Manages loading, configuration, and execution of plugins.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin manager.

        Args:
            config: Global configuration dictionary
        """
        self.plugins: Dict[str, BasePlugin] = {}
        self.config = config or {}
        self.plugin_categories: Dict[PluginCategory, List[BasePlugin]] = {
            category: [] for category in PluginCategory
        }

    def discover_plugins(self, plugin_dir: str = "plugins") -> List[str]:
        """
        Discover available plugins in the plugin directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            List of discovered plugin module paths
        """
        discovered = []
        plugin_path = Path(plugin_dir)

        if not plugin_path.exists():
            print(f"Warning: Plugin directory {plugin_dir} not found")
            return discovered

        # Scan all subdirectories for Python files
        for category_dir in ['analytics', 'predictors', 'generators', 'visualizers', 'validators', 'exporters']:
            category_path = plugin_path / category_dir

            if not category_path.exists():
                continue

            for py_file in category_path.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue

                module_path = f"{plugin_dir}.{category_dir}.{py_file.stem}"
                discovered.append(module_path)

        return discovered

    def load_plugin(self, module_path: str) -> Optional[BasePlugin]:
        """
        Load a single plugin from a module path.

        Args:
            module_path: Python module path (e.g., 'plugins.analytics.style_analyzer')

        Returns:
            Loaded plugin instance or None if loading failed
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)

            # Find all classes that inherit from BasePlugin
            plugin_classes = [
                obj for name, obj in inspect.getmembers(module, inspect.isclass)
                if issubclass(obj, BasePlugin) and obj != BasePlugin
            ]

            if not plugin_classes:
                print(f"Warning: No plugin class found in {module_path}")
                return None

            # Instantiate the first plugin class found
            plugin_class = plugin_classes[0]
            plugin = plugin_class()

            # Configure the plugin
            plugin_config = self.config.get('plugins', {}).get(plugin.name, {})
            plugin.configure(plugin_config)

            # Validate the plugin
            if not plugin.validate():
                print(f"Warning: Plugin {plugin.name} failed validation")
                return None

            print(f"Loaded plugin: {plugin}")
            return plugin

        except Exception as e:
            print(f"Error loading plugin from {module_path}: {e}")
            return None

    def load_all_plugins(self, plugin_dir: str = "plugins") -> int:
        """
        Discover and load all available plugins.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            Number of plugins successfully loaded
        """
        discovered = self.discover_plugins(plugin_dir)
        loaded_count = 0

        for module_path in discovered:
            plugin = self.load_plugin(module_path)
            if plugin:
                self.register_plugin(plugin)
                loaded_count += 1

        return loaded_count

    def register_plugin(self, plugin: BasePlugin) -> None:
        """
        Register a plugin instance.

        Args:
            plugin: Plugin instance to register
        """
        self.plugins[plugin.name] = plugin
        self.plugin_categories[plugin.category].append(plugin)

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a specific plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)

    def get_plugins_by_category(self, category: PluginCategory) -> List[BasePlugin]:
        """
        Get all plugins in a specific category.

        Args:
            category: Plugin category

        Returns:
            List of plugins in that category
        """
        return self.plugin_categories.get(category, [])

    def execute_plugin(self, plugin_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific plugin.

        Args:
            plugin_name: Name of the plugin to execute
            data: Input data for the plugin

        Returns:
            Plugin execution results
        """
        plugin = self.get_plugin(plugin_name)

        if not plugin:
            return {'error': f'Plugin {plugin_name} not found'}

        if not plugin.enabled:
            return {'status': 'skipped', 'reason': 'Plugin disabled'}

        try:
            result = plugin.execute(data)
            plugin.cleanup()
            return result
        except Exception as e:
            print(f"Error executing plugin {plugin_name}: {e}")
            return plugin.on_error(e)

    def execute_category(self, category: PluginCategory, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all enabled plugins in a category, sorted by priority.

        Args:
            category: Plugin category to execute
            data: Input data for plugins

        Returns:
            Combined results from all plugins in category
        """
        plugins = self.get_plugins_by_category(category)

        # Sort by priority (high to low)
        plugins.sort(key=lambda p: p.priority.value)

        results = {}

        for plugin in plugins:
            if not plugin.enabled:
                continue

            try:
                plugin_result = plugin.execute(data)
                results[plugin.name] = plugin_result
                plugin.cleanup()
            except Exception as e:
                print(f"Error executing plugin {plugin.name}: {e}")
                results[plugin.name] = plugin.on_error(e)

        return results

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all registered plugins.

        Returns:
            List of plugin metadata dictionaries
        """
        return [plugin.get_metadata() for plugin in self.plugins.values()]

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_name: Name of plugin to enable

        Returns:
            True if plugin was enabled successfully
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = True
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_name: Name of plugin to disable

        Returns:
            True if plugin was disabled successfully
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = False
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded plugins.

        Returns:
            Dictionary with plugin statistics
        """
        total = len(self.plugins)
        enabled = sum(1 for p in self.plugins.values() if p.enabled)

        by_category = {
            category.value: len(plugins)
            for category, plugins in self.plugin_categories.items()
        }

        return {
            'total_plugins': total,
            'enabled_plugins': enabled,
            'disabled_plugins': total - enabled,
            'by_category': by_category
        }
