import os
import requests
from typing import List
from src.state import Article
from datetime import datetime

class SlackBot:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def _format_message(self, articles: List[Article]) -> dict:
        if not articles:
            return {"text": "No high-relevance updates for today."}

        blocks = []
        
        # Header
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🧠 InsightBot Daily Briefing ({datetime.now().strftime('%Y-%m-%d')})",
                "emoji": True
            }
        })
        blocks.append({"type": "divider"})

        # Articles (Limit to top 10 to avoid Slack payload limits)
        for article in articles[:10]:
            title_link = f"<{article.url}|*{article.title}*>"
            score = f"`Relevance: {article.relevance_score:.2f}`"
            source = f"_{article.source.upper()}_"
            
            summary_text = article.summary.replace("\n", " ") if article.summary else "No summary."
            # Truncate summary if too long
            if len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."

            insight_text = f"💡 *Insight:* {article.insight}" if article.insight else ""

            text_block = f"{title_link}  {score} {source}\n{summary_text}\n{insight_text}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text_block
                }
            })
            blocks.append({"type": "divider"})
            
        if len(articles) > 10:
             blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_+ {len(articles) - 10} more articles..._"
                    }
                ]
            })

        return {"blocks": blocks}

    def send_message(self, articles: List[Article]):
        if not self.webhook_url:
            print("⚠️ SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
            return

        payload = self._format_message(articles)
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("💬 Slack message sent successfully.")
            else:
                print(f"❌ Failed to send Slack message: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Error sending Slack message: {e}")
