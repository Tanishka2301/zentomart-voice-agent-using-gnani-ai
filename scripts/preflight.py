"""Preflight checks for local dataset and credentials before a capstone run."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

from dotenv import load_dotenv


REQUIRED_DATASET_PATHS = (
    "tools/tools.py",
    "kb",
    "data",
    "practice/questions.csv",
    "practice/conversations.csv",
)


def check_dataset(root: Path) -> list[str]:
    missing = [relative for relative in REQUIRED_DATASET_PATHS if not (root / relative).exists()]
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local credentials, dataset layout, KB files, and audio dependencies without making API calls."
    )
    parser.add_argument("--dataset-dir", default=os.getenv("ZENTOMART_DATA_DIR", ""))
    parser.add_argument("--kb-dir", default="data/knowledge_base")
    parser.add_argument("--audio", action="store_true", help="Also check the Gnani audio SDK imports")
    args = parser.parse_args()
    load_dotenv()

    failed = False
    for key in ("GEMINI_API_KEY", "GNANI_API_KEY"):
        present = bool(os.getenv(key, "").strip())
        print(f"{'OK' if present else 'MISSING'}: {key}")
        failed |= not present

    if not args.dataset_dir:
        print("MISSING: ZENTOMART_DATA_DIR / --dataset-dir")
        failed = True
    else:
        root = Path(args.dataset_dir).expanduser().resolve()
        if not root.is_dir():
            print(f"MISSING: dataset directory does not exist: {root}")
            failed = True
        else:
            missing = check_dataset(root)
            if missing:
                print("MISSING dataset paths:")
                for path in missing:
                    print(f"  - {path}")
                failed = True
            else:
                print(f"OK: dataset layout ({root})")

    kb = Path(args.kb_dir)
    kb_files = sorted(kb.rglob("*.md")) if kb.is_dir() else []
    if kb_files:
        print(f"OK: knowledge base has {len(kb_files)} Markdown file(s) in {kb}")
    else:
        print(f"MISSING: no Markdown knowledge-base files in {kb}")
        print("Run scripts/import_dataset.py with the extracted dataset folder.")
        failed = True

    for module in ("google.genai",):
        if importlib.util.find_spec(module) is None:
            print(f"MISSING: Python module {module}")
            failed = True
        else:
            print(f"OK: Python module {module}")

    if args.audio:
        for module in ("gnani.stt", "gnani.tts"):
            try:
                available = importlib.util.find_spec(module) is not None
            except (ImportError, ModuleNotFoundError, ValueError):
                available = False
            if not available:
                print(f"MISSING: Python module {module} (install requirements.txt and check Gnani SDK access)")
                failed = True
            else:
                print(f"OK: Python module {module}")

    if failed:
        print("\nPreflight FAILED. Fix the missing items above; no API calls were made.")
        return 1
    print("\nPreflight PASSED. Configuration looks ready; API access has not been tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
