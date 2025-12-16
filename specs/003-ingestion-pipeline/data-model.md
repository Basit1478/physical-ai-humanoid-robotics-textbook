# Data Model: Ingestion Pipeline

## Overview
Data model for the backend ingestion pipeline that crawls Docusaurus website, extracts book content, generates Cohere embeddings, and stores vectors in Qdrant.

## Document Entity

### Attributes
- `document_id`: UUID (Primary Key)
  - Unique identifier for each crawled document
  - Generated automatically upon creation
- `source_url`: String (URL)
  - Original URL of the crawled page
  - Required, unique
- `title`: String
  - Page title extracted from HTML
  - Required
- `content`: Text
  - Clean, extracted text content
  - Required
- `hash`: String (SHA-256)
  - Content hash for change detection
  - Required, indexed
- `created_at`: DateTime (UTC)
  - Timestamp of document creation
  - Required
- `updated_at`: DateTime (UTC)
  - Timestamp of last update
  - Required
- `status`: Enum
  - Current processing status: ['pending', 'processing', 'processed', 'failed']
  - Default: 'pending'
- `metadata`: JSON
  - Additional metadata from page (author, tags, etc.)
  - Optional

### Relationships
- One-to-Many: Document to Chunks

## Chunk Entity

### Attributes
- `chunk_id`: UUID (Primary Key)
  - Unique identifier for each text chunk
  - Generated automatically upon creation
- `document_id`: UUID (Foreign Key)
  - Reference to parent document
  - Required, indexed
- `text`: Text
  - Chunked content (500-1200 tokens)
  - Required
- `token_count`: Integer
  - Number of tokens in the chunk
  - Required, positive
- `position`: Integer
  - Sequential position within document
  - Required, starts from 0
- `hash`: String (SHA-256)
  - Hash of the chunk text
  - Required, unique
- `created_at`: DateTime (UTC)
  - Timestamp of chunk creation
  - Required

### Relationships
- Many-to-One: Chunk to Document
- One-to-One: Chunk to Embedding

## Embedding Entity

### Attributes
- `embedding_id`: UUID (Primary Key)
  - Unique identifier for each embedding
  - Generated automatically upon creation
- `chunk_id`: UUID (Foreign Key)
  - Reference to parent chunk
  - Required, unique
- `vector`: Array<Float>
  - The embedding vector values
  - Required (dimension depends on model)
- `model`: String
  - Name of the embedding model used
  - Required (e.g., 'embed-multilingual-v2.0')
- `created_at`: DateTime (UTC)
  - Timestamp of embedding creation
  - Required

### Relationships
- Many-to-One: Embedding to Chunk

## Processing Log Entity

### Attributes
- `log_id`: UUID (Primary Key)
  - Unique identifier for each log entry
  - Generated automatically upon creation
- `document_url`: String (URL)
  - URL of the document being processed
  - Required
- `operation`: Enum
  - Type of operation: ['crawl', 'extract', 'chunk', 'embed', 'store']
  - Required
- `status`: Enum
  - Operation status: ['success', 'failed', 'in_progress']
  - Required
- `message`: Text
  - Detailed log message
  - Optional
- `timestamp`: DateTime (UTC)
  - When the operation occurred
  - Required
- `duration_ms`: Integer
  - Duration of the operation in milliseconds
  - Optional

## Qdrant Collection Schema

### Collection Name
- `textbook_content`

### Vector Configuration
- Size: 1024 (for Cohere embed-multilingual-v2.0)
- Distance: Cosine

### Payload Schema
```
{
  "document_id": "uuid",
  "chunk_id": "uuid",
  "source_url": "string",
  "title": "string",
  "text": "string",
  "position": "integer",
  "token_count": "integer",
  "created_at": "string (ISO date)",
  "metadata": "object"
}
```

### Indexes
- `source_url`: Keyword index for filtering by source
- `document_id`: Keyword index for document-level operations
- `position`: Integer index for ordering chunks

## Constraints and Validation

### Document Constraints
- `source_url` must be a valid URL format
- `hash` must be a valid SHA-256 hex string
- `token_count` must be positive
- `position` must be non-negative

### Chunk Constraints
- `text` length must be appropriate for target token count (500-1200 tokens)
- `position` must be sequential within document (no gaps)
- `token_count` must be between 500-1200 for main chunks

### Embedding Constraints
- Vector dimensions must match the model specification
- `chunk_id` must reference an existing chunk
- One embedding per chunk

## Performance Considerations

### Indexing Strategy
- Index `source_url` for fast lookups by URL
- Index `document_id` for document-level operations
- Composite index on (`document_id`, `position`) for ordered retrieval

### Partitioning
- Consider partitioning by document type or date if dataset grows large
- For initial implementation, single collection should suffice

## Data Flow

### Ingestion Process
1. Crawl URL → Create Document record (status: pending)
2. Extract content → Update Document record (status: processing, content populated)
3. Chunk content → Create multiple Chunk records
4. Generate embeddings → Create Embedding records
5. Store in Qdrant → Update Document record (status: processed)

### Update Process
1. Recrawl URL → Compare content hash
2. If different, update Document and create new Chunks/Embeddings
3. Update Qdrant collection with new vectors
4. Mark old vectors as obsolete (or remove)

## Data Integrity

### Referential Integrity
- Foreign key constraints ensure valid relationships
- Cascading deletes: when Document is deleted, Chunks and Embeddings are deleted
- Unique constraints prevent duplicate processing

### Audit Trail
- Created/updated timestamps on all entities
- Processing logs capture operation history
- Content hashes enable change detection