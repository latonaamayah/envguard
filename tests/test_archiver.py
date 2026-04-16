import json
import pytest
from pathlib import Path
from envguard.archiver import (
    archive,
    save_archive,
    load_archive,
    ArchiveResult,
    ArchiveEntry,
)


@pytest.fixture
def env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_archive_creates_entry(env):
    entry = archive(env, label="v1")
    assert entry.label == "v1"
    assert entry.variables == env


def test_archive_entry_has_timestamp(env):
    entry = archive(env, label="v1")
    assert entry.timestamp != ""


def test_archive_result_has_entries():
    result = ArchiveResult(entries=[ArchiveEntry("v1", "2024-01-01T00:00:00", {"X": "1"})])
    assert result.has_entries()


def test_archive_result_labels():
    result = ArchiveResult(entries=[
        ArchiveEntry("v1", "t", {}),
        ArchiveEntry("v2", "t", {}),
    ])
    assert result.labels() == ["v1", "v2"]


def test_archive_result_get_existing():
    entry = ArchiveEntry("v1", "t", {"A": "1"})
    result = ArchiveResult(entries=[entry])
    assert result.get("v1") is entry


def test_archive_result_get_missing():
    result = ArchiveResult()
    assert result.get("nope") is None


def test_save_and_load_roundtrip(tmp_path, env):
    path = tmp_path / "archive.json"
    entry = archive(env, label="snap1")
    result = ArchiveResult(entries=[entry])
    save_archive(result, path)
    loaded = load_archive(path)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].label == "snap1"
    assert loaded.entries[0].variables == env


def test_load_archive_missing_file_returns_empty(tmp_path):
    result = load_archive(tmp_path / "missing.json")
    assert not result.has_entries()


def test_save_archive_is_valid_json(tmp_path, env):
    path = tmp_path / "archive.json"
    result = ArchiveResult(entries=[archive(env, "v1")])
    save_archive(result, path)
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert data[0]["label"] == "v1"


def test_summary_message():
    result = ArchiveResult(entries=[
        ArchiveEntry("a", "t", {}),
        ArchiveEntry("b", "t", {}),
    ])
    assert "2" in result.summary()
