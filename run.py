"""Run the ZentroMart agent in text mode while the voice layer is developed."""
from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from src.agent import SupportAgent
from src.retrieval import KnowledgeBase


def main() -> int:
    parser = argparse.ArgumentParser(description="ZentroMart customer-support agent")
    parser.add_argument(
        "--kb-dir",
        default="data/knowledge_base",
        help="Folder containing the extracted ZentroMart kb/*.md files",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of evidence chunks to retrieve")
    args = parser.parse_args()

    load_dotenv()
    kb_path = Path(args.kb_dir)
    try:
        knowledge_base = KnowledgeBase.from_directory(kb_path)
        agent = SupportAgent(knowledge_base)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Setup error: {exc}")
        print("See README.md for setup instructions.")
        return 2

    print("ZentroMart AI Support Agent (text prototype)")
    print("Type 'exit' or 'quit' to stop. This prototype does not yet perform order lookups or create tickets.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        result = agent.respond(question, top_k=args.top_k)
        print(f"Agent: {result['answer']}")
        if result["sources"]:
            print("Evidence used:")
            for source in result["sources"]:
                print(f"  - {source['section_id']} ({source['source']})")
        else:
            print("Evidence used: none retrieved")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
