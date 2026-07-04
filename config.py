import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

CHROMA_PATH = os.environ.get("CHROMA_PATH", str(BASE_DIR / "data" / "chroma_db"))
TOP_K = int(os.environ.get("TOP_K", "4"))

SOURCE_DIR = BASE_DIR / "data" / "source"
RESUME_PATH = SOURCE_DIR / "resume.pdf"
MCP_AGENT_README_PATH = SOURCE_DIR / "mcp_agent_readme.md"
LANGCHAIN_README_PATH = SOURCE_DIR / "langchain_readme.md"
WORK_HISTORY_PATH = SOURCE_DIR / "Venu.txt"

# Used only by the test-runner tool, which needs a full, live, `npm install`-ed clone
# with Playwright browsers available — not just source text. Locally this is the real
# sibling repo; in a Render deploy the build step clones it fresh from GitHub instead
# (see render.yaml), since the container has no access to the local filesystem.
PLAYWRIGHT_REPO_PATH = os.environ.get(
    "PLAYWRIGHT_REPO_PATH",
    r"C:\Users\venum\OneDrive\Desktop\Venu\MCP_Agent\MCP_Agent",
)

# Used only for code RAG ingestion (read as plain text, never executed) — vendored
# copies committed into this repo under vendored/, so ingestion is self-contained and
# doesn't depend on sibling folders existing (they won't, in a deployed container, and
# the LangChain repo's actual source was never pushed to GitHub to begin with).
VENDORED_DIR = BASE_DIR / "vendored"
VENDORED_PLAYWRIGHT_SRC = VENDORED_DIR / "playwright-framework"
VENDORED_LANGCHAIN_SRC = VENDORED_DIR / "langchain-framework"

CHAT_RATE_LIMIT_PER_HOUR = int(os.environ.get("CHAT_RATE_LIMIT_PER_HOUR", "60"))
TEST_RUN_RATE_LIMIT_PER_HOUR = int(os.environ.get("TEST_RUN_RATE_LIMIT_PER_HOUR", "3"))

# Headed (visible-browser) test runs only make sense on a local machine with a display —
# a headless server deployment (e.g. Render) has no display and would just error out.
# Off by default; only flip on for local dev.
ALLOW_HEADED = os.environ.get("ALLOW_HEADED", "false").lower() == "true"
