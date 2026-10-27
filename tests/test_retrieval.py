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

def test_hindi_refund_query_expands_to_english_policy(tmp_path: Path):
    (tmp_path / "refund.md").write_text("---\ndoc_type: policy\nstatus: current\n---\n## [REF-1] Refund timeline\nRefund timeline begins after quality check.", encoding="utf-8")
    kb = KnowledgeBase.from_directory(tmp_path)
    assert kb.search("मेरा रिफ़ंड कहाँ है")[0][0].section_id == "REF-1"


def test_current_policy_ranks_above_marketing_for_same_terms(tmp_path: Path):
    (tmp_path / "policy.md").write_text(
        "---\ndoc_type: policy\nstatus: current\n---\n## [POL-1] Return policy\nRefund return window is seven days.",
        encoding="utf-8",
    )
    (tmp_path / "marketing.md").write_text(
        "---\ndoc_type: marketing\nstatus: current\n---\n## [MKT-1] Return offer\nRefund return window is seven days.",
        encoding="utf-8",
    )
    kb = KnowledgeBase.from_directory(tmp_path)
    results = kb.search("refund return window")
    assert results[0][0].section_id == "POL-1"
