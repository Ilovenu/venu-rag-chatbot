"""Agentic RAG generation via Groq's OpenAI-compatible chat completions API: injects
retrieved context, lets the model call the test-runner tool when asked to run tests,
and returns a final natural-language answer."""

import json

from groq import Groq

import config
import retrieval
import tools

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
- Be concise, specific, and professional.
- Only call the run_playwright_tests tool when the user is clearly asking you to run, \
execute, or check a test — not when they're asking what a test does or where it's \
defined (answer those from the provided code excerpts instead)."""

client = Groq(api_key=config.GROQ_API_KEY)

# Groq/OpenAI-compatible function-calling shape wraps the same name/description/schema
# under a "function" key with the field renamed to "parameters".
GROQ_RUN_TESTS_TOOL = {
    "type": "function",
    "function": {
        "name": tools.RUN_TESTS_TOOL["name"],
        "description": tools.RUN_TESTS_TOOL["description"],
        "parameters": tools.RUN_TESTS_TOOL["input_schema"],
    },
}


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
        tools=[GROQ_RUN_TESTS_TOOL],
        messages=messages,
    )

    message = response.choices[0].message
    tool_used = None

    if response.choices[0].finish_reason == "tool_calls" and message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_input = json.loads(tool_call.function.arguments)
        tool_used = {"name": tool_call.function.name, "input": tool_input}

        tool_result = tools.execute_test_run(rate_limit_key=rate_limit_key, **tool_input)

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            }
        )

        # Force a text summary here instead of passing `tools` again — otherwise the
        # model tends to just re-issue the same tool call instead of summarizing the
        # result it was just given.
        messages.append(
            {
                "role": "user",
                "content": (
                    "Summarize the test run result above in plain language. State the "
                    "exact passed/failed counts and name every failed test, if any."
                ),
            }
        )
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            max_tokens=1024,
            tool_choice="none",
            messages=messages,
        )
        message = response.choices[0].message

    answer_text = message.content or ""

    return {"answer": answer_text, "sources": sources, "tool_used": tool_used}
