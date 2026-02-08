import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz
from src.collectors.arxiv_collector import ArxivCollector
from src.collectors.rss_crawler import RSSCollector
from src.collectors.anthropic_news_collector import AnthropicNewsCollector
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

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_news_collector(self, mock_get_page):
        """Test AnthropicNewsCollector parses Sanity CMS Flight data and fetches article content."""
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # Mock the news listing page with Sanity CMS-style Flight data
        flight_html = f'''
        <html><head></head><body>
        <script>self.__next_f.push([1,"test data"])</script>
        <script>self.__next_f.push([1,"\\"publishedOn\\":\\"{now}\\",\\"slug\\":{{\\"_type\\":\\"slug\\",\\"current\\":\\"introducing-test-model\\"}},\\"directories\\":[{{\\"value\\":\\"news\\"}}],\\"subjects\\":[{{\\"label\\":\\"Announcements\\"}}],\\"title\\":\\"Introducing Test Model\\",\\"summary\\":\\"A new AI model announcement\\""])</script>
        </body></html>
        '''

        # Mock individual article page with meta description
        article_html = '''
        <html><head>
        <meta name="description" content="We are excited to announce Test Model, a breakthrough in AI capabilities with improved reasoning and safety." />
        </head><body></body></html>
        '''

        def side_effect(url):
            if url == "https://www.anthropic.com/news":
                return flight_html
            elif "introducing-test-model" in url:
                return article_html
            # Return empty pages for /research and /economic-futures
            return "<html><body></body></html>"

        mock_get_page.side_effect = side_effect

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        articles = collector.fetch_data()

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].source, "anthropic")
        self.assertEqual(articles[0].title, "Introducing Test Model")
        self.assertEqual(articles[0].url, "https://www.anthropic.com/news/introducing-test-model")
        self.assertIn("breakthrough", articles[0].content)

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_multi_page_collection(self, mock_get_page):
        """Test collector collects from multiple pages and deduplicates."""
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        news_html = f'''
        <html><body>
        <script>self.__next_f.push([1,"\\"publishedOn\\":\\"{now}\\",\\"slug\\":{{\\"_type\\":\\"slug\\",\\"current\\":\\"model-release\\"}},\\"directories\\":[{{\\"value\\":\\"news\\"}}],\\"subjects\\":[{{\\"label\\":\\"Announcements\\"}}],\\"title\\":\\"Model Release\\",\\"summary\\":\\"New model\\""])</script>
        </body></html>
        '''

        research_html = f'''
        <html><body>
        <script>self.__next_f.push([1,"\\"publishedOn\\":\\"{now}\\",\\"slug\\":{{\\"_type\\":\\"slug\\",\\"current\\":\\"safety-paper\\"}},\\"directories\\":[{{\\"value\\":\\"research\\"}}],\\"subjects\\":[{{\\"label\\":\\"Research\\"}}],\\"title\\":\\"Safety Research Paper\\",\\"summary\\":\\"AI safety findings\\""])</script>
        </body></html>
        '''

        # economic-futures page has the same slug as news (should be deduplicated)
        econ_html = f'''
        <html><body>
        <script>self.__next_f.push([1,"\\"publishedOn\\":\\"{now}\\",\\"slug\\":{{\\"_type\\":\\"slug\\",\\"current\\":\\"model-release\\"}},\\"directories\\":[{{\\"value\\":\\"news\\"}}],\\"subjects\\":[{{\\"label\\":\\"News\\"}}],\\"title\\":\\"Model Release\\",\\"summary\\":\\"New model\\""])</script>
        </body></html>
        '''

        article_html = '''
        <html><head>
        <meta name="description" content="Detailed article content for testing the multi-page collector." />
        </head><body></body></html>
        '''

        def side_effect(url):
            if url == "https://www.anthropic.com/news":
                return news_html
            elif url == "https://www.anthropic.com/research":
                return research_html
            elif url == "https://www.anthropic.com/economic-futures":
                return econ_html
            return article_html

        mock_get_page.side_effect = side_effect

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        articles = collector.fetch_data()

        # 2 unique articles (model-release + safety-paper), not 3
        self.assertEqual(len(articles), 2)
        slugs = {a.raw_data["slug"] for a in articles}
        self.assertEqual(slugs, {"model-release", "safety-paper"})

        # Check URL prefixes from directories
        urls = {a.url for a in articles}
        self.assertIn("https://www.anthropic.com/news/model-release", urls)
        self.assertIn("https://www.anthropic.com/research/safety-paper", urls)

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_research_url_prefix(self, mock_get_page):
        """Test that research articles get /research/ URL prefix from directories field."""
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        research_html = f'''
        <html><body>
        <script>self.__next_f.push([1,"\\"publishedOn\\":\\"{now}\\",\\"slug\\":{{\\"_type\\":\\"slug\\",\\"current\\":\\"alignment-study\\"}},\\"directories\\":[{{\\"value\\":\\"research\\"}},{{\\"value\\":\\"news\\"}}],\\"subjects\\":[{{\\"label\\":\\"Research\\"}}],\\"title\\":\\"Alignment Study\\",\\"summary\\":\\"New alignment research\\""])</script>
        </body></html>
        '''

        article_html = '''
        <html><head>
        <meta name="description" content="This paper presents new findings on AI alignment techniques." />
        </head><body></body></html>
        '''

        def side_effect(url):
            if url == "https://www.anthropic.com/research":
                return research_html
            elif "alignment-study" in url:
                return article_html
            return "<html><body></body></html>"

        mock_get_page.side_effect = side_effect

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        # Only test /research page
        collector.pages = ["/research"]
        articles = collector.fetch_data()

        self.assertEqual(len(articles), 1)
        # First directory value is "research", so URL should use /research/
        self.assertEqual(articles[0].url, "https://www.anthropic.com/research/alignment-study")

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_news_collector_empty_page(self, mock_get_page):
        """Test collector handles empty/broken pages gracefully."""
        mock_get_page.return_value = "<html><body>No data</body></html>"

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        articles = collector.fetch_data()

        self.assertEqual(len(articles), 0)

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_news_collector_network_error(self, mock_get_page):
        """Test collector handles network failures gracefully."""
        mock_get_page.return_value = None

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        articles = collector.fetch_data()

        self.assertEqual(len(articles), 0)

    @patch('src.collectors.anthropic_news_collector.AnthropicNewsCollector._get_page')
    def test_anthropic_news_collector_html_fallback(self, mock_get_page):
        """Test collector falls back to HTML link parsing."""
        article_html = '''
        <html><head>
        <meta name="description" content="A detailed description of the new feature announcement from Anthropic." />
        </head><body></body></html>
        '''

        listing_html = '''
        <html><body>
        <a href="/news/some-feature-release">Some Feature Release</a>
        <a href="/news/another-update">Another Update</a>
        </body></html>
        '''

        def side_effect(url):
            if url == "https://www.anthropic.com/news":
                return listing_html
            return article_html

        mock_get_page.side_effect = side_effect

        collector = AnthropicNewsCollector(config_path="config/settings.yaml")
        collector.pages = ["/news"]  # Only test one page for fallback
        articles = collector.fetch_data()

        self.assertGreaterEqual(len(articles), 1)
        self.assertEqual(articles[0].source, "anthropic")


if __name__ == '__main__':
    unittest.main()
