import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz
from src.collectors.arxiv_collector import ArxivCollector
from src.collectors.rss_crawler import RSSCollector
from src.state import Article

class TestCollectors(unittest.TestCase):
    
    @patch('src.collectors.arxiv_collector.arxiv.Client')
    def test_arxiv_collector(self, MockClient):
        # Setup mock behavior
        mock_client_instance = MockClient.return_value
        
        mock_result = MagicMock()
        mock_result.title = "Test Paper"
        mock_result.published = datetime.now(pytz.utc)
        mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678"
        mock_result.summary = "Test Summary"
        
        # Proper way to mock an object with a 'name' attribute
        mock_author = MagicMock()
        mock_author.name = "John Doe"
        mock_result.authors = [mock_author]
        
        mock_result.primary_category = "cs.AI"
        mock_result.entry_id = "1234.5678"
        
        mock_client_instance.results.return_value = [mock_result]
        
        collector = ArxivCollector(config_path="config/settings.yaml")
        articles = collector.fetch_data()
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Test Paper")
        self.assertEqual(articles[0].source, "arxiv")
        self.assertEqual(articles[0].author, "John Doe")

    @patch('src.collectors.rss_crawler.feedparser.parse')
    def test_rss_collector(self, mock_parse):
        # Setup mock behavior
        mock_feed = MagicMock()
        
        # entry needs to support both attribute access (published_parsed) and .get()
        mock_entry = MagicMock()
        mock_entry.title = "Test Blog Post"
        mock_entry.link = "http://example.com/blog/1"
        mock_entry.published_parsed = datetime.now().timetuple()
        
        # Configure .get() for the entry
        def entry_get(key, default=None):
            vals = {
                'title': "Test Blog Post",
                'link': "http://example.com/blog/1",
                'summary': "Blog Summary",
                'author': "Jane Doe"
            }
            return vals.get(key, default)
        
        mock_entry.get.side_effect = entry_get
        
        mock_feed.entries = [mock_entry]
        
        # feed.feed also needs .get()
        mock_feed_metadata = MagicMock()
        mock_feed_metadata.get.return_value = "Test Blog"
        mock_feed.feed = mock_feed_metadata
        
        mock_parse.return_value = mock_feed
        
        collector = RSSCollector(config_path="config/settings.yaml")
        # Override feed urls for testing
        collector.feed_urls = ["http://example.com/rss"]
        
        articles = collector.fetch_data()
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Test Blog Post")
        self.assertEqual(articles[0].source, "rss")

if __name__ == '__main__':
    unittest.main()
