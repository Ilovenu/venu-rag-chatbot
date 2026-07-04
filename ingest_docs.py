"""Chunk the resume PDF and project READMEs into the 'portfolio' Chroma collection."""

import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

import config

RESUME_SECTION_HEADERS = [
    "PROFESSIONAL SUMMARY",
    "TECHNOLOGY COMPETENCIES",
    "CORE SKILLS",
    "PROFESSIONAL EXPERIENCE",
    "KEY ACHIEVEMENTS",
    "CERTIFICATIONS",
    "EDUCATION",
    "PROJECT HIGHLIGHTS",
]

# Exact employer-opening lines within PROFESSIONAL EXPERIENCE, in resume order.
JOB_ENTRY_MARKERS = [
    "Perigon Infotech",
    "Dell Technologies",
    "UST Global",
    "Dell Technologies",
    "Capgemini India",
    "Earlier Experience",
]

MAX_CHUNK_CHARS = 1000
CHUNK_OVERLAP = 200


def clean_resume_lines(raw_text: str) -> list[str]:
    lines = raw_text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in ("•", "-"):
            continue
        if stripped.isdigit():  # bare page-number artifact
            continue
        cleaned.append(stripped)
    return cleaned


def split_resume_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in lines:
        if line in RESUME_SECTION_HEADERS:
            current = line
            sections[current] = []
            continue
        if current is None:
            continue  # skip the name/title/contact-info preamble
        sections[current].append(line)
    return sections


def split_job_entries(lines: list[str]) -> list[tuple[str, list[str]]]:
    entries: list[tuple[str, list[str]]] = []
    current_label = None
    current_lines: list[str] = []
    remaining_markers = list(JOB_ENTRY_MARKERS)

    for line in lines:
        if remaining_markers and line.startswith(remaining_markers[0]):
            if current_label is not None:
                entries.append((current_label, current_lines))
            current_label = line
            current_lines = []
            remaining_markers.pop(0)
            continue
        current_lines.append(line)

    if current_label is not None:
        entries.append((current_label, current_lines))
    return entries


def chunk_resume() -> list[dict]:
    reader = PdfReader(str(config.RESUME_PATH))
    raw_text = "\n".join(page.extract_text() for page in reader.pages)
    lines = clean_resume_lines(raw_text)
    sections = split_resume_sections(lines)

    chunks = []
    chunk_index = 0
    for header, section_lines in sections.items():
        if header == "PROFESSIONAL EXPERIENCE":
            for label, entry_lines in split_job_entries(section_lines):
                text = f"{label}\n" + "\n".join(entry_lines)
                chunks.append(
                    {
                        "document": text[:MAX_CHUNK_CHARS],
                        "metadata": {
                            "source": "resume.pdf",
                            "doc_type": "resume",
                            "section": f"Professional Experience — {label}",
                            "chunk_index": chunk_index,
                        },
                    }
                )
                chunk_index += 1
        else:
            text = "\n".join(section_lines)
            chunks.append(
                {
                    "document": text[:MAX_CHUNK_CHARS],
                    "metadata": {
                        "source": "resume.pdf",
                        "doc_type": "resume",
                        "section": header.title(),
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1
    return chunks


def recursive_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    parts = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        parts.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return parts


def find_markdown_headers(text: str) -> list[re.Match]:
    """Match `^#{1,3} ...` headers, skipping any that fall inside a fenced code block
    (``` ... ```) — e.g. a `# 1. Clone the repo` shell comment inside a bash fence."""
    header_pattern = re.compile(r"^#{1,3}\s+.+$", re.MULTILINE)
    fence_pattern = re.compile(r"^```", re.MULTILINE)

    fence_starts = sorted(m.start() for m in fence_pattern.finditer(text))
    in_fence_ranges = []
    for i in range(0, len(fence_starts) - 1, 2):
        in_fence_ranges.append((fence_starts[i], fence_starts[i + 1]))

    def inside_fence(pos: int) -> bool:
        return any(start <= pos < end for start, end in in_fence_ranges)

    return [m for m in header_pattern.finditer(text) if not inside_fence(m.start())]


def chunk_markdown(path, source_name: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    matches = find_markdown_headers(text)

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = match.group().lstrip("#").strip()
        sections.append((title, text[start:end]))

    if not sections:
        sections = [(source_name, text)]

    chunks = []
    chunk_index = 0
    for title, body in sections:
        for piece in recursive_split(body, MAX_CHUNK_CHARS, CHUNK_OVERLAP):
            chunks.append(
                {
                    "document": piece,
                    "metadata": {
                        "source": source_name,
                        "doc_type": "project_readme",
                        "section": title,
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1
    return chunks


def chunk_plain_sections(path, source_name: str, doc_type: str) -> list[dict]:
    """Split a plain-text file on '---' divider lines into per-entry sections (e.g. one
    per employer), titling each from its first line."""
    text = path.read_text(encoding="utf-8")
    raw_sections = [s.strip() for s in re.split(r"\n-{3,}\n", text) if s.strip()]

    chunks = []
    chunk_index = 0
    for section in raw_sections:
        first_line = section.splitlines()[0].strip()
        title = first_line.removeprefix("Company:").strip() if first_line.startswith("Company:") else first_line.title()
        for piece in recursive_split(section, MAX_CHUNK_CHARS, CHUNK_OVERLAP):
            chunks.append(
                {
                    "document": piece,
                    "metadata": {
                        "source": source_name,
                        "doc_type": doc_type,
                        "section": title,
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1
    return chunks


def main() -> None:
    chunks = chunk_resume()
    chunks += chunk_markdown(config.MCP_AGENT_README_PATH, "mcp_agent_readme.md")
    chunks += chunk_markdown(config.LANGCHAIN_README_PATH, "langchain_readme.md")
    chunks += chunk_plain_sections(config.WORK_HISTORY_PATH, "work_history.txt", "work_history")

    print(f"Collected {len(chunks)} portfolio chunks.")

    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(name="portfolio", embedding_function=embedding_fn)

    ids = [f"{c['metadata']['source']}-{c['metadata']['chunk_index']}" for c in chunks]
    documents = [c["document"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Upserted {len(ids)} chunks into the 'portfolio' collection at {config.CHROMA_PATH}")

    for c in chunks:
        m = c["metadata"]
        print(f"\n--- [{m['source']}] {m['section']} ({len(c['document'])} chars) ---")
        print(c["document"][:180])


if __name__ == "__main__":
    main()
