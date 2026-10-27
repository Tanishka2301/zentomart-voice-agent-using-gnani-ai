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


def test_main_reads_dataset_dir_after_loading_dotenv(tmp_path, monkeypatch, capsys):
    import sys
    from scripts import preflight

    dataset = tmp_path / "dataset"
    for relative in REQUIRED_DATASET_PATHS:
        path = dataset / relative
        if relative.endswith(".py") or relative.endswith(".csv"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "policy.md").write_text("# Test policy", encoding="utf-8")

    def fake_load_dotenv():
        monkeypatch.setenv("GEMINI_API_KEY", "test")
        monkeypatch.setenv("GNANI_API_KEY", "test")
        monkeypatch.setenv("ZENTOMART_DATA_DIR", str(dataset))

    monkeypatch.setattr(preflight, "load_dotenv", fake_load_dotenv)
    monkeypatch.setattr(sys, "argv", ["preflight.py", "--kb-dir", str(kb)])
    assert preflight.main() == 0
    assert f"OK: dataset layout ({dataset})" in capsys.readouterr().out
