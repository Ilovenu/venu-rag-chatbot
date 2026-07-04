# src/utils/mongo_reporter.py
# MongoDB test result persistence — stores and analyzes test trends
# Built by Venu Madhav Mahadevu | Staff SDET Automation Architect

import logging
from datetime import datetime
from typing import Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)


class MongoTestReporter:
    """
    Stores test results in MongoDB for trend analysis and executive dashboards.
    This matches the architecture used at Dell Technologies.
    """

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Connect to MongoDB."""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
            self.client.server_info()  # Test connection
            self.db = self.client[settings.MONGO_DB]
            self.collection = self.db["test_results"]
            logger.info("✅ MongoDB connected")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB not available (using local only): {str(e)}")
            self.client = None

    def save_result(self, result: dict, country: str = "US", run_id: str = "") -> bool:
        """Save a test result to MongoDB."""
        if not self.client:
            logger.info(f"📝 [LOCAL] Test: {result.get('test_name')} | Status: {result.get('status')}")
            return False
        try:
            doc = {
                **result,
                "country": country,
                "run_id": run_id or datetime.now().strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.now(),
                "framework": "LangChain + Playwright + MCP",
                "engineer": "Venu Madhav Mahadevu"
            }
            self.collection.insert_one(doc)
            logger.info(f"✅ Saved to MongoDB: {result.get('test_name')}")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB save failed: {str(e)}")
            return False

    def get_trend(self, days: int = 7, country: str = None) -> dict:
        """Get test trend for the last N days."""
        if not self.client:
            return {"error": "MongoDB not connected"}
        try:
            from datetime import timedelta
            query = {"timestamp": {"$gte": datetime.now() - timedelta(days=days)}}
            if country:
                query["country"] = country
            results = list(self.collection.find(query))
            total = len(results)
            passed = sum(1 for r in results if r.get("status") == "PASS")
            return {
                "period": f"Last {days} days",
                "country": country or "All",
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A"
            }
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")
