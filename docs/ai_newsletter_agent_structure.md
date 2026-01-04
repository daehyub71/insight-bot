# 📂 Project Structure: AI Daily Briefing Agent (InsightBot)

This document outlines the recommended directory structure for the InsightBot project, designed for scalability and maintainability using Python and LangGraph.

## 🏗️ Directory Tree

```plaintext
insight-bot/
├── .github/
│   └── workflows/
│       └── daily_briefing.yml    # GitHub Actions Workflow (Cron Schedule)
├── config/
│   ├── settings.yaml             # Global configuration (URL sources, thresholds)
│   └── secrets.example.yaml      # Template for API keys (never commit real secrets)
├── src/
│   ├── __init__.py
│   ├── main.py                   # Application Entry Point (LangGraph Runner)
│   ├── graph.py                  # LangGraph Construction (Nodes & Edges)
│   ├── state.py                  # State definitions (TypedDict)
│   ├── collectors/               # [Phase 1] Data Collection Modules
│   │   ├── __init__.py
│   │   ├── arxiv_collector.py
│   │   ├── rss_crawler.py
│   │   └── web_scraper.py
│   ├── processors/               # [Phase 2] LLM Processing Modules
│   │   ├── __init__.py
│   │   ├── filters.py            # Relevance Scoring Logic
│   │   ├── summarizer.py         # Summary Generation (3-step prompt)
│   │   └── insight_generator.py  # Insight Extraction
│   ├── publishers/               # [Phase 4] Distribution Modules
│   │   ├── __init__.py
│   │   ├── email_sender.py
│   │   ├── slack_bot.py
│   │   └── tts_generator.py      # (Optional) Audio briefing
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging setup
│       └── llm_client.py         # OpenAI API Wrapper
├── templates/                    # [Phase 3] Formatting Templates
│   ├── email_template.html       # Jinja2 HTML Template
│   └── slack_template.md         # Markdown Template
├── tests/                        # Unit & Integration Tests
│   ├── __init__.py
│   ├── test_collectors.py
│   └── test_processors.py
├── .env.example                  # Environment variables example
├── .gitignore                    # Python gitignore
├── README.md                     # Project Documentation
└── requirements.txt              # Dependency List (langgraph, openai, etc.)
```

## 📝 Key Components Description

### 1. Root Configuration
*   **.github/workflows/daily_briefing.yml**: The heartbeat of the system. Configured to run `python src/main.py` every day at a specific time using `cron`.
*   **config/settings.yaml**: Central place to manage target ArXiv categories, RSS feed URLs, and LLM scoring thresholds.

### 2. Source Code (`src/`)
*   **main.py**: Initializes the LangGraph and executes the workflow. It's the command-line entry point.
*   **graph.py**: Defines the "Flow". It allows you to visualize and manage how data moves from `Collector` -> `Filter` -> `Summary` -> `Publisher`.
*   **state.py**: Defines the data structure (schema) passed between nodes. For example, a list of `Article` objects containing title, url, summary, score.

### 3. Modules
*   **collectors/**: Pure Python scripts to fetch raw text. Each file handles a specific source type.
*   **processors/**: Contains the core "Brain". This is where prompt engineering lives. Separating `summarizer` and `insight_generator` allows for easier tuning of prompts.
*   **publishers/**: Handles the formatting and sending. `email_sender.py` will load `templates/email_template.html` and fill it with data.

### 4. Templates (`templates/`)
*   Decoupling logic from presentation. Use Jinja2 for HTML to easily iterate on the email design without touching Python code.

## 🚀 Getting Started Command

```bash
# 1. Create directory
mkdir insight-bot
cd insight-bot

# 2. Key files creation (example)
touch src/main.py src/graph.py requirements.txt
mkdir -p src/collectors src/processors src/publishers templates config .github/workflows
```
