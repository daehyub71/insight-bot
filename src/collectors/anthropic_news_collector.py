import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import List, Optional
import yaml

from src.collectors.base import BaseCollector
from src.state import Article


class AnthropicNewsCollector(BaseCollector):
    """Collects articles from Anthropic's website pages (news, research, economic-futures).

    Anthropic's site uses Next.js RSC (React Server Components) with Sanity CMS.
    Article data is extracted from the embedded Flight data stream. The Sanity
    ``directories`` field determines the URL path prefix (/news/ or /research/).
    Individual article pages are fetched for content via meta description tags.
    """

    BASE_URL = "https://www.anthropic.com"
    DEFAULT_PAGES = ["/news", "/research", "/economic-futures"]

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        collector_cfg = self.config.get("collector", {})
        self.lookback_days = collector_cfg.get("anthropic_lookback_days", 3)
        self.max_results = collector_cfg.get("anthropic_max_results", 10)
        self.pages = collector_cfg.get("anthropic_pages", self.DEFAULT_PAGES)

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def fetch_data(self) -> List[Article]:
        """Fetch recent articles from configured Anthropic pages."""
        cutoff = datetime.now().astimezone() - timedelta(days=self.lookback_days)
        seen_slugs: set = set()
        articles: List[Article] = []

        for page_path in self.pages:
            if len(articles) >= self.max_results:
                break

            page_url = f"{self.BASE_URL}{page_path}"
            html = self._get_page(page_url)
            if not html:
                continue

            raw_posts = self._extract_posts(html, page_path)

            for post in raw_posts:
                if len(articles) >= self.max_results:
                    break

                slug = post.get("slug", "")
                if not slug or slug in seen_slugs:
                    continue

                # Date filtering
                date_str = post.get("date")
                if date_str:
                    try:
                        dt = date_parser.parse(date_str)
                        if not dt.tzinfo:
                            dt = dt.astimezone()
                        if dt < cutoff:
                            continue
                    except (ValueError, TypeError):
                        pass

                seen_slugs.add(slug)

                # Determine URL from directories field or page path
                url_prefix = post.get("url_prefix", page_path)
                url = f"{self.BASE_URL}{url_prefix}/{slug}"

                # Fetch individual article page for content
                content = self._fetch_article_content(url)
                if not content:
                    content = post.get("summary") or post.get("title", "")

                articles.append(Article(
                    source="anthropic",
                    title=post.get("title", ""),
                    url=url,
                    content=content,
                    author="Anthropic",
                    date=date_str,
                    category=post.get("category", "anthropic-news"),
                    raw_data=post,
                ))

        print(f"[AnthropicNewsCollector] Fetched {len(articles)} articles from {len(self.pages)} pages")
        return articles

    def _get_page(self, url: str) -> Optional[str]:
        """Fetch a page with error handling."""
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (compatible; InsightBot/1.0)"
            })
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"[AnthropicNewsCollector] Failed to fetch {url}: {e}")
            return None

    def _extract_posts(self, html: str, page_path: str) -> List[dict]:
        """Extract post data from Next.js page source using multiple strategies."""
        soup = BeautifulSoup(html, 'html.parser')

        # Strategy 1: __NEXT_DATA__ JSON (traditional Next.js)
        posts = self._try_next_data(soup)
        if posts:
            return posts

        # Strategy 2: Next.js Flight/RSC data stream
        posts = self._parse_flight_data(html, page_path)
        if posts:
            return posts

        # Strategy 3: Fallback to HTML link parsing
        return self._parse_html_links(soup, page_path)

    def _try_next_data(self, soup: BeautifulSoup) -> List[dict]:
        """Try to extract posts from __NEXT_DATA__ script tag."""
        script = soup.find('script', id='__NEXT_DATA__')
        if not script or not script.string:
            return []
        try:
            data = json.loads(script.string)
            page_props = data.get("props", {}).get("pageProps", {})
            for key in ["posts", "articles", "publications", "items"]:
                items = page_props.get(key)
                if isinstance(items, list) and items:
                    return items
        except (json.JSONDecodeError, AttributeError):
            pass
        return []

    def _parse_flight_data(self, html: str, page_path: str) -> List[dict]:
        """Parse article data from Next.js RSC Flight data chunks.

        Anthropic uses Next.js RSC with Sanity CMS. Article data is embedded as
        self.__next_f.push([type, "data..."]) calls with Sanity-style objects:
          - slug: {"_type":"slug","current":"<slug-value>"}
          - date: "publishedOn":"2026-02-05T18:00:00.000Z"
          - directories: [{"value":"research"}, {"value":"news"}]
          - subjects: [{"label":"Announcements","value":"announcements"}]
        """
        chunks = re.findall(
            r'self\.__next_f\.push\(\[\d+,"(.*?)"\]\)',
            html,
            re.DOTALL,
        )
        if not chunks:
            return []

        # Concatenate and unescape all Flight data
        raw = ""
        for chunk in chunks:
            raw += chunk.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')

        posts = []
        seen_slugs = set()

        # Sanity CMS uses "publishedOn" + nested slug: {"current":"<value>"}
        for match in re.finditer(r'"publishedOn"\s*:\s*"([^"]+)"', raw):
            date_str = match.group(1)

            # Look in a surrounding window for related fields
            start = max(0, match.start() - 300)
            end = min(len(raw), match.end() + 1500)
            window = raw[start:end]

            # Sanity slug format: "slug":{"_type":"slug","current":"<value>"}
            slug_m = re.search(r'"current"\s*:\s*"([\w-]+)"', window)
            if not slug_m:
                continue

            slug = slug_m.group(1)
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            title_m = re.search(r'"title"\s*:\s*"([^"]+)"', window)
            if not title_m:
                continue

            summary_m = re.search(r'"summary"\s*:\s*"([^"]*)"', window)
            # Sanity subjects: "label":"Announcements"
            label_m = re.search(r'"label"\s*:\s*"([^"]*)"', window)

            # Determine URL prefix from Sanity directories field
            url_prefix = self._extract_url_prefix(window, page_path)

            posts.append({
                "slug": slug,
                "title": title_m.group(1),
                "date": date_str,
                "summary": summary_m.group(1) if summary_m else None,
                "category": label_m.group(1).lower() if label_m else "anthropic-news",
                "url_prefix": url_prefix,
            })

        return posts

    @staticmethod
    def _extract_url_prefix(window: str, default_path: str) -> str:
        """Extract the URL path prefix from Sanity directories field.

        Sanity stores directories as:
          "directories":[{"_key":"research","value":"research"},{"_key":"news","value":"news"}]
        The first directory value is used as the URL prefix.
        """
        dirs_m = re.search(r'"directories"\s*:\s*\[([^\]]*)\]', window)
        if dirs_m:
            first_val = re.search(r'"value"\s*:\s*"([\w-]+)"', dirs_m.group(1))
            if first_val:
                return f"/{first_val.group(1)}"
        return default_path

    def _parse_html_links(self, soup: BeautifulSoup, page_path: str) -> List[dict]:
        """Fallback: extract article links from HTML anchor tags."""
        posts = []
        seen = set()
        # Match links for both /news/ and /research/ paths
        for link in soup.find_all('a', href=re.compile(r'^/(news|research)/[\w-]+')):
            href = link.get('href', '')
            parts = href.strip('/').split('/', 1)
            if len(parts) != 2:
                continue
            prefix, slug = parts
            if not slug or slug in seen:
                continue
            seen.add(slug)

            title = link.get_text(strip=True)
            if not title:
                continue

            posts.append({
                "slug": slug,
                "title": title,
                "date": None,
                "summary": None,
                "url_prefix": f"/{prefix}",
            })
        return posts

    def _fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch content from an individual article page via meta tags.

        Meta description / og:description are reliably present in SSR pages
        even when the body content is client-rendered.
        """
        html = self._get_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # Try meta description
        for attr in [
            {'name': 'description'},
            {'property': 'og:description'},
        ]:
            tag = soup.find('meta', attrs=attr)
            if tag:
                content = tag.get('content', '').strip()
                if len(content) > 30:
                    return content

        # Try parsing visible text from main/article element
        for container_tag in ['article', 'main']:
            container = soup.find(container_tag)
            if container:
                paragraphs = container.find_all('p')
                text = ' '.join(p.get_text(strip=True) for p in paragraphs[:5])
                if len(text) > 30:
                    return text

        return None


if __name__ == "__main__":
    collector = AnthropicNewsCollector()
    items = collector.fetch_data()
    print(f"\nFetched {len(items)} articles total")
    for item in items:
        print(f"- [{item.date}] {item.title}")
        print(f"  URL: {item.url}")
        print(f"  Category: {item.category}")
        print(f"  Content: {item.content[:100]}..." if len(item.content) > 100 else f"  Content: {item.content}")
        print()
