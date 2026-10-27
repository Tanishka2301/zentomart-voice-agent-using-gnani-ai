"""Copy the supplied knowledge-base Markdown files into the project.

The full synthetic dataset, raw CSVs, practice labels, and ticket output stay
outside the repository. Set ZENTOMART_DATA_DIR to the extracted dataset root
for order lookup and ticket tools.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir", help="Extracted Capstone_Project_Dataset_FTTT_2026 folder")
    parser.add_argument("--destination", default="data/knowledge_base")
    args = parser.parse_args()
    source = Path(args.dataset_dir).expanduser().resolve()
    kb = source / "kb"
    if not kb.is_dir():
        parser.error(f"Could not find kb/ in {source}")
    destination = Path(args.destination)
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for file in sorted(kb.glob("*.md")):
        shutil.copy2(file, destination / file.name)
        copied += 1
    print(f"Copied {copied} knowledge-base documents to {destination}")
    print(f"Set ZENTOMART_DATA_DIR to: {source}")
    print("Run python validate_dataset.py from the dataset folder before testing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
