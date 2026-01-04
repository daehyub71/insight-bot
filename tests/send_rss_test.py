import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.rss_crawler import RSSCollector
from src.processors.filters import RelevanceFilter
from src.processors.summarizer import Summarizer
from src.processors.insight_generator import InsightGenerator
from src.publishers.slack_bot import SlackBot

def main():
    load_dotenv()
    print("🚀 Starting RSS-only Test Run (Sending to Slack)...")
    
    # 1. Fetch (RSS Only)
    collector = RSSCollector()
    print("Fetching RSS data (last 30 days)...")
    articles = collector.fetch_data()
    print(f"Fetched {len(articles)} RSS articles.")
    
    # 2. Filter
    print("Filtering (This may take a moment)...")
    relevant_articles = []
    r_filter = RelevanceFilter()
    
    for i, art in enumerate(articles):
        # Quick check to avoid rate limits or too long wait - maybe process first 20? 
        # No, let's process all but print progress
        print(f"[{i+1}/{len(articles)}] Filtering: {art.title[:50]}...", end="\r")
        is_rel, score = r_filter.filter_article(art)
        art.relevance_score = score
        if is_rel:
            relevant_articles.append(art)
    
    print(f"\nFound {len(relevant_articles)} relevant articles.")

    # Sort and Take Top 10
    relevant_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    top_articles = relevant_articles[:10]
    
    # 3. Process
    print(f"Processing Top {len(top_articles)}...")
    summarizer = Summarizer()
    insight_gen = InsightGenerator()
    
    for art in top_articles:
        print(f"Generating Summary/Insight for: {art.title}")
        try:
            art.summary = summarizer.summarize(art)
            art.insight = insight_gen.generate_insight(art, art.summary)
        except Exception as e:
            print(f"Error processing {art.title}: {e}")
        
    # 4. Publish
    print("Sending to Slack...")
    bot = SlackBot()
    bot.send_message(top_articles)
    print("✅ Done! Check Slack.")

if __name__ == "__main__":
    main()
