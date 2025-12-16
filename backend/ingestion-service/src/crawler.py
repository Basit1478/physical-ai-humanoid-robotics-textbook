"""
Async crawler service for the ingestion pipeline
"""
import asyncio
import httpx
from typing import Set, List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging
import time
from bs4 import BeautifulSoup
import hashlib

from config.settings import (
    DOCUSAURUS_BASE_URL, CRAWLER_DELAY, MAX_CONCURRENT_REQUESTS,
    REQUEST_TIMEOUT, RETRY_ATTEMPTS, RETRY_DELAY
)
from utils.url_utils import (
    is_valid_url, normalize_url, extract_links_from_html,
    should_crawl_url, is_content_page, get_sitemap_urls
)
from utils.content_extraction import extract_main_content, extract_page_title
from utils.tokenization import chunk_text, clean_text


class AsyncCrawler:
    def __init__(self):
        self.base_url = DOCUSAURUS_BASE_URL
        self.delay = CRAWLER_DELAY
        self.max_concurrent = MAX_CONCURRENT_REQUESTS
        self.timeout = REQUEST_TIMEOUT
        self.retry_attempts = RETRY_ATTEMPTS
        self.retry_delay = RETRY_DELAY

        # Use httpx for async requests
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Docusaurus-Ingestion-Bot/1.0; +http://example.com/bot)'
            }
        )

        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()
        self.content_pages: List[Dict] = []
        self.failed_urls: List[Dict] = []

        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def crawl_site(self) -> List[Dict]:
        """
        Main method to crawl the entire site.
        """
        self.logger.info(f"Starting crawl of {self.base_url}")

        # First, try to get URLs from sitemap
        sitemap_urls = get_sitemap_urls(self.base_url)
        self.logger.info(f"Found {len(sitemap_urls)} URLs from sitemap")

        # If no sitemap URLs found, crawl by following links
        if not sitemap_urls:
            self.logger.info("No sitemap found, crawling by following links")
            await self.crawl_by_following_links()
        else:
            # Process sitemap URLs
            for url in sitemap_urls:
                if is_content_page(url) and is_valid_url(url, self.base_url):
                    await self.process_url(url)

        self.logger.info(f"Crawl completed. Processed {len(self.content_pages)} content pages, {len(self.failed_urls)} failed.")
        return self.content_pages

    async def crawl_by_following_links(self):
        """
        Crawl by following links from the base URL.
        """
        urls_to_visit = {self.base_url}

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            normalized_url = normalize_url(current_url)

            if normalized_url in self.visited_urls:
                continue

            self.visited_urls.add(normalized_url)

            if not should_crawl_url(normalized_url) or not is_content_page(normalized_url):
                continue

            # Process the URL
            page_data = await self.process_url(normalized_url)

            if page_data:
                # Extract links from the page content
                try:
                    soup = BeautifulSoup(page_data['html_content'], 'html.parser')
                    links = extract_links_from_html(str(soup), self.base_url)

                    # Add new links to visit if they're valid content pages
                    for link in links:
                        normalized_link = normalize_url(link)
                        if (is_valid_url(normalized_link, self.base_url) and
                            is_content_page(normalized_link) and
                            normalized_link not in self.visited_urls):
                            urls_to_visit.add(normalized_link)
                except Exception as e:
                    self.logger.error(f"Error extracting links from {normalized_url}: {str(e)}")

            # Respect rate limiting
            await asyncio.sleep(self.delay)

    async def process_url(self, url: str) -> Optional[Dict]:
        """
        Process a single URL - fetch, extract content, and store.
        """
        async with self.semaphore:  # Limit concurrent requests
            for attempt in range(self.retry_attempts):
                try:
                    self.logger.info(f"Processing URL: {url} (attempt {attempt + 1})")

                    response = await self.client.get(url)

                    if response.status_code == 200:
                        html_content = response.text

                        # Extract main content
                        main_content = extract_main_content(html_content, url)

                        if main_content and len(main_content.strip()) > 50:  # Filter out very short content
                            page_title = extract_page_title(html_content)

                            page_data = {
                                'url': url,
                                'title': page_title,
                                'content': main_content,
                                'html_content': html_content,
                                'content_hash': hashlib.md5(main_content.encode()).hexdigest(),
                                'fetched_at': time.time()
                            }

                            self.content_pages.append(page_data)
                            self.logger.info(f"Successfully processed: {url}")
                            return page_data
                        else:
                            self.logger.warning(f"No substantial content found at: {url}")
                            return None
                    else:
                        self.logger.warning(f"Failed to fetch {url}: Status {response.status_code}")

                except httpx.RequestError as e:
                    self.logger.error(f"Request error for {url} (attempt {attempt + 1}): {str(e)}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        self.failed_urls.append({
                            'url': url,
                            'error': str(e),
                            'attempted_at': time.time()
                        })

                except Exception as e:
                    self.logger.error(f"Unexpected error for {url} (attempt {attempt + 1}): {str(e)}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        self.failed_urls.append({
                            'url': url,
                            'error': str(e),
                            'attempted_at': time.time()
                        })

            return None

    def get_crawled_content(self) -> List[Dict]:
        """
        Get the list of crawled content pages.
        """
        return self.content_pages

    def get_failed_urls(self) -> List[Dict]:
        """
        Get the list of URLs that failed to crawl.
        """
        return self.failed_urls

    def get_crawl_summary(self) -> Dict:
        """
        Get a summary of the crawl operation.
        """
        return {
            'total_urls_visited': len(self.visited_urls),
            'successful_pages': len(self.content_pages),
            'failed_pages': len(self.failed_urls),
            'start_time': getattr(self, '_start_time', None),
            'end_time': time.time() if hasattr(self, '_start_time') else None
        }


class ContentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_content(self, crawled_data: List[Dict],
                       min_tokens: int = 500,
                       max_tokens: int = 1200,
                       overlap: int = 100) -> List[Dict]:
        """
        Process crawled content by chunking and preparing for embedding.
        """
        processed_chunks = []

        for page_data in crawled_data:
            content = page_data['content']

            # Chunk the content
            chunks = chunk_text(content, min_tokens, max_tokens, overlap)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{page_data['content_hash']}_chunk_{i}"

                processed_chunk = {
                    'chunk_id': chunk_id,
                    'url': page_data['url'],
                    'title': page_data['title'],
                    'text': chunk['text'],
                    'token_count': chunk['token_count'],
                    'position': i,
                    'page_hash': page_data['content_hash'],
                    'source_metadata': {
                        'original_url': page_data['url'],
                        'title': page_data['title'],
                        'position_in_page': i,
                        'total_chunks_in_page': len(chunks)
                    }
                }

                processed_chunks.append(processed_chunk)

        self.logger.info(f"Processed {len(crawled_data)} pages into {len(processed_chunks)} chunks")
        return processed_chunks