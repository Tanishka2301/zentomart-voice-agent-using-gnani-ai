"""Regression tests for evaluation CLI configuration loaded from .env."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from types import SimpleNamespace

from scripts import evaluate, evaluate_conversations


class FakeAgent:
    def __init__(self, *args, **kwargs):
        pass

    def reset(self):
        pass

    def respond(self, question):
        return {"answer": "The return window is seven days.", "sources": [], "tool_calls": []}


def _write_csv(path: Path, fieldnames: list[str], row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def _fake_load_dotenv(monkeypatch, dataset: Path):
    def load_dotenv():
        monkeypatch.setenv("ZENTOMART_DATA_DIR", str(dataset))
    return load_dotenv


def test_question_evaluator_reads_dataset_path_after_dotenv(tmp_path, monkeypatch):
    dataset = tmp_path / "dataset"
    _write_csv(
        dataset / "practice" / "questions.csv",
        ["id", "intent", "question", "asr_text", "expected_decision", "must_include", "must_not_include", "gold_evidence"],
        {"id": "Q1", "intent": "policy", "question": "What is the return window?", "asr_text": "",
         "expected_decision": "answer", "must_include": "seven days", "must_not_include": "", "gold_evidence": ""},
    )
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    (kb_dir / "policy.md").write_text("## [RET-1] Return policy\nThe return window is seven days.", encoding="utf-8")
    monkeypatch.delenv("ZENTOMART_DATA_DIR", raising=False)
    monkeypatch.setattr(evaluate, "load_dotenv", _fake_load_dotenv(monkeypatch, dataset))
    monkeypatch.setattr(evaluate, "SupportAgent", FakeAgent)
    monkeypatch.setattr(sys, "argv", ["evaluate.py", "--kb-dir", str(kb_dir), "--limit", "1", "--output", str(tmp_path / "out.json")])

    assert evaluate.main() == 0
    assert (tmp_path / "out.json").is_file()


def test_conversation_evaluator_reads_dataset_path_after_dotenv(tmp_path, monkeypatch):
    dataset = tmp_path / "dataset"
    _write_csv(
        dataset / "practice" / "conversations.csv",
        ["conversation_id", "turn", "customer_message", "expected_tool_calls", "must_include", "must_not_include", "expected_decision"],
        {"conversation_id": "C1", "turn": "1", "customer_message": "What is the return window?",
         "expected_tool_calls": "", "must_include": "seven days", "must_not_include": "", "expected_decision": "answer"},
    )
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    (kb_dir / "policy.md").write_text("## [RET-1] Return policy\nThe return window is seven days.", encoding="utf-8")
    monkeypatch.delenv("ZENTOMART_DATA_DIR", raising=False)
    monkeypatch.setattr(evaluate_conversations, "load_dotenv", _fake_load_dotenv(monkeypatch, dataset))
    monkeypatch.setattr(evaluate_conversations, "SupportAgent", FakeAgent)
    monkeypatch.setattr(sys, "argv", ["evaluate_conversations.py", "--kb-dir", str(kb_dir), "--limit", "1", "--output", str(tmp_path / "conversations.json")])

    assert evaluate_conversations.main() == 0
    assert (tmp_path / "conversations.json").is_file()
