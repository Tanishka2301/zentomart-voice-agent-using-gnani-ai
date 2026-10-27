from src.retrieval import KnowledgeBase


def test_retrieval_finds_relevant_policy_chunk(tmp_path):
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    (kb_dir / "pol_returns.md").write_text(
        "# Returns\n[RETURNS-01]\nCustomers can request a return within the policy window.",
        encoding="utf-8",
    )
    (kb_dir / "faq_delivery.md").write_text(
        "# Delivery\n[DELIVERY-01]\nDelivery tracking shows the shipment status.",
        encoding="utf-8",
    )

    kb = KnowledgeBase.from_directory(kb_dir)
    results = kb.search("request a return policy", top_k=2)

    assert results
    assert results[0][0].source.endswith("pol_returns.md")
    assert results[0][0].section_id == "RETURNS-01"


def test_empty_query_returns_no_results(tmp_path):
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    (kb_dir / "policy.md").write_text("# Policy\nA simple policy.", encoding="utf-8")

    kb = KnowledgeBase.from_directory(kb_dir)
    assert kb.search("   ") == []
