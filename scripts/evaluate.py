"""Evaluate the agent against supplied practice questions (requires local dataset)."""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from src.agent import SupportAgent
from src.retrieval import KnowledgeBase


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def split_facts(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(" ; ") if part.strip()]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value.casefold())).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=os.getenv("ZENTOMART_DATA_DIR", ""))
    parser.add_argument("--kb-dir", default="data/knowledge_base")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for a quick smoke run")
    parser.add_argument("--output", default="outputs/evaluation.json")
    args = parser.parse_args()
    load_dotenv()
    if not args.dataset_dir:
        parser.error("Pass --dataset-dir or set ZENTOMART_DATA_DIR.")
    dataset = Path(args.dataset_dir)
    rows = read_rows(dataset / "practice" / "questions.csv")
    if args.limit:
        rows = rows[:args.limit]
    kb = KnowledgeBase.from_directory(args.kb_dir)
    agent = SupportAgent(kb)
    results = []
    for row in rows:
        agent.reset()
        prompt = row.get("asr_text") or row["question"]
        try:
            result = agent.respond(prompt)
            answer = result["answer"]
            norm_answer = normalize(answer)
            required = split_facts(row.get("must_include", ""))
            forbidden = split_facts(row.get("must_not_include", ""))
            missing = [fact for fact in required if normalize(fact) not in norm_answer]
            violations = [fact for fact in forbidden if normalize(fact) and normalize(fact) in norm_answer]
            gold = [x.strip() for x in row.get("gold_evidence", "").split(" ; ") if x.strip()]
            found_sections = {item["section_id"] for item in result.get("sources", [])}
            results.append({
                "id": row.get("id"), "intent": row.get("intent"),
                "expected_decision": row.get("expected_decision"),
                "answer": answer, "missing_must_include": missing,
                "must_not_include_violations": violations,
                "gold_evidence": gold, "retrieved_sections": sorted(found_sections),
                "evidence_hit": bool(set(gold) & found_sections),
                "tool_calls": result.get("tool_calls", []),
            })
        except Exception as exc:
            results.append({"id": row.get("id"), "error_type": type(exc).__name__, "error": str(exc)})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    evaluated = [r for r in results if "error" not in r]
    print(f"Evaluated {len(evaluated)}/{len(rows)} questions. Results: {output}")
    if evaluated:
        print(f"Evidence hit rate: {sum(r['evidence_hit'] for r in evaluated) / len(evaluated):.1%}")
        print(f"Rows with missing required facts: {sum(bool(r['missing_must_include']) for r in evaluated)}")
        print(f"Rows with forbidden-claim matches: {sum(bool(r['must_not_include_violations']) for r in evaluated)}")
    return 0 if len(evaluated) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
