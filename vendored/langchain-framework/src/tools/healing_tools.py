# src/tools/healing_tools.py
# AI-powered self-healing selector tool
# When selectors break, AI finds the new correct selector automatically
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import json
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class SelfHealingEngine:
    """
    AI-powered self-healing engine that automatically fixes broken selectors.
    When a Playwright action fails due to a selector not found, this engine:
    1. Takes a screenshot of the current page
    2. Analyzes the page HTML
    3. Uses AI to identify the correct new selector
    4. Updates the selector registry for future runs
    """

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.selector_registry = {}  # Stores known good selectors
        self.heal_count = 0

    async def heal_selector(
        self,
        page: Page,
        broken_selector: str,
        action_description: str,
        context: str = ""
    ) -> Optional[str]:
        """
        Try to find a working replacement for a broken selector.

        Args:
            page: Playwright page instance
            broken_selector: The selector that failed
            action_description: What the selector was supposed to do
            context: Additional context about the element

        Returns:
            New working selector or None if healing failed
        """
        logger.warning(f"🔧 Self-healing triggered for: '{broken_selector}'")

        try:
            # Get page HTML for AI analysis
            page_html = await page.content()
            # Truncate to avoid token limits
            page_html_snippet = page_html[:8000]

            # Build AI prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert web automation engineer specializing in 
                Playwright test automation. Your job is to find working CSS selectors 
                for web elements when the original selector has broken.
                
                Analyze the HTML and find the BEST selector for the described element.
                Return ONLY a JSON object with these fields:
                - new_selector: The new CSS/XPath selector that will work
                - selector_type: "css" or "xpath" or "text" or "role"  
                - confidence: 0-100 confidence score
                - reasoning: Brief explanation of why this selector will work
                - fallback_selectors: List of 2-3 alternative selectors"""),

                ("human", f"""The following selector has BROKEN and needs to be healed:

BROKEN SELECTOR: {broken_selector}
ACTION DESCRIPTION: {action_description}
CONTEXT: {context}

CURRENT PAGE HTML (snippet):
{page_html_snippet}

Find the correct selector for this element. Return JSON only.""")
            ])

            chain = prompt | self.llm
            response = chain.invoke({})
            
            # Parse AI response
            result_text = response.content.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            new_selector = result.get("new_selector")
            confidence = result.get("confidence", 0)
            reasoning = result.get("reasoning", "")

            logger.info(f"🤖 AI suggested selector: '{new_selector}' (confidence: {confidence}%)")
            logger.info(f"💡 Reasoning: {reasoning}")

            # Verify the new selector works
            if new_selector:
                try:
                    element = page.locator(new_selector).first
                    is_visible = await element.is_visible(timeout=3000)
                    if is_visible:
                        # Save to registry for future use
                        self.selector_registry[broken_selector] = {
                            "new_selector": new_selector,
                            "confidence": confidence,
                            "fallbacks": result.get("fallback_selectors", [])
                        }
                        self.heal_count += 1
                        logger.info(f"✅ Selector healed successfully! Total heals: {self.heal_count}")
                        return new_selector
                except:
                    # Try fallback selectors
                    for fallback in result.get("fallback_selectors", []):
                        try:
                            element = page.locator(fallback).first
                            is_visible = await element.is_visible(timeout=2000)
                            if is_visible:
                                logger.info(f"✅ Fallback selector worked: '{fallback}'")
                                return fallback
                        except:
                            continue

            logger.error(f"❌ Self-healing failed for: '{broken_selector}'")
            return None

        except Exception as e:
            logger.error(f"❌ Healing engine error: {str(e)}")
            return None

    async def click_with_healing(self, page: Page, selector: str, description: str = "") -> bool:
        """Click an element with automatic self-healing if it fails."""
        try:
            await page.locator(selector).first.click(timeout=5000)
            return True
        except Exception as e:
            logger.warning(f"Click failed for '{selector}': {e}")
            # Try to heal
            healed_selector = await self.heal_selector(page, selector, f"click {description or selector}")
            if healed_selector:
                try:
                    await page.locator(healed_selector).first.click(timeout=5000)
                    return True
                except:
                    pass
            return False

    async def fill_with_healing(self, page: Page, selector: str, value: str, description: str = "") -> bool:
        """Fill an input with automatic self-healing if it fails."""
        try:
            await page.locator(selector).first.fill(value, timeout=5000)
            return True
        except Exception as e:
            logger.warning(f"Fill failed for '{selector}': {e}")
            healed_selector = await self.heal_selector(page, selector, f"fill {description or selector} with {value}")
            if healed_selector:
                try:
                    await page.locator(healed_selector).first.fill(value, timeout=5000)
                    return True
                except:
                    pass
            return False

    def get_healing_report(self) -> dict:
        """Get a report of all healing operations performed."""
        return {
            "total_heals": self.heal_count,
            "healed_selectors": self.selector_registry
        }


# Singleton instance
healing_engine = SelfHealingEngine()
