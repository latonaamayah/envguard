"""Tests for envguard.grapher."""
import pytest
from envguard.grapher import graph, GraphResult, GraphNode


@pytest.fixture()
def env():
    return {
        "BASE_URL": "https://example.com",
        "API_URL": "${BASE_URL}/api",
        "FULL_URL": "${API_URL}/v1",
        "PORT": "8080",
        "HOST": "localhost",
    }


def test_returns_graph_result(env):
    result = graph(env)
    assert isinstance(result, GraphResult)


def test_node_count_matches_env(env):
    result = graph(env)
    # BASE_URL, API_URL, FULL_URL, PORT, HOST
    assert len(result.nodes) == 5


def test_reference_detected(env):
    result = graph(env)
    assert "BASE_URL" in result.nodes["API_URL"].references


def test_chained_reference(env):
    result = graph(env)
    assert "API_URL" in result.nodes["FULL_URL"].references


def test_referenced_by_populated(env):
    result = graph(env)
    assert "API_URL" in result.nodes["BASE_URL"].referenced_by


def test_no_reference_for_plain_value(env):
    result = graph(env)
    assert result.nodes["PORT"].references == []


def test_has_references_true(env):
    result = graph(env)
    assert result.nodes["API_URL"].has_references()


def test_has_references_false(env):
    result = graph(env)
    assert not result.nodes["PORT"].has_references()


def test_no_cycles_in_normal_env(env):
    result = graph(env)
    assert not result.has_cycles()


def test_cycle_detected():
    cyclic = {"A": "${B}", "B": "${A}"}
    result = graph(cyclic)
    assert result.has_cycles()


def test_roots_are_unreferenced(env):
    result = graph(env)
    roots = result.roots()
    # BASE_URL and PORT and HOST are not referenced by anyone
    assert "BASE_URL" in roots
    assert "PORT" in roots


def test_leaves_have_no_outgoing(env):
    result = graph(env)
    leaves = result.leaves()
    assert "PORT" in leaves
    assert "HOST" in leaves


def test_summary_contains_nodes(env):
    result = graph(env)
    s = result.summary()
    assert "nodes=5" in s


def test_summary_contains_cycle_info(env):
    result = graph(env)
    assert "cycles=no" in result.summary()


def test_dollar_without_braces():
    e = {"A": "hello", "B": "$A/world"}
    result = graph(e)
    assert "A" in result.nodes["B"].references
