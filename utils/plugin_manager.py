import importlib
import inspect
import os
import sys
from typing import Dict, List, Optional

from utils.plugin_base import BasePlugin

PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))


class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Scan plugin directory and load all plugins."""
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        if PLUGIN_DIR not in sys.path:
            sys.path.insert(0, PLUGIN_DIR)
        self._plugins = {}
        for fname in os.listdir(PLUGIN_DIR):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            mod_name = fname[:-3]
            try:
                mod = importlib.import_module(mod_name)
                for name, obj in inspect.getmembers(mod):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BasePlugin)
                        and obj is not BasePlugin
                        and not inspect.isabstract(obj)
                    ):
                        instance = obj()
                        self._plugins[instance.name] = instance
            except Exception:
                import traceback

                traceback.print_exc()

    def reload(self):
        """Reload all plugins from disk."""
        self._plugins = {}
        # Remove cached modules so they get re-imported
        for mod_name in list(sys.modules.keys()):
            if mod_name not in ("utils.plugin_base",) and hasattr(
                sys.modules[mod_name], "__file__"
            ):
                fpath = getattr(sys.modules[mod_name], "__file__", "")
                if fpath and fpath.startswith(PLUGIN_DIR):
                    del sys.modules[mod_name]
        self._load_plugins()

    def get_plugins(self) -> List[dict]:
        """Return list of registered plugin metadata."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "category": p.category,
            }
            for p in self._plugins.values()
        ]

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def run_plugin(self, name: str, df, **kwargs) -> dict:
        plugin = self.get_plugin(name)
        if not plugin:
            return {"success": False, "error": f"Plugin '{name}' not found"}
        try:
            return plugin.run(df, **kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}


_manager = None


def get_plugin_manager() -> PluginManager:
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager
