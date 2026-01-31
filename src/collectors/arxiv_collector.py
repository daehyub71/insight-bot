import arxiv
from datetime import datetime, timedelta
import yaml
from typing import List, Optional
from src.collectors.base import BaseCollector
from src.state import Article
import os

class ArxivCollector(BaseCollector):
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.categories = self.config.get("collector", {}).get("arxiv_categories", ["cs.AI", "cs.LG", "cs.CL"])
        self.lookback_days = self.config.get("collector", {}).get("arxiv_lookback_days", 3)  # 기본 3일

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def fetch_data(self) -> List[Article]:
        articles = []
        # Calculate time range: last 24 hours
        # arxiv date filtering is a bit complex in search query, usually better to fetch recent and filter
        # But we can try submittedDate
        
        # Construct query for multiple categories
        query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=100,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        cutoff_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=self.lookback_days)

        for result in client.results(search):
            published_date = result.published
            # Ensure timezone awareness compatibility
            if published_date < cutoff_date:
                 # Since it's sorted by date descending, we can stop early if we hit older papers
                 # However, ArXiv updates are batched, so safe to check a bit more or just filter
                 break
            
            # ArXiv results are already timezone aware
            if result.published >= cutoff_date:
                article = Article(
                    source="arxiv",
                    title=result.title,
                    url=result.pdf_url,
                    content=result.summary,
                    author=", ".join([a.name for a in result.authors]),
                    date=result.published.isoformat(),
                    category=result.primary_category,
                    raw_data={"entry_id": result.entry_id}
                )
                articles.append(article)
                
        return articles

if __name__ == "__main__":
    # Simple manual test
    collector = ArxivCollector()
    headers = collector.fetch_data()
    print(f"Fetched {len(headers)} papers")
    for a in headers[:3]:
        print(f"- {a.title} ({a.date})")
