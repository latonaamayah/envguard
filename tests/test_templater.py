import pytest
from envguard.templater import render_templates, TemplateEntry, TemplateResult


@pytest.fixture
def context():
    return {
        "HOST": "localhost",
        "PORT": "5432",
        "USER": "admin",
    }


def test_returns_template_result(context):
    result = render_templates({"DB_URL": "postgres://{{USER}}@{{HOST}}:{{PORT}}/db"}, context)
    assert isinstance(result, TemplateResult)


def test_simple_substitution(context):
    result = render_templates({"ADDR": "{{HOST}}:{{PORT}}"}, context)
    assert result.as_dict()["ADDR"] == "localhost:5432"


def test_no_placeholders_unchanged(context):
    result = render_templates({"PLAIN": "no_vars_here"}, context)
    assert result.as_dict()["PLAIN"] == "no_vars_here"


def test_missing_var_left_as_placeholder(context):
    result = render_templates({"X": "{{MISSING}}"}, context)
    assert result.as_dict()["X"] == "{{MISSING}}"


def test_missing_var_recorded(context):
    result = render_templates({"X": "{{MISSING}}"}, context)
    entry = result.entries[0]
    assert "MISSING" in entry.missing_vars


def test_has_errors_false_without_strict(context):
    result = render_templates({"X": "{{MISSING}}"}, context, strict=False)
    assert not result.has_errors


def test_has_errors_true_with_strict(context):
    result = render_templates({"X": "{{MISSING}}"}, context, strict=True)
    assert result.has_errors


def test_strict_error_message_contains_key(context):
    result = render_templates({"MY_KEY": "{{MISSING}}"}, context, strict=True)
    assert any("MY_KEY" in e for e in result.errors)


def test_multiple_templates(context):
    templates = {"A": "{{HOST}}", "B": "{{PORT}}"}
    result = render_templates(templates, context)
    d = result.as_dict()
    assert d["A"] == "localhost"
    assert d["B"] == "5432"


def test_summary_no_missing(context):
    result = render_templates({"A": "{{HOST}}"}, context)
    assert "0 with missing" in result.summary()


def test_summary_with_missing(context):
    result = render_templates({"A": "{{MISSING}}"}, context)
    assert "1 with missing" in result.summary()


def test_entry_has_missing_false_when_resolved(context):
    result = render_templates({"A": "{{HOST}}"}, context)
    assert not result.entries[0].has_missing


def test_entry_has_missing_true_when_unresolved(context):
    result = render_templates({"A": "{{NOPE}}"}, context)
    assert result.entries[0].has_missing


def test_whitespace_in_placeholder(context):
    result = render_templates({"A": "{{ HOST }}"}, context)
    assert result.as_dict()["A"] == "localhost"
