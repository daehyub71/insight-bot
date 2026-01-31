# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InsightBot is an AI Daily Briefing Agent that automatically collects AI news from ArXiv and tech blogs (RSS), filters for relevance using LLM, generates Korean summaries and insights, and publishes to Slack and Email.

## Common Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline
python src/main.py

# Run unit tests
python -m pytest tests/test_collectors.py -v

# Manual test individual collectors
python src/collectors/arxiv_collector.py
python src/collectors/rss_crawler.py

# Test email sending (requires SMTP credentials)
python tests/test_email.py
```

## Architecture

LangGraph-based sequential pipeline with 4 nodes:

```
fetch → filter → process → publish
```

### Pipeline Nodes ([graph.py](src/graph.py))

1. **fetch** - Collects articles from ArXiv (last 24h papers in cs.AI/LG/CL) and RSS feeds
2. **filter** - LLM scores relevance (0-1); keeps articles scoring >= 0.7
3. **process** - Generates Korean summary (배경-방법-결과 format) and technical insight
4. **publish** - Sends to Slack (Block Kit) and Email (HTML via Jinja2)

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| State | [src/state.py](src/state.py) | `Article` dataclass and `AgentState` TypedDict |
| ArXiv Collector | [src/collectors/arxiv_collector.py](src/collectors/arxiv_collector.py) | Fetches papers via `arxiv` library |
| RSS Collector | [src/collectors/rss_crawler.py](src/collectors/rss_crawler.py) | Parses feeds via `feedparser` |
| Relevance Filter | [src/processors/filters.py](src/processors/filters.py) | LLM-based scoring |
| Summarizer | [src/processors/summarizer.py](src/processors/summarizer.py) | Different prompts for papers vs news |
| Insight Generator | [src/processors/insight_generator.py](src/processors/insight_generator.py) | One-sentence technical insight |
| Email Sender | [src/publishers/email_sender.py](src/publishers/email_sender.py) | SMTP via Gmail, uses Jinja2 template |
| Slack Bot | [src/publishers/slack_bot.py](src/publishers/slack_bot.py) | Webhook with Block Kit formatting |

## Configuration

### Environment Variables (.env)

```ini
# Required
OPENAI_API_KEY=sk-...

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=app-password
RECIPIENT_EMAIL=recipient@example.com
```

### Settings ([config/settings.yaml](config/settings.yaml))

- `collector.arxiv_categories`: ArXiv categories to monitor (default: cs.AI, cs.LG, cs.CL)
- `collector.rss_feeds`: List of RSS feed URLs
- `processing.relevance_threshold`: Filter threshold (default: 0.7)
- `processing.summary_model`: OpenAI model (default: gpt-4o-mini)

## Scheduling

GitHub Actions workflow ([.github/workflows/daily_briefing.yml](.github/workflows/daily_briefing.yml)) runs daily at 23:10 UTC (8:10 AM KST). Requires GitHub Secrets for all environment variables.
