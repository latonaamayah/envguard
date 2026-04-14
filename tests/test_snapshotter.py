"""Tests for envguard.snapshotter."""
import json
import os
import pytest

from envguard.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


ENV_A = {"APP_ENV": "production", "DB_HOST": "localhost", "PORT": "8080"}
ENV_B = {"APP_ENV": "staging", "DB_HOST": "localhost", "NEW_KEY": "value"}


def test_take_snapshot_stores_variables():
    snap = take_snapshot(ENV_A, source=".env")
    assert snap.variables == ENV_A
    assert snap.source == ".env"
    assert snap.timestamp  # non-empty


def test_snapshot_to_dict_roundtrip():
    snap = take_snapshot(ENV_A, source=".env")
    restored = Snapshot.from_dict(snap.to_dict())
    assert restored.variables == snap.variables
    assert restored.source == snap.source
    assert restored.timestamp == snap.timestamp


def test_save_and_load_snapshot(tmp_path):
    snap = take_snapshot(ENV_A, source=".env")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded.variables == ENV_A
    assert loaded.source == ".env"


def test_save_snapshot_is_valid_json(tmp_path):
    snap = take_snapshot(ENV_A, source=".env")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert "variables" in data
    assert "timestamp" in data


def test_load_snapshot_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_snapshot("/nonexistent/path/snap.json")


def test_diff_no_changes():
    snap1 = take_snapshot(ENV_A, source=".env")
    snap2 = take_snapshot(ENV_A, source=".env")
    diff = diff_snapshots(snap1, snap2)
    assert not diff.has_changes
    assert diff.summary() == "no changes"


def test_diff_detects_added_key():
    snap1 = take_snapshot(ENV_A, source=".env")
    snap2 = take_snapshot(ENV_B, source=".env")
    diff = diff_snapshots(snap1, snap2)
    assert "NEW_KEY" in diff.added
    assert diff.added["NEW_KEY"] == "value"


def test_diff_detects_removed_key():
    snap1 = take_snapshot(ENV_A, source=".env")
    snap2 = take_snapshot(ENV_B, source=".env")
    diff = diff_snapshots(snap1, snap2)
    assert "PORT" in diff.removed


def test_diff_detects_changed_value():
    snap1 = take_snapshot(ENV_A, source=".env")
    snap2 = take_snapshot(ENV_B, source=".env")
    diff = diff_snapshots(snap1, snap2)
    assert "APP_ENV" in diff.changed
    assert diff.changed["APP_ENV"] == ("production", "staging")


def test_diff_summary_lists_counts():
    snap1 = take_snapshot(ENV_A, source=".env")
    snap2 = take_snapshot(ENV_B, source=".env")
    diff = diff_snapshots(snap1, snap2)
    summary = diff.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary
