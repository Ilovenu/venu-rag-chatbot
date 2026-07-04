# src/agents/test_agent.py
# Main AI-powered test agent using LangChain + Playwright + MCP
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import asyncio
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from src.tools.playwright_tools import PLAYWRIGHT_TOOLS, close_browser
from src.tools.healing_tools import healing_engine
from src.config.settings import settings
from src.config.country_configs import COUNTRY_CONFIGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class AITestAgent:
    """
    Main AI-powered test agent.
    
    This agent can:
    - Execute natural language test instructions
    - Navigate websites intelligently
    - Heal broken selectors automatically
    - Generate test reports
    - Run multi-country test scenarios
    """

    def __init__(self, model: str = None, verbose: bool = True):
        self.model = model or settings.OPENAI_MODEL
        self.verbose = verbose
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.agent_executor = self._create_agent()
        self.test_results = []

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with Playwright tools."""
        
        system_prompt = """You are an expert SDET (Software Development Engineer in Test) 
with 16+ years of experience in web automation. You are powered by Playwright browser 
automation tools and specialize in:

1. **Web Navigation**: Browse websites and interact with UI elements
2. **Form Filling**: Fill forms with test data accurately
3. **Validation**: Verify expected outcomes and report failures clearly
4. **Multi-Country Testing**: Handle locale, currency, and timezone differences
5. **AI-Augmented Testing**: Use intelligence to handle dynamic elements

IMPORTANT RULES:
- Always take a screenshot before and after major actions
- Validate each step before proceeding to the next
- Report results clearly with PASS/FAIL status
- If an element is not found, try alternative selectors
- Always verify the current URL after navigation

When executing tests, format your final result as:
✅ PASS: [description] or ❌ FAIL: [description with reason]"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=PLAYWRIGHT_TOOLS,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=PLAYWRIGHT_TOOLS,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=20,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    async def run_test(self, test_instruction: str, test_name: str = "AI Test") -> dict:
        """
        Run a test using natural language instruction.
        
        Args:
            test_instruction: Natural language description of what to test
            test_name: Name for this test case
            
        Returns:
            Test result dictionary with status, steps, and details
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Running Test: {test_name}")
        logger.info(f"📋 Instruction: {test_instruction}")
        logger.info(f"{'='*60}\n")

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent_executor.invoke({
                    "input": test_instruction
                })
            )

            output = result.get("output", "")
            steps = result.get("intermediate_steps", [])

            # Determine pass/fail
            status = "PASS" if "✅" in output or "PASS" in output.upper() else "FAIL"
            if "❌" in output or "FAIL" in output.upper() or "error" in output.lower():
                status = "FAIL"

            test_result = {
                "test_name": test_name,
                "status": status,
                "output": output,
                "steps_count": len(steps),
                "healing_report": healing_engine.get_healing_report()
            }

            self.test_results.append(test_result)
            self._log_result(test_result)
            return test_result

        except Exception as e:
            logger.error(f"❌ Test execution error: {str(e)}")
            test_result = {
                "test_name": test_name,
                "status": "ERROR",
                "output": str(e),
                "steps_count": 0
            }
            self.test_results.append(test_result)
            return test_result

    def _log_result(self, result: dict):
        """Log test result with formatting."""
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        logger.info(f"\n{status_icon} Test: {result['test_name']}")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Steps: {result['steps_count']}")
        if result.get("healing_report", {}).get("total_heals", 0) > 0:
            logger.info(f"   🔧 Self-heals: {result['healing_report']['total_heals']}")

    def get_summary(self) -> dict:
        """Get summary of all test results."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = total - passed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "results": self.test_results
        }

    async def cleanup(self):
        """Clean up browser resources."""
        await close_browser()
        logger.info("🧹 Browser closed")


# ── Demo Scenarios ────────────────────────────────────────────────────────────

async def run_demo():
    """Run demo test scenarios to showcase the framework."""
    
    print("\n" + "="*70)
    print("🤖 LangChain + Playwright + MCP — AI-Powered Test Framework")
    print("   Built by: Venu Madhav Mahadevu | Staff SDET | 16+ Years")
    print("="*70 + "\n")

    agent = AITestAgent(verbose=True)

    # ── Demo 1: Basic Navigation Test ─────────────────────────────────────
    await agent.run_test(
        test_instruction="""
        1. Navigate to https://www.google.com
        2. Verify the page title contains 'Google'
        3. Take a screenshot named 'google_homepage'
        4. Search for 'Playwright automation testing'
        5. Verify search results are displayed
        6. Take a screenshot named 'search_results'
        7. Report PASS if all steps succeeded
        """,
        test_name="Google Search Test"
    )

    # ── Demo 2: Multi-Country Config Test ─────────────────────────────────
    for country_code in ["US", "UK"]:
        config = COUNTRY_CONFIGS[country_code]
        await agent.run_test(
            test_instruction=f"""
            1. Navigate to https://www.google.com
            2. Search for 'Dell XPS laptop {config['currency']}'
            3. Take a screenshot named 'search_{country_code}'
            4. Verify search results appear
            5. Report PASS if results are displayed
            """,
            test_name=f"Product Search - {config['name']} ({config['currency']})"
        )

    # ── Demo 3: Form Interaction Test ─────────────────────────────────────
    await agent.run_test(
        test_instruction="""
        1. Navigate to https://www.google.com
        2. Verify the search input field is visible
        3. Click on the search input field
        4. Type 'LangChain Playwright MCP automation'
        5. Press Enter
        6. Wait for results to load
        7. Take a screenshot named 'langchain_search'
        8. Verify the results page loaded (URL should contain 'search')
        9. Report PASS if completed successfully
        """,
        test_name="Form Interaction & Search Test"
    )

    # Print summary
    summary = agent.get_summary()
    print("\n" + "="*70)
    print("📊 TEST EXECUTION SUMMARY")
    print("="*70)
    print(f"  Total Tests  : {summary['total']}")
    print(f"  ✅ Passed    : {summary['passed']}")
    print(f"  ❌ Failed    : {summary['failed']}")
    print(f"  Pass Rate    : {summary['pass_rate']}")
    print(f"  🔧 AI Heals  : {healing_engine.heal_count}")
    print("="*70 + "\n")

    await agent.cleanup()
    return summary


if __name__ == "__main__":
    asyncio.run(run_demo())
