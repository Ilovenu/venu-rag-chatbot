# 🤖 LangChain + Playwright + MCP — AI-Powered Web Automation Framework

> **Built by:** Venu Madhav Mahadevu | Staff SDET Automation Architect | 16+ Years
> **LinkedIn:** [linkedin.com/in/venumadhav-sdet](https://linkedin.com/in/venumadhav-sdet)

---

## 🌟 What This Project Does

This framework combines **LangChain AI**, **Playwright browser automation**, and **MCP (Model Context Protocol)** to create an intelligent, self-healing, natural-language-driven test automation system.

```
Natural Language Goal
        ↓
   LangChain AI Agent (Brain)
        ↓
   MCP Protocol (Communication)
        ↓
   Playwright Tools (Browser Hands)
        ↓
   Smart Results + Auto Bug Reports
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **AI Test Generation** | Write tests in plain English — AI generates Playwright code |
| 🔧 **Self-Healing Selectors** | Broken selectors auto-fixed by AI |
| 🌍 **Multi-Country Testing** | Data-driven across 15+ locales |
| 🐛 **AI Bug Reporter** | Automatic JIRA tickets with root cause |
| 📊 **Smart Reporting** | AI-generated test summaries |
| 🔌 **MCP Integration** | Model Context Protocol for AI-browser communication |

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **LangChain** — AI agent framework
- **Playwright** — Browser automation
- **MCP** — Model Context Protocol
- **OpenAI GPT-4** — AI brain
- **MongoDB** — Test result persistence
- **Allure** — Test reporting
- **pytest** — Test runner

---

## 📁 Project Structure

```
langchain-playwright-mcp/
├── src/
│   ├── agents/
│   │   ├── test_agent.py          # Main AI test agent
│   │   ├── bug_reporter.py        # AI bug reporter
│   │   └── test_generator.py      # AI test generator
│   ├── tools/
│   │   ├── playwright_tools.py    # Playwright as LangChain tools
│   │   ├── mcp_tools.py           # MCP integration
│   │   └── healing_tools.py       # Self-healing selectors
│   ├── utils/
│   │   ├── mongo_reporter.py      # MongoDB test results
│   │   ├── jira_integration.py    # JIRA auto-ticketing
│   │   └── screenshot_utils.py    # Screenshot helpers
│   └── config/
│       ├── settings.py            # App configuration
│       └── country_configs.py     # 15+ country test data
├── tests/
│   ├── test_ai_agent.py           # AI agent tests
│   ├── test_self_healing.py       # Self-healing tests
│   └── test_multi_country.py      # Multi-country tests
├── .env.example
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/venumadhav/langchain-playwright-mcp
cd langchain-playwright-mcp

# 2. Install dependencies
pip install -r requirements.txt
playwright install

# 3. Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY

# 4. Run demo
python src/agents/test_agent.py

# 5. Run all tests
pytest tests/ -v --alluredir=reports/
```

---

## 📜 License
MIT License — Free to use and modify
