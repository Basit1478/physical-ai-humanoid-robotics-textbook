# Research: Ingestion Pipeline for Docusaurus Website

## Overview
Research document for the backend ingestion pipeline to crawl the Physical AI & Humanoid Robotics Docusaurus website, extract content, generate embeddings, and store in Qdrant.

## Docusaurus Website Structure Analysis

### Common Docusaurus Elements
- Navigation sidebar with hierarchical structure
- Markdown/MDX content files in `/docs` directory
- Auto-generated table of contents
- Code blocks with syntax highlighting
- Inline images and diagrams
- Cross-references between pages

### Content Extraction Considerations
- Need to preserve semantic structure while removing presentation elements
- Docusaurus-specific CSS classes to identify content containers
- Common selectors for main content area: `.main-wrapper`, `.doc-markdown`, `.markdown`
- Handle both static and dynamically loaded content

## Web Crawling Approaches

### 1. Static Crawling
- Use `requests` and `BeautifulSoup` for simple static sites
- Follow links recursively from base URL
- Handle robots.txt and rate limiting

### 2. JavaScript-Rendered Content
- Use `Selenium` or `Playwright` for JavaScript-heavy sites
- Wait for dynamic content to load
- More resource-intensive but handles modern SPAs

### 3. Sitemap-Based Approach
- Check for `/sitemap.xml` to get all page URLs
- More reliable than link following
- Requires less crawling logic

## Text Extraction Techniques

### HTML Cleaning
- Remove navigation, headers, footers, sidebars
- Preserve content hierarchy (headings, paragraphs)
- Handle code blocks appropriately
- Extract alt text from images if relevant

### Libraries for Text Extraction
- `BeautifulSoup` - HTML parsing and cleaning
- `trafilatura` - web content extraction
- `newspaper3k` - article content extraction
- `readability-lxml` - content extraction similar to Firefox reader view

## Content Chunking Strategies

### Token-Based Chunking
- Target 500-1200 token range as specified
- Use tokenizers that match the embedding model
- Consider sentence boundaries to preserve context

### Semantic Chunking
- Split at paragraph or section boundaries
- Preserve related content together
- Overlap chunks to maintain context across boundaries

### Libraries for Chunking
- `langchain.text_splitter` - various splitting strategies
- `tiktoken` - token counting for OpenAI models
- Custom implementations for specific needs

## Cohere Embeddings

### API Access
- Requires Cohere API key
- Different model options available (e.g., embed-multilingual-v2.0)
- Rate limits and pricing considerations

### Embedding Process
- Batch requests for efficiency
- Handle rate limiting and retries
- Store embeddings with proper metadata

## Qdrant Vector Database

### Cloud vs Local
- Qdrant Cloud Free Tier limitations
- Collection creation and configuration
- Vector storage and indexing

### Schema Design
- Payload structure for metadata
- Vector dimension matching
- Indexing strategies for performance

## Implementation Architecture

### Pipeline Components
1. Crawler - discover and fetch pages
2. Extractor - clean and extract content
3. Chunker - split content into appropriate sizes
4. Embedder - generate vector embeddings
5. Storage - upload to Qdrant with metadata

### Error Handling
- Network timeouts and retries
- API rate limiting
- Content parsing errors
- Storage failures

## Existing Tools and Libraries

### Crawling
- `scrapy` - robust crawling framework
- `requests-html` - simple HTTP requests with JavaScript support
- `pyppeteer` - headless Chrome control

### Text Processing
- `spaCy` - advanced NLP processing
- `nltk` - natural language toolkit
- `transformers` - Hugging Face models

## Potential Challenges

### Dynamic Content
- Some Docusaurus sites load content via JavaScript
- Need to handle client-side rendering
- May require headless browser automation

### Rate Limiting
- Respect website's rate limits
- Implement backoff strategies
- Handle API limits for Cohere

### Content Structure
- Docusaurus sites may have varying structures
- Need robust selectors for content extraction
- Handle different page layouts consistently

## References
- Docusaurus documentation: https://docusaurus.io/
- Cohere embedding documentation: https://docs.cohere.com/docs/embeddings
- Qdrant documentation: https://qdrant.tech/documentation/