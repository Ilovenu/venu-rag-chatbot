"""RAG generation via Groq's OpenAI-compatible chat completions API: injects retrieved
context and returns a grounded natural-language answer. Q&A only -- no tool use."""

from groq import Groq

import config
import retrieval

SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions about \
Venu Madhav Mahadevu — his resume/experience, his portfolio projects, and the actual \
source code of those projects — based strictly on the reference excerpts provided in \
each user message.

Guidelines:
- Answer only using the provided context excerpts. If the answer isn't contained in \
them, say so plainly rather than guessing or inventing details.
- Never invent job titles, dates, years of experience, or skills not present in the \
provided context — different sources may describe his experience differently; always \
defer to what the retrieved excerpts actually say rather than assuming one framing.
- When explaining code, reference the specific file and line citation shown in the \
excerpt (e.g. "in src/api/apiClient.ts:27-81").
- Be concise, specific, and professional."""

client = Groq(api_key=config.GROQ_API_KEY)


def build_user_message(question: str, chunks: list[dict]) -> str:
    context_block = retrieval.format_context(chunks)
    return f"Context:\n{context_block}\n\nQuestion: {question}"


def answer_question(question: str, rate_limit_key: str) -> dict:
    chunks = retrieval.retrieve(question)
    sources = retrieval.dedupe_sources(chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(question, chunks)},
    ]

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        max_tokens=1024,
        messages=messages,
    )

    answer_text = response.choices[0].message.content or ""

    return {"answer": answer_text, "sources": sources}
