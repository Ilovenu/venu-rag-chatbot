# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Playwright
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER: str = os.getenv("BROWSER", "chromium")
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30000"))
    
    # MCP
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    
    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "test_results")
    
    # JIRA
    JIRA_URL: str = os.getenv("JIRA_URL", "")
    JIRA_EMAIL: str = os.getenv("JIRA_EMAIL", "")
    JIRA_TOKEN: str = os.getenv("JIRA_TOKEN", "")
    JIRA_PROJECT: str = os.getenv("JIRA_PROJECT", "AUTO")
    
    # Reports
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "reports")
    SCREENSHOTS_DIR: str = os.getenv("SCREENSHOTS_DIR", "reports/screenshots")

settings = Settings()
