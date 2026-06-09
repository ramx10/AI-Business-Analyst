import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np

from utils.progress import ProgressTracker, get_progress, set_progress, clear_progress
from utils.large_dataset import (
    estimate_memory,
    get_chunk_size,
    process_in_chunks,
    get_processing_mode,
)


class TestEstimateMemory:
    def test_returns_float_greater_than_zero(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
        mem = estimate_memory(df)
        assert isinstance(mem, float)
        assert mem > 0

    def test_larger_df_uses_more_memory(self):
        small = pd.DataFrame({"a": range(10)})
        large = pd.DataFrame({"a": range(1000)})
        assert estimate_memory(large) > estimate_memory(small)


class TestGetChunkSize:
    def test_returns_positive_int(self):
        df = pd.DataFrame({"a": range(1000), "b": ["x"] * 1000})
        size = get_chunk_size(df)
        assert isinstance(size, int)
        assert size > 0

    def test_does_not_exceed_row_count(self):
        df = pd.DataFrame({"a": range(50)})
        size = get_chunk_size(df)
        assert size <= len(df)

    def test_empty_df_returns_default(self):
        df = pd.DataFrame({"a": []})
        size = get_chunk_size(df)
        assert size == 10000


class TestProcessInChunks:
    def test_produces_same_result_as_normal_processing(self):
        df = pd.DataFrame({"value": [3, 1, 2, np.nan, 5, np.nan]})

        def fill_constant(chunk):
            return chunk.fillna(0)

        # Normal
        normal_result = fill_constant(df)

        # Chunked
        chunked_result = process_in_chunks(df, fill_constant, chunk_size=2)

        pd.testing.assert_frame_equal(normal_result, chunked_result)

    def test_works_with_single_chunk(self):
        df = pd.DataFrame({"a": [1, 2, 3]})

        def identity(x):
            return x

        result = process_in_chunks(df, identity, chunk_size=100)
        pd.testing.assert_frame_equal(df, result)

    def test_preserves_row_count(self):
        df = pd.DataFrame({"a": range(100)})

        def identity(x):
            return x

        result = process_in_chunks(df, identity, chunk_size=30)
        assert len(result) == len(df)

    def test_calls_progress_callback(self):
        df = pd.DataFrame({"a": range(100)})
        calls = []

        def identity(x):
            return x

        def callback(current, total):
            calls.append((current, total))

        process_in_chunks(df, identity, chunk_size=30, progress_callback=callback)
        assert len(calls) > 0
        assert calls[-1][0] == calls[-1][1]  # last call has current == total


class TestGetProcessingMode:
    def test_returns_chunked_with_very_low_threshold(self):
        df = pd.DataFrame({"a": range(10), "b": range(10)})
        mode = get_processing_mode(df, threshold_mb=0.00001)
        assert mode == "chunked"

    def test_returns_chunked_for_large_dataframe(self):
        df = pd.DataFrame({"a": range(10), "b": range(10)})
        mode = get_processing_mode(df, threshold_mb=1000)
        assert mode == "full"


class TestProgressTracker:
    def test_tracks_steps_correctly(self):
        tracker = ProgressTracker(total_steps=5, description="Test")
        assert tracker.get_status()["current"] == 0
        assert tracker.get_status()["percent"] == 0.0

        tracker.step()
        assert tracker.current == 1
        assert tracker.get_status()["percent"] == 20.0

        tracker.step(2)
        assert tracker.current == 3
        assert tracker.get_status()["percent"] == 60.0

        tracker.step(2)
        assert tracker.current == 5
        assert tracker.get_status()["percent"] == 100.0

    def test_total_steps_zero_returns_zero_percent(self):
        tracker = ProgressTracker(total_steps=0)
        assert tracker.get_status()["percent"] == 0

    def test_step_with_detail_updates_description(self):
        tracker = ProgressTracker(total_steps=3)
        tracker.step(1, "Processing chunk 1 of 3")
        assert "chunk 1" in tracker.description

    def test_global_store_functions(self):
        clear_progress("test_sid")
        assert get_progress("test_sid") is None

        tracker = ProgressTracker(10)
        set_progress("test_sid", tracker)
        assert get_progress("test_sid") is tracker

        clear_progress("test_sid")
        assert get_progress("test_sid") is None

    def test_get_status_returns_correct_keys(self):
        tracker = ProgressTracker(5, "Testing")
        tracker.result = {"key": "val"}
        tracker.error = None
        status = tracker.get_status()
        assert set(status.keys()) == {"current", "total", "percent", "description", "result", "error"}
        assert status["result"] == {"key": "val"}
