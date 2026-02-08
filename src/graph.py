from langgraph.graph import StateGraph, END
from src.state import AgentState, Article
from src.collectors.arxiv_collector import ArxivCollector
from src.collectors.rss_crawler import RSSCollector
from src.collectors.anthropic_news_collector import AnthropicNewsCollector
from src.processors.filters import RelevanceFilter
from src.processors.summarizer import Summarizer
from src.processors.insight_generator import InsightGenerator
from src.publishers.email_sender import EmailSender
from src.publishers.slack_bot import SlackBot
from typing import List

class InsightBotGraph:
    def __init__(self):
        self.arxiv_collector = ArxivCollector()
        self.rss_collector = RSSCollector()
        self.anthropic_collector = AnthropicNewsCollector()
        self.filter = RelevanceFilter()
        self.summarizer = Summarizer()
        self.insight_generator = InsightGenerator()
        self.email_sender = EmailSender()
        self.slack_bot = SlackBot()

    def fetch_data_node(self, state: AgentState) -> AgentState:
        print("--- [Node] Fetching Data ---")
        arxiv_data = self.arxiv_collector.fetch_data()
        rss_data = self.rss_collector.fetch_data()
        anthropic_data = self.anthropic_collector.fetch_data()
        all_articles = arxiv_data + rss_data + anthropic_data
        print(f"Fetched {len(all_articles)} articles.")
        return {"articles": all_articles}

    def filter_data_node(self, state: AgentState) -> AgentState:
        print("--- [Node] Filtering Data ---")
        filtered_articles = []
        for article in state["articles"]:
            is_relevant, score = self.filter.filter_article(article)
            article.relevance_score = score
            if is_relevant:
                print(f"✅ Relevant ({score}): {article.title}")
                filtered_articles.append(article)
            else:
                # print(f"❌ Low Relevance ({score}): {article.title}") # Optional verbose log
                pass
        
        # Sort by relevance score descending
        filtered_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        print(f"Filtered down to {len(filtered_articles)} articles.")
        return {"articles": filtered_articles}

    def process_data_node(self, state: AgentState) -> AgentState:
        print("--- [Node] Processing (Summary & Insight) ---")
        processed_articles = []
        for article in state["articles"]:
            try:
                # Summary
                summary = self.summarizer.summarize(article)
                article.summary = summary
                
                # Insight
                insight = self.insight_generator.generate_insight(article, summary)
                article.insight = insight
                
                processed_articles.append(article)
                print(f"Processed: {article.title}")
            except Exception as e:
                print(f"Error processing {article.title}: {e}")
        
        return {"articles": processed_articles}

    def publish_data_node(self, state: AgentState) -> AgentState:
        print("--- [Node] Publishing Data ---")
        articles = state["articles"]
        if not articles:
            print("No articles to publish.")
            return state

        # Send to Email
        print("Sending Email...")
        self.email_sender.send_email(articles)

        # Send to Slack
        print("Sending Slack Notification...")
        self.slack_bot.send_message(articles)
        
        return state

    def build_graph(self):
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("fetch", self.fetch_data_node)
        workflow.add_node("filter", self.filter_data_node)
        workflow.add_node("process", self.process_data_node)
        workflow.add_node("publish", self.publish_data_node)
        
        # Add Edges
        workflow.set_entry_point("fetch")
        
        workflow.add_edge("fetch", "filter")
        workflow.add_edge("filter", "process")
        workflow.add_edge("process", "publish")
        workflow.add_edge("publish", END)

        return workflow.compile()
