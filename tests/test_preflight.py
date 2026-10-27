from scripts.preflight import REQUIRED_DATASET_PATHS, check_dataset


def test_check_dataset_reports_missing_required_paths(tmp_path):
    missing = check_dataset(tmp_path)
    assert missing == list(REQUIRED_DATASET_PATHS)


def test_check_dataset_accepts_expected_layout(tmp_path):
    for relative in REQUIRED_DATASET_PATHS:
        path = tmp_path / relative
        if relative.endswith(".py") or relative.endswith(".csv"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)
    assert check_dataset(tmp_path) == []
