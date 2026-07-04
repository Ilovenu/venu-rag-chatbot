"""Standalone CLI to sanity-check retrieval quality before wiring up the LLM."""

import sys

sys.stdout.reconfigure(encoding="utf-8")

import retrieval


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        run(question)
        return

    print("Interactive retrieval check. Type a question (or 'quit').")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        run(question)


def run(question: str) -> None:
    chunks = retrieval.retrieve(question)
    print(f"\nQuery: {question}")
    print(f"Retrieved {len(chunks)} chunks:\n")
    for c in chunks:
        label = retrieval.citation_label(c["metadata"])
        print(f"  [{c['distance']:.3f}] {label}")
        print(f"      {c['document'][:120]!r}")


if __name__ == "__main__":
    main()
