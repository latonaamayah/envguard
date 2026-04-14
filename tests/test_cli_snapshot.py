"""Tests for envguard.cli_snapshot."""
import json
import os
import pytest

from envguard.cli_snapshot import build_snapshot_parser, run_snapshot
from envguard.snapshotter import save_snapshot, take_snapshot


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    with open(path, "w") as fh:
        fh.write(content)
    return str(path)


def _args(parser, argv):
    return parser.parse_args(argv)


def test_save_exits_zero(tmp_env):
    env_file = _write(tmp_env / ".env", "APP_ENV=production\nPORT=8080\n")
    out = str(tmp_env / "snap.json")
    parser = build_snapshot_parser()
    args = _args(parser, ["save", env_file, out])
    assert run_snapshot(args) == 0
    assert os.path.exists(out)


def test_save_creates_valid_json(tmp_env):
    env_file = _write(tmp_env / ".env", "KEY=value\n")
    out = str(tmp_env / "snap.json")
    parser = build_snapshot_parser()
    args = _args(parser, ["save", env_file, out])
    run_snapshot(args)
    with open(out) as fh:
        data = json.load(fh)
    assert data["variables"]["KEY"] == "value"


def test_save_missing_env_file_exits_two(tmp_env):
    out = str(tmp_env / "snap.json")
    parser = build_snapshot_parser()
    args = _args(parser, ["save", str(tmp_env / "missing.env"), out])
    assert run_snapshot(args) == 2


def test_diff_no_changes_exits_zero(tmp_env):
    env = {"APP": "prod", "PORT": "80"}
    snap = take_snapshot(env, source=".env")
    old_path = str(tmp_env / "old.json")
    new_path = str(tmp_env / "new.json")
    save_snapshot(snap, old_path)
    save_snapshot(snap, new_path)
    parser = build_snapshot_parser()
    args = _args(parser, ["diff", old_path, new_path])
    assert run_snapshot(args) == 0


def test_diff_with_changes_exits_one(tmp_env):
    old_snap = take_snapshot({"APP": "prod"}, source=".env")
    new_snap = take_snapshot({"APP": "staging", "NEW": "1"}, source=".env")
    old_path = str(tmp_env / "old.json")
    new_path = str(tmp_env / "new.json")
    save_snapshot(old_snap, old_path)
    save_snapshot(new_snap, new_path)
    parser = build_snapshot_parser()
    args = _args(parser, ["diff", old_path, new_path])
    assert run_snapshot(args) == 1


def test_diff_missing_snapshot_exits_two(tmp_env):
    snap = take_snapshot({"A": "1"}, source=".env")
    old_path = str(tmp_env / "old.json")
    save_snapshot(snap, old_path)
    parser = build_snapshot_parser()
    args = _args(parser, ["diff", old_path, str(tmp_env / "missing.json")])
    assert run_snapshot(args) == 2
