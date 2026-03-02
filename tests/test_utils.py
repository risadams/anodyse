"""Unit tests for shared utility helpers."""

from anodyse.utils import classify_comment, parse_todo


def test_classify_annotation() -> None:
    assert classify_comment("@task.description: install packages") == "annotation"


def test_classify_todo_colon() -> None:
    assert classify_comment("TODO: fix this") == "todo"


def test_classify_todo_author() -> None:
    assert classify_comment("TODO(ris): fix this") == "todo"


def test_classify_fixme() -> None:
    assert classify_comment("FIXME: broken") == "todo"


def test_classify_prose() -> None:
    assert classify_comment("installs packages") == "prose"


def test_classify_case_insensitive() -> None:
    assert classify_comment("todo: lowercase") == "todo"


def test_parse_todo_basic() -> None:
    item = parse_todo("TODO: fix this now")
    assert item is not None
    assert item.text == "fix this now"
    assert item.author is None


def test_parse_todo_with_author() -> None:
    item = parse_todo("TODO(ris): fix this now")
    assert item is not None
    assert item.text == "fix this now"
    assert item.author == "ris"


def test_parse_todo_fixme() -> None:
    item = parse_todo("FIXME: broken on rhel")
    assert item is not None
    assert item.text == "broken on rhel"
    assert item.author is None


def test_parse_todo_non_match_returns_none() -> None:
    assert parse_todo("installs package dependencies") is None
