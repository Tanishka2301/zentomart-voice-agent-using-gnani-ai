
"""Compare prompt-only and RAG answers with independent error handling."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from src.agent import SupportAgent
from src.retrieval import KnowledgeBase


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def split_facts(value: str) -> list[str]:
    return [
        part.strip()
        for part in (value or "").split(" ; ")
        if part.strip()
    ]


def normalize(value: str) -> str:
    return re.sub(
        r"\s+", " ",
        re.sub(r"[^\w\s]", " ", value.casefold())
    ).strip()


def fact_satisfied(fact: str, normalized_answer: str) -> bool:
    alternatives = [
        normalize(part)
        for part in fact.split(" / ")
        if normalize(part)
    ]
    return any(part in normalized_answer for part in alternatives)


def score_answer(answer: str, row: dict[str, str]) -> dict:
    norm_answer = normalize(answer)
    required = split_facts(row.get("must_include", ""))
    forbidden = split_facts(row.get("must_not_include", ""))

    return {
        "missing_must_include": [
            fact for fact in required
            if not fact_satisfied(fact, norm_answer)
        ],
        "must_not_include_violations": [
            fact for fact in forbidden
            if normalize(fact) and normalize(fact) in norm_answer
        ],
    }


def call_with_retry(agent: SupportAgent, prompt: str, retries: int = 2):
    """Retry temporary provider errors a limited number of times."""
    for attempt in range(retries + 1):
        try:
            return agent.respond(prompt)
        except Exception as exc:
            message = str(exc)
            temporary = (
                "503" in message
                or "429" in message
                or "UNAVAILABLE" in message
                or "RESOURCE_EXHAUSTED" in message
            )

            if not temporary or attempt == retries:
                raise

            wait_seconds = 15 * (attempt + 1)
            print(
                f"Temporary API error. "
                f"Retrying in {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=None)
    parser.add_argument("--kb-dir", default="data/knowledge_base")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output", default="outputs/evaluation.json")
    args = parser.parse_args()

    load_dotenv()

    dataset_dir = (
        args.dataset_dir
        or os.getenv("ZENTOMART_DATA_DIR", "").strip()
    )

    if not dataset_dir:
        parser.error(
            "Pass --dataset-dir or set ZENTOMART_DATA_DIR in .env."
        )

    rows = read_rows(
        Path(dataset_dir) / "practice" / "questions.csv"
    )

    if args.limit:
        rows = rows[:args.limit]

    kb = KnowledgeBase.from_directory(args.kb_dir)
    baseline = SupportAgent(kb, use_retrieval=False)
    rag = SupportAgent(kb, use_retrieval=True)

    results = []
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    for index, row in enumerate(rows, start=1):
        baseline.reset()
        rag.reset()

        prompt = row.get("asr_text") or row["question"]

        result = {
            "id": row.get("id"),
            "intent": row.get("intent"),
            "expected_decision": row.get("expected_decision"),
        }

        for mode, agent in (
            ("prompt_only", baseline),
            ("rag", rag),
        ):
            try:
                response = call_with_retry(agent, prompt)

                mode_result = {
                    "answer": response["answer"],
                    **score_answer(response["answer"], row),
                }

                if mode == "rag":
                    gold = [
                        x.strip()
                        for x in row.get("gold_evidence", "").split(" ; ")
                        if x.strip()
                    ]
                    found_sections = {
                        item["section_id"]
                        for item in response.get("sources", [])
                    }

                    mode_result.update({
                        "gold_evidence": gold,
                        "retrieved_sections": sorted(found_sections),
                        "evidence_hit": bool(
                            set(gold) & found_sections
                        ),
                        "tool_calls": response.get("tool_calls", []),
                    })

                result[mode] = mode_result

            except Exception as exc:
                result[mode] = {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }

        results.append(result)

        # Save after every question, so completed work is preserved.
        output.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"Processed question {index}/{len(rows)}")

    successful_rag = [
        item for item in results
        if "rag" in item and "answer" in item["rag"]
    ]

    print(f"Results saved: {output}")
    print(
        f"Successful RAG answers: "
        f"{len(successful_rag)}/{len(rows)}"
    )

    return 0 if all(
        "answer" in item.get("prompt_only", {})
        and "answer" in item.get("rag", {})
        for item in results
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
