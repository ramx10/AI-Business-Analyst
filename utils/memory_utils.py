"""
utils/memory_utils.py — Memory monitoring utilities for process-level tracking.
"""

import os


def log_memory_usage(label: str = "") -> str:
    """Log current RSS memory usage of the process in MB.

    Returns a formatted string like: "[my label] RSS: 123.4 MB"
    Returns a fallback message if psutil is not available.
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)
        prefix = f"[{label}] " if label else ""
        return f"{prefix}RSS: {mem:.1f} MB"
    except ImportError:
        return f"[{label}] psutil not available" if label else "psutil not available"
