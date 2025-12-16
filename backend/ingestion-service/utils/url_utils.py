"""
URL handling and crawling utilities for the ingestion service
"""
from urllib.parse import urljoin, urlparse, urlunparse
import re
from typing import Set, List, Optional
import requests
from bs4 import BeautifulSoup


def is_valid_url(url: str, base_domain: str) -> bool:
    """
    Check if a URL is valid and belongs to the same domain.
    """
    try:
        parsed = urlparse(url)
        base_parsed = urlparse(base_domain)

        # Check if it's a valid URL
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check if it's the same domain or subdomain
        if parsed.netloc == base_parsed.netloc or parsed.netloc.endswith('.' + base_parsed.netloc):
            # Check if it's not an external link
            return True

        return False
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing fragments and standardizing format.
    """
    try:
        parsed = urlparse(url)
        # Remove fragment but keep query parameters
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # fragment
        ))
        return normalized
    except Exception:
        return url


def extract_links_from_html(html_content: str, base_url: str) -> Set[str]:
    """
    Extract all valid links from HTML content.
    """
    links = set()
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)

            # Normalize the URL
            normalized_url = normalize_url(absolute_url)

            # Add to links if it's valid
            if is_valid_url(normalized_url, base_url):
                links.add(normalized_url)

    except Exception as e:
        print(f"Error extracting links from HTML: {str(e)}")

    return links


def get_robots_txt(base_url: str) -> Optional[str]:
    """
    Fetch robots.txt file from the base URL.
    """
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None


def should_crawl_url(url: str, robots_txt: Optional[str] = None) -> bool:
    """
    Check if a URL should be crawled based on robots.txt rules.
    """
    if not robots_txt:
        return True

    # Simple robots.txt parsing (in a real implementation, you'd want a more robust parser)
    # For now, we'll just check for common disallow patterns
    parsed = urlparse(url)
    path = parsed.path

    lines = robots_txt.split('\n')
    for line in lines:
        if line.strip().startswith('Disallow:'):
            disallowed_path = line.split(':', 1)[1].strip()
            if path.startswith(disallowed_path):
                return False

    return True


def is_content_page(url: str) -> bool:
    """
    Determine if a URL likely points to content that should be ingested.
    """
    # Exclude common non-content URLs
    excluded_patterns = [
        r'\.(pdf|jpg|jpeg|png|gif|svg|css|js|zip|exe|dmg|mp4|mp3|avi|mov|iso|ico)$',
        r'/tag/',
        r'/category/',
        r'/author/',
        r'/feed/',
        r'/admin/',
        r'/wp-admin/',
        r'/wp-content/',
        r'/wp-includes/',
        r'/wp-json/',
        r'/cart',
        r'/checkout',
        r'/account',
        r'/login',
        r'/register',
        r'/search',
        r'/api/',
        r'/sitemap',
        r'/robots.txt',
        r'/favicon.ico'
    ]

    # Check if URL matches any excluded pattern
    for pattern in excluded_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False

    # Include common content patterns
    included_patterns = [
        r'/docs/',
        r'/blog/',
        r'/posts/',
        r'/articles/',
        r'/tutorial/',
        r'/guide/',
        r'/manual/',
        r'/handbook/',
        r'/book/',
        r'/chapter/'
    ]

    # If it matches an included pattern, definitely include it
    for pattern in included_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    # If it doesn't match any excluded pattern and doesn't have a file extension,
    # assume it's a content page
    path = urlparse(url).path
    if not re.search(r'\.[a-zA-Z0-9]+$', path):
        return True

    # Otherwise, it's probably not a content page
    return False


def get_sitemap_urls(base_url: str) -> List[str]:
    """
    Attempt to extract URLs from the site's sitemap.
    """
    urls = []
    sitemap_urls = [
        urljoin(base_url, '/sitemap.xml'),
        urljoin(base_url, '/sitemap_index.xml'),
        urljoin(base_url, '/sitemap.txt')
    ]

    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url, timeout=30)
            if response.status_code == 200:
                content = response.text

                # Check if it's an XML sitemap index
                if '<sitemapindex' in content:
                    # Parse sitemap index
                    soup = BeautifulSoup(content, 'xml')
                    sitemaps = soup.find_all('sitemap')
                    for sitemap in sitemaps:
                        loc = sitemap.find('loc')
                        if loc:
                            urls.extend(get_sitemap_urls_from_url(loc.text))
                else:
                    # Parse regular sitemap
                    urls.extend(get_sitemap_urls_from_content(content))

                if urls:  # If we found URLs in any sitemap, break
                    break

        except Exception as e:
            print(f"Error fetching sitemap {sitemap_url}: {str(e)}")

    return urls


def get_sitemap_urls_from_url(sitemap_url: str) -> List[str]:
    """
    Extract URLs from a specific sitemap URL.
    """
    urls = []
    try:
        response = requests.get(sitemap_url, timeout=30)
        if response.status_code == 200:
            urls.extend(get_sitemap_urls_from_content(response.text))
    except Exception as e:
        print(f"Error fetching sitemap {sitemap_url}: {str(e)}")

    return urls


def get_sitemap_urls_from_content(content: str) -> List[str]:
    """
    Extract URLs from sitemap XML content.
    """
    urls = []
    try:
        soup = BeautifulSoup(content, 'xml')
        url_elements = soup.find_all('url')
        for url_elem in url_elements:
            loc = url_elem.find('loc')
            if loc:
                urls.append(loc.text)
    except Exception as e:
        print(f"Error parsing sitemap content: {str(e)}")

    return urls