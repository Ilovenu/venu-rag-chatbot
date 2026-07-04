# src/agents/test_generator.py
# AI-powered test generator — converts natural language to Playwright code
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import json
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.config.settings import settings

logger = logging.getLogger(__name__)


class AITestGenerator:
    """
    Generates complete Playwright test code from natural language descriptions.
    
    Example:
        generator = AITestGenerator()
        code = generator.generate_test(
            "Test that the login page shows error for invalid credentials"
        )
        # Returns complete Playwright TypeScript test code
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY
        )

    def generate_test(self, description: str, url: str = "", tech_stack: str = "TypeScript") -> str:
        """
        Generate a complete Playwright test from a description.
        
        Args:
            description: Natural language test description
            url: Target URL for the test
            tech_stack: 'TypeScript' or 'Python'
            
        Returns:
            Complete test code as string
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert SDET with 16+ years of experience writing 
Playwright {tech_stack} tests. Generate production-quality test code following these standards:

1. Use Page Object Model (POM) pattern
2. Include proper assertions with meaningful error messages
3. Add comments explaining each step
4. Use getByRole(), getByLabel(), getByTestId() for stable selectors
5. Include proper error handling
6. Add screenshot on failure
7. Follow SOLID principles

The developer is Venu Madhav Mahadevu — Staff SDET at Dell Technologies.
Generate ONLY the code, no explanation needed."""),

            ("human", f"""Generate a complete Playwright {tech_stack} test for:

DESCRIPTION: {description}
URL: {url if url else 'Use appropriate URL from context'}

Include:
- Import statements
- Page Object class
- Test spec with beforeEach/afterEach
- At least 3 meaningful assertions
- Screenshot capture on failure
- Data-driven approach if applicable""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({})
        
        generated_code = response.content
        logger.info(f"✅ Generated {tech_stack} test for: {description[:50]}...")
        return generated_code

    def generate_multi_country_test(self, feature: str, countries: list) -> str:
        """
        Generate a data-driven multi-country Playwright test.
        Similar to Dell's global e-commerce framework approach.
        
        Args:
            feature: Feature to test (e.g., 'checkout', 'product search')
            countries: List of country codes ['US', 'UK', 'JP']
            
        Returns:
            Complete data-driven test code
        """
        from src.config.country_configs import COUNTRY_CONFIGS
        
        country_data = {c: COUNTRY_CONFIGS[c] for c in countries if c in COUNTRY_CONFIGS}
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Staff SDET architect who built Dell's global 
e-commerce test framework covering 15+ international markets. Generate 
production-quality data-driven Playwright TypeScript tests."""),

            ("human", f"""Generate a data-driven Playwright TypeScript test for:

FEATURE: {feature}
COUNTRIES: {json.dumps(country_data, indent=2)}

Requirements:
1. Use a config array to drive tests for all countries
2. Set correct locale and timezone per country
3. Validate currency symbol per country
4. Check tax/VAT rates per country
5. Handle different payment methods per country
6. Generate one test spec that covers ALL countries
7. Use descriptive test names like: 'Checkout - United States (USD)'

This should match the Dell architecture that achieved 40% dev time reduction.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content

    def generate_api_test(self, endpoint: str, method: str, description: str) -> str:
        """Generate Playwright API test code."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in API testing with Playwright. Generate clean, production-ready API test code."),
            ("human", f"""Generate a Playwright TypeScript API test:

ENDPOINT: {endpoint}
METHOD: {method}
DESCRIPTION: {description}

Include:
- Request setup with headers
- Response status assertion  
- Response body validation
- Error scenario tests
- Performance check (response time < 2000ms)""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    generator = AITestGenerator()

    print("\n🤖 AI Test Generator Demo\n" + "="*50)

    # Generate basic login test
    print("\n📝 Generating: Login Test")
    login_test = generator.generate_test(
        description="Test user login with valid and invalid credentials, verify error messages",
        url="https://example.com/login",
        tech_stack="TypeScript"
    )
    print(login_test)

    # Generate multi-country test
    print("\n\n🌍 Generating: Multi-Country Test")
    multi_country = generator.generate_multi_country_test(
        feature="product search and cart",
        countries=["US", "UK", "JP", "IN"]
    )
    print(multi_country)
