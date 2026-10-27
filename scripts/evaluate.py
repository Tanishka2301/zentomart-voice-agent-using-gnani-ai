"""Compare prompt-only and retrieval-grounded answers on the supplied questions."""
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

def fact_satisfied(fact: str, normalized_answer: str) -> bool:
    alternatives = [normalize(part) for part in fact.split(" / ") if normalize(part)]
    return any(part in normalized_answer for part in alternatives)

def score_answer(answer: str, row: dict[str, str]) -> dict:
    norm_answer = normalize(answer)
    required = split_facts(row.get("must_include", ""))
    forbidden = split_facts(row.get("must_not_include", ""))
    return {
        "missing_must_include": [fact for fact in required if not fact_satisfied(fact, norm_answer)],
        "must_not_include_violations": [fact for fact in forbidden if normalize(fact) and normalize(fact) in norm_answer],
    }

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
    rows = read_rows(Path(args.dataset_dir) / "practice" / "questions.csv")
    if args.limit:
        rows = rows[:args.limit]
    kb = KnowledgeBase.from_directory(args.kb_dir)
    baseline = SupportAgent(kb, use_retrieval=False)
    rag = SupportAgent(kb, use_retrieval=True)
    results = []
    for row in rows:
        baseline.reset()
        rag.reset()
        prompt = row.get("asr_text") or row["question"]
        try:
            base_result = baseline.respond(prompt)
            rag_result = rag.respond(prompt)
            gold = [x.strip() for x in row.get("gold_evidence", "").split(" ; ") if x.strip()]
            found_sections = {item["section_id"] for item in rag_result.get("sources", [])}
            results.append({
                "id": row.get("id"),
                "intent": row.get("intent"),
                "expected_decision": row.get("expected_decision"),
                "prompt_only": {
                    "answer": base_result["answer"],
                    **score_answer(base_result["answer"], row),
                },
                "rag": {
                    "answer": rag_result["answer"],
                    **score_answer(rag_result["answer"], row),
                    "gold_evidence": gold,
                    "retrieved_sections": sorted(found_sections),
                    "evidence_hit": bool(set(gold) & found_sections),
                    "tool_calls": rag_result.get("tool_calls", []),
                },
            })
        except Exception as exc:
            results.append({"id": row.get("id"), "error_type": type(exc).__name__, "error": str(exc)})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    evaluated = [r for r in results if "error" not in r]
    print(f"Evaluated {len(evaluated)}/{len(rows)} questions. Results: {output}")
    if evaluated:
        print(f"RAG evidence hit rate: {sum(r['rag']['evidence_hit'] for r in evaluated) / len(evaluated):.1%}")
        for mode in ("prompt_only", "rag"):
            missing = sum(bool(r[mode]["missing_must_include"]) for r in evaluated)
            forbidden = sum(bool(r[mode]["must_not_include_violations"]) for r in evaluated)
            print(f"{mode}: {missing} rows missing required facts; {forbidden} rows with forbidden-claim matches")
    return 0 if len(evaluated) == len(rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())
