"""Query both Chroma collections and format retrieved chunks for the LLM prompt."""

import chromadb
from chromadb.utils import embedding_functions

import config

_client = None
_portfolio_collection = None
_codebase_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    return _client


def _get_collections():
    global _portfolio_collection, _codebase_collection
    client = _get_client()
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    if _portfolio_collection is None:
        _portfolio_collection = client.get_or_create_collection(
            name="portfolio", embedding_function=embedding_fn
        )
    if _codebase_collection is None:
        _codebase_collection = client.get_or_create_collection(
            name="codebase", embedding_function=embedding_fn
        )
    return _portfolio_collection, _codebase_collection


def _query_collection(collection, query: str, k: int) -> list[dict]:
    count = collection.count()
    if count == 0:
        return []
    result = collection.query(query_texts=[query], n_results=min(k, count))
    chunks = []
    for doc, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        chunks.append({"document": doc, "metadata": meta, "distance": distance})
    return chunks


def retrieve(query: str, k: int = None) -> list[dict]:
    k = k or config.TOP_K
    portfolio_collection, codebase_collection = _get_collections()
    chunks = _query_collection(portfolio_collection, query, k)
    chunks += _query_collection(codebase_collection, query, k)
    chunks.sort(key=lambda c: c["distance"])
    return chunks


def citation_label(meta: dict) -> str:
    if meta.get("doc_type") == "code":
        symbol = f" — {meta['symbol']}" if meta.get("symbol") else ""
        return f"{meta['source']}:{meta['line_start']}-{meta['line_end']}{symbol}"
    return f"{meta['source']} — {meta['section']}"


def format_context(chunks: list[dict]) -> str:
    blocks = []
    for c in chunks:
        blocks.append(f"[{citation_label(c['metadata'])}]\n{c['document']}")
    return "\n\n".join(blocks)


def dedupe_sources(chunks: list[dict]) -> list[str]:
    seen = []
    for c in chunks:
        label = citation_label(c["metadata"])
        if label not in seen:
            seen.append(label)
    return seen
