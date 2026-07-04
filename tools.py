"""The run_playwright_tests tool: schema, input hardening, rate limiting, and execution."""

import re
import subprocess
import time
from pathlib import Path

import config

RUN_TESTS_TOOL = {
    "name": "run_playwright_tests",
    "description": (
        "Run tests from Venu's Playwright E2E framework and report pass/fail results. "
        "Use when the user asks to run, execute, check, or verify tests — a specific "
        "test file, the smoke suite, the regression suite, or tests for a particular "
        "browser/suite. Do not use this to answer questions about what a test does — "
        "answer those from the retrieved code context instead."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "suite": {"type": "string", "enum": ["ui", "api", "hybrid", "all"]},
            "project": {
                "type": "string",
                "enum": ["chromium", "firefox", "webkit", "api", "hybrid-chromium"],
            },
            "tag": {"type": "string", "enum": ["@smoke", "@regression", "@hybrid", "@api"]},
            "test_file": {
                "type": "string",
                "description": "Path relative to tests/, e.g. 'ui/auth/login.spec.ts'",
            },
            "headed": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
}

_ALLOWED_SUITES = {"ui", "api", "hybrid", "all"}
_ALLOWED_PROJECTS = {"chromium", "firefox", "webkit", "api", "hybrid-chromium"}
_ALLOWED_TAGS = {"@smoke", "@regression", "@hybrid", "@api"}
_TEST_FILE_PATTERN = re.compile(r"^[a-zA-Z0-9_/-]+\.spec\.ts$")


class RateLimiter:
    """In-memory per-key sliding-window rate limiter (no Redis needed at this scale)."""

    def __init__(self, limit_per_hour: int):
        self.limit_per_hour = limit_per_hour
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start = now - 3600
        hits = [t for t in self._hits.get(key, []) if t > window_start]
        if len(hits) >= self.limit_per_hour:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True


test_run_limiter = RateLimiter(config.TEST_RUN_RATE_LIMIT_PER_HOUR)


class ToolInputError(ValueError):
    pass


def _validate_test_file(test_file: str) -> str:
    """Allow-list validation + path-containment check — blocks path traversal and shell
    metacharacter injection regardless of what the model's tool schema otherwise allows."""
    if not _TEST_FILE_PATTERN.match(test_file):
        raise ToolInputError(f"Invalid test_file format: {test_file!r}")

    repo_root = Path(config.PLAYWRIGHT_REPO_PATH).resolve()
    tests_root = (repo_root / "tests").resolve()
    candidate = (tests_root / test_file).resolve()

    if tests_root not in candidate.parents and candidate != tests_root:
        raise ToolInputError(f"test_file escapes the tests/ directory: {test_file!r}")
    if not candidate.is_file():
        raise ToolInputError(f"test_file does not exist: {test_file!r}")

    return test_file


def _parse_results(output: str) -> dict:
    passed_match = re.search(r"(\d+)\s+passed", output)
    failed_match = re.search(r"(\d+)\s+failed", output)
    failed_names = re.findall(r"^\s*x\s+\d+\s+(.+)$", output, re.MULTILINE)

    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "failed_test_names": failed_names[:10],
    }


def execute_test_run(
    rate_limit_key: str,
    suite: str | None = None,
    project: str | None = None,
    tag: str | None = None,
    test_file: str | None = None,
    headed: bool = False,
) -> dict:
    if not test_run_limiter.allow(rate_limit_key):
        return {
            "error": (
                f"Rate limit reached ({config.TEST_RUN_RATE_LIMIT_PER_HOUR} runs/hour). "
                "Please try again later."
            )
        }

    if suite is not None and suite not in _ALLOWED_SUITES:
        return {"error": f"Invalid suite: {suite!r}"}
    if project is not None and project not in _ALLOWED_PROJECTS:
        return {"error": f"Invalid project: {project!r}"}
    if tag is not None and tag not in _ALLOWED_TAGS:
        return {"error": f"Invalid tag: {tag!r}"}

    cmd = ["npx", "playwright", "test"]

    if test_file:
        try:
            validated = _validate_test_file(test_file)
        except ToolInputError as e:
            return {"error": str(e)}
        cmd.append(f"tests/{validated}")
    elif suite and suite != "all":
        cmd.append(f"tests/{suite}")

    if project:
        cmd.append(f"--project={project}")
    if tag:
        cmd.append(f"--grep={tag}")
    if headed and config.ALLOW_HEADED:
        cmd.append("--headed")

    # subprocess.run(list, shell=True) is NOT equivalent across platforms: on POSIX,
    # only cmd[0] becomes the actual shell command and the rest are passed as unused
    # positional shell args ($1, $2, ...) -- silently running bare "npx" with no
    # arguments. Join into a single string so shell=True behaves the same (and
    # correctly) on both Windows and Linux.
    cmd_str = " ".join(cmd)

    try:
        result = subprocess.run(
            cmd_str,
            cwd=config.PLAYWRIGHT_REPO_PATH,
            capture_output=True,
            text=True,
            shell=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return {"error": "Test run timed out after 5 minutes."}

    # Logged server-side (captured by the host's log stream) so failures can be
    # diagnosed without needing a dedicated debug endpoint.
    print(f"[run_playwright_tests] cmd={' '.join(cmd)!r} exit_code={result.returncode}")
    print(f"[run_playwright_tests] stdout:\n{result.stdout[-3000:]}")
    print(f"[run_playwright_tests] stderr:\n{result.stderr[-2000:]}")

    parsed = _parse_results(result.stdout)
    response = {
        "exit_code": result.returncode,
        "command": " ".join(cmd),
        **parsed,
    }
    if result.returncode != 0 and parsed["passed"] == 0 and parsed["failed"] == 0:
        # Real execution failure (not just failing tests) -- surface a hint instead of
        # silently reporting "0 passed, 0 failed" as if the suite were simply empty.
        response["error"] = "The test run failed to execute (see stderr for details)."
        response["stderr_snippet"] = result.stderr[-500:]
    return response
