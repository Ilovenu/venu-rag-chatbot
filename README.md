# Chat with Venu

A RAG chatbot that answers questions about Venu Madhav Mahadevu's resume, his portfolio
projects, and the **actual source code** of those projects — and can trigger real
Playwright test runs on request, reporting results back in chat.

## What it does

- **Resume + portfolio Q&A** — grounded in the real resume PDF and both project READMEs,
  chunked by section/heading (not naive character splits).
- **Codebase Q&A** — indexes the actual TypeScript (Playwright E2E framework) and Python
  (LangChain automation framework) source, chunked per class/function/test so answers
  cite a real `file:line-range`.
- **Test execution tool** — the model can call `run_playwright_tests` to actually run the
  smoke suite, regression suite, a specific test file, or a given browser project, and
  summarize the real pass/fail result.
- Every claim is retrieved, not recalled: the "Sources" footer under each answer is built
  directly from retrieval metadata, never parsed out of the model's own text.

## Architecture

```
ingest_docs.py   → chunks resume.pdf + READMEs        → Chroma "portfolio" collection
ingest_code.py   → chunks vendored/ source (ts + py)   → Chroma "codebase" collection
retrieval.py     → queries both collections, merges + formats context with citations
tools.py         → run_playwright_tests: schema, input hardening, rate limiting, exec
llm.py           → Groq chat completions + tool-use loop, grounded system prompt
app.py           → FastAPI: /api/chat, /api/chat/stream, serves static/
static/          → chat UI (vanilla HTML/CSS/JS, no build step)
```

**LLM provider:** [Groq](https://groq.com) (OpenAI-compatible chat completions API),
default model `llama-3.3-70b-versatile`.

**Embeddings:** Chroma's local default embedding function (`all-MiniLM-L6-v2` via
`onnxruntime`) — no separate API key needed.

**Vendored source:** `vendored/playwright-framework/` and `vendored/langchain-framework/`
are committed copies of both projects' source, used only for code-RAG ingestion (read as
plain text, never executed). This keeps ingestion self-contained — a deployed container
has no access to sibling folders on your local machine, and the LangChain project's
source was never pushed to GitHub, so it can't be cloned at build time either. If you
change the original projects, re-copy the changed files into `vendored/` and re-run
`ingest_code.py`.

**Test-runner tool vs. vendored source:** these are different concerns. The
`run_playwright_tests` tool needs a full, live, `npm install`-ed clone with Playwright
browsers — not just source text — so it always points at `PLAYWRIGHT_REPO_PATH` (the
real sibling repo locally; a fresh `git clone` of the GitHub repo in the Render build
step, since that repo's actual Playwright project *is* pushed to GitHub).

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate          # or: source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # paste in your GROQ_API_KEY

python ingest_docs.py           # builds the "portfolio" Chroma collection
python ingest_code.py           # builds the "codebase" Chroma collection

uvicorn app:app --reload
# open http://localhost:8000
```

Optional CLI sanity check before touching the web UI:

```bash
python query_cli.py "What testing frameworks does Venu know?"
```

## Deploying to Render

`render.yaml` is included (Render "Blueprint" format):

1. Push this repo to GitHub.
2. In Render: New → Blueprint → point at the repo.
3. Set the `GROQ_API_KEY` secret when prompted (it's marked `sync: false` so Render asks
   for it rather than committing it).
4. Deploy. The build step installs Python deps, clones the real Playwright framework repo
   fresh (for the test-runner tool), installs its npm deps + browsers, then runs both
   ingestion scripts so the Chroma collections are rebuilt on every deploy — no paid
   persistent disk needed for a corpus this size.

### Public-access hardening

Since this is deployed for anyone to use, not just you:

- **Per-IP rate limiting** (in-memory, no Redis needed at this scale): a general limit on
  `/api/chat` (`CHAT_RATE_LIMIT_PER_HOUR`, default 60) and a much tighter one on the
  test-runner tool specifically (`TEST_RUN_RATE_LIMIT_PER_HOUR`, default 3), since that
  one spins up a real subprocess.
- **Input hardening on `test_file`**: allow-list pattern (`^[a-zA-Z0-9_/-]+\.spec\.ts$`)
  plus a path-containment check that resolves the path and verifies it's still inside
  the repo's `tests/` directory — blocks path traversal and shell metacharacter
  injection regardless of what the model's tool schema otherwise allows.
- **`--headed` is always ignored** unless `ALLOW_HEADED=true` is explicitly set — a
  headless server deployment has no display, and a public deployment shouldn't be able
  to pop a visible browser window regardless.
- **Every argument is re-validated in Python** (`suite`/`project`/`tag` allow-lists),
  not just trusted from the tool's JSON-schema `enum` — defense in depth in case a model
  call ever supplies something outside the schema.

## Known limitations (documented tradeoffs, not bugs)

- **Streaming is chunked-after-generation, not true token streaming.** The manual
  tool-use loop (check `finish_reason` → maybe execute a tool → maybe call again) doesn't
  compose trivially with true incremental streaming, so `/api/chat/stream` runs the full
  request to completion and then re-chunks the text over SSE for a "typing" feel in the
  UI. A future version could stream the first (non-tool-use) turn natively and fall back
  to chunking only when a tool call is involved.
- **Local embeddings (MiniLM) are weaker than a hosted model** on nuanced paraphrase
  queries — acceptable at this corpus size (~150 chunks total), where the correct chunk
  reliably lands in the top-8 results even when ranked slightly below a coincidentally
  similar one.
- **Resume/persona discrepancy**: source documents describe Venu's experience somewhat
  differently across documents (e.g. years of experience, exact title). The system
  prompt deliberately never hardcodes these facts — it only ever states what a specific
  retrieved excerpt says, so the bot can't contradict (or be contradicted by) the actual
  documents.

## License

MIT
