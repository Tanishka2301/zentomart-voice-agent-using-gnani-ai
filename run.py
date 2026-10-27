"""Run the ZentroMart support agent in text mode."""
from __future__ import annotations
import argparse
from pathlib import Path
from dotenv import load_dotenv
from src.agent import SupportAgent
from src.retrieval import KnowledgeBase

def main() -> int:
    parser = argparse.ArgumentParser(description="ZentroMart customer-support agent")
    parser.add_argument("--kb-dir", default="data/knowledge_base", help="Folder containing the extracted ZentroMart kb/*.md files")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    load_dotenv()
    try:
        agent = SupportAgent(KnowledgeBase.from_directory(Path(args.kb_dir)))
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Setup error: {exc}")
        print("See README.md for setup instructions.")
        return 2
    print("ZentroMart AI Support Agent")
    print("Type 'exit' or 'quit' to stop. Order lookups require verification.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if question.casefold() in {"exit", "quit"}:
            print("Goodbye.")
            break
        try:
            result = agent.respond(question, top_k=args.top_k)
            print(f"Agent: {result['answer']}")
            if result["sources"]:
                print("Evidence: " + ", ".join(f"{x['section_id']} ({x['source']})" for x in result["sources"]))
            if result["tool_calls"]:
                print("Actions: " + ", ".join(x["tool"] for x in result["tool_calls"]))
        except Exception as exc:
            print(f"Sorry, the request failed safely ({type(exc).__name__}). Please try again.")
        print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
