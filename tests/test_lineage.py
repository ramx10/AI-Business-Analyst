import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.lineage import LineageTracker, LineageStep, LINEAGE_DIR


class TestLineageTracker:
    def setup_method(self):
        self.session_id = "test_session_001"
        self.tracker = LineageTracker(self.session_id)

    def teardown_method(self):
        path = self.tracker._get_path()
        if os.path.exists(path):
            os.remove(path)

    def test_starts_empty(self):
        assert self.tracker.get_steps() == []

    def test_add_step_persists_and_retrieves(self):
        step = LineageStep(
            step_id="clean_1",
            step_name="Correct Data Types",
            category="clean",
            description="Converted 2 columns",
            affected_columns=["price", "date"],
            rows_before=100,
            rows_after=100,
            columns_before=5,
            columns_after=5,
            duration_ms=150,
            timestamp="2026-06-09T10:30:00",
        )
        self.tracker.add_step(step)
        steps = self.tracker.get_steps()
        assert len(steps) == 1
        assert steps[0].step_id == "clean_1"
        assert steps[0].rows_before == 100
        assert steps[0].rows_after == 100
        assert steps[0].affected_columns == ["price", "date"]

    def test_multiple_steps(self):
        s1 = LineageStep(step_id="upload", step_name="Upload", category="upload", description="Uploaded file")
        s2 = LineageStep(step_id="clean_1", step_name="Clean", category="clean", description="Cleaned data")
        self.tracker.add_step(s1)
        self.tracker.add_step(s2)
        assert len(self.tracker.get_steps()) == 2

    def test_multiple_sessions_dont_interfere(self):
        tracker_a = LineageTracker("session_a")
        tracker_b = LineageTracker("session_b")
        step_a = LineageStep(step_id="s1", step_name="A", category="upload", description="Step A")
        step_b = LineageStep(step_id="s2", step_name="B", category="upload", description="Step B")
        tracker_a.add_step(step_a)
        tracker_b.add_step(step_b)
        assert len(tracker_a.get_steps()) == 1
        assert len(tracker_b.get_steps()) == 1
        assert tracker_a.get_steps()[0].step_id == "s1"
        assert tracker_b.get_steps()[0].step_id == "s2"
        path_a = tracker_a._get_path()
        path_b = tracker_b._get_path()
        if os.path.exists(path_a):
            os.remove(path_a)
        if os.path.exists(path_b):
            os.remove(path_b)

    def test_clear_removes_all_steps(self):
        step = LineageStep(step_id="s1", step_name="Test", category="clean", description="Test")
        self.tracker.add_step(step)
        assert len(self.tracker.get_steps()) == 1
        self.tracker.clear()
        assert self.tracker.get_steps() == []

    def test_lineage_step_dataclass_fields(self):
        step = LineageStep(
            step_id="clean_3",
            step_name="Remove Duplicate Records",
            category="clean",
            description="Removed 12 duplicate rows",
            affected_columns=["*"],
            rows_before=2823,
            rows_after=2811,
            columns_before=9,
            columns_after=9,
            duration_ms=150,
            timestamp="2026-06-09T10:30:00",
        )
        assert step.step_id == "clean_3"
        assert step.step_name == "Remove Duplicate Records"
        assert step.category == "clean"
        assert step.description == "Removed 12 duplicate rows"
        assert step.affected_columns == ["*"]
        assert step.rows_before == 2823
        assert step.rows_after == 2811
        assert step.columns_before == 9
        assert step.columns_after == 9
        assert step.duration_ms == 150
        assert step.timestamp == "2026-06-09T10:30:00"
