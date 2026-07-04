# src/agents/bug_reporter.py
# AI-powered bug reporter — automatically creates JIRA tickets from test failures
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.config.settings import settings

logger = logging.getLogger(__name__)


class AIBugReporter:
    """
    Automatically generates bug reports from test failures and creates JIRA tickets.
    
    When a Playwright test fails, this agent:
    1. Analyzes the error message and stack trace
    2. Reviews the failure screenshot
    3. Generates a detailed bug report with root cause
    4. Creates a JIRA ticket automatically
    5. Assigns priority based on severity
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.bug_reports = []

    def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: str = "",
        screenshot_path: str = "",
        country: str = "US",
        url: str = ""
    ) -> dict:
        """
        Analyze a test failure and generate a detailed bug report.
        
        Args:
            test_name: Name of the failed test
            error_message: Error message from Playwright
            stack_trace: Full stack trace
            screenshot_path: Path to failure screenshot
            country: Country/locale where failure occurred
            url: URL where failure occurred
            
        Returns:
            Bug report dictionary with JIRA-ready fields
        """
        logger.info(f"🐛 Analyzing failure: {test_name}")

        # Encode screenshot if available
        screenshot_content = ""
        if screenshot_path and Path(screenshot_path).exists():
            with open(screenshot_path, "rb") as f:
                screenshot_content = f"[Screenshot available at: {screenshot_path}]"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior QA engineer and bug triage expert with 16+ years 
of experience. Analyze test failures and generate comprehensive, actionable bug reports.
Return ONLY a valid JSON object with no additional text."""),

            ("human", f"""Analyze this test failure and generate a JIRA bug report:

TEST NAME: {test_name}
COUNTRY/LOCALE: {country}
URL: {url}
ERROR MESSAGE: {error_message}
STACK TRACE: {stack_trace[:1000] if stack_trace else 'Not available'}
SCREENSHOT: {screenshot_content}
TIMESTAMP: {datetime.now().isoformat()}

Return a JSON object with these exact fields:
{{
    "title": "Concise bug title (max 80 chars)",
    "severity": "Critical/High/Medium/Low",
    "priority": "P1/P2/P3/P4",
    "root_cause": "Technical root cause analysis (2-3 sentences)",
    "steps_to_reproduce": ["step 1", "step 2", "step 3"],
    "expected_result": "What should have happened",
    "actual_result": "What actually happened",
    "affected_countries": ["list of potentially affected countries"],
    "component": "UI/API/Database/Network/Authentication",
    "labels": ["automation", "regression", "list of relevant labels"],
    "suggested_fix": "Brief suggestion for developers",
    "test_environment": "Browser/OS/Environment details"
}}""")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            
            # Parse response
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            bug_report = json.loads(content)
            bug_report["test_name"] = test_name
            bug_report["screenshot_path"] = screenshot_path
            bug_report["timestamp"] = datetime.now().isoformat()
            bug_report["status"] = "NEW"

            self.bug_reports.append(bug_report)
            logger.info(f"✅ Bug report generated: [{bug_report['priority']}] {bug_report['title']}")
            return bug_report

        except Exception as e:
            logger.error(f"❌ Bug analysis failed: {str(e)}")
            return {
                "title": f"[AUTO] Test Failed: {test_name}",
                "severity": "High",
                "priority": "P2",
                "root_cause": error_message,
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "status": "NEW"
            }

    def create_jira_ticket(self, bug_report: dict) -> str:
        """
        Create a JIRA ticket from a bug report.
        
        Args:
            bug_report: Bug report dictionary from analyze_failure()
            
        Returns:
            JIRA ticket ID or error message
        """
        if not all([settings.JIRA_URL, settings.JIRA_EMAIL, settings.JIRA_TOKEN]):
            logger.warning("⚠️ JIRA not configured — ticket not created")
            logger.info("📋 Bug Report Preview:")
            logger.info(json.dumps(bug_report, indent=2))
            return "JIRA_NOT_CONFIGURED"

        try:
            from jira import JIRA

            jira = JIRA(
                server=settings.JIRA_URL,
                basic_auth=(settings.JIRA_EMAIL, settings.JIRA_TOKEN)
            )

            # Format description
            description = f"""
*Root Cause:* {bug_report.get('root_cause', '')}

*Steps to Reproduce:*
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(bug_report.get('steps_to_reproduce', [])))}

*Expected Result:* {bug_report.get('expected_result', '')}

*Actual Result:* {bug_report.get('actual_result', '')}

*Suggested Fix:* {bug_report.get('suggested_fix', '')}

*Affected Countries:* {', '.join(bug_report.get('affected_countries', []))}

*Test Name:* {bug_report.get('test_name', '')}
*Timestamp:* {bug_report.get('timestamp', '')}
*Screenshot:* {bug_report.get('screenshot_path', 'N/A')}

_Auto-generated by AI Bug Reporter | LangChain + Playwright + MCP Framework_
_Built by Venu Madhav Mahadevu | Staff SDET Automation Architect_
"""
            issue = jira.create_issue(
                project=settings.JIRA_PROJECT,
                summary=bug_report.get("title", "Automated Test Failure"),
                description=description,
                issuetype={"name": "Bug"},
                priority={"name": bug_report.get("severity", "High")},
                labels=bug_report.get("labels", ["automation"])
            )

            ticket_id = issue.key
            logger.info(f"✅ JIRA ticket created: {ticket_id}")
            bug_report["jira_ticket"] = ticket_id
            return ticket_id

        except Exception as e:
            logger.error(f"❌ JIRA ticket creation failed: {str(e)}")
            return f"ERROR: {str(e)}"

    def generate_failure_summary(self, test_results: list) -> str:
        """
        Generate an AI-powered summary of all test failures.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            Executive summary as formatted string
        """
        failed_tests = [r for r in test_results if r.get("status") != "PASS"]
        if not failed_tests:
            return "✅ All tests passed! No failures to report."

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a QA lead generating executive test summary reports."),
            ("human", f"""Generate an executive summary for these test failures:

FAILURES: {json.dumps(failed_tests, indent=2)}
TOTAL TESTS: {len(test_results)}
PASSED: {len(test_results) - len(failed_tests)}
FAILED: {len(failed_tests)}

Write a concise executive summary (max 200 words) that:
1. States overall test health
2. Identifies patterns in failures
3. Highlights critical issues
4. Recommends next steps
5. Uses bullet points for clarity""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    reporter = AIBugReporter()

    # Demo: Analyze a sample failure
    bug = reporter.analyze_failure(
        test_name="Checkout - Japan (JPY)",
        error_message="TimeoutError: Waiting for selector '#checkout-btn' failed",
        stack_trace="at PWTest.click (/tests/checkout.spec.ts:45:12)",
        country="JP",
        url="https://dell.com/ja-jp/checkout"
    )

    print("\n🐛 Generated Bug Report:")
    print(json.dumps(bug, indent=2))

    # Try to create JIRA ticket (will show preview if not configured)
    ticket = reporter.create_jira_ticket(bug)
    print(f"\n🎫 JIRA Result: {ticket}")
