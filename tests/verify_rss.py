from dotenv import load_dotenv
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.rss_crawler import RSSCollector

def test_rss():
    load_dotenv()
    print("📰 Testing RSS Collector (Tech Blogs)...")
    print("Looking back 30 days to ensure we find blog posts.\n")
    
    collector = RSSCollector()
    articles = collector.fetch_data()
    
    print(f"Found {len(articles)} articles from RSS feeds.\n")
    
    for idx, article in enumerate(articles, 1):
        print(f"[{idx}] {article.title}")
        print(f"    Source: {article.source}")
        print(f"    Date: {article.date}")
        print(f"    URL: {article.url}\n")

if __name__ == "__main__":
    test_rss()
