import feedparser
from datetime import datetime, timedelta
from dateutil import parser
import yaml
from typing import List
from src.collectors.base import BaseCollector
from src.state import Article
import time

class RSSCollector(BaseCollector):
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.feed_urls = self.config.get("collector", {}).get("rss_feeds", [])

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def fetch_data(self) -> List[Article]:
        articles = []
        cutoff_date = datetime.now().astimezone() - timedelta(days=1)

        for url in self.feed_urls:
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                # Normalize date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime.fromtimestamp(time.mktime(entry.published_parsed)).astimezone()
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime.fromtimestamp(time.mktime(entry.updated_parsed)).astimezone()
                
                if published and published >= cutoff_date:
                    # Clean summary (remove HTML if simple) - for now keep raw
                    summary = entry.get('summary', '') or entry.get('description', '')
                    
                    article = Article(
                        source="rss",
                        title=entry.get('title', 'No Title'),
                        url=entry.get('link', ''),
                        content=summary,
                        author=entry.get('author', feed.feed.get('title', 'Unknown')),
                        date=published.isoformat(),
                        category="blog", # Generic category for RSS
                        raw_data={"feed_url": url}
                    )
                    articles.append(article)
        
        return articles

if __name__ == "__main__":
    collector = RSSCollector()
    items = collector.fetch_data()
    print(f"Fetched {len(items)} posts")
    for item in items:
        print(f"- {item.title} ({item.date})")
