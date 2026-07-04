"""FastAPI backend: non-streaming and streaming chat endpoints, static file serving."""

import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
import llm
from tools import RateLimiter

app = FastAPI(title="Chat with Venu")

chat_limiter = RateLimiter(config.CHAT_RATE_LIMIT_PER_HOUR)


class ChatRequest(BaseModel):
    message: str


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@app.post("/api/chat")
def chat(payload: ChatRequest, request: Request):
    key = client_key(request)
    if not chat_limiter.allow(key):
        return {
            "answer": f"Rate limit reached ({config.CHAT_RATE_LIMIT_PER_HOUR} messages/hour). Please try again later.",
            "sources": [],
        }
    result = llm.answer_question(payload.message, rate_limit_key=key)
    return result


@app.post("/api/chat/stream")
def chat_stream(payload: ChatRequest, request: Request):
    key = client_key(request)

    def event_stream():
        if not chat_limiter.allow(key):
            msg = f"Rate limit reached ({config.CHAT_RATE_LIMIT_PER_HOUR} messages/hour). Please try again later."
            yield f"event: token\ndata: {json.dumps({'text': msg})}\n\n"
            yield f"event: done\ndata: {json.dumps({'sources': []})}\n\n"
            return

        result = llm.answer_question(payload.message, rate_limit_key=key)
        # Chunk the answer for a streaming feel (llm.answer_question already ran to
        # completion — see the note in README about upgrading to true token streaming).
        text = result["answer"]
        chunk_size = 20
        for i in range(0, len(text), chunk_size):
            yield f"event: token\ndata: {json.dumps({'text': text[i : i + chunk_size]})}\n\n"
        yield f"event: done\ndata: {json.dumps({'sources': result['sources']})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
