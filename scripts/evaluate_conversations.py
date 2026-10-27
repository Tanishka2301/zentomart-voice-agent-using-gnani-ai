"""Evaluate multi-turn practice conversations with stateful tool checks."""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv
from src.agent import SupportAgent
from src.retrieval import KnowledgeBase

def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (value or "").casefold())).strip()

def facts(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(" ; ") if x.strip()]

def satisfied(fact: str, answer: str) -> bool:
    return any(normalize(option) in normalize(answer) for option in fact.split(" / ") if normalize(option))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=os.getenv("ZENTOMART_DATA_DIR", ""))
    parser.add_argument("--kb-dir", default="data/knowledge_base")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on number of conversations")
    parser.add_argument("--output", default="outputs/conversation_evaluation.json")
    args = parser.parse_args()
    load_dotenv()
    if not args.dataset_dir:
        parser.error("Pass --dataset-dir or set ZENTOMART_DATA_DIR.")
    grouped = defaultdict(list)
    for row in rows(Path(args.dataset_dir) / "practice" / "conversations.csv"):
        grouped[row["conversation_id"]].append(row)
    ids = sorted(grouped)
    if args.limit:
        ids = ids[:args.limit]
    agent = SupportAgent(KnowledgeBase.from_directory(args.kb_dir))
    report = []
    for conversation_id in ids:
        agent.reset()
        turns = []
        for row in sorted(grouped[conversation_id], key=lambda item: int(item["turn"])):
            try:
                result = agent.respond(row["customer_message"])
                answer = result["answer"]
                expected_calls = row.get("expected_tool_calls", "")
                expected_names = [name for name in ("lookup_order", "create_ticket") if name in expected_calls]
                actual_names = [call.get("tool") for call in result.get("tool_calls", [])]
                missing_facts = [fact for fact in facts(row.get("must_include", "")) if not satisfied(fact, answer)]
                forbidden = [phrase for phrase in facts(row.get("must_not_include", "")) if normalize(phrase) and normalize(phrase) in normalize(answer)]
                turns.append({
                    "turn": int(row["turn"]),
                    "expected_decision": row.get("expected_decision"),
                    "answer": answer,
                    "missing_required_facts": missing_facts,
                    "forbidden_claim_matches": forbidden,
                    "expected_tool_names": expected_names,
                    "actual_tool_names": actual_names,
                    "missing_tool_calls": [name for name in expected_names if name not in actual_names],
                    "retrieved_sections": sorted({s["section_id"] for s in result.get("sources", [])}),
                })
            except Exception as exc:
                turns.append({"turn": int(row["turn"]), "error_type": type(exc).__name__, "error": str(exc)})
        report.append({"conversation_id": conversation_id, "turns": turns})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    all_turns = [turn for conv in report for turn in conv["turns"]]
    failed = sum(bool(turn.get("error") or turn.get("missing_required_facts") or turn.get("forbidden_claim_matches") or turn.get("missing_tool_calls")) for turn in all_turns)
    print(f"Evaluated {len(report)} conversations / {len(all_turns)} turns; turns with flagged issues: {failed}. Report: {output}")
    return 0 if not any("error" in turn for turn in all_turns) else 1

if __name__ == "__main__":
    raise SystemExit(main())
