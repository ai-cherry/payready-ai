from pathlib import Path

from cli.agents._io import append_jsonl, append_text, new_run_dir


def test_append_text_creates_file(tmp_path):
    target = tmp_path / "session-log.md"
    append_text(target, "Hello")
    append_text(target, "World")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "Hello" in content and content.rstrip().endswith("World")


def test_append_jsonl_appends_objects(tmp_path):
    target = tmp_path / "events.jsonl"
    append_jsonl(target, {"a": 1})
    append_jsonl(target, {"b": 2})
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0] == '{"a": 1}'


def test_new_run_dir_unique(tmp_path):
    first = new_run_dir(tmp_path)
    second = new_run_dir(tmp_path)
    assert first != second
    assert first.is_dir() and second.is_dir()
    assert first.parent == tmp_path / "runs"
