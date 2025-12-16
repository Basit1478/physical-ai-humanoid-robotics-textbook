"""
Content extraction utilities for the ingestion service
"""
from bs4 import BeautifulSoup
import re
from typing import Optional, List
from .tokenization import clean_text


def extract_main_content(html_content: str, url: str = "") -> Optional[str]:
    """
    Extract main content from HTML, removing navigation, headers, footers, etc.

    Args:
        html_content: Raw HTML content
        url: URL of the page (for additional context if needed)

    Returns:
        Extracted main content text, or None if extraction failed
    """
    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Try to find main content area using common selectors
        main_content = None

        # Look for main content containers
        selectors_to_try = [
            'main',
            '[role="main"]',
            '.main-content',
            '.doc-content',
            '.markdown',
            '.theme-content',
            '.container',
            'article',
            '.post-content',
            '.content'
        ]

        for selector in selectors_to_try:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no specific main content found, use body
        if not main_content:
            main_content = soup.find('body')

        if not main_content:
            # If we can't find a main content area, try to extract text directly
            text = soup.get_text()
            return clean_text(text)

        # Remove common non-content elements
        for elem in main_content.find_all(['nav', 'header', 'footer', 'aside', 'form', 'button']):
            elem.decompose()

        # Remove elements that are likely navigation or UI elements
        for elem in main_content.find_all(class_=re.compile(r'navbar|nav|menu|sidebar|toc|footer|header|button|form')):
            elem.decompose()

        # Extract text from the main content
        text = main_content.get_text(separator=' ')

        # Clean up the text
        cleaned_text = clean_text(text)

        # Filter out very short or low-value content
        if len(cleaned_text) < 50:
            # Try alternative extraction methods
            return extract_with_trafilatura(html_content) or cleaned_text

        return cleaned_text

    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return None


def extract_with_trafilatura(html_content: str) -> Optional[str]:
    """
    Alternative content extraction using trafilatura as fallback.
    """
    try:
        import trafilatura
        content = trafilatura.extract(html_content,
                                    include_comments=False,
                                    include_tables=True,
                                    no_fallback=False)
        if content:
            return clean_text(content)
    except ImportError:
        # trafilatura not available
        pass
    except Exception as e:
        print(f"Error using trafilatura: {str(e)}")

    return None


def extract_page_title(html_content: str) -> str:
    """
    Extract page title from HTML content.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Try different methods to get the title
        title = ""

        # Look for title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()

        # If no title tag or it's empty, look for h1
        if not title:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text().strip()

        # If still no title, try to find title in meta tags
        if not title:
            meta_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_title:
                title = meta_title.get('content', '').strip()

        # Clean the title
        if title:
            title = re.sub(r'\s+', ' ', title)
            title = title.strip()

        return title

    except Exception:
        return ""


def extract_headings(html_content: str) -> List[dict]:
    """
    Extract headings from HTML content to provide context.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        headings = []
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            heading_text = heading.get_text().strip()
            if heading_text:
                headings.append({
                    'level': int(heading.name[1]),
                    'text': clean_text(heading_text),
                    'position': i
                })

        return headings

    except Exception:
        return []