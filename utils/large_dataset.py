"""
utils/large_dataset.py — Chunked processing utilities for large DataFrame handling.
"""

from typing import Callable, Optional

import pandas as pd


def estimate_memory(df: pd.DataFrame) -> float:
    """Return memory usage of the DataFrame in MB."""
    return df.memory_usage(deep=True).sum() / (1024 * 1024)


def get_chunk_size(df: pd.DataFrame, target_mb: float = 100) -> int:
    """Calculate optimal chunk size in rows based on memory footprint."""
    if len(df) == 0:
        return 10000
    mem_per_row = estimate_memory(df) / len(df)
    if mem_per_row <= 0:
        return 10000
    target_rows = int(target_mb / mem_per_row)
    return min(max(1000, target_rows), len(df))


def process_in_chunks(
    df: pd.DataFrame,
    process_func: Callable[[pd.DataFrame], pd.DataFrame],
    chunk_size: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> pd.DataFrame:
    """Process a DataFrame in chunks, returning the combined result.

    Args:
        df: Input DataFrame.
        process_func: Function that accepts a DataFrame chunk and returns a processed chunk.
        chunk_size: Number of rows per chunk. Auto-calculated if None.
        progress_callback: Optional callable(current_chunk, total_chunks).

    Returns:
        Processed DataFrame with all chunks concatenated.
    """
    if chunk_size is None:
        chunk_size = get_chunk_size(df)
    if chunk_size >= len(df):
        return process_func(df)

    chunks = []
    n_chunks = (len(df) + chunk_size - 1) // chunk_size

    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i : i + chunk_size].copy()
        result = process_func(chunk)
        chunks.append(result)
        if progress_callback:
            progress_callback(i // chunk_size + 1, n_chunks)

    combined = pd.concat(chunks, ignore_index=True)
    return combined


def get_processing_mode(df: pd.DataFrame, threshold_mb: float = 200) -> str:
    """Return 'chunked' if df memory > threshold_mb, else 'full'."""
    mem = estimate_memory(df)
    return "chunked" if mem > threshold_mb else "full"
