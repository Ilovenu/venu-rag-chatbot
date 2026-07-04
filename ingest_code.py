"""Chunk source files from both portfolio repos into the 'codebase' Chroma collection.

Python files are chunked with the ast module (one chunk per top-level class/function).
TypeScript files are chunked with a brace-depth-tracking splitter (one chunk per
top-level class/interface/function/test block), since adding a real TS parser would
require a Node.js bridge.
"""

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import chromadb
from chromadb.utils import embedding_functions

import config

PY_REPOS = [("langchain-framework", config.VENDORED_LANGCHAIN_SRC / "src")]
TS_REPOS = [
    ("playwright-framework", config.VENDORED_PLAYWRIGHT_SRC / "src"),
    ("playwright-framework", config.VENDORED_PLAYWRIGHT_SRC / "tests"),
]

MAX_CHUNK_CHARS = 1200


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()


def chunk_python_file(path: Path, repo: str, rel_source: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            segment = ast.get_source_segment(text, node)
            if not segment:
                continue
            chunks.append(
                {
                    "document": segment[:MAX_CHUNK_CHARS],
                    "metadata": {
                        "source": rel_source,
                        "repo": repo,
                        "doc_type": "code",
                        "symbol": node.name,
                        "language": "python",
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                    },
                }
            )

    if not chunks and lines:
        # Fallback: no class/function definitions found (e.g. a plain script) — one chunk for the file.
        chunks.append(
            {
                "document": text[:MAX_CHUNK_CHARS],
                "metadata": {
                    "source": rel_source,
                    "repo": repo,
                    "doc_type": "code",
                    "symbol": None,
                    "language": "python",
                    "line_start": 1,
                    "line_end": len(lines),
                },
            }
        )
    return chunks


TS_BRACE_BODIED_PATTERN = re.compile(
    r"^(export\s+)?(class|interface|function)\s+(\w+)"
    r"|^\s*test(\.describe)?\s*\(\s*['\"](.+?)['\"]",
    re.MULTILINE,
)

TS_CONST_PATTERN = re.compile(r"^(export\s+)?const\s+(\w+)", re.MULTILINE)

BRACKET_OPEN = {"{": "}", "[": "]", "(": ")"}
BRACKET_CLOSE = {"}", "]", ")"}


def find_matching_brace(text: str, open_brace_index: int) -> int:
    depth = 0
    for i in range(open_brace_index, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def find_statement_end(text: str, start_index: int) -> int:
    """Scan forward from a `const` declaration to the terminating top-level semicolon,
    tracking bracket depth so a `;` inside an object/array/regex literal doesn't end the
    statement early."""
    depth = 0
    for i in range(start_index, len(text)):
        ch = text[i]
        if ch in BRACKET_OPEN:
            depth += 1
        elif ch in BRACKET_CLOSE:
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            return i
    return len(text) - 1


def chunk_typescript_file(path: Path, repo: str, rel_source: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")

    spans = []
    for match in TS_BRACE_BODIED_PATTERN.finditer(text):
        symbol = match.group(3) or match.group(5) or "test"

        # For `test('...', async ({ destructured }) => { body })`, the callback's
        # destructured-params object has its own `{...}` that appears *before* the
        # arrow — searching for the first bare `{` latches onto that and truncates the
        # chunk to just the parameter list. Whenever an arrow function follows within a
        # reasonable window, the real body brace is the first `{` *after* the arrow;
        # class/interface declarations have no arrow, so they fall back to the plain
        # first-brace search.
        arrow_index = text.find("=>", match.end(), match.end() + 400)
        if arrow_index != -1:
            brace_index = text.find("{", arrow_index)
        else:
            brace_index = text.find("{", match.end())

        if brace_index == -1:
            continue
        end_index = find_matching_brace(text, brace_index)
        spans.append((match.start(), end_index, symbol))

    for match in TS_CONST_PATTERN.finditer(text):
        symbol = match.group(2)
        end_index = find_statement_end(text, match.end())
        spans.append((match.start(), end_index, symbol))

    if not spans:
        lines = text.splitlines()
        return [
            {
                "document": text[:MAX_CHUNK_CHARS],
                "metadata": {
                    "source": rel_source,
                    "repo": repo,
                    "doc_type": "code",
                    "symbol": None,
                    "language": "typescript",
                    "line_start": 1,
                    "line_end": len(lines),
                },
            }
        ]

    spans.sort(key=lambda s: s[0])

    chunks = []
    for start, end, symbol in spans:
        segment = text[start : end + 1]
        line_start = text.count("\n", 0, start) + 1
        line_end = text.count("\n", 0, end) + 1

        chunks.append(
            {
                "document": segment[:MAX_CHUNK_CHARS],
                "metadata": {
                    "source": rel_source,
                    "repo": repo,
                    "doc_type": "code",
                    "symbol": symbol,
                    "language": "typescript",
                    "line_start": line_start,
                    "line_end": line_end,
                },
            }
        )
    return chunks


def collect_chunks() -> list[dict]:
    all_chunks = []

    for repo, root in PY_REPOS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            rel_source = str(path.relative_to(root.parent)).replace("\\", "/")
            all_chunks.extend(chunk_python_file(path, repo, rel_source))

    for repo, root in TS_REPOS:
        if not root.exists():
            continue
        for path in root.rglob("*.ts"):
            rel_source = str(path.relative_to(root.parent)).replace("\\", "/")
            all_chunks.extend(chunk_typescript_file(path, repo, rel_source))

    return all_chunks


def main() -> None:
    chunks = collect_chunks()
    print(f"Collected {len(chunks)} code chunks.")

    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(name="codebase", embedding_function=embedding_fn)

    ids = [
        f"{c['metadata']['repo']}:{c['metadata']['source']}:{c['metadata']['line_start']}"
        for c in chunks
    ]
    documents = [c["document"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Upserted {len(ids)} chunks into the 'codebase' collection at {config.CHROMA_PATH}")

    for c in chunks[:5]:
        m = c["metadata"]
        print(f"\n--- {m['source']}:{m['line_start']}-{m['line_end']} ({m['symbol']}) ---")
        print(c["document"][:200])


if __name__ == "__main__":
    main()
