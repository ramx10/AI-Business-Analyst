from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class BasePlugin(ABC):
    """Base class for all plugins. Third-party plugins must subclass this."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable plugin name."""
        ...

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return ""

    @property
    def category(self) -> str:
        """One of: 'analysis', 'cleaning', 'visualization', 'export', 'other'."""
        return "other"

    @abstractmethod
    def run(self, df: pd.DataFrame, **kwargs) -> dict:
        """
        Execute the plugin. Must return a dict with at least:
        - 'result': transformed DataFrame or analysis result
        - 'summary': human-readable summary string
        - 'success': bool
        """
        ...
