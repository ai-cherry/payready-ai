import json
from pathlib import Path

from cli.agents.context import load_context, summaries_from_runs


def test_load_context_reads_memory(tmp_path):
    memory_dir = tmp_path
    (memory_dir / "session-log.md").write_text("Entry", encoding="utf-8")
    events_path = memory_dir / "events.jsonl"
    events_path.write_text(json.dumps({"timestamp": "2025-01-01", "agent": "shell"}) + "\n", encoding="utf-8")

    runs_dir = memory_dir / "runs"
    runs_dir.mkdir()
    run_dir = runs_dir / "20250101T000000Z"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(json.dumps({"summary": "Test"}), encoding="utf-8")

    context = load_context(memory_dir)
    assert context["session_markdown"].strip() == "Entry"
    assert context["events"][0]["agent"] == "shell"
    assert context["recent_runs"][0]["summary"] == "Test"


def test_load_context_reads_extra_file(tmp_path):
    memory_dir = tmp_path
    extra = tmp_path / "extra.md"
    extra.write_text("Extra", encoding="utf-8")
    context = load_context(memory_dir, extra)
    assert context["extra_context"] == "Extra"


def test_summaries_from_runs_limit(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    for index in range(6):
        run_dir = runs_dir / f"20250101T00000{index}Z"
        run_dir.mkdir()
        (run_dir / "metadata.json").write_text(json.dumps({"summary": index}), encoding="utf-8")

    summaries = summaries_from_runs(tmp_path, limit=3)
    assert len(summaries) == 3
    assert summaries[0]["summary"] == 5
