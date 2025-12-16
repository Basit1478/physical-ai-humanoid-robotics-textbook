# Specification: Ingestion Pipeline for Docusaurus Website

## Overview
Create a backend ingestion pipeline to crawl the Physical AI & Humanoid Robotics Docusaurus website, extract book content, generate Cohere embeddings, and store vectors in Qdrant. This pipeline will enable RAG (Retrieval Augmented Generation) functionality for the textbook content.

## Target
Backend ingestion pipeline for the Physical AI & Humanoid Robotics Docusaurus website.

## Focus
Crawl all published book URLs, clean and chunk text, generate Cohere embeddings, and upload vectors + metadata into a Qdrant Cloud collection.

## Success Criteria
- All book pages crawled (intro + modules 1–4 + capstone)
- Clean text extraction with no HTML noise
- Chunks between 500–1200 tokens
- Cohere embeddings generated for each chunk
- Qdrant collection created with correct schema
- Idempotent ingestion with logging

## Constraints
- Python only
- Cohere embeddings
- Qdrant Cloud Free Tier

## Not Building
- Retrieval logic or agents

## Timeline
3 days

## User Scenarios & Testing

### Scenario 1: Content Ingestion
As a system administrator, I want to run the ingestion pipeline so that all content from the Docusaurus website is available for RAG queries.

### Scenario 2: Content Update
As a content maintainer, I want the system to handle updates to existing content without duplicating vectors.

### Scenario 3: Error Handling
As a developer, I want the system to log failures and continue processing so that partial content ingestion is still valuable.

## Functional Requirements

### FR-1: Website Crawling
The system SHALL crawl all published book pages from the Docusaurus website including:
- Introduction page
- Module 1-4 pages
- Capstone project page
- Any additional content pages

### FR-2: Content Extraction
The system SHALL extract clean text content from HTML pages, removing:
- HTML tags and attributes
- Navigation elements
- Footer information
- Code syntax highlighting containers
- Table of contents

### FR-3: Content Chunking
The system SHALL split extracted text into chunks between 500-1200 tokens with:
- Overlap of 100 tokens between adjacent chunks
- Preservation of semantic boundaries
- Proper sentence boundaries where possible

### FR-4: Embedding Generation
The system SHALL generate Cohere embeddings for each text chunk using the Cohere API.

### FR-5: Vector Storage
The system SHALL store embeddings and metadata in Qdrant Cloud with proper schema including:
- Document ID
- Source URL
- Chunk text
- Embedding vector
- Metadata (page title, section, etc.)

### FR-6: Idempotent Processing
The system SHALL avoid duplicate entries when reprocessing the same content by using:
- Document URL as unique identifier
- Content hash comparison
- Update existing records instead of creating duplicates

### FR-7: Logging and Monitoring
The system SHALL log all ingestion activities including:
- Pages crawled successfully
- Pages that failed to crawl
- Processing time per page
- Embedding generation status

## Non-Functional Requirements

### NFR-1: Performance
- Process 100 pages within 30 minutes
- Generate embeddings at rate of 10 chunks per minute

### NFR-2: Reliability
- Handle network timeouts gracefully
- Retry failed requests up to 3 times
- Continue processing when individual pages fail

### NFR-3: Scalability
- Support up to 1000 pages in the website
- Handle content updates without reprocessing entire dataset

## Key Entities

### Document
- document_id (unique identifier)
- source_url (original page URL)
- title (page title)
- content (clean extracted text)
- hash (content hash for change detection)

### Chunk
- chunk_id (unique identifier)
- document_id (reference to parent document)
- text (chunked content, 500-1200 tokens)
- token_count (number of tokens in chunk)
- position (order within document)

### Embedding
- embedding_id (unique identifier)
- chunk_id (reference to parent chunk)
- vector (Cohere embedding vector)
- metadata (additional context information)

## Assumptions
- Docusaurus website is publicly accessible
- Website structure remains consistent
- Cohere API is available and responsive
- Qdrant Cloud Free Tier provides sufficient capacity for the project

## Dependencies
- Cohere API access
- Qdrant Cloud account
- Docusaurus website accessibility