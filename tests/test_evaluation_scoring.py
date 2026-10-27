from scripts.evaluate import fact_satisfied, normalize, score_answer, split_facts


def test_normalize_ignores_punctuation_and_case():
    assert normalize("Refund—STATUS!!") == "refund status"


def test_split_facts_uses_dataset_delimiter():
    assert split_facts("refund issued ; 3 business days") == [
        "refund issued",
        "3 business days",
    ]


def test_fact_satisfied_supports_alternative_phrasing():
    answer = normalize("Your refund will be issued within 3 business days.")
    assert fact_satisfied("within 3 business days / 3 business days", answer)


def test_score_answer_reports_missing_and_forbidden_facts():
    row = {
        "must_include": "refund issued ; 3 business days",
        "must_not_include": "guaranteed today",
    }
    result = score_answer("Your refund is issued in 3 business days.", row)
    assert result["missing_must_include"] == []
    assert result["must_not_include_violations"] == []

    result = score_answer("Your refund is guaranteed today.", row)
    assert result["missing_must_include"] == ["refund issued", "3 business days"]
    assert result["must_not_include_violations"] == ["guaranteed today"]
