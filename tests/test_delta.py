"""Test module for delta tracking functionality.

This module contains tests for the DeltaTracker class that computes
row-level differences between DataFrame snapshots using SQLite persistence.
"""

import tempfile
from pathlib import Path
import pandas as pd

from app.core.delta import DeltaTracker


class TestDeltaTracker:
    """Test cases for the DeltaTracker class."""

    def test_delta_tracker_initialization(self):
        """Test that DeltaTracker initializes correctly with default db path."""
        tracker = DeltaTracker()

        assert tracker.db_path == Path("delta.db")
        assert not tracker._db_initialized  # DB not initialized until first use

    def test_delta_tracker_initialization_with_custom_path(self):
        """Test that DeltaTracker initializes with custom db path."""
        custom_path = Path("/tmp/custom_delta.db")
        tracker = DeltaTracker(db_path=custom_path)

        assert tracker.db_path == custom_path

    def test_compute_diff_empty_database_first_dataframe(self):
        """Test compute_diff with empty database and first DataFrame (3x3)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            # Create a 3x3 DataFrame
            df_v1 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Bob"],
                    "Age": [30, 25, 35],
                    "City": ["NYC", "LA", "Chicago"],
                }
            )

            result = tracker.compute_diff(df_v1)

            # Expect all rows to be added
            assert result["added"] == 3
            assert result["updated"] == 0
            assert result["deleted"] == 0
            assert isinstance(result["diff_df"], pd.DataFrame)
            assert len(result["diff_df"]) == 3  # All rows are "new"

    def test_compute_diff_one_row_updated(self):
        """Test compute_diff where one row value changes between versions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            # Push first DataFrame (3x3)
            df_v1 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Bob"],
                    "Age": [30, 25, 35],
                    "City": ["NYC", "LA", "Chicago"],
                }
            )
            tracker.compute_diff(df_v1)

            # Create second DataFrame with one changed value
            df_v2 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Bob"],
                    "Age": [30, 26, 35],  # Jane's age changed from 25 to 26
                    "City": ["NYC", "LA", "Chicago"],
                }
            )

            result = tracker.compute_diff(df_v2)

            # Expect one row to be updated
            assert result["added"] == 0
            assert result["updated"] == 1
            assert result["deleted"] == 0
            assert isinstance(result["diff_df"], pd.DataFrame)
            assert len(result["diff_df"]) == 1  # Only the changed row

    def test_compute_diff_empty_dataframe_all_deleted(self):
        """Test compute_diff with empty DataFrame after having data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            # Push first DataFrame (3x3)
            df_v1 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Bob"],
                    "Age": [30, 25, 35],
                    "City": ["NYC", "LA", "Chicago"],
                }
            )
            tracker.compute_diff(df_v1)

            # Push empty DataFrame
            df_empty = pd.DataFrame()

            result = tracker.compute_diff(df_empty)

            # Expect all rows to be deleted
            assert result["added"] == 0
            assert result["updated"] == 0
            assert result["deleted"] == 3
            assert isinstance(result["diff_df"], pd.DataFrame)

    def test_compute_diff_mixed_operations(self):
        """Test compute_diff with mixed add/update/delete operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            # Push first DataFrame (3x3)
            df_v1 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Bob"],
                    "Age": [30, 25, 35],
                    "City": ["NYC", "LA", "Chicago"],
                }
            )
            tracker.compute_diff(df_v1)

            # Create DataFrame with mixed changes:
            # - Keep John unchanged
            # - Update Jane's age
            # - Remove Bob
            # - Add Alice
            df_v2 = pd.DataFrame(
                {
                    "Name": ["John", "Jane", "Alice"],
                    "Age": [30, 26, 28],  # Jane's age updated, Alice added
                    "City": ["NYC", "LA", "Seattle"],
                }
            )

            result = tracker.compute_diff(df_v2)

            # Expect 1 add, 1 update, 1 delete
            assert result["added"] == 1
            assert result["updated"] == 1
            assert result["deleted"] == 1
            assert isinstance(result["diff_df"], pd.DataFrame)

    def test_compute_diff_result_is_json_serializable(self):
        """Test that the diff result is JSON-serializable."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            df = pd.DataFrame({"Name": ["John"], "Age": [30], "City": ["NYC"]})

            result = tracker.compute_diff(df)

            # Create a JSON-serializable version (excluding diff_df for this test)
            json_result = {
                "added": result["added"],
                "updated": result["updated"],
                "deleted": result["deleted"],
            }

            # Should not raise exception
            json_string = json.dumps(json_result)
            assert isinstance(json_string, str)

    def test_database_persistence(self):
        """Test that data persists correctly in SQLite database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"

            # Create first tracker instance
            tracker1 = DeltaTracker(db_path=db_path)
            df = pd.DataFrame({"Name": ["John"], "Age": [30], "City": ["NYC"]})
            tracker1.compute_diff(df)

            # Create second tracker instance with same db path
            tracker2 = DeltaTracker(db_path=db_path)

            # Add a row - should detect existing data
            df2 = pd.DataFrame(
                {"Name": ["John", "Jane"], "Age": [30, 25], "City": ["NYC", "LA"]}
            )

            result = tracker2.compute_diff(df2)

            # Should detect 1 existing row and 1 new row
            assert result["added"] == 1
            assert result["updated"] == 0
            assert result["deleted"] == 0

    def test_identical_dataframes_no_changes(self):
        """Test compute_diff with identical DataFrames shows no changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_delta.db"
            tracker = DeltaTracker(db_path=db_path)

            df = pd.DataFrame(
                {"Name": ["John", "Jane"], "Age": [30, 25], "City": ["NYC", "LA"]}
            )

            # Push first time
            tracker.compute_diff(df)

            # Push identical DataFrame
            result = tracker.compute_diff(df)

            # Should show no changes
            assert result["added"] == 0
            assert result["updated"] == 0
            assert result["deleted"] == 0
            assert len(result["diff_df"]) == 0
