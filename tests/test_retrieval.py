from pathlib import Path
from src.retrieval import KnowledgeBase, Chunk, tokenize
from collections import Counter

def test_tokenize_lowercases():
    assert tokenize("Refund REFUND 123") == ["refund", "refund", "123"]

def test_superseded_policy_is_excluded(tmp_path: Path):
    (tmp_path / "current.md").write_text("---\ndoc_type: policy\nstatus: current\n---\n## [RET-4] Current return window\nReturn window is 7 days.", encoding="utf-8")
    (tmp_path / "old.md").write_text("---\ndoc_type: policy\nstatus: superseded\n---\n## [RET-3] Old return window\nReturn window is 30 days.", encoding="utf-8")
    kb = KnowledgeBase.from_directory(tmp_path)
    assert all(chunk.section_id != "RET-3" for chunk in kb.chunks)
    assert kb.search("return window")[0][0].section_id == "RET-4"

def test_empty_query():
    kb = KnowledgeBase([Chunk("x.md", "X-1", "some text", Counter({"some": 1}), "faq")])
    assert kb.search("!!!") == []


def test_unicode_tokenization():
    assert "नमस्ते" in tokenize("नमस्ते ग्राहक")
