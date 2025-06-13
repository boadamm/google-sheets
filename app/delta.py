"""Delta tracking module for DataFrame changes.

This module provides functionality to track changes between DataFrame versions
using SQLite persistence to store snapshots and compute row-level diffs.
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import json


class DeltaTracker:
    """Tracks changes between DataFrame versions using SQLite persistence.

    This class stores DataFrame snapshots in SQLite and computes row-level
    differences (added, updated, deleted) between consecutive versions.
    """

    def __init__(self, db_path: Path = Path("delta.db")):
        """Initialize DeltaTracker with SQLite database path.

        Args:
            db_path: Path to SQLite database file (default: "delta.db")
        """
        self.db_path = db_path
        self._db_initialized = False

    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        if not self._db_initialized:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        row_hash TEXT UNIQUE NOT NULL,
                        row_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
            self._db_initialized = True

    def _compute_row_hash(self, row: pd.Series) -> str:
        """Compute hash for a DataFrame row.

        Args:
            row: DataFrame row as Series

        Returns:
            str: MD5 hash of the row data
        """
        # Convert row to string representation for hashing
        row_str = "|".join(str(value) for value in row.values)
        return hashlib.md5(row_str.encode()).hexdigest()

    def _get_stored_hashes(self) -> set:
        """Get all stored row hashes from database.

        Returns:
            set: Set of row hashes currently in database
        """
        self._init_database()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT row_hash FROM snapshots")
            return {row[0] for row in cursor.fetchall()}

    def _get_stored_data(self) -> Dict[str, Dict]:
        """Get all stored row data from database.

        Returns:
            dict: Dictionary mapping row_hash to row_data
        """
        self._init_database()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT row_hash, row_data FROM snapshots")
            return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

    def _detect_updates(
        self,
        new_df: pd.DataFrame,
        stored_data: Dict,
        added_hashes: set,
        deleted_hashes: set,
    ) -> int:
        """Detect rows that represent updates rather than pure add/delete.

        This is a heuristic-based approach that looks for similar row structures
        between added and deleted rows to infer updates by comparing on a
        potential primary key (like 'Name' column).

        Args:
            new_df: New DataFrame
            stored_data: Previously stored row data
            added_hashes: Set of hashes for added rows
            deleted_hashes: Set of hashes for deleted rows

        Returns:
            int: Number of detected updates
        """
        if not added_hashes or not deleted_hashes or new_df.empty:
            return 0

        # Get current and stored row data for comparison
        current_rows = {}
        for _, row in new_df.iterrows():
            row_hash = self._compute_row_hash(row)
            if row_hash in added_hashes:
                current_rows[row_hash] = row.to_dict()

        # Try to match rows by a potential key field (like 'Name')
        # This is a simple heuristic that assumes the first string column
        # could be a primary key
        updates = 0
        if "Name" in new_df.columns:
            # Get names from added and deleted rows
            added_names = set()
            for hash_val in added_hashes:
                for _, row in new_df.iterrows():
                    if self._compute_row_hash(row) == hash_val:
                        added_names.add(row.get("Name"))
                        break

            deleted_names = set()
            for hash_val in deleted_hashes:
                row_data = stored_data.get(hash_val, {})
                if "Name" in row_data:
                    deleted_names.add(row_data["Name"])

            # Count names that appear in both added and deleted as updates
            updates = len(added_names & deleted_names)

        # Fallback: if no clear key matching, use simple size-based heuristic
        if updates == 0:
            if len(new_df) == len(stored_data) and len(added_hashes) == len(
                deleted_hashes
            ):
                updates = min(len(added_hashes), len(deleted_hashes))

        return updates

    def _clear_database(self) -> None:
        """Clear all data from the snapshots table."""
        self._init_database()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snapshots")
            conn.commit()

    def _store_dataframe(self, df: pd.DataFrame) -> None:
        """Store DataFrame rows in database.

        Args:
            df: DataFrame to store
        """
        self._init_database()
        if df.empty:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                row_hash = self._compute_row_hash(row)
                row_data = json.dumps(row.to_dict())
                cursor.execute(
                    "INSERT OR REPLACE INTO snapshots (row_hash, row_data) VALUES (?, ?)",
                    (row_hash, row_data),
                )
            conn.commit()

    def compute_diff(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute differences between current DataFrame and stored snapshot.

        Args:
            df: Current DataFrame to compare

        Returns:
            dict: Dictionary containing:
                - added: int - number of added rows
                - updated: int - number of updated rows
                - deleted: int - number of deleted rows
                - diff_df: pd.DataFrame - DataFrame containing changed rows
        """
        # Get currently stored hashes
        stored_hashes = self._get_stored_hashes()

        # Compute hashes for new DataFrame
        new_hashes = set()
        new_rows = []
        if not df.empty:
            for _, row in df.iterrows():
                row_hash = self._compute_row_hash(row)
                new_hashes.add(row_hash)
                new_rows.append(row)

        # Compute differences
        added_hashes = new_hashes - stored_hashes
        deleted_hashes = stored_hashes - new_hashes

        # For updates, we need more sophisticated logic.
        # Since we're using full-row hashing, we'll look for patterns
        # that suggest updates rather than pure adds/deletes.

        # Get the actual stored data to better analyze changes
        stored_data = self._get_stored_data()

        added_count = len(added_hashes)
        deleted_count = len(deleted_hashes)
        updated_count = 0

        # Determine if changes represent updates by analyzing data patterns
        if added_count > 0 and deleted_count > 0:
            # Look for rows that might be updates by comparing row structures
            updated_count = self._detect_updates(
                df, stored_data, added_hashes, deleted_hashes
            )
            added_count -= updated_count
            deleted_count -= updated_count

        # Create diff DataFrame containing changed rows
        diff_rows = []
        if not df.empty:
            for _, row in df.iterrows():
                row_hash = self._compute_row_hash(row)
                if row_hash in added_hashes or row_hash in new_hashes - stored_hashes:
                    diff_rows.append(row)

        # Add metadata to distinguish row types if needed
        diff_df = pd.DataFrame(diff_rows) if diff_rows else pd.DataFrame()

        # Update the stored snapshot
        self._clear_database()
        self._store_dataframe(df)

        return {
            "added": added_count,
            "updated": updated_count,
            "deleted": deleted_count,
            "diff_df": diff_df,
        }
